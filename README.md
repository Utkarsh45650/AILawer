# LegalAI - Full-Stack AI-Powered Legal Assistant

A comprehensive React.js web application with a FastAPI backend, featuring AI-powered legal assistance, document analysis, and RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Features

### 🔐 Authentication System
- User registration and login with JWT tokens
- Subscription tier management (Free, Premium, Enterprise)
- Persistent authentication sessions

### 💬 Legal Chat Assistant
- Real-time AI-powered legal consultations
- Gemini 1.5 Pro Latest integration
- Conversation history and message management
- Professional legal advice with disclaimers

### 📄 RAG Document Analysis
- Upload legal documents (PDF, TXT, DOC, DOCX)
- AI-powered document querying and analysis
- Vector search with Pinecone integration
- Source citation and relevance scoring
- Document set management and organization

### 📊 Case Study Analysis
- Comprehensive legal case analysis
- Detailed breakdown of legal issues
- Professional recommendations and insights

### ⚖️ Expert Legal Advice
- Specialized legal guidance by practice area
- 12+ legal practice areas supported
- Professional disclaimers and ethical guidelines

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Modern CSS** with responsive design
- **Lucide React** icons for UI
- **Axios** for API communication
- **Context API** for state management

### Backend
- **FastAPI** with Python 3.8+
- **Gemini 1.5 Pro Latest** AI model
- **LangChain** for document processing
- **Pinecone** vector database
- **JWT** authentication
- **JSON-based** data storage

## 📦 Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+ and pip
- Google AI API key (for Gemini)
- Pinecone API key (optional, for RAG functionality)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # On Windows
   # or
   source venv/bin/activate     # On macOS/Linux
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   Create a `.env` file in the backend directory:
   ```env
   GOOGLE_API_KEY=your_google_ai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   SECRET_KEY=your_jwt_secret_key_here
   ```

5. **Start the FastAPI server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the React development server**
   ```bash
   npm start
   ```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
LegalAI/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   │   ├── auth.py      # Authentication routes
│   │   │   ├── chat.py      # Chat functionality
│   │   │   ├── rag.py       # Document analysis
│   │   │   ├── case_study.py # Case analysis
│   │   │   └── expert_advice.py # Legal advice
│   │   ├── services/        # Business logic
│   │   ├── models/          # Data models
│   │   ├── database/        # Database management
│   │   └── utils/           # Utility functions
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── AuthPage.tsx # Authentication UI
│   │   │   ├── ChatPage.tsx # Chat interface
│   │   │   ├── DocumentsPage.tsx # RAG interface
│   │   │   ├── CaseStudyPage.tsx # Case analysis
│   │   │   ├── ExpertAdvicePage.tsx # Legal advice
│   │   │   └── Header.tsx   # Navigation
│   │   ├── contexts/        # React context
│   │   ├── services/        # API services
│   │   ├── types.ts         # TypeScript types
│   │   ├── App.tsx          # Main app component
│   │   ├── App.css          # Comprehensive styling
│   │   └── index.tsx        # App entry point
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── tsconfig.json        # TypeScript configuration
└── README.md                # This file
```

## 🎯 Key Features Demonstration

### Authentication Flow
1. Access http://localhost:3000
2. Click "Sign Up" to create an account
3. Fill in your details and select a subscription tier
4. Login with your credentials
5. Access the full application features

### Chat Assistant
1. Navigate to the Chat tab
2. Ask legal questions like:
   - "What are the requirements for forming an LLC?"
   - "Explain the difference between civil and criminal law"
   - "What is intellectual property law?"

### Document Analysis (RAG)
1. Go to the Documents tab
2. Upload legal documents (PDF, TXT, DOC, DOCX)
3. Wait for processing to complete
4. Query your documents with questions
5. Review AI responses with source citations

### Case Study Analysis
1. Visit the Case Study tab
2. Enter detailed case information
3. Receive comprehensive legal analysis
4. Review recommendations and insights

### Expert Legal Advice
1. Navigate to Expert Advice tab
2. Select a legal practice area (optional)
3. Submit your legal question
4. Get specialized professional guidance

## 🛡️ Security Features

- JWT token-based authentication
- Secure password handling
- Input validation and sanitization
- CORS configuration for API security
- Professional legal disclaimers

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Interface**: Clean, professional design with gradients
- **Loading States**: Smooth user feedback during operations
- **Error Handling**: User-friendly error messages
- **Accessibility**: Semantic HTML and keyboard navigation
- **Progressive Enhancement**: Works without JavaScript for basic features

## 🔧 Development Notes

### Backend API Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info
- `POST /chat/` - Send chat messages
- `POST /rag/upload` - Upload documents
- `POST /rag/query` - Query documents
- `GET /rag/document-sets` - List document sets
- `DELETE /rag/document-sets/{namespace}` - Delete document set
- `POST /case-study/analyze` - Analyze legal cases
- `POST /expert-advice/` - Get expert legal advice

### Environment Variables
- `GOOGLE_API_KEY` - Required for AI functionality
- `PINECONE_API_KEY` - Optional for RAG features
- `SECRET_KEY` - Required for JWT token security

### Browser Support
- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## 🚀 Production Deployment

### Frontend (React)
```bash
cd frontend
npm run build
# Deploy the build/ directory to your hosting service
```

### Backend (FastAPI)
```bash
cd backend
# Use a production WSGI server like Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📝 License

This project is for educational and demonstration purposes. Please ensure compliance with legal AI ethics and data protection regulations when deploying in production.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the console logs in your browser's developer tools
2. Review the FastAPI server logs
3. Ensure all environment variables are set correctly
4. Verify API keys are valid and have proper permissions

---

**Built with ❤️ for the legal technology community**#   A I L a w e r  
 