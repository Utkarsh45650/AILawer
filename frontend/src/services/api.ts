import axios from 'axios';
import { User, RegisterData, ChatResponse, RAGQueryResponse, DocumentSet } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (userData: RegisterData) => {
    const backendData = {
      name: userData.full_name,
      email: userData.email,
      password: userData.password,
    };
    const response = await api.post('/auth/register', backendData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (message: string, conversationId: string = 'default'): Promise<ChatResponse> => {
    const response = await api.post('/chat/advice', {
      message,
      session_id: conversationId,
    });
    return response.data;
  },
};

// RAG API
export const ragAPI = {
  uploadDocuments: async (files: FileList) => {
    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    const response = await api.post('/rag/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  queryDocuments: async (query: string, namespace?: string, k: number = 5): Promise<RAGQueryResponse> => {
    const formData = new FormData();
    formData.append('query', query);
    if (namespace) formData.append('namespace', namespace);
    formData.append('k', k.toString());
    
    const response = await api.post('/rag/query', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getDocumentSets: async (): Promise<{ document_sets: DocumentSet[] }> => {
    const response = await api.get('/rag/document-sets');
    return response.data;
  },

  deleteDocumentSet: async (namespace: string) => {
    const response = await api.delete(`/rag/document-sets/${namespace}`);
    return response.data;
  },
};

// Case Study API
export const caseStudyAPI = {
  analyzeCase: async (caseDetails: string) => {
    const response = await api.post('/case-study/analyze', {
      case_details: caseDetails,
    });
    return response.data;
  },
};

// Expert Advice API
export const expertAdviceAPI = {
  getAdvice: async (query: string, legalArea: string) => {
    const response = await api.post('/expert-advice/', {
      query,
      legal_area: legalArea,
    });
    return response.data;
  },
};