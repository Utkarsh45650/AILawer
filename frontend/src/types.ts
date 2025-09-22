// Types for the application
export interface User {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: 'free' | 'premium' | 'enterprise';
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  loading: boolean;
  showSubscriptionPage: boolean;
  completeSubscriptionSetup: (tier: string) => void;
}

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
  subscription_tier?: 'free' | 'premium' | 'enterprise';
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
}

export interface RAGDocument {
  id: string;
  filename: string;
  upload_date: string;
  size: number;
}

export interface RAGQueryResponse {
  response: string;
  sources: Array<{
    page_content: string;
    score: number;
    metadata: Record<string, any>;
  }>;
  success: boolean;
}

export interface DocumentSet {
  namespace: string;
  document_count: number;
  created_at: string;
}