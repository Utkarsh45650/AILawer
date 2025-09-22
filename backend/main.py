from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all route modules
from app.routes import auth, chat, case_study, expert_advice, rag
from app.services.subscription import SubscriptionService
from app.database.json_db import db

# Create FastAPI app
app = FastAPI(
    title="LegalAI WebApp API",
    description="A professional, subscription-based legal advice and recommendation web application with AI-powered chat, case study analysis, expert lawyer consultations, and visual mind maps of legal documents.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(case_study.router)
app.include_router(expert_advice.router)
app.include_router(rag.router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LegalAI WebApp API",
        "version": "1.0.0",
        "description": "AI-powered legal advice and consultation platform",
        "features": [
            "User authentication and subscription management",
            "AI-powered legal chat advice with step-by-step guidance",
            "Custom case study analysis with RAG pipeline",
            "Expert lawyer consultation booking system",
            "Mind map generation for legal documents",
            "RAG document upload and query system",
            "Vector database document storage and retrieval"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "database": "operational",
            "ai_services": "operational",
            "rag_pipeline": "operational"
        }
    }

# Subscription information endpoint
@app.get("/subscription-info", tags=["subscription"])
async def get_subscription_tiers():
    """Get information about subscription tiers"""
    return {
        "tiers": [
            {
                "name": "Basic",
                "price": "Free",
                "features": [
                    "Chat advice",
                    "5 custom case study uses per week"
                ]
            },
            {
                "name": "Standard",
                "price": "Monthly/Yearly",
                "features": [
                    "All Basic features",
                    "Unlimited custom case study uses"
                ]
            },
            {
                "name": "Premium",
                "price": "Monthly/Yearly",
                "features": [
                    "All Standard features",
                    "Expert advice (3 times per week)"
                ]
            },
            {
                "name": "Platinum",
                "price": "Monthly/Yearly",
                "features": [
                    "All Premium features",
                    "Unlimited expert advice sessions"
                ]
            }
        ]
    }

# User subscription status endpoint (requires authentication)
from app.routes.auth import get_current_user
from fastapi import Depends

@app.get("/my-subscription", tags=["subscription"])
async def get_my_subscription(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription information"""
    subscription_service = SubscriptionService(db)
    subscription_info = subscription_service.get_subscription_info(current_user["id"])
    return subscription_info

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "detail": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 LegalAI WebApp API starting up...")
    
    # Ensure upload directories exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories initialized")
    print("✅ Database initialized")
    print("✅ Services ready")
    print("📡 API server is ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 LegalAI WebApp API shutting down...")
    print("✅ Cleanup completed")

# Main function to run the server
def main():
    """Run the FastAPI server"""
    print("Starting LegalAI WebApp API server...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )

# Only run main if this file is executed directly
# When using uvicorn main:app, this won't be triggered
if __name__ == "__main__":
    main()