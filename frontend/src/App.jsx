import { useState, useEffect } from 'react';
import { FileUpload, SummaryDisplay, ChatInterface } from './components';
import { checkHealth } from './services/api';
import './App.css';

function App() {
  const [currentDocument, setCurrentDocument] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API health on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        await checkHealth();
        setApiStatus('healthy');
      } catch (error) {
        setApiStatus('error');
      }
    };
    checkApiHealth();
  }, []);

  const handleUploadStart = (file) => {
    setIsUploading(true);
    setUploadingFile(file);
    setCurrentDocument(null);
  };

  const handleUploadSuccess = (result) => {
    setCurrentDocument(result);
    setIsUploading(false);
    setUploadingFile(null);
  };

  const handleNewUpload = () => {
    setCurrentDocument(null);
    setIsUploading(false);
    setUploadingFile(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
            <h1>Research Assistant</h1>
          </div>
          <div className={`api-status ${apiStatus}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {apiStatus === 'checking' && 'Connecting...'}
              {apiStatus === 'healthy' && 'API Connected'}
              {apiStatus === 'error' && 'API Offline'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {/* Show upload progress */}
        {isUploading && uploadingFile && (
          <div className="upload-progress">
            <div className="progress-content">
              <div className="spinner"></div>
              <div className="progress-text">
                <p className="progress-title">Analyzing your research paper...</p>
                <p className="progress-subtitle">{uploadingFile.name}</p>
              </div>
            </div>
            <div className="progress-steps">
              <div className="step active">
                <span className="step-icon">📤</span>
                <span>Uploading</span>
              </div>
              <div className="step">
                <span className="step-icon">🔍</span>
                <span>Extracting Text</span>
              </div>
              <div className="step">
                <span className="step-icon">🤖</span>
                <span>Generating Summary</span>
              </div>
              <div className="step">
                <span className="step-icon">✅</span>
                <span>Complete</span>
              </div>
            </div>
          </div>
        )}

        {/* Show upload zone when no document */}
        {!currentDocument && !isUploading && (
          <section className="upload-section">
            <div className="section-header">
              <h2>Upload Research Paper</h2>
              <p>Upload a PDF to get an AI-generated structured summary and ask questions</p>
            </div>
            <FileUpload
              onUploadStart={handleUploadStart}
              onUploadSuccess={handleUploadSuccess}
              disabled={isUploading || apiStatus !== 'healthy'}
            />
            
            {apiStatus === 'error' && (
              <div className="api-error-banner">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span>Backend API is not available. Please make sure the server is running on port 8000.</span>
              </div>
            )}

            {/* Features */}
            <div className="features">
              <div className="feature">
                <div className="feature-icon">📄</div>
                <h3>Structured Summary</h3>
                <p>Get organized summaries with title, abstract, methodology, results & conclusion</p>
              </div>
              <div className="feature">
                <div className="feature-icon">💬</div>
                <h3>Ask Questions</h3>
                <p>Chat with your paper using our RAG-powered AI assistant</p>
              </div>
              <div className="feature">
                <div className="feature-icon">⚡</div>
                <h3>Fast Analysis</h3>
                <p>Powered by Gemini AI for quick and accurate insights</p>
              </div>
            </div>
          </section>
        )}

        {/* Show summary and chat when document is loaded */}
        {currentDocument && !isUploading && (
          <div className="document-view">
            <div className="document-actions">
              <button className="btn-new-upload" onClick={handleNewUpload}>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Upload New Paper
              </button>
            </div>

            <div className="document-content">
              {/* Summary Section */}
              <section className="summary-section">
                <SummaryDisplay document={currentDocument} />
              </section>

              {/* Q&A Section */}
              <section className="qa-section">
                <ChatInterface
                  documentId={currentDocument.id}
                  documentName={currentDocument.filename}
                />
              </section>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Research Assistant for PDFs • Powered by Gemini AI & RAG</p>
      </footer>
    </div>
  );
}

export default App;
