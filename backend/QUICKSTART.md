# Quick Start Guide

## Prerequisites
- Python 3.9 or higher
- pip or conda
- Gemini API key (from Google AI Studio)

## Installation (5 minutes)

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create and activate virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
# Copy template
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

### 5. Initialize application
```bash
python init_app.py
```

### 6. Run the server
```bash
# Using start script (Windows)
start.bat

# Using start script (macOS/Linux)
bash start.sh

# Or manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation
Open in your browser:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Getting Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key
4. Paste in `.env` file: `GEMINI_API_KEY=your_key_here`

## First Test

### 1. Upload a PDF
Use the Swagger UI at http://localhost:8000/docs
- Click on "POST /documents/upload"
- Click "Try it out"
- Select a PDF file
- Click "Execute"

### 2. Ask a Question
- Copy the `id` from the upload response
- Click on "POST /qa/ask"
- Click "Try it out"
- Paste the ID in `document_id`
- Enter your question
- Click "Execute"

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Backend will be available at http://localhost:8000
```

## Project Structure Summary

```
backend/
├── app/              # Main application code
│   ├── models/       # Data schemas
│   ├── services/     # Business logic (RAG, Gemini)
│   ├── routes/       # API endpoints
│   └── utils/        # Utilities (PDF, Vector DB, Cache)
├── config/           # Configuration
├── data/             # Storage (uploads, ChromaDB)
├── requirements.txt  # Dependencies
├── .env.example      # Environment template
├── README.md         # Full documentation
└── API_EXAMPLES.py   # API examples
```

## Key Features Implemented

✅ **PDF Upload** - Upload research papers in PDF format
✅ **Auto Summary** - Generates structured summaries with:
  - Title & Authors
  - Abstract
  - Problem Statement
  - Methodology
  - Key Results
  - Conclusion

✅ **Q&A System** - Ask questions with RAG/CAG:
  - Retrieves relevant chunks from ChromaDB
  - Uses Gemini API for answer generation
  - Caches results for performance

✅ **Document Management** - List, retrieve, and delete documents
✅ **Vector Database** - ChromaDB for storing embeddings
✅ **Caching System** - In-memory cache for Q&A results

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health/` | Health check |
| POST | `/documents/upload` | Upload PDF |
| GET | `/documents/list` | List documents |
| GET | `/documents/{id}` | Get document info |
| DELETE | `/documents/{id}` | Delete document |
| POST | `/qa/ask` | Ask question |
| POST | `/qa/batch` | Batch questions |

## Environment Variables

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# Gemini
GEMINI_API_KEY=your_key_here

# ChromaDB
CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION_NAME=research_papers

# Files
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=./data/uploads

# LLM
LLM_MODEL_NAME=gemini-pro
MAX_TOKENS=1000
TEMPERATURE=0.7

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Troubleshooting

### ModuleNotFoundError
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API Key Error
- Verify `GEMINI_API_KEY` is set in `.env`
- Check key from Google AI Studio is correct
- Test API key validity

### ChromaDB Path Error
```bash
# Ensure data directory exists and is writable
mkdir -p data/uploads data/chroma_db
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

## Next Steps

1. **Frontend Development** - Build React UI for document upload and Q&A
2. **Testing** - Add pytest test cases
3. **Deployment** - Deploy to cloud (Google Cloud, AWS, Azure)
4. **Enhancements** - Add batch processing, export features, etc.

## Support

For full documentation, see:
- `README.md` - Complete feature documentation
- `DEVELOPMENT.md` - Development guidelines
- `PROJECT_STRUCTURE.md` - Detailed architecture
- `API_EXAMPLES.py` - API request/response examples

## Performance Tips

- Keep PDF files under 50MB for optimal processing
- Adjust chunk size based on content type
- Monitor cache statistics regularly
- Use batch Q&A for multiple questions on same document
