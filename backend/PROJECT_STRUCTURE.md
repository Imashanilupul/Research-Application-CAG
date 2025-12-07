# Backend Project Structure

```
backend/
│
├── app/                              # Main application package
│   ├── __init__.py
│   ├── main.py                       # FastAPI application setup
│   │
│   ├── models/                       # Pydantic data models
│   │   ├── __init__.py
│   │   └── schemas.py                # All request/response schemas
│   │
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── gemini_service.py         # Google Gemini API integration
│   │   │   └── GeminiService class
│   │       ├── generate_summary()
│   │       └── answer_question()
│   │   │
│   │   └── rag_service.py            # RAG/CAG orchestration
│   │       └── RAGService class
│   │           ├── process_pdf()
│   │           ├── answer_question() (with caching)
│   │           ├── get_document_metadata()
│   │           ├── get_all_documents()
│   │           └── delete_document()
│   │
│   ├── routes/                       # API endpoint routes
│   │   ├── __init__.py
│   │   ├── health.py                 # Health check endpoints
│   │   │   ├── GET /health/
│   │   │   └── GET /health/ready
│   │   │
│   │   ├── documents.py              # Document management
│   │   │   ├── POST /documents/upload
│   │   │   ├── GET /documents/list
│   │   │   ├── GET /documents/{id}
│   │   │   └── DELETE /documents/{id}
│   │   │
│   │   └── qa.py                     # Question answering
│   │       ├── POST /qa/ask
│   │       └── POST /qa/batch
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── pdf_processor.py          # PDF text extraction
│       │   └── PDFProcessor class
│       │       ├── extract_text()
│       │       ├── extract_text_with_pdfplumber()
│       │       └── get_pdf_metadata()
│       │   └── chunk_text() function
│       │
│       ├── vector_store.py           # ChromaDB wrapper
│       │   └── VectorStoreManager class
│       │       ├── add_documents()
│       │       ├── search()
│       │       ├── delete_document()
│       │       ├── get_collection_info()
│       │       └── clear_collection()
│       │
│       └── cache.py                  # CAG caching system
│           ├── Cache class
│           │   ├── get()
│           │   ├── set()
│           │   ├── delete()
│           │   ├── delete_by_document()
│           │   ├── clear()
│           │   └── get_stats()
│           │
│           ├── CAGCache class (extends Cache)
│           │   ├── store_qa_result()
│           │   └── get_qa_result()
│           │
│           └── Global instances: cache, cag_cache
│
├── config/                           # Configuration module
│   ├── __init__.py
│   └── settings.py                   # Pydantic Settings with .env support
│
├── data/                             # Data storage
│   ├── uploads/                      # Temporary PDF storage
│   ├── chroma_db/                    # ChromaDB persistent storage
│   └── .gitkeep
│
├── logs/                             # Application logs
│   └── .gitkeep
│
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Project configuration
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── README.md                         # Project documentation
├── DEVELOPMENT.md                    # Development guidelines
├── API_EXAMPLES.py                   # API request/response examples
├── init_app.py                       # Application initialization
├── conftest.py                       # pytest configuration
├── wsgi.py                           # WSGI entry point for production
├── Dockerfile                        # Docker container configuration
├── docker-compose.yml                # Docker Compose setup
├── start.sh                          # Linux/Mac startup script
└── start.bat                         # Windows startup script
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                          │
│  ┌────────────┬──────────────┬────────────┐                     │
│  │  Health    │   Documents  │    Q&A     │                     │
│  │  Routes    │   Routes     │   Routes   │                     │
│  └────────────┴──────────────┴────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Service Layer (Business Logic)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              RAG Service                                 │   │
│  │  • PDF Processing  • Chunking  • Q&A with Cache         │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Gemini Service (LLM Integration)                 │   │
│  │  • Summary Generation  • Question Answering              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│              Utility & Infrastructure Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ PDF Parser   │  │ Vector Store │  │   Cache      │           │
│  │ (pdfplumber) │  │ (ChromaDB)   │  │ (In-Memory)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 External Services & Storage                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Google       │  │ ChromaDB     │  │ File System  │           │
│  │ Gemini API   │  │ Embeddings   │  │ PDF Upload   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Request/Response Flow

### PDF Upload Flow
```
1. Client sends PDF file
   ↓
2. FastAPI validates file (type, size)
   ↓
3. RAGService.process_pdf()
   ├─ Extract text (PDFProcessor)
   ├─ Generate summary (GeminiService)
   ├─ Chunk text
   ├─ Store in ChromaDB (VectorStoreManager)
   └─ Store metadata
   ↓
4. Return document ID + summary to client
```

### Question Answering Flow
```
1. Client sends question + document_id
   ↓
2. RAGService.answer_question()
   ├─ Check CAGCache for cached result
   │  └─ If cache hit, return immediately
   │
   ├─ Query ChromaDB for relevant chunks
   ├─ Combine chunks as context
   ├─ Send to GeminiService.answer_question()
   ├─ Store result in CAGCache
   └─ Return answer + sources + confidence
   ↓
3. Return AnswerResponse to client
```

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | Web API server |
| ASGI Server | Uvicorn | Application server |
| Data Validation | Pydantic | Request/response schemas |
| PDF Processing | pdfplumber, PyPDF2 | Extract text from PDFs |
| Vector DB | ChromaDB | Store and retrieve embeddings |
| Embeddings | Sentence Transformers | Generate text embeddings |
| LLM | Google Gemini API | Generate summaries & answers |
| Caching | In-Memory Cache | Cache Q&A results (CAG) |
| Config | python-dotenv | Manage environment variables |

## Configuration Hierarchy

```
1. Environment Variables (.env)
   ↓
2. Pydantic Settings (config/settings.py)
   ↓
3. FastAPI Application (app/main.py)
   ↓
4. Services & Routes
```

## Error Handling

```
Request
  ↓
Try Process
  ├─ Success → Return Response
  └─ Error → HTTPException
              ↓
         Log Error
              ↓
         Return Error Response
         (with meaningful message)
```

## Performance Considerations

- **Chunking**: 500 chars with 100 char overlap for better context
- **Embeddings**: all-MiniLM-L6-v2 (lightweight, fast)
- **Caching**: In-memory cache for repeated questions
- **Vector Search**: Cosine similarity (fast, accurate)
- **Batch Processing**: Support for batch Q&A requests

## Security Features

- ✅ File type validation (PDF only)
- ✅ File size limits
- ✅ Input validation (Pydantic)
- ✅ CORS configuration
- ✅ Error messages don't expose internals
- ✅ API key management via .env
