import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Bot, User, Loader } from 'lucide-react';
import { chatAPI } from '../services/api';
import { ChatMessage } from '../types';

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      content: newMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(newMessage);
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-title">
          <MessageCircle size={24} />
          <h2>Legal Chat Assistant</h2>
        </div>
        <button onClick={clearChat} className="clear-btn">
          Clear Chat
        </button>
      </div>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <Bot size={48} />
              <h3>Welcome to LegalAI Chat</h3>
              <p>Ask me any legal questions and I'll help you with professional advice.</p>
              <div className="example-questions">
                <h4>Try asking:</h4>
                <ul>
                  <li>"What are the requirements for forming an LLC?"</li>
                  <li>"Explain the difference between civil and criminal law"</li>
                  <li>"What is intellectual property law?"</li>
                </ul>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.sender}`}
              >
                <div className="message-avatar">
                  {message.sender === 'user' ? (
                    <User size={20} />
                  ) : (
                    <Bot size={20} />
                  )}
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-sender">
                      {message.sender === 'user' ? 'You' : 'LegalAI'}
                    </span>
                    <span className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-text">
                    {message.content}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-sender">LegalAI</span>
                  <span className="message-time">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-text loading">
                  <Loader size={16} className="spinner" />
                  Thinking...
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="message-input-form">
          <div className="input-container">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Ask a legal question..."
              className="message-input"
              maxLength={500}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-btn"
              disabled={!newMessage.trim() || isLoading}
            >
              <Send size={18} />
            </button>
          </div>
          <div className="input-hint">
            Press Enter to send • {newMessage.length}/500 characters
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;