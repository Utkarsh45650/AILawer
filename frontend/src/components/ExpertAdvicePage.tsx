import React, { useState } from 'react';
import { Scale, Loader, BookOpen } from 'lucide-react';
import { expertAdviceAPI } from '../services/api';

const ExpertAdvicePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [legalArea, setLegalArea] = useState('');
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(false);

  const legalAreas = [
    'Corporate Law',
    'Criminal Law',
    'Family Law',
    'Employment Law',
    'Real Estate Law',
    'Intellectual Property',
    'Immigration Law',
    'Tax Law',
    'Personal Injury',
    'Contract Law',
    'Constitutional Law',
    'Environmental Law',
  ];

  const handleGetAdvice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setAdvice('');

    try {
      const response = await expertAdviceAPI.getAdvice(query, legalArea);
      setAdvice(response.advice);
    } catch (error: any) {
      setAdvice(`Error: ${error.response?.data?.detail || 'Failed to get advice'}`);
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setQuery('');
    setLegalArea('');
    setAdvice('');
  };

  return (
    <div className="expert-advice-page">
      <div className="page-header">
        <h2>⚖️ Expert Legal Advice</h2>
        <p>Get professional legal guidance from our AI expert system</p>
      </div>

      <div className="advice-container">
        <form onSubmit={handleGetAdvice} className="advice-form">
          <div className="form-group">
            <label htmlFor="legalArea">
              <Scale size={16} />
              Legal Area (Optional)
            </label>
            <select
              id="legalArea"
              value={legalArea}
              onChange={(e) => setLegalArea(e.target.value)}
              className="area-select"
              disabled={loading}
            >
              <option value="">Select a legal area (optional)</option>
              {legalAreas.map((area) => (
                <option key={area} value={area}>
                  {area}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="query">
              <BookOpen size={16} />
              Your Legal Question
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe your legal question or situation in detail..."
              className="query-textarea"
              rows={6}
              maxLength={1500}
              disabled={loading}
            />
            <div className="char-count">
              {query.length}/1500 characters
            </div>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="advice-btn"
              disabled={!query.trim() || loading}
            >
              {loading ? <Loader size={16} className="spinner" /> : <Scale size={16} />}
              {loading ? 'Getting Advice...' : 'Get Expert Advice'}
            </button>
            <button
              type="button"
              onClick={clearForm}
              className="clear-btn"
              disabled={loading}
            >
              Clear
            </button>
          </div>
        </form>

        {advice && (
          <div className="advice-result">
            <h3>
              <Scale size={20} />
              Expert Legal Advice
            </h3>
            <div className="advice-content">
              {advice}
            </div>
            <div className="disclaimer">
              <strong>Disclaimer:</strong> This advice is for informational purposes only and does not constitute legal advice. 
              Please consult with a qualified attorney for specific legal matters.
            </div>
          </div>
        )}

        {!advice && !loading && (
          <div className="advice-examples">
            <h3>Common Legal Questions:</h3>
            <div className="examples-grid">
              <div className="example-card" onClick={() => setQuery("What are the key elements of a valid contract?")}>
                <h4>Contract Law</h4>
                <p>What are the key elements of a valid contract?</p>
              </div>
              <div className="example-card" onClick={() => setQuery("What should I do if I'm facing wrongful termination?")}>
                <h4>Employment Law</h4>
                <p>What should I do if I'm facing wrongful termination?</p>
              </div>
              <div className="example-card" onClick={() => setQuery("How do I protect my intellectual property?")}>
                <h4>IP Law</h4>
                <p>How do I protect my intellectual property?</p>
              </div>
              <div className="example-card" onClick={() => setQuery("What are my rights as a tenant?")}>
                <h4>Real Estate</h4>
                <p>What are my rights as a tenant?</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExpertAdvicePage;