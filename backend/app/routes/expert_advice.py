from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.services.expert_advice import ExpertAdviceService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/expert-advice", tags=["expert_advice"])

expert_service = ExpertAdviceService()

@router.get("/lawyers")
async def get_available_lawyers(
    specialization: Optional[str] = Query(None, description="Filter by lawyer specialization"),
    current_user: dict = Depends(get_current_user)
):
    """Get available lawyers based on user's subscription"""
    result = expert_service.get_available_lawyers(
        user_id=current_user["id"],
        specialization=specialization
    )
    
    if "error" in result:
        if result.get("upgrade_required"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return result

@router.get("/lawyers/online")
async def get_online_lawyers(current_user: dict = Depends(get_current_user)):
    """Get only online lawyers"""
    result = expert_service.get_online_lawyers(current_user["id"])
    
    if "error" in result:
        if result.get("upgrade_required"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return result

@router.get("/specializations")
async def get_specializations():
    """Get list of all lawyer specializations"""
    specializations = expert_service.get_lawyer_specializations()
    return {"specializations": specializations}

@router.post("/")
async def get_expert_advice(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Get expert legal advice based on query and legal area"""
    query = request.get("query", "")
    legal_area = request.get("legal_area", "general")
    
    # For now, return a structured advice response
    # This could be enhanced to connect with actual experts or AI
    result = expert_service.get_expert_advice_response(
        user_id=current_user["id"],
        query=query,
        legal_area=legal_area
    )
    
    if "error" in result:
        if result.get("upgrade_required"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return result

@router.post("/book")
async def book_consultation(
    lawyer_id: str,
    appointment_time: str,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Book a consultation with a lawyer"""
    result = expert_service.book_consultation(
        user_id=current_user["id"],
        lawyer_id=lawyer_id,
        appointment_time=appointment_time,
        description=description
    )
    
    if "error" in result:
        if result.get("upgrade_required"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result["error"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
    
    return result

@router.get("/bookings")
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    """Get all bookings for the current user"""
    bookings = expert_service.get_user_bookings(current_user["id"])
    return {"bookings": bookings}

@router.get("/bookings/{booking_id}")
async def get_booking_details(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific booking"""
    booking = expert_service.get_booking_details(booking_id, current_user["id"])
    
    if "error" in booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=booking["error"]
        )
    
    return booking

@router.put("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a booking"""
    result = expert_service.cancel_booking(booking_id, current_user["id"])
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result

@router.put("/bookings/{booking_id}/reschedule")
async def reschedule_booking(
    booking_id: str,
    new_appointment_time: str,
    current_user: dict = Depends(get_current_user)
):
    """Reschedule an existing booking"""
    result = expert_service.reschedule_booking(
        booking_id=booking_id,
        user_id=current_user["id"],
        new_appointment_time=new_appointment_time
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result