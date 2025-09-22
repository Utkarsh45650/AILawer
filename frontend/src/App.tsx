import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthPage from './components/AuthPage';
import SubscriptionPage from './components/SubscriptionPage';
import Header from './components/Header';
import ChatPage from './components/ChatPage';
import DocumentsPage from './components/DocumentsPage';
import CaseStudyPage from './components/CaseStudyPage';
import ExpertAdvicePage from './components/ExpertAdvicePage';
import './App.css';

const AppContent: React.FC = () => {
  const { user, loading, showSubscriptionPage } = useAuth();
  const [currentPage, setCurrentPage] = useState('chat');

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <h1>🏛️ LegalAI</h1>
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  if (showSubscriptionPage) {
    return <SubscriptionPage />;
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'chat':
        return <ChatPage />;
      case 'documents':
        return <DocumentsPage />;
      case 'case-study':
        return <CaseStudyPage />;
      case 'expert-advice':
        return <ExpertAdvicePage />;
      default:
        return <ChatPage />;
    }
  };

  return (
    <div className="app">
      <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="main-content">
        {renderCurrentPage()}
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;