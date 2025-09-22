from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token, SubscriptionTier
from app.database.json_db import db
from app.utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash, 
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token, credentials_exception)
    user = db.get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    user_data = {
        "name": user.name,
        "email": user.email,
        "password_hash": hashed_password
    }
    
    user_id = db.create_user(user_data)
    created_user = db.get_user_by_id(user_id)
    
    return UserResponse(
        id=created_user["id"],
        name=created_user["name"],
        email=created_user["email"],
        subscription_tier=SubscriptionTier(created_user["subscription_tier"]),
        subscription_expiry=created_user.get("subscription_expiry"),
        created_at=created_user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        subscription_tier=SubscriptionTier(current_user["subscription_tier"]),
        subscription_expiry=current_user.get("subscription_expiry"),
        created_at=current_user["created_at"]
    )

@router.put("/subscription", response_model=UserResponse)
async def update_subscription(
    subscription_tier: SubscriptionTier,
    current_user: dict = Depends(get_current_user)
):
    """Update user subscription tier"""
    db.update_user(current_user["id"], {"subscription_tier": subscription_tier.value})
    updated_user = db.get_user_by_id(current_user["id"])
    
    return UserResponse(
        id=updated_user["id"],
        name=updated_user["name"],
        email=updated_user["email"],
        subscription_tier=SubscriptionTier(updated_user["subscription_tier"]),
        subscription_expiry=updated_user.get("subscription_expiry"),
        created_at=updated_user["created_at"]
    )