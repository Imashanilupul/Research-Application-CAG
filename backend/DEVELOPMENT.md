# Backend Development and Deployment

## Local Development

### Quick Start
```bash
# Setup
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
uvicorn app.main:app --reload
```

### Development Commands
```bash
# Format code
black app/

# Lint
flake8 app/

# Run tests
pytest

# Run with specific log level
python -m uvicorn app.main:app --reload --log-level debug
```

## Project Layout Explanation

### app/
Main application package containing all code.

- **models/**: Data schemas and validation using Pydantic
- **services/**: Business logic (RAG, LLM integration)
- **routes/**: API endpoints grouped by functionality
- **utils/**: Reusable utility functions
- **main.py**: FastAPI application setup

### config/
Configuration management with environment variables.

### data/
Runtime data storage:
- **uploads/**: Temporary storage of uploaded PDFs
- **chroma_db/**: Vector database persistent storage

### logs/
Application logs and debugging information.

## Key Components

### RAG Service (app/services/rag_service.py)
Orchestrates the entire RAG/CAG workflow:
- PDF processing
- Text chunking
- Vector storage
- Question answering with caching

### Gemini Service (app/services/gemini_service.py)
Handles all interactions with Google's Gemini API:
- Summary generation
- Question answering

### Vector Store Manager (app/utils/vector_store.py)
Wrapper around ChromaDB for:
- Storing embeddings
- Similarity search
- Document management

### Cache System (app/utils/cache.py)
Implements CAG with in-memory caching:
- Q&A result caching
- Cache key generation
- Cache statistics

## API Design

### Resource-Oriented
- `/documents/` - Document management
- `/qa/` - Question answering

### Response Format
All responses follow consistent format:
```json
{
  "status": "success|error",
  "data": {},
  "message": "string"
}
```

## Database Schema (ChromaDB)

Collections store:
- **documents**: Text chunks from PDFs
- **metadatas**: Associated metadata (doc_id, chunk_index, etc.)
- **embeddings**: Vector embeddings from sentence transformers

## Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Using Docker (future)
See main Docker configuration at project root.

## Environment Variables

Required:
- `GEMINI_API_KEY` - Your Gemini API key

Optional (with defaults):
- `API_HOST` - Default: 0.0.0.0
- `API_PORT` - Default: 8000
- `DEBUG` - Default: False
- `LOG_LEVEL` - Default: INFO
- `MAX_FILE_SIZE_MB` - Default: 50
- `MAX_TOKENS` - Default: 1000

## Security Considerations

- File upload validation (PDF only, size limits)
- Input validation using Pydantic
- CORS configuration for frontend integration
- Error messages don't expose sensitive info

## Performance Tips

1. Adjust chunk size based on your documents
2. Use appropriate embedding model size
3. Implement pagination for document listings
4. Monitor cache hit rates
5. Use production ASGI server (Gunicorn, Uvicorn with workers)

## Testing Strategy (Future)

```
tests/
├── unit/
│   ├── test_pdf_processor.py
│   ├── test_gemini_service.py
│   └── test_rag_service.py
├── integration/
│   └── test_api_endpoints.py
└── conftest.py
```
