# Research Assistant for PDFs

Full-stack RAG app to upload a research PDF, auto-summarize it, and chat with an LLM that continuously familiarizes itself through summary-aware vectors, caching, and per-conversation memory.

## System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (React + Vite)"]
        FU[FileUpload.jsx]
        SD[SummaryDisplay.jsx]
        CI[ChatInterface.jsx]
        API[services/api.js]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        MAIN[main.py<br/>Routes + CORS]
        
        subgraph Routes
            DOC[documents.py<br/>/upload]
            CHAT[chat.py<br/>/qa/ask]
            QUERY[query.py<br/>/query]
        end
        
        subgraph Core["Core Services"]
            CACHE[cache.py<br/>SimpleTTLCache<br/>MemoryStore]
            DB[db.py<br/>Chroma Client]
            EMB[embeddings.py<br/>Gemini Embed]
            CFG[config.py<br/>Env Vars]
        end
        
        MAIN --> Routes
        Routes --> Core
    end
    
    subgraph External["External Services"]
        CHROMA[(Chroma Cloud<br/>documents_collection<br/>summaries_collection)]
        GEMINI[Google Gemini<br/>LLM + Embeddings]
    end
    
    FU -->|Upload PDF| API
    CI -->|Ask Question| API
    API -->|HTTP/REST| MAIN
    
    DOC -->|Store Chunks| CHROMA
    DOC -->|Store Summaries| CHROMA
    DOC -->|Generate Summary| GEMINI
    
    CHAT -->|Query Vectors| CHROMA
    CHAT -->|Generate Answer| GEMINI
    CHAT -->|Cache Check/Set| CACHE
    
    SD -.->|Display| FU
    CI -.->|Display| CHAT
    
    style Frontend fill:#e1f5ff
    style Backend fill:#fff4e1
    style External fill:#f0f0f0
    style CACHE fill:#ffebcc
    style CHROMA fill:#e8f5e9
    style GEMINI fill:#fce4ec
```

## Data Flow Diagrams

### Upload Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Chroma
    participant Gemini
    
    User->>Frontend: Drop PDF
    Frontend->>Backend: POST /documents/upload
    Backend->>Backend: Extract text (PyPDF2)
    Backend->>Backend: Chunk text (overlap)
    Backend->>Backend: Embed chunks (SentenceTransformers)
    Backend->>Chroma: Store in documents_collection
    Backend->>Gemini: Generate structured summary
    Backend->>Backend: Embed summary sections
    Backend->>Chroma: Store in summaries_collection
    Backend->>Frontend: Return summary + metadata
    Frontend->>User: Display structured summary
```

### Chat Flow (with Cache & Memory)
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant ChatEndpoint
    participant Cache
    participant Memory
    participant Chroma
    participant Gemini
    
    User->>Frontend: Ask question
    Frontend->>ChatEndpoint: POST /qa/ask
    ChatEndpoint->>Memory: Get conversation history
    ChatEndpoint->>Cache: Check response cache
    
    alt Cache Hit
        Cache-->>ChatEndpoint: Return cached answer
        ChatEndpoint->>Memory: Append assistant turn
        ChatEndpoint-->>Frontend: Return answer
    else Cache Miss
        ChatEndpoint->>ChatEndpoint: Embed question
        ChatEndpoint->>Chroma: Query documents_collection
        ChatEndpoint->>Chroma: Query summaries_collection
        ChatEndpoint->>ChatEndpoint: Merge contexts
        ChatEndpoint->>ChatEndpoint: Build prompt (context + history)
        ChatEndpoint->>Gemini: Generate answer
        ChatEndpoint->>ChatEndpoint: Calculate confidence
        ChatEndpoint->>Cache: Store response
        ChatEndpoint->>Memory: Append assistant turn
        ChatEndpoint-->>Frontend: Return answer + sources
    end
    
    Frontend->>User: Display answer with sources
```

### Cache & Memory Architecture
```mermaid
graph LR
    subgraph ResponseCache["SimpleTTLCache"]
        RC["document_id::question → ChatResponse<br/>TTL: 10 min"]
    end
    
    subgraph MemoryStore["MemoryStore"]
        MS["conversation_id → history<br/>TTL: 24 hrs | Cap: 10 turns"]
    end
    
    subgraph VectorStores["Chroma Collections"]
        DOC_COL[("documents_collection<br/>Fine-grained chunks")]
        SUM_COL[("summaries_collection<br/>Section embeddings")]
    end
    
    Q[Question] --> RC
    RC -->|Hit| ANS[Return Cached]
    RC -->|Miss| VectorStores
    VectorStores --> MERGE[Merge Contexts]
    Q --> MS
    MS --> PROMPT[Build Prompt]
    MERGE --> PROMPT
    PROMPT --> LLM[Gemini LLM]
    LLM --> RC
    LLM --> MS
    
    style RC fill:#ffebcc
    style MS fill:#e1f5ff
    style DOC_COL fill:#e8f5e9
    style SUM_COL fill:#e8f5e9
```

## What it does
- **PDF upload and parsing**: Single-PDF intake, text extraction, chunking with overlap.
- **Structured summaries**: Gemini generates concise sections (Title/Authors, Abstract, Problem, Methodology, Key Results, Conclusion) returned to the UI.
- **Dual vector stores**:
	- `documents_collection`: fine-grained chunks for detailed grounding.
	- `summaries_collection`: section-level summary embeddings to make the chatbot feel more familiar and faster on re-asks.
- **Self-improving chat loop**:
	- Per-conversation memory keeps recent turns to maintain context.
	- Response cache avoids repeating identical LLM calls for the same doc/question.
	- Combined retrieval (chunks + summaries) gives both breadth and focus.
- **Sources and confidence**: Answers include retrieved context snippets and a simple confidence estimate derived from vector distances.

## Backend
- **FastAPI** entrypoint: `backend/main.py` (routes + CORS wiring).
- **Documents pipeline**: `routes/documents.py`
	1) Extract text (PyPDF2) and chunk with overlap.
	2) Embed chunks (SentenceTransformers all-mpnet-base-v2) → `documents_collection` in Chroma Cloud.
	3) Generate structured summary (Gemini) and embed each section → `summaries_collection`.
	4) Return metadata + summary to the frontend.
- **Chat / RAG**: `routes/chat.py`
	- Endpoint: `/qa/ask` takes `document_id`, `question`, optional `conversation_id`, `top_k`.
	- Retrieves relevant chunks **and** summary vectors, merges context, builds a prompt with conversation memory, and calls Gemini for the answer.
	- Response cache and conversation memory (see `cache.py`) reduce latency and cost.
- **Caching & memory**: `cache.py`
	- `SimpleTTLCache`: memoizes answers per document/question for a short TTL.
	- `MemoryStore`: keeps the last N exchanges per conversation with a TTL to preserve context.
- **Embeddings**: `embeddings.py` (Gemini embeddings helper for legacy/simple queries).
- **Config**: `config.py` loads env vars (Chroma keys, collections, cache/memory settings).
- **Models**: `models/chat_models.py` defines request/response contracts.

## Frontend (React + Vite)
- `FileUpload.jsx`: drag/drop upload with size/type validation and progress states.
- `SummaryDisplay.jsx`: renders the structured summary returned by the backend.
- `ChatInterface.jsx`: conversation-scoped chat; shows sources and confidence; supplies `conversationId` to maintain memory.
- `services/api.js`: central API client (`uploadDocument`, `askQuestion`, `checkHealth` if desired by the app).

## Environment
Copy `.env.example` to `.env` and set at least:
- `GEMINI_API_KEY`
- `CHROMA_API_KEY`, `CHROMA_TENENT`, `CHROMA_DATABSE`
- `CHROMA_COLLECTION` (default `documents_collection`)
- `SUMMARIES_COLLECTION` (default `summaries_collection`)
- `CACHE_TTL_SECONDS`, `MEMORY_TTL_SECONDS`, `MEMORY_MAX_MESSAGES`

## Run locally
Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend
```bash
cd frontend
npm install
npm run dev
```

## Usage flow
1) Start backend and frontend.
2) Upload a PDF → get structured summary and metadata.
3) Ask questions → RAG uses chunks + summary vectors; answers include sources and confidence; repeated identical questions hit the response cache; conversation memory keeps context per `conversationId`.

## Notes
- Re-upload a document to refresh both chunk and summary embeddings.
- The chatbot “self-improves” per session by combining cached answers, short-term memory, and summary-aware retrieval, making follow-up questions feel more tailored without retraining the model.
