from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    PLATINUM = "Platinum"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    subscription_tier: SubscriptionTier
    subscription_expiry: Optional[datetime] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    has_checkboxes: bool = False
    gov_links: List[str] = []

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatSession(BaseModel):
    id: str
    user_id: str
    title: str
    messages: List[ChatMessage] = []
    created_at: datetime
    updated_at: datetime

class CaseStudyRequest(BaseModel):
    title: str
    description: Optional[str] = None

class CaseStudyResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    file_name: str
    summary: str
    highlights: List[str] = []
    mind_map_data: dict = {}
    created_at: datetime

class LawyerAvailability(BaseModel):
    id: str
    name: str
    specialization: str
    available_slots: List[datetime] = []
    is_online: bool = False

class BookingRequest(BaseModel):
    lawyer_id: str
    appointment_time: datetime
    description: Optional[str] = None

class BookingResponse(BaseModel):
    id: str
    user_id: str
    lawyer_id: str
    appointment_time: datetime
    description: Optional[str] = None
    status: str  # 'pending', 'confirmed', 'cancelled'
    created_at: datetime