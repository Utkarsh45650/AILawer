import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, User, Settings } from 'lucide-react';

interface HeaderProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

const Header: React.FC<HeaderProps> = ({ currentPage, setCurrentPage }) => {
  const { user, logout } = useAuth();

  const navigationItems = [
    { id: 'chat', label: '💬 Chat', icon: '💬' },
    { id: 'documents', label: '📄 Documents', icon: '📄' },
    { id: 'case-study', label: '📊 Case Study', icon: '📊' },
    { id: 'expert-advice', label: '⚖️ Expert Advice', icon: '⚖️' },
  ];

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="logo">🏛️ LegalAI</h1>
          <nav className="navigation">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <User size={16} />
            <span className="user-name">{user?.full_name || user?.email}</span>
            <span className="user-tier">{user?.subscription_tier}</span>
          </div>
          <button className="logout-btn" onClick={logout} title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;