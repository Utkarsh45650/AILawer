# LegalAI WebApp Backend

A professional, subscription-based legal advice and recommendation web application with AI-powered chat, case study analysis, expert lawyer consultations, and visual mind maps of legal documents.

## Features

### Core Features
- **User Authentication**: JWT-based authentication with user registration and login
- **Subscription Management**: 4-tier subscription system (Basic, Standard, Premium, Platinum)
- **AI Chat Advice**: Step-by-step legal guidance with government links and checkboxes
- **Case Study Analysis**: RAG pipeline for document analysis with mind map generation
- **Expert Advice**: Lawyer consultation booking system with real-time availability
- **JSON Database**: File-based storage for development (easily upgradeable to PostgreSQL)

### Subscription Tiers
1. **Basic (Free)**
   - Chat advice (unlimited)
   - 5 custom case study uses per week

2. **Standard (Paid)**
   - All Basic features
   - Unlimited custom case study uses

3. **Premium (Paid)**
   - All Standard features
   - Expert advice (3 times per week)

4. **Platinum (Paid)**
   - All Premium features
   - Unlimited expert advice sessions

## Project Structure

```
backend/
├── app/                     # Main application package
│   ├── models/             # Pydantic models and schemas
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic services
│   ├── database/           # Database managers
│   └── utils/              # Utility functions
├── data/                   # JSON database files
├── uploads/                # Uploaded document storage
├── venv/                   # Virtual environment
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── start.bat              # Windows startup script
└── README.md              # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Windows PowerShell or Command Prompt

### Installation

1. **Clone and Navigate to Backend Directory**
   ```bash
   cd "backend"
   ```

2. **Create Virtual Environment** (Already done)
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # Or use PowerShell
   venv\Scripts\Activate.ps1
   ```

4. **Install Dependencies** (Already done)
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` file and add your API keys:
   - OpenAI API Key (for AI chat functionality)
   - Gemini API Key (if using Google Generative AI)
   - Pinecone API Key (if using Pinecone vector database)

6. **Run the Application**
   ```bash
   # Option 1: Use the startup script
   start.bat

   # Option 2: Run directly
   python main.py
   ```

### Quick Start
Double-click `start.bat` to launch the backend server automatically.

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `PUT /auth/subscription` - Update subscription tier

### Chat Advice
- `POST /chat/advice` - Get AI legal advice
- `GET /chat/history` - Get chat history
- `GET /chat/session/{session_id}` - Get specific chat session

### Case Study Analysis
- `POST /case-study/analyze` - Analyze uploaded document
- `GET /case-study/list` - Get user's case studies
- `GET /case-study/{case_study_id}` - Get case study details
- `GET /case-study/{case_study_id}/mind-map` - Get mind map data

### Expert Advice
- `GET /expert-advice/lawyers` - Get available lawyers
- `GET /expert-advice/lawyers/online` - Get online lawyers
- `POST /expert-advice/book` - Book consultation
- `GET /expert-advice/bookings` - Get user bookings

### General
- `GET /` - API information
- `GET /health` - Health check
- `GET /subscription-info` - Subscription tier details
- `GET /my-subscription` - User's subscription status

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Integration with Existing RAG Pipeline

The backend integrates with the existing RAG pipeline from the `Final` folder:
- Document text extraction
- AI-powered summarization
- Highlight identification
- Mind map generation

## Development Notes

### Database
- Currently uses JSON files for data storage
- Easily upgradeable to PostgreSQL or MongoDB
- User data stored in `data/users.json`
- Chat sessions in `data/chat_sessions.json`
- Case studies in `data/case_studies.json`
- Bookings in `data/bookings.json`

### Security
- JWT token-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- File upload size limits

### Scalability
- Modular architecture for easy expansion
- Service-based business logic
- Configurable subscription limits
- Environment-based configuration

## Production Deployment

For production deployment:

1. **Environment Variables**
   - Set secure `SECRET_KEY`
   - Configure production API keys
   - Set `DEBUG=False`

2. **Database Migration**
   - Replace JSON database with PostgreSQL
   - Update database connection settings

3. **File Storage**
   - Use cloud storage (AWS S3) for uploads
   - Configure CDN for file delivery

4. **Security**
   - Enable HTTPS
   - Configure proper CORS origins
   - Set up rate limiting
   - Add input sanitization

## API Usage Examples

### User Registration
```python
import requests

response = requests.post("http://127.0.0.1:8000/auth/register", json={
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword"
})
```

### Get Legal Advice
```python
headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}
response = requests.post("http://127.0.0.1:8000/chat/advice", 
    json={"message": "I need help with employment law"},
    headers=headers
)
```

### Upload Case Study
```python
files = {"file": open("legal_document.pdf", "rb")}
data = {"title": "Contract Analysis", "description": "Review this contract"}
response = requests.post("http://127.0.0.1:8000/case-study/analyze",
    files=files, data=data, headers=headers
)
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**
   - Make sure to activate the virtual environment before running

2. **Missing API Keys**
   - Check `.env` file for correct API key configuration

3. **Port Already in Use**
   - Change port in `main.py` or stop conflicting services

4. **Module Import Errors**
   - Ensure all dependencies are installed in the virtual environment

### Support
For technical support or questions about the LegalAI WebApp backend, please refer to the project documentation or contact the development team.