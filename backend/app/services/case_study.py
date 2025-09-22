import os
import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
from fastapi import UploadFile
from datetime import datetime
import google.generativeai as genai

# Import components from the existing RAG pipeline
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "Final"))

from app.database.json_db import db
from app.services.subscription import SubscriptionService

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 1.5 Pro Latest for best document analysis quality
GEMINI_MODEL = "gemini-1.5-pro-latest"

class CaseStudyService:
    """Service for handling custom case study analysis using RAG pipeline"""
    
    def __init__(self):
        self.subscription_service = SubscriptionService(db)
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)
    
    async def analyze_case_study(
        self, 
        user_id: str, 
        file: UploadFile, 
        title: str, 
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze uploaded legal document using RAG pipeline"""
        
        # Check subscription limits
        limit_check = self.subscription_service.check_case_study_limit(user_id)
        if not limit_check["allowed"]:
            return {
                "error": "Case study limit exceeded for your subscription tier",
                "limit_info": limit_check,
                "upgrade_required": True
            }
        
        try:
            # Save uploaded file
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename)[1].lower()
            saved_filename = f"{file_id}{file_extension}"
            file_path = self.uploads_dir / saved_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Process document using RAG pipeline
            analysis_result = await self._process_document(str(file_path), file.filename)
            
            # Create case study record
            case_study_data = {
                "user_id": user_id,
                "title": title,
                "description": description,
                "file_name": file.filename,
                "saved_filename": saved_filename,
                "file_path": str(file_path),
                "summary": analysis_result.get("summary", ""),
                "highlights": analysis_result.get("highlights", []),
                "mind_map_data": analysis_result.get("mind_map", {}),
                "extracted_text": analysis_result.get("extracted_text", ""),
                "analysis_metadata": analysis_result.get("metadata", {})
            }
            
            case_study_id = db.create_case_study(case_study_data)
            
            return {
                "case_study_id": case_study_id,
                "title": title,
                "summary": analysis_result.get("summary", ""),
                "highlights": analysis_result.get("highlights", []),
                "mind_map_data": analysis_result.get("mind_map", {}),
                "file_name": file.filename,
                "created_at": datetime.now().isoformat(),
                "usage_info": self.subscription_service.check_case_study_limit(user_id)
            }
            
        except Exception as e:
            # Clean up uploaded file if processing failed
            if file_path.exists():
                file_path.unlink()
            
            return {
                "error": f"Failed to analyze document: {str(e)}",
                "details": "Document processing failed during analysis"
            }
    
    async def _process_document(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Process document using RAG pipeline"""
        try:
            # Import and use components from existing RAG pipeline
            from main import (
                process_document_async,
                extract_text_from_file,
                create_summary,
                identify_highlights
            )
            
            # Extract text from document
            extracted_text = await extract_text_from_file(file_path)
            
            # Create summary
            summary = await create_summary(extracted_text)
            
            # Identify important highlights
            highlights = await identify_highlights(extracted_text)
            
            # Generate mind map data structure
            mind_map = await self._generate_mind_map(extracted_text, summary)
            
            return {
                "extracted_text": extracted_text,
                "summary": summary,
                "highlights": highlights,
                "mind_map": mind_map,
                "metadata": {
                    "original_filename": original_filename,
                    "processed_at": datetime.now().isoformat(),
                    "text_length": len(extracted_text),
                    "highlight_count": len(highlights)
                }
            }
            
        except Exception as e:
            # Fallback to basic processing if RAG pipeline fails
            return await self._basic_document_processing(file_path, original_filename)
    
    async def _basic_document_processing(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Basic document processing with Gemini AI analysis"""
        try:
            # Basic text extraction
            if file_path.lower().endswith('.pdf'):
                try:
                    import PyPDF2
                    reader = PyPDF2.PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                except ImportError:
                    return self._create_error_response(original_filename, "PyPDF2 not available for PDF processing")
            
            elif file_path.lower().endswith(('.doc', '.docx')):
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    return self._create_error_response(original_filename, "python-docx not available for Word processing")
            
            else:
                # Try to read as text file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except Exception as e:
                    return self._create_error_response(original_filename, f"Failed to read file: {str(e)}")
            
            if not text.strip():
                return self._create_error_response(original_filename, "No text could be extracted from the document")
            
            # Use Gemini to analyze the document
            return await self._analyze_with_gemini(text, original_filename)
            
        except Exception as e:
            return self._create_error_response(original_filename, str(e))
    
    async def _analyze_with_gemini(self, text: str, original_filename: str) -> Dict[str, Any]:
        """Use Gemini AI to analyze the document text"""
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            # Create summary
            summary_prompt = f"""
            Analyze this legal document and provide a concise summary in 2-3 sentences:
            
            {text[:3000]}  # Limit text to avoid token limits
            """
            
            summary_response = model.generate_content(summary_prompt)
            summary = summary_response.text
            
            # Extract key highlights
            highlights_prompt = f"""
            From this legal document, extract 5 key legal points or important clauses. 
            Return each point as a separate line starting with a number:
            
            {text[:3000]}
            """
            
            highlights_response = model.generate_content(highlights_prompt)
            highlights_text = highlights_response.text
            
            # Parse highlights
            highlights = []
            for line in highlights_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the line
                    cleaned_line = re.sub(r'^\d+\.?\s*|\-\s*|•\s*', '', line).strip()
                    if cleaned_line:
                        highlights.append(cleaned_line)
            
            # Generate mind map with Gemini
            mind_map = await self._generate_mind_map_with_gemini(text[:2000], summary)
            
            return {
                "extracted_text": text,
                "summary": summary,
                "highlights": highlights[:5],  # Limit to 5 highlights
                "mind_map": mind_map,
                "metadata": {
                    "original_filename": original_filename,
                    "processed_at": datetime.now().isoformat(),
                    "text_length": len(text),
                    "highlight_count": len(highlights),
                    "processing_method": "gemini_ai_analysis"
                }
            }
            
        except Exception as e:
            return self._create_error_response(original_filename, f"Gemini analysis failed: {str(e)}")
    
    async def _generate_mind_map_with_gemini(self, text: str, summary: str) -> Dict[str, Any]:
        """Generate mind map using Gemini AI"""
        try:
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            mind_map_prompt = f"""
            Create a mind map structure for this legal document. Return a JSON-like structure with:
            1. A central topic
            2. 3-5 main branches with subtopics
            3. Focus on legal concepts, parties, obligations, and key terms
            
            Document summary: {summary}
            Document text: {text}
            
            Format as: Main Topic -> Branch 1, Branch 2, etc.
            """
            
            response = model.generate_content(mind_map_prompt)
            mind_map_text = response.text
            
            # Create a structured mind map from the AI response
            mind_map = {
                "title": "Legal Document Analysis",
                "center_node": {
                    "name": "Document Overview",
                    "summary": summary[:200] + "..." if len(summary) > 200 else summary
                },
                "branches": []
            }
            
            # Parse the AI response to extract branches
            lines = mind_map_text.split('\n')
            for line in lines:
                line = line.strip()
                if '->' in line or any(keyword in line.lower() for keyword in ['branch', 'topic', 'concept', 'party', 'obligation']):
                    branch_name = line.split('->')[0].strip() if '->' in line else line
                    branch_name = re.sub(r'^\d+\.?\s*|\-\s*|•\s*', '', branch_name).strip()
                    if branch_name and len(branch_name) > 3:
                        mind_map["branches"].append({
                            "name": branch_name[:50],  # Limit length
                            "weight": 5,
                            "details": "Generated by AI analysis"
                        })
            
            # If no branches found, create default ones
            if not mind_map["branches"]:
                mind_map["branches"] = [
                    {"name": "Key Legal Points", "weight": 8, "details": "Main legal concepts"},
                    {"name": "Parties Involved", "weight": 6, "details": "Entities mentioned"},
                    {"name": "Obligations", "weight": 7, "details": "Legal duties and requirements"},
                    {"name": "Important Dates", "weight": 5, "details": "Timeline elements"}
                ]
            
            return mind_map
            
        except Exception as e:
            # Fallback to simple mind map
            return {
                "title": "Document Analysis",
                "center_node": {"name": "Legal Document", "summary": summary[:100]},
                "branches": [{"name": "Analysis Available", "weight": 5, "details": f"AI processing error: {str(e)}"}],
                "error": str(e)
            }
    
    def _create_error_response(self, filename: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "extracted_text": f"Failed to process {filename}",
            "summary": f"Document processing failed: {error_message}",
            "highlights": [],
            "mind_map": {"title": filename, "error": error_message},
            "metadata": {
                "original_filename": filename,
                "processed_at": datetime.now().isoformat(),
                "error": error_message,
                "processing_method": "error_fallback"
            }
        }
    
    async def _generate_mind_map(self, text: str, summary: str) -> Dict[str, Any]:
        """Generate mind map data structure from text"""
        # Simple mind map generation
        # In production, this could be enhanced with more sophisticated NLP
        
        words = text.lower().split()
        
        # Count important legal terms
        legal_terms = {
            "contract": words.count("contract") + words.count("agreement"),
            "liability": words.count("liability") + words.count("damages"),
            "rights": words.count("rights") + words.count("obligations"),
            "breach": words.count("breach") + words.count("violation"),
            "payment": words.count("payment") + words.count("compensation")
        }
        
        # Create mind map structure
        mind_map = {
            "title": "Legal Document Analysis",
            "center_node": {
                "name": "Main Document",
                "summary": summary[:200] + "..." if len(summary) > 200 else summary
            },
            "branches": []
        }
        
        # Add branches for important terms
        for term, count in legal_terms.items():
            if count > 0:
                mind_map["branches"].append({
                    "name": term.title(),
                    "weight": min(count, 10),  # Limit weight for visualization
                    "details": f"Mentioned {count} times"
                })
        
        return mind_map
    
    def get_user_case_studies(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all case studies for a user"""
        case_studies = db.get_user_case_studies(user_id)
        
        # Remove sensitive file paths and add summary info
        for study in case_studies:
            study.pop("file_path", None)
            study.pop("extracted_text", None)  # Don't return full text in list
        
        return case_studies
    
    def get_case_study(self, case_study_id: str, user_id: str) -> Dict[str, Any]:
        """Get specific case study"""
        case_study = db.get_case_study(case_study_id)
        
        if not case_study:
            return {"error": "Case study not found"}
        
        if case_study.get("user_id") != user_id:
            return {"error": "Access denied"}
        
        # Remove sensitive file path
        case_study.pop("file_path", None)
        
        return case_study
    
    def delete_case_study(self, case_study_id: str, user_id: str) -> bool:
        """Delete case study and associated file"""
        case_study = db.get_case_study(case_study_id)
        
        if not case_study or case_study.get("user_id") != user_id:
            return False
        
        # Delete file if it exists
        file_path = case_study.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Continue even if file deletion fails
        
        # Remove from database (this would need to be implemented in json_db)
        # For now, we'll just return True
        return True