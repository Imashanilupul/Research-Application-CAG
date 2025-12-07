import './SummaryDisplay.css';

/**
 * SummaryDisplay Component
 * Displays structured summary of the research paper
 */
function SummaryDisplay({ document }) {
  if (!document) return null;

  const { filename, upload_date, file_size, summary } = document;

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Summary sections to display
  const sections = [
    { key: 'title_and_authors', icon: '📄', color: '#6366f1' },
    { key: 'abstract', icon: '📋', color: '#8b5cf6' },
    { key: 'problem_statement', icon: '❓', color: '#ec4899' },
    { key: 'methodology', icon: '🔬', color: '#14b8a6' },
    { key: 'key_results', icon: '📊', color: '#f59e0b' },
    { key: 'conclusion', icon: '✅', color: '#22c55e' },
  ];

  return (
    <div className="summary-container">
      {/* Document Info Header */}
      <div className="document-header">
        <div className="document-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        </div>
        <div className="document-info">
          <h2 className="document-filename">{filename}</h2>
          <div className="document-meta">
            <span className="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              {formatDate(upload_date)}
            </span>
            <span className="meta-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              {formatFileSize(file_size)}
            </span>
          </div>
        </div>
      </div>

      {/* Summary Sections */}
      <div className="summary-sections">
        <h3 className="summary-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
          Paper Summary
        </h3>

        <div className="sections-grid">
          {sections.map(({ key, icon, color }) => {
            const section = summary[key];
            if (!section) return null;

            return (
              <div
                key={key}
                className="section-card"
                style={{ '--accent-color': color }}
              >
                <div className="section-header">
                  <span className="section-icon">{icon}</span>
                  <h4 className="section-title">{section.title}</h4>
                </div>
                <div className="section-content">
                  {section.content}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default SummaryDisplay;
