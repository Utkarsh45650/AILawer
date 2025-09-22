from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Dict, Any
import os
import aiofiles
from pathlib import Path

from app.services.rag import RAGService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/rag", tags=["RAG"])

# Initialize service lazily to prevent startup blocking
_rag_service = None

def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Upload and process documents for RAG"""
    
    # Validate file types
    allowed_extensions = {'.pdf', '.docx', '.doc'}
    uploaded_files = []
    
    try:
        # Create user uploads directory
        user_upload_dir = Path(f"uploads/user_{current_user['id']}")
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded files
        for file in files:
            if not file.filename:
                continue
                
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
                )
            
            file_path = user_upload_dir / file.filename
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            uploaded_files.append(str(file_path))
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No valid files uploaded")
        
        # Process documents with RAG service
        result = await get_rag_service().process_and_store_documents(
            uploaded_files, 
            current_user["id"]
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": "Documents uploaded and processed successfully",
            "namespace": result["namespace"],
            "chunks_created": result["chunks_created"],
            "files_processed": len(uploaded_files)
        }
        
    except Exception as e:
        # Clean up uploaded files on error
        for file_path in uploaded_files:
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@router.post("/query")
async def query_documents(
    namespace: str = Form(...),
    query: str = Form(...),
    k: int = Form(5),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Query documents using RAG"""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    result = await get_rag_service().query_documents(
        query=query,
        namespace=namespace,
        user_id=current_user["id"],
        k=min(k, 10)  # Limit to max 10 results
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "success": True,
        "answer": result["answer"],
        "sources": result["sources"],
        "namespace": result["namespace"],
        "query": query
    }

@router.get("/document-sets")
async def get_document_sets(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all document sets for the current user"""
    
    document_sets = get_rag_service().get_user_document_sets(current_user["id"])
    
    # Format for frontend
    formatted_sets = []
    for ds in document_sets:
        formatted_sets.append({
            "id": ds["id"],
            "file_names": [os.path.basename(fp) for fp in ds.get("file_paths", [])],
            "chunk_count": ds.get("chunk_count", 0),
            "created_at": ds.get("created_at"),
            "status": ds.get("status", "unknown")
        })
    
    return {
        "success": True,
        "document_sets": formatted_sets,
        "total": len(formatted_sets)
    }

@router.delete("/document-sets/{namespace}")
async def delete_document_set(
    namespace: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a document set"""
    
    result = get_rag_service().delete_document_set(namespace, current_user["id"])
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "success": True,
        "message": "Document set deleted successfully"
    }

@router.get("/status")
async def get_rag_status() -> Dict[str, Any]:
    """Get RAG service status"""
    
    pinecone_configured = bool(os.getenv("PINECONE_API_KEY"))
    
    return {
        "rag_available": pinecone_configured,
        "pinecone_configured": pinecone_configured,
        "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2",
        "llm_model": "gemini-1.5-pro-latest"
    }