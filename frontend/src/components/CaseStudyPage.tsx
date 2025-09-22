import React, { useState } from 'react';
import { FileText, Loader, Brain } from 'lucide-react';
import { caseStudyAPI } from '../services/api';

const CaseStudyPage: React.FC = () => {
  const [caseDetails, setCaseDetails] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseDetails.trim()) return;

    setLoading(true);
    setAnalysis('');

    try {
      const response = await caseStudyAPI.analyzeCase(caseDetails);
      setAnalysis(response.analysis);
    } catch (error: any) {
      setAnalysis(`Error: ${error.response?.data?.detail || 'Analysis failed'}`);
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setCaseDetails('');
    setAnalysis('');
  };

  return (
    <div className="case-study-page">
      <div className="page-header">
        <h2>📊 Case Study Analysis</h2>
        <p>Submit case details for comprehensive legal analysis</p>
      </div>

      <div className="case-study-container">
        <form onSubmit={handleAnalyze} className="case-form">
          <div className="form-group">
            <label htmlFor="caseDetails">
              <FileText size={16} />
              Case Details
            </label>
            <textarea
              id="caseDetails"
              value={caseDetails}
              onChange={(e) => setCaseDetails(e.target.value)}
              placeholder="Describe the case details, including relevant facts, legal issues, parties involved, and any specific questions you have..."
              className="case-textarea"
              rows={10}
              maxLength={2000}
              disabled={loading}
            />
            <div className="char-count">
              {caseDetails.length}/2000 characters
            </div>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="analyze-btn"
              disabled={!caseDetails.trim() || loading}
            >
              {loading ? <Loader size={16} className="spinner" /> : <Brain size={16} />}
              {loading ? 'Analyzing...' : 'Analyze Case'}
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

        {analysis && (
          <div className="analysis-result">
            <h3>
              <Brain size={20} />
              Legal Analysis
            </h3>
            <div className="analysis-content">
              {analysis}
            </div>
          </div>
        )}

        {!analysis && !loading && (
          <div className="case-examples">
            <h3>Example Case Types:</h3>
            <div className="examples-grid">
              <div className="example-card">
                <h4>Contract Dispute</h4>
                <p>Breach of contract, non-performance, damages assessment</p>
              </div>
              <div className="example-card">
                <h4>Employment Law</h4>
                <p>Wrongful termination, discrimination, wage disputes</p>
              </div>
              <div className="example-card">
                <h4>Personal Injury</h4>
                <p>Negligence claims, liability assessment, damages calculation</p>
              </div>
              <div className="example-card">
                <h4>Intellectual Property</h4>
                <p>Patent infringement, trademark disputes, copyright violations</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseStudyPage;