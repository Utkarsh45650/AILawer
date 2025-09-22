import google.generativeai as genai
import re
from typing import List, Dict, Any
from datetime import datetime
import os
from app.database.json_db import db
from app.services.subscription import SubscriptionService

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print(f"✅ Gemini API configured with key: {GEMINI_API_KEY[:10]}...")
else:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")

# Use a stable Gemini model
GEMINI_MODEL = "gemini-1.5-pro"

class LegalChatService:
    """Service for handling legal advice chat with step-by-step responses"""
    
    def __init__(self):
        self.subscription_service = SubscriptionService(db)
        self.government_links = {
            "labor_law": [
                "https://www.dol.gov/general/topic/wages",
                "https://www.eeoc.gov/",
                "https://www.nlrb.gov/"
            ],
            "consumer_protection": [
                "https://www.ftc.gov/tips-advice/business-center/guidance",
                "https://www.consumerfinance.gov/"
            ],
            "immigration": [
                "https://www.uscis.gov/",
                "https://www.ice.gov/"
            ],
            "family_law": [
                "https://www.childwelfare.gov/",
                "https://www.acf.hhs.gov/"
            ],
            "criminal_law": [
                "https://www.justice.gov/",
                "https://www.fbi.gov/"
            ],
            "civil_rights": [
                "https://www.justice.gov/crt",
                "https://www.aclu.org/"
            ],
            "intellectual_property": [
                "https://www.uspto.gov/",
                "https://www.copyright.gov/"
            ],
            "business_law": [
                "https://www.sba.gov/",
                "https://www.sec.gov/"
            ]
        }
    
    def identify_legal_area(self, message: str) -> str:
        """Identify the legal area based on the user message"""
        message_lower = message.lower()
        
        # Keywords for different legal areas
        keywords_map = {
            "labor_law": ["employment", "workplace", "wages", "discrimination", "firing", "hiring", "overtime"],
            "consumer_protection": ["consumer", "fraud", "scam", "warranty", "refund", "purchase"],
            "immigration": ["visa", "citizenship", "deportation", "immigration", "green card"],
            "family_law": ["divorce", "custody", "marriage", "adoption", "child support", "alimony"],
            "criminal_law": ["criminal", "arrest", "charges", "felony", "misdemeanor", "court"],
            "civil_rights": ["discrimination", "civil rights", "harassment", "freedom"],
            "intellectual_property": ["patent", "trademark", "copyright", "intellectual property"],
            "business_law": ["business", "corporation", "contract", "llc", "partnership"]
        }
        
        for area, keywords in keywords_map.items():
            if any(keyword in message_lower for keyword in keywords):
                return area
        
        return "general"
    
    def get_relevant_gov_links(self, legal_area: str) -> List[str]:
        """Get relevant government links for the legal area"""
        return self.government_links.get(legal_area, [])
    
    def format_response_with_steps(self, response: str, gov_links: List[str]) -> Dict[str, Any]:
        """Format AI response into step-by-step format with checkboxes"""
        # Split response into steps (look for numbered items or bullet points)
        steps = []
        
        # Try to identify steps in the response
        lines = response.split('\n')
        current_step = ""
        step_number = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new step
            if (re.match(r'^\d+\.', line) or 
                re.match(r'^Step \d+', line, re.IGNORECASE) or
                line.startswith('-') or 
                line.startswith('•')):
                
                if current_step:
                    steps.append({
                        "step_number": step_number - 1,
                        "content": current_step.strip(),
                        "completed": False
                    })
                
                current_step = re.sub(r'^\d+\.|\-|•|Step \d+:?', '', line, flags=re.IGNORECASE).strip()
                step_number += 1
            else:
                current_step += " " + line
        
        # Add the last step
        if current_step:
            steps.append({
                "step_number": step_number - 1,
                "content": current_step.strip(),
                "completed": False
            })
        
        # If no clear steps were found, create a single step
        if not steps:
            steps.append({
                "step_number": 1,
                "content": response,
                "completed": False
            })
        
        return {
            "response": response,
            "steps": steps,
            "government_links": gov_links,
            "has_checkboxes": len(steps) > 1
        }
    
    async def get_legal_advice(self, user_id: str, message: str, session_id: str = None) -> Dict[str, Any]:
        """Get legal advice from AI with step-by-step formatting"""
        # Check if user has access to chat advice
        if not self.subscription_service.check_feature_access(user_id, "chat_advice"):
            return {
                "error": "Chat advice not available for your subscription tier",
                "upgrade_required": True
            }
        
        # Identify legal area
        legal_area = self.identify_legal_area(message)
        gov_links = self.get_relevant_gov_links(legal_area)
        
        # Create or get chat session
        if not session_id:
            session_id = db.create_chat_session(user_id, f"Legal Advice - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Add user message to session
        db.add_message_to_session(session_id, {
            "role": "user",
            "content": message,
            "has_checkboxes": False,
            "gov_links": []
        })
        
        try:
            # Check if API key is available
            if not GEMINI_API_KEY:
                print("❌ Error: GEMINI_API_KEY not configured")
                return {
                    "error": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable.",
                    "session_id": session_id
                }
            
            print(f"🤖 Attempting to get AI response for legal area: {legal_area}")
            
            # Get AI response using Gemini 2.0 Flash model
            system_prompt = f"""You are a legal advice assistant. Provide step-by-step legal guidance in a clear, structured format. 
            
            Guidelines:
            1. Break down advice into numbered steps when appropriate
            2. Be specific and actionable
            3. Include relevant legal considerations
            4. Mention when professional legal consultation is recommended
            5. Focus on {legal_area} if relevant
            6. Do not provide definitive legal conclusions
            7. Always recommend consulting with a qualified attorney for complex matters
            
            Format your response with clear, actionable steps when possible.
            
            User question: {message}"""
            
            print(f"🔍 Using Gemini model: {GEMINI_MODEL}")
            
            # Use Gemini model
            model = genai.GenerativeModel(GEMINI_MODEL)
            print("📡 Sending request to Gemini API...")
            response = model.generate_content(system_prompt)
            print("✅ Received response from Gemini API")
            ai_response = response.text
            
            # Format response with steps
            formatted_response = self.format_response_with_steps(ai_response, gov_links)
            
            # Add AI response to session
            db.add_message_to_session(session_id, {
                "role": "assistant",
                "content": ai_response,
                "has_checkboxes": formatted_response["has_checkboxes"],
                "gov_links": gov_links
            })
            
            return {
                "session_id": session_id,
                "legal_area": legal_area,
                **formatted_response
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error in get_legal_advice: {error_message}")
            print(f"❌ Error type: {type(e).__name__}")
            
            # Check for specific error types
            if "API_KEY" in error_message.upper():
                error_message = "Invalid or expired Gemini API key. Please check your API key configuration."
            elif "QUOTA" in error_message.upper():
                error_message = "API quota exceeded. Please try again later or upgrade your API plan."
            elif "MODEL" in error_message.upper():
                error_message = f"Model '{GEMINI_MODEL}' not available. Please check model name."
            elif "NETWORK" in error_message.upper() or "CONNECTION" in error_message.upper():
                error_message = "Network connection error. Please check your internet connection."
            
            return {
                "error": f"Failed to get legal advice: {error_message}",
                "session_id": session_id,
                "debug_info": {
                    "original_error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's chat session history"""
        return db.get_user_chat_sessions(user_id)
    
    def get_chat_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get specific chat session"""
        session = db.get_chat_session(session_id)
        if not session or session.get("user_id") != user_id:
            return {"error": "Session not found or access denied"}
        return session
    
    def mark_step_completed(self, session_id: str, message_index: int, step_number: int) -> bool:
        """Mark a specific step as completed (this would need custom implementation)"""
        # This would require extending the database schema to track step completion
        # For now, we'll return True as a placeholder
        return True