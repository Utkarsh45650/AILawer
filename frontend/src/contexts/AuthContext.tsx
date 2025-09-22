import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType, RegisterData } from '../types';
import { authAPI } from '../services/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [loading, setLoading] = useState(true);
  const [showSubscriptionPage, setShowSubscriptionPage] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
          setToken(storedToken);
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('authToken');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await authAPI.login(email, password);
      const newToken = response.access_token;
      
      localStorage.setItem('authToken', newToken);
      setToken(newToken);
      
      // Get user data
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      
      // Check if this is the first login (no subscription setup completed)
      const hasCompletedSubscription = localStorage.getItem(`subscription_completed_${userData.id}`);
      if (!hasCompletedSubscription) {
        setShowSubscriptionPage(true);
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    try {
      await authAPI.register(userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
    setShowSubscriptionPage(false);
  };

  const completeSubscriptionSetup = (tier: string) => {
    if (user) {
      localStorage.setItem(`subscription_completed_${user.id}`, 'true');
      setShowSubscriptionPage(false);
      // Here you could also update the user's subscription tier via API
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    loading,
    showSubscriptionPage,
    completeSubscriptionSetup,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};