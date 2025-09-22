from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models.schemas import ChatMessage, ChatSession, ChatRequest
from app.services.chat import LegalChatService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat_advice"])

chat_service = LegalChatService()

@router.post("/advice")
async def get_legal_advice(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get legal advice from AI assistant"""
    result = await chat_service.get_legal_advice(
        user_id=current_user["id"],
        message=request.message,
        session_id=request.session_id
    )
    
    if "error" in result:
        if result.get("upgrade_required"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
    
    return result

@router.get("/history")
async def get_chat_history(current_user: dict = Depends(get_current_user)):
    """Get user's chat session history"""
    history = chat_service.get_chat_history(current_user["id"])
    return {"sessions": history}

@router.get("/session/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific chat session"""
    session = chat_service.get_chat_session(session_id, current_user["id"])
    
    if "error" in session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=session["error"]
        )
    
    return session

@router.post("/session/{session_id}/step/{step_number}/complete")
async def mark_step_completed(
    session_id: str,
    step_number: int,
    message_index: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Mark a specific step as completed"""
    success = chat_service.mark_step_completed(session_id, message_index, step_number)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to mark step as completed"
        )
    
    return {"success": True, "message": "Step marked as completed"}