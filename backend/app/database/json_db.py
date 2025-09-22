import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class JSONDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize database files
        self.users_file = self.data_dir / "users.json"
        self.lawyers_file = self.data_dir / "lawyers.json"
        self.chat_sessions_file = self.data_dir / "chat_sessions.json"
        self.case_studies_file = self.data_dir / "case_studies.json"
        self.bookings_file = self.data_dir / "bookings.json"
        self.document_sets_file = self.data_dir / "document_sets.json"
        
        # Create files if they don't exist
        self._init_file(self.users_file, {})
        self._init_file(self.lawyers_file, {})
        self._init_file(self.chat_sessions_file, {})
        self._init_file(self.case_studies_file, {})
        self._init_file(self.bookings_file, {})
        self._init_file(self.document_sets_file, {})
        
        # Initialize with sample lawyers
        self._init_sample_lawyers()
    
    def _init_file(self, file_path: Path, default_data: Any):
        """Initialize a JSON file with default data if it doesn't exist"""
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, default=str)
    
    def _load_data(self, file_path: Path) -> Dict:
        """Load data from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: Path, data: Dict):
        """Save data to a JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    
    def _init_sample_lawyers(self):
        """Initialize sample lawyers if none exist"""
        lawyers = self._load_data(self.lawyers_file)
        if not lawyers:
            sample_lawyers = {
                "lawyer_1": {
                    "id": "lawyer_1",
                    "name": "Sarah Johnson",
                    "specialization": "Corporate Law",
                    "available_slots": [],
                    "is_online": True,
                    "created_at": datetime.now().isoformat()
                },
                "lawyer_2": {
                    "id": "lawyer_2",
                    "name": "Michael Chen",
                    "specialization": "Criminal Law",
                    "available_slots": [],
                    "is_online": False,
                    "created_at": datetime.now().isoformat()
                },
                "lawyer_3": {
                    "id": "lawyer_3",
                    "name": "Emily Rodriguez",
                    "specialization": "Family Law",
                    "available_slots": [],
                    "is_online": True,
                    "created_at": datetime.now().isoformat()
                }
            }
            self._save_data(self.lawyers_file, sample_lawyers)
    
    # User operations
    def create_user(self, user_data: Dict) -> str:
        """Create a new user and return user ID"""
        users = self._load_data(self.users_file)
        user_id = str(uuid.uuid4())
        
        users[user_id] = {
            **user_data,
            "id": user_id,
            "created_at": datetime.now().isoformat(),
            "subscription_tier": "Basic",
            "subscription_expiry": None,
            "chat_history": [],
            "case_study_history": [],
            "expert_advice_bookings": []
        }
        
        self._save_data(self.users_file, users)
        return user_id
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self._load_data(self.users_file)
        for user in users.values():
            if user.get("email") == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        users = self._load_data(self.users_file)
        return users.get(user_id)
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Update user data"""
        users = self._load_data(self.users_file)
        if user_id in users:
            users[user_id].update(update_data)
            self._save_data(self.users_file, users)
            return True
        return False
    
    # Chat session operations
    def create_chat_session(self, user_id: str, title: str) -> str:
        """Create a new chat session"""
        sessions = self._load_data(self.chat_sessions_file)
        session_id = str(uuid.uuid4())
        
        sessions[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_data(self.chat_sessions_file, sessions)
        return session_id
    
    def get_user_chat_sessions(self, user_id: str) -> List[Dict]:
        """Get all chat sessions for a user"""
        sessions = self._load_data(self.chat_sessions_file)
        return [session for session in sessions.values() if session.get("user_id") == user_id]
    
    def get_chat_session(self, session_id: str) -> Optional[Dict]:
        """Get specific chat session"""
        sessions = self._load_data(self.chat_sessions_file)
        return sessions.get(session_id)
    
    def add_message_to_session(self, session_id: str, message: Dict):
        """Add a message to a chat session"""
        sessions = self._load_data(self.chat_sessions_file)
        if session_id in sessions:
            sessions[session_id]["messages"].append({
                **message,
                "timestamp": datetime.now().isoformat()
            })
            sessions[session_id]["updated_at"] = datetime.now().isoformat()
            self._save_data(self.chat_sessions_file, sessions)
    
    # Case study operations
    def create_case_study(self, case_study_data: Dict) -> str:
        """Create a new case study"""
        case_studies = self._load_data(self.case_studies_file)
        case_study_id = str(uuid.uuid4())
        
        case_studies[case_study_id] = {
            **case_study_data,
            "id": case_study_id,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_data(self.case_studies_file, case_studies)
        return case_study_id
    
    def get_user_case_studies(self, user_id: str) -> List[Dict]:
        """Get all case studies for a user"""
        case_studies = self._load_data(self.case_studies_file)
        return [case_study for case_study in case_studies.values() if case_study.get("user_id") == user_id]
    
    def get_case_study(self, case_study_id: str) -> Optional[Dict]:
        """Get specific case study"""
        case_studies = self._load_data(self.case_studies_file)
        return case_studies.get(case_study_id)
    
    # Lawyer operations
    def get_all_lawyers(self) -> List[Dict]:
        """Get all lawyers"""
        lawyers = self._load_data(self.lawyers_file)
        return list(lawyers.values())
    
    def get_online_lawyers(self) -> List[Dict]:
        """Get only online lawyers"""
        lawyers = self._load_data(self.lawyers_file)
        return [lawyer for lawyer in lawyers.values() if lawyer.get("is_online", False)]
    
    def get_lawyer(self, lawyer_id: str) -> Optional[Dict]:
        """Get specific lawyer"""
        lawyers = self._load_data(self.lawyers_file)
        return lawyers.get(lawyer_id)
    
    # Booking operations
    def create_booking(self, booking_data: Dict) -> str:
        """Create a new booking"""
        bookings = self._load_data(self.bookings_file)
        booking_id = str(uuid.uuid4())
        
        bookings[booking_id] = {
            **booking_data,
            "id": booking_id,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self._save_data(self.bookings_file, bookings)
        return booking_id
    
    def get_user_bookings(self, user_id: str) -> List[Dict]:
        """Get all bookings for a user"""
        bookings = self._load_data(self.bookings_file)
        return [booking for booking in bookings.values() if booking.get("user_id") == user_id]
    
    def update_booking_status(self, booking_id: str, status: str) -> bool:
        """Update booking status"""
        bookings = self._load_data(self.bookings_file)
        if booking_id in bookings:
            bookings[booking_id]["status"] = status
            self._save_data(self.bookings_file, bookings)
            return True
        return False
    
    # Document Sets Management
    def store_document_set(self, document_set: Dict[str, Any]) -> str:
        """Store a new document set"""
        document_sets = self._load_data(self.document_sets_file)
        document_set_id = document_set["id"]
        document_sets[document_set_id] = document_set
        self._save_data(self.document_sets_file, document_sets)
        return document_set_id
    
    def get_document_set(self, document_set_id: str) -> Optional[Dict[str, Any]]:
        """Get document set by ID"""
        document_sets = self._load_data(self.document_sets_file)
        return document_sets.get(document_set_id)
    
    def get_user_document_sets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all document sets for a user"""
        document_sets = self._load_data(self.document_sets_file)
        return [ds for ds in document_sets.values() if ds.get("user_id") == user_id]
    
    def delete_document_set(self, document_set_id: str) -> bool:
        """Delete a document set"""
        document_sets = self._load_data(self.document_sets_file)
        if document_set_id in document_sets:
            del document_sets[document_set_id]
            self._save_data(self.document_sets_file, document_sets)
            return True
        return False

# Global database instance
db = JSONDatabase(data_dir="data")