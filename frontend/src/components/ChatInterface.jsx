import { useEffect, useRef, useState } from 'react';
import { askQuestion } from '../services/api';
import './ChatInterface.css';

/**
 * ChatInterface Component
 * Q&A chatbot for asking questions about the uploaded paper
 */
function ChatInterface({ documentId, documentName }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const buildConversationId = () => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return `conv-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Add welcome message when document changes
  useEffect(() => {
    if (documentId) {
      setConversationId(buildConversationId());
      setMessages([{
        id: 'welcome',
        type: 'assistant',
        content: `I'm ready to answer questions about "${documentName}". Feel free to ask anything about the research paper!`,
        timestamp: new Date().toISOString()
      }]);
    }
  }, [documentId, documentName]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const question = inputValue.trim();
    if (!question || isLoading) return;

    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: question,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const convId = conversationId || buildConversationId();
      setConversationId(convId);
      const response = await askQuestion(documentId, convId, question);
      
      // Add assistant response
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Add error message
      const errorMessage = {
        id: `error-${Date.now()}`,
        type: 'error',
        content: error.message || 'Failed to get answer. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Sample questions
  const sampleQuestions = [
    "What is the main contribution of this paper?",
    "What methodology was used?",
    "What are the key findings?",
    "What are the limitations?",
  ];

  const handleSampleQuestion = (question) => {
    setInputValue(question);
    inputRef.current?.focus();
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <div>
          <h3 className="chat-title">Ask Questions</h3>
          <p className="chat-subtitle">About: {documentName}</p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="sample-questions">
              <p>Try asking:</p>
              <div className="sample-buttons">
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    className="sample-question-btn"
                    onClick={() => handleSampleQuestion(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.type}`}
          >
            {message.type === 'assistant' && (
              <div className="message-avatar assistant-avatar">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="10 8 16 12 10 16 10 8" />
                </svg>
              </div>
            )}
            
            {message.type === 'user' && (
              <div className="message-avatar user-avatar">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            )}

            {message.type === 'error' && (
              <div className="message-avatar error-avatar">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
              </div>
            )}

            <div className="message-content">
              <p className="message-text">{message.content}</p>
              
              {message.sources && message.sources.length > 0 && (
                <div className="message-sources">
                  <details>
                    <summary>View sources ({message.sources.length})</summary>
                    <div className="sources-list">
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="source-item">
                          <span className="source-label">Source {idx + 1}:</span>
                          <p className="source-text">{source}</p>
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}

              {message.confidence !== undefined && message.confidence > 0 && (
                <div className="message-confidence">
                  <span>Confidence: {Math.round(message.confidence * 100)}%</span>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="message-avatar assistant-avatar">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10 8 16 12 10 16 10 8" />
              </svg>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="chat-input-container">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder="Ask a question about the paper..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={!inputValue.trim() || isLoading}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;
