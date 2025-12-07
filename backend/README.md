# PDF Research Assistant Backend

A FastAPI-based backend for a PDF research paper analysis system using Retrieval Augmented Generation (RAG) with Cache Augmented Generation (CAG).

## Features

- **PDF Upload**: Upload research papers in PDF format
- **Automatic Summary Generation**: Generates structured summaries with:
  - Title & Authors
  - Abstract
  - Problem Statement
  - Methodology
  - Key Results
  - Conclusion
- **Question Answering**: Ask natural language questions about uploaded papers
- **RAG/CAG System**: Uses ChromaDB for vector storage and Gemini API for LLM capabilities
- **Caching**: In-memory cache for improved performance on repeated queries

## Project Structure

```
backend/
├── app/
│   ├── models/           # Pydantic schemas and data models
│   │   └── schemas.py
│   ├── services/         # Business logic services
│   │   ├── gemini_service.py    # Gemini LLM integration
│   │   └── rag_service.py       # RAG/CAG service with ChromaDB
│   ├── routes/           # API endpoint routes
│   │   ├── health.py
│   │   ├── documents.py
│   │   └── qa.py
│   ├── utils/            # Utility functions
│   │   ├── pdf_processor.py     # PDF text extraction
│   │   ├── vector_store.py      # ChromaDB wrapper
│   │   └── cache.py             # CAG caching system
│   ├── main.py           # FastAPI application
│   └── __init__.py
├── config/
│   ├── settings.py       # Configuration management
│   └── __init__.py
├── data/
│   ├── uploads/          # Uploaded PDF files
│   └── chroma_db/        # ChromaDB vector storage
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── wsgi.py              # WSGI entry point
└── README.md            # This file
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- pip or conda package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # Using venv
   python -m venv venv
   
   # Activate venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   # Development mode (with auto-reload)
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production mode
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

6. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health/` - Health check
- `GET /health/ready` - Readiness check

### Document Management
- `POST /documents/upload` - Upload PDF document
- `GET /documents/list` - List all documents
- `GET /documents/{document_id}` - Get document metadata
- `DELETE /documents/{document_id}` - Delete document

### Question Answering
- `POST /qa/ask` - Ask question about a document
- `POST /qa/batch` - Ask multiple questions

## Configuration

Environment variables in `.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# Gemini API
GEMINI_API_KEY=your_api_key_here

# ChromaDB Configuration
CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION_NAME=research_papers

# File Upload Configuration
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=./data/uploads

# LLM Configuration
LLM_MODEL_NAME=gemini-pro
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
MAX_TOKENS=1000
TEMPERATURE=0.7

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Usage Examples

### Upload a PDF
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@research_paper.pdf"
```

### Ask a Question
```bash
curl -X POST "http://localhost:8000/qa/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "document-uuid",
    "question": "What are the main findings?",
    "top_k": 3
  }'
```

### List Documents
```bash
curl "http://localhost:8000/documents/list"
```

## System Architecture

### RAG (Retrieval Augmented Generation)
1. PDF is uploaded and text is extracted
2. Text is chunked into smaller segments
3. Embeddings are generated and stored in ChromaDB
4. When a question is asked, relevant chunks are retrieved
5. Chunks are passed as context to Gemini API
6. LLM generates answer based on context

### CAG (Cache Augmented Generation)
- Q&A results are cached to avoid repeated LLM calls
- Cache is stored in-memory with document_id + question hash as key
- Cache is cleared when documents are deleted

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **ChromaDB**: Vector database for embeddings
- **Gemini API**: Large Language Model for text generation
- **PyPDF2/pdfplumber**: PDF processing
- **Sentence Transformers**: Embedding models
- **Pydantic**: Data validation

## Logging

Logs are stored in the `logs/` directory. Configuration can be adjusted in `app/main.py`.

## Error Handling

The API includes comprehensive error handling:
- File validation (PDF only, size limits)
- Document existence checks
- API error responses with detailed messages
- Global exception handler

## Performance Considerations

- **Caching**: Q&A results cached to reduce API calls
- **Chunking**: Text chunked efficiently for better retrieval
- **Embedding**: Using lightweight embedding models for speed
- **Connection pooling**: Configured for ChromaDB

## Future Enhancements

- Support for multiple document uploads in batch
- Advanced search filters
- Citation tracking
- Document comparison
- Export functionality (PDF, Word, etc.)
- Redis integration for distributed caching
- WebSocket support for real-time updates

## Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Gemini API Issues
- Verify API key is correctly set in `.env`
- Check API quota and rate limits
- Ensure network connectivity

### ChromaDB Issues
- Verify database directory is writable
- Check disk space availability
- Clear data folder if corrupted: `rm -rf data/chroma_db`

## License

This project is part of the Fire Rescue Robot Webbot assignment.

## Support

For issues and support, please refer to the project repository.
