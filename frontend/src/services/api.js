/**
 * API Service for Research Assistant
 * Handles all communication with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Upload a PDF document and get structured summary
 * @param {File} file - PDF file to upload
 * @returns {Promise<Object>} Upload response with summary
 */
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload document');
  }

  return response.json();
};

/**
 * Get list of all uploaded documents
 * @returns {Promise<Object>} List of documents
 */
export const listDocuments = async () => {
  const response = await fetch(`${API_BASE_URL}/documents/list`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch documents');
  }

  return response.json();
};

/**
 * Ask a question about a specific document
 * @param {string} documentId - Document ID
 * @param {string} question - Question to ask
 * @param {number} topK - Number of chunks to retrieve
 * @returns {Promise<Object>} Answer response
 */
export const askQuestion = async (documentId, question, topK = 3) => {
  const response = await fetch(`${API_BASE_URL}/qa/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      document_id: documentId,
      question: question,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get answer');
  }

  return response.json();
};

/**
 * Check API health status
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/health/`);
  
  if (!response.ok) {
    throw new Error('API is not available');
  }

  return response.json();
};

export default {
  uploadDocument,
  listDocuments,
  askQuestion,
  checkHealth,
};
