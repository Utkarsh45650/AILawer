import logging
import asyncio
import uuid
import os
import time
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add the Final folder to the path to reuse existing RAG components
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "Final"))

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

from app.database.json_db import db
from app.services.subscription import SubscriptionService

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RAGService:
    """Enhanced RAG service for legal document processing and retrieval"""
    
    def __init__(self):
        self.subscription_service = SubscriptionService(db)
        
        # RAG Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        # Initialize components with error handling
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("✅ Embeddings model loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load embeddings model: {e}")
            self.embeddings = None
            
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro-latest", 
                google_api_key=self.gemini_api_key, 
                temperature=0.1
            )
            logger.info("✅ Gemini LLM initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Gemini LLM: {e}")
            self.llm = None
        
        # Initialize Pinecone
        if self.pinecone_api_key:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self.index_name = "legalai-index"
            self._ensure_pinecone_index()
        else:
            logger.warning("Pinecone API key not found. RAG functionality will be limited.")
            self.pc = None
    
    def _ensure_pinecone_index(self):
        """Ensure Pinecone index exists"""
        try:
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # For all-MiniLM-L6-v2
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
                time.sleep(10)
            else:
                logger.info(f"Pinecone index '{self.index_name}' already exists")
        except Exception as e:
            logger.error(f"Error setting up Pinecone index: {e}")
    
    def semantic_chunk_documents(self, docs: List[Document]) -> List[Document]:
        """Apply semantic chunking based on paragraph breaks and topic boundaries"""
        semantic_chunks = []
        
        for doc in docs:
            text = doc.page_content
            
            # Split by double newlines (paragraph breaks) first
            paragraphs = text.split('\n\n')
            
            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                    
                # If adding this paragraph would exceed 2000 chars, save current chunk
                if len(current_chunk) + len(para) > 2000 and current_chunk:
                    # Add overlap by including last sentence from previous chunk
                    sentences = re.split(r'[.!?]+', current_chunk)
                    overlap = sentences[-1].strip() if len(sentences) > 1 else ""
                    
                    semantic_chunks.append(Document(
                        page_content=current_chunk.strip(),
                        metadata=doc.metadata
                    ))
                    
                    # Start new chunk with overlap
                    current_chunk = overlap + " " + para if overlap else para
                else:
                    current_chunk += " " + para if current_chunk else para
            
            # Add the last chunk
            if current_chunk.strip():
                semantic_chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata=doc.metadata
                ))
        
        # Filter out very small chunks
        semantic_chunks = [chunk for chunk in semantic_chunks if len(chunk.page_content) > 100]
        
        logger.info(f"Generated {len(semantic_chunks)} semantic chunks")
        return semantic_chunks
    
    def load_documents(self, file_path: str) -> List[Document]:
        """Load documents from file path"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        return loader.load()
    
    async def process_and_store_documents(
        self, 
        file_paths: List[str], 
        user_id: str,
        batch_size: int = 64
    ) -> Dict[str, Any]:
        """Process and store documents in RAG system"""
        
        # Check if user has access to RAG functionality
        if not self.subscription_service.check_feature_access(user_id, "document_upload"):
            return {
                "success": False,
                "error": "Document upload not available for your subscription tier"
            }
        
        if not self.pc:
            return {
                "success": False,
                "error": "Pinecone not configured. Please add PINECONE_API_KEY to environment."
            }
            
        if not self.embeddings:
            return {
                "success": False,
                "error": "Embeddings model not available. Please check network connection."
            }
        
        try:
            # Load all documents
            all_docs = []
            for fp in file_paths:
                docs = self.load_documents(fp)
                all_docs.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from {fp}")
            
            # Create semantic chunks
            chunks = self.semantic_chunk_documents(all_docs)
            logger.info(f"Created {len(chunks)} chunks from all documents")
            
            # Create unique namespace for this document set
            namespace = f"user_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Store in Pinecone in batches
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i+batch_size]
                batch_number = i // batch_size + 1
                
                PineconeVectorStore.from_documents(
                    batch_chunks, 
                    self.embeddings, 
                    namespace=namespace, 
                    index_name=self.index_name
                )
                logger.info(f"Stored batch {batch_number}/{total_batches}")
            
            # Store namespace info in database
            document_set = {
                "id": namespace,
                "user_id": user_id,
                "file_paths": file_paths,
                "chunk_count": len(chunks),
                "created_at": time.time(),
                "status": "ready"
            }
            db.store_document_set(document_set)
            
            logger.info(f"✅ Successfully processed and stored documents for user {user_id}")
            return {
                "success": True,
                "namespace": namespace,
                "chunks_created": len(chunks),
                "message": "Documents successfully processed and indexed"
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing documents: {e}")
            return {
                "success": False,
                "error": f"Error processing documents: {str(e)}"
            }
    
    async def query_documents(
        self, 
        query: str, 
        namespace: str, 
        user_id: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """Query documents using RAG"""
        
        if not self.pc:
            return {
                "success": False,
                "error": "Pinecone not configured"
            }
            
        if not self.embeddings:
            return {
                "success": False,
                "error": "Embeddings model not available"
            }
            
        if not self.llm:
            return {
                "success": False,
                "error": "LLM not available"
            }
        
        try:
            # Verify user has access to this namespace
            document_set = db.get_document_set(namespace)
            if not document_set or document_set.get("user_id") != user_id:
                return {
                    "success": False,
                    "error": "Document set not found or access denied"
                }
            
            # Create vector store for querying
            vector_store = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace=namespace
            )
            
            retriever = vector_store.as_retriever(
                search_kwargs={"k": k, "namespace": namespace}
            )
            
            # Legal-specific prompt template
            prompt_template = """You are a legal AI assistant that answers questions based on the provided legal documents. 
Use only the information from the context to answer the question. Be precise and cite relevant sections when possible.
If the answer is not available in the provided documents, say "I cannot find this information in the provided documents."

Legal Context:
{context}

Question: {question}

Legal Analysis: """

            prompt = PromptTemplate(
                template=prompt_template, 
                input_variables=["context", "question"]
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
            # Execute query
            result = qa_chain.invoke({"query": query})
            
            # Format sources
            sources = []
            for doc in result['source_documents']:
                sources.append({
                    "content": doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""),
                    "metadata": doc.metadata
                })
            
            return {
                "success": True,
                "answer": result['result'],
                "sources": sources,
                "namespace": namespace
            }
            
        except Exception as e:
            logger.error(f"❌ Error querying documents: {e}")
            return {
                "success": False,
                "error": f"Error querying documents: {str(e)}"
            }
    
    def get_user_document_sets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all document sets for a user"""
        return db.get_user_document_sets(user_id)
    
    def delete_document_set(self, namespace: str, user_id: str) -> Dict[str, Any]:
        """Delete a document set"""
        try:
            document_set = db.get_document_set(namespace)
            if not document_set or document_set.get("user_id") != user_id:
                return {
                    "success": False,
                    "error": "Document set not found or access denied"
                }
            
            # Note: In production, you'd also want to delete from Pinecone
            # For now, we'll just mark as deleted in our database
            db.delete_document_set(namespace)
            
            return {
                "success": True,
                "message": "Document set deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error deleting document set: {str(e)}"
            }