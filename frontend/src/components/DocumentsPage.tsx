import React, { useState, useEffect } from 'react';
import { Upload, Search, File, Trash2, Loader, AlertCircle, CheckCircle } from 'lucide-react';
import { ragAPI } from '../services/api';
import { DocumentSet, RAGQueryResponse } from '../types';

const DocumentsPage: React.FC = () => {
  const [documentSets, setDocumentSets] = useState<DocumentSet[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [queryLoading, setQueryLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [namespace, setNamespace] = useState('');
  const [queryResults, setQueryResults] = useState<RAGQueryResponse | null>(null);
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error' | '', message: string }>({ type: '', message: '' });

  useEffect(() => {
    loadDocumentSets();
  }, []);

  const loadDocumentSets = async () => {
    setLoading(true);
    try {
      const response = await ragAPI.getDocumentSets();
      setDocumentSets(response.document_sets);
    } catch (error: any) {
      console.error('Failed to load document sets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploadLoading(true);
    setUploadStatus({ type: '', message: '' });

    try {
      const response = await ragAPI.uploadDocuments(files);
      setUploadStatus({
        type: 'success',
        message: `Successfully uploaded ${files.length} documents to namespace: ${response.namespace}`
      });
      loadDocumentSets();
      // Clear the file input
      e.target.value = '';
    } catch (error: any) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Upload failed'
      });
    } finally {
      setUploadLoading(false);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setQueryLoading(true);
    setQueryResults(null);

    try {
      const response = await ragAPI.queryDocuments(query, namespace || undefined);
      setQueryResults(response);
    } catch (error: any) {
      setQueryResults({
        response: `Error: ${error.response?.data?.detail || 'Query failed'}`,
        sources: [],
        success: false
      });
    } finally {
      setQueryLoading(false);
    }
  };

  const handleDeleteSet = async (namespaceToDelete: string) => {
    if (!window.confirm(`Are you sure you want to delete the document set "${namespaceToDelete}"?`)) {
      return;
    }

    try {
      await ragAPI.deleteDocumentSet(namespaceToDelete);
      loadDocumentSets();
    } catch (error: any) {
      alert(`Failed to delete document set: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="documents-page">
      <div className="page-header">
        <h2>📄 Document Management</h2>
        <p>Upload legal documents and query them using AI-powered search</p>
      </div>

      {/* Upload Section */}
      <div className="section upload-section">
        <h3>
          <Upload size={20} />
          Upload Documents
        </h3>
        <div className="upload-area">
          <input
            type="file"
            id="fileInput"
            multiple
            accept=".pdf,.txt,.doc,.docx"
            onChange={handleFileUpload}
            disabled={uploadLoading}
            className="file-input"
          />
          <label htmlFor="fileInput" className={`file-input-label ${uploadLoading ? 'disabled' : ''}`}>
            {uploadLoading ? (
              <>
                <Loader size={20} className="spinner" />
                Uploading...
              </>
            ) : (
              <>
                <Upload size={20} />
                Choose Files (PDF, TXT, DOC, DOCX)
              </>
            )}
          </label>
        </div>

        {uploadStatus.message && (
          <div className={`alert ${uploadStatus.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {uploadStatus.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
            {uploadStatus.message}
          </div>
        )}
      </div>

      {/* Query Section */}
      <div className="section query-section">
        <h3>
          <Search size={20} />
          Query Documents
        </h3>
        <form onSubmit={handleQuery} className="query-form">
          <div className="query-inputs">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask questions about your documents..."
              className="query-input"
              disabled={queryLoading}
            />
            <input
              type="text"
              value={namespace}
              onChange={(e) => setNamespace(e.target.value)}
              placeholder="Document set name (optional)"
              className="namespace-input"
              disabled={queryLoading}
            />
            <button
              type="submit"
              className="query-btn"
              disabled={!query.trim() || queryLoading}
            >
              {queryLoading ? <Loader size={16} className="spinner" /> : <Search size={16} />}
              {queryLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {queryResults && (
          <div className="query-results">
            <div className="ai-response">
              <h4>🤖 AI Response:</h4>
              <div className="response-content">
                {queryResults.response}
              </div>
            </div>

            {queryResults.sources && queryResults.sources.length > 0 && (
              <div className="sources">
                <h4>📚 Sources:</h4>
                {queryResults.sources.map((source, index) => (
                  <div key={index} className="source-item">
                    <div className="source-header">
                      <span className="source-title">Source {index + 1}</span>
                      <span className="source-score">Score: {source.score?.toFixed(3)}</span>
                    </div>
                    <div className="source-content">
                      {source.page_content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Document Sets Section */}
      <div className="section document-sets-section">
        <div className="section-header">
          <h3>
            <File size={20} />
            Your Document Sets
          </h3>
          <button onClick={loadDocumentSets} className="refresh-btn" disabled={loading}>
            {loading ? <Loader size={16} className="spinner" /> : 'Refresh'}
          </button>
        </div>

        {loading ? (
          <div className="loading-state">
            <Loader size={24} className="spinner" />
            Loading document sets...
          </div>
        ) : documentSets.length === 0 ? (
          <div className="empty-state">
            <File size={48} />
            <h4>No document sets found</h4>
            <p>Upload some documents to get started with document analysis.</p>
          </div>
        ) : (
          <div className="document-sets-grid">
            {documentSets.map((set) => (
              <div key={set.namespace} className="document-set-card">
                <div className="card-header">
                  <div className="set-info">
                    <h4 className="set-name">📁 {set.namespace}</h4>
                    <p className="set-count">{set.document_count} documents</p>
                  </div>
                  <button
                    onClick={() => handleDeleteSet(set.namespace)}
                    className="delete-btn"
                    title="Delete document set"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="card-footer">
                  <span className="creation-date">
                    Created: {new Date(set.created_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={() => setNamespace(set.namespace)}
                    className="use-btn"
                  >
                    Use in Query
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentsPage;