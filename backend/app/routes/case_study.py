from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from app.services.case_study import CaseStudyService
from app.routes.auth import get_current_user

router = APIRouter(prefix="/case-study", tags=["case_study"])

case_study_service = CaseStudyService()

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Analyze uploaded legal document using RAG pipeline"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    file_extension = file.filename.split('.')[-1].lower()
    
    if f'.{file_extension}' not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    result = await case_study_service.analyze_case_study(
        user_id=current_user["id"],
        file=file,
        title=title,
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
    
    return result

@router.get("/list")
async def get_case_studies(current_user: dict = Depends(get_current_user)):
    """Get all case studies for the current user"""
    case_studies = case_study_service.get_user_case_studies(current_user["id"])
    return {"case_studies": case_studies}

@router.get("/{case_study_id}")
async def get_case_study(
    case_study_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific case study details"""
    case_study = case_study_service.get_case_study(case_study_id, current_user["id"])
    
    if "error" in case_study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=case_study["error"]
        )
    
    return case_study

@router.delete("/{case_study_id}")
async def delete_case_study(
    case_study_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a case study"""
    success = case_study_service.delete_case_study(case_study_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case study not found or access denied"
        )
    
    return {"success": True, "message": "Case study deleted successfully"}

@router.get("/{case_study_id}/mind-map")
async def get_mind_map(
    case_study_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get mind map data for a case study"""
    case_study = case_study_service.get_case_study(case_study_id, current_user["id"])
    
    if "error" in case_study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=case_study["error"]
        )
    
    return {
        "mind_map_data": case_study.get("mind_map_data", {}),
        "title": case_study.get("title", ""),
        "case_study_id": case_study_id
    }