import logging
import asyncio
import uuid
import os
import time
import re
from typing import List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader, UnstructuredImageLoader
)
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler("rag_pipeline.log", mode="a", encoding="utf-8")]
)
logger = logging.getLogger(__name__)

# -------------------------------
# Environment variables
# -------------------------------
load_dotenv(override=True)
gemini_api_key = os.getenv("GEMINI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI(title="Async RAG API")

# -------------------------------
# Global reusable objects
# -------------------------------
EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=gemini_api_key, temperature=0.1)
PC = Pinecone(api_key=pinecone_api_key)
INDEX_NAME = "hugging-face-index"

# Ensure Pinecone index exists
if INDEX_NAME not in PC.list_indexes().names():
    logger.info("Creating new index...")
    PC.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(10)
else:
    logger.info("Index already exists")

# -------------------------------
# Semantic Chunking
# -------------------------------
def semantic_chunk_documents(docs):
    """Apply semantic chunking based on paragraph breaks and topic boundaries."""
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

# -------------------------------
# Document loading
# -------------------------------
def load_documents(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".pptx":
        loader = UnstructuredPowerPointLoader(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        loader = UnstructuredImageLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    return loader.load()

def chunk_documents(docs):
    # Use semantic chunking instead of character-based chunking
    chunks = semantic_chunk_documents(docs)
    logger.info(f"Generated {len(chunks)} chunks")
    return chunks

# -------------------------------
# Async document processing
# -------------------------------
async def process_and_store_documents(file_paths: List[str], batch_size=64):
    all_docs = []
    for fp in file_paths:
        all_docs.extend(load_documents(fp))
        logger.info(f"Loaded {len(all_docs)} pages from {fp}")

    chunks = chunk_documents(all_docs)
    logger.info(f"Created {len(chunks)} chunks from all documents")

    # Save chunks locally for debugging
    with open("chunks.txt", "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"\n--- Chunk {i+1} ---\n")
            f.write(chunk.page_content + "\n")

    namespace = uuid.uuid4().hex
    logger.info(f"Using namespace: {namespace}")

    # Async batch upsertion
    async def upsert_batch(batch_chunks, batch_number, total_batches):
        PineconeVectorStore.from_documents(batch_chunks, EMBEDDINGS, namespace=namespace, index_name=INDEX_NAME)
        logger.info(f"Stored batch {batch_number}/{total_batches}")

    tasks = []
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        batch_number = i // batch_size + 1
        tasks.append(upsert_batch(batch_chunks, batch_number, total_batches))

    await asyncio.gather(*tasks)
    logger.info("✅ All embeddings stored in Pinecone")
    return namespace

# -------------------------------
# Async query retrieval
# -------------------------------
async def retrieve_and_answer(query: str, namespace: str):
    vector_store = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=EMBEDDINGS,
        namespace=namespace
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 5, "namespace": namespace})

    prompt_template = """You are a helpful assistant that answers questions based on the provided context. 
Use only the information from the context to answer the question. If the answer is not available in the context, 
say "I cannot find this information in the provided documents."

Context:
{context}

Question: {question}

Answer: """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    qa_chain = RetrievalQA.from_chain_type(
        llm=LLM,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    try:
        result = qa_chain.invoke({"query": query})
        sources = [{"snippet": doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else "")}
                   for doc in result['source_documents']]
        return {"answer": result['result'], "sources": sources}
    except Exception as e:
        logger.error(f"❌ Error processing query: {e}")
        return {"answer": None, "sources": [], "error": str(e)}

# -------------------------------
# API Endpoints
# -------------------------------
@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    saved_files = []
    try:
        for file in files:
            save_path = os.path.join("uploads", file.filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(await file.read())
            saved_files.append(save_path)
        namespace = await process_and_store_documents(saved_files)
        return {"status": "success", "namespace": namespace}
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

@app.post("/query")
async def query_documents(namespace: str = Form(...), query: str = Form(...)):
    result = await retrieve_and_answer(query, namespace)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
