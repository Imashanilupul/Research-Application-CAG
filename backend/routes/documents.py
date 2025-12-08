import io
import json
import uuid
from datetime import datetime
from typing import List, Optional

import google.generativeai as genai
import PyPDF2
from fastapi import APIRouter, File, HTTPException, UploadFile
from sentence_transformers import SentenceTransformer

import config
from db import get_chroma_client

router = APIRouter()
client = get_chroma_client()
collection = client.get_or_create_collection(config.CHROMA_COLLECTION)

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
genai.configure(api_key=config.GEMINI_API_KEY)

SUMMARY_MODEL = "gemini-1.5-flash"
SUMMARY_MAX_CHARS = 8000  # Trim very large PDFs to keep prompt size reasonable

def get_free_embedding(text: str):
    """Generate embeddings using free SentenceTransformers"""
    return embedding_model.encode(text).tolist()


def generate_structured_summary(full_text: str) -> dict:
    """Generate a structured summary using Gemini; fall back gracefully on errors."""
    trimmed_text = full_text[:SUMMARY_MAX_CHARS]
    prompt = f"""
    You are a research-paper summarizer. Produce a concise JSON object with exactly these keys:
        - title_and_authors: {{"title": "Title & Authors", "content": "..."}}
        - abstract: {{"title": "Abstract", "content": "..."}}
        - problem_statement: {{"title": "Problem Statement", "content": "..."}}
        - methodology: {{"title": "Methodology", "content": "..."}}
        - key_results: {{"title": "Key Results", "content": "..."}}
        - conclusion: {{"title": "Conclusion", "content": "..."}}

    Rules:
        - Keep each section short (2-4 sentences) and factual.
        - If information is missing, write "Not clearly stated".
        - Return only valid JSON (no code fences, no prose outside the JSON).

    Paper content:
    {trimmed_text}
    """

    try:
        model = genai.GenerativeModel(SUMMARY_MODEL)
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception:
        def _fallback(title: str) -> dict:
            return {"title": title, "content": "Not clearly stated."}

        return {
            "title_and_authors": _fallback("Title & Authors"),
            "abstract": _fallback("Abstract"),
            "problem_statement": _fallback("Problem Statement"),
            "methodology": _fallback("Methodology"),
            "key_results": _fallback("Key Results"),
            "conclusion": _fallback("Conclusion"),
        }

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end < len(text):
            # Try to break at sentence boundary
            sentence_end = text.rfind('. ', start, end)
            if sentence_end > start:
                end = sentence_end + 1
            else:
                # Break at word boundary
                word_end = text.rfind(' ', start, end)
                if word_end > start:
                    end = word_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

@router.post("/upload")
@router.post("/upload_pdf")  # Backwards compatibility
async def upload_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    category: Optional[str] = None,
    source: Optional[str] = None,
):
    """Upload a PDF, chunk + embed it, and return a structured summary."""

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        pdf_content = await file.read()
        full_text = extract_text_from_pdf(pdf_content)

        if not full_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        base_id = str(uuid.uuid4())
        uploaded_at = datetime.utcnow().isoformat()

        base_metadata = {
            "filename": file.filename,
            "file_type": "pdf",
            "upload_date": uploaded_at,
            "title": title or file.filename,
            "category": category or "general",
            "source": source or "upload",
            "total_length": len(full_text),
            "embedding_model": "sentence-transformers/all-mpnet-base-v2",
            "document_base_id": base_id,
        }

        text_chunks = chunk_text(full_text)

        documents = []
        embeddings = []
        ids = []
        metadatas = []

        for i, chunk in enumerate(text_chunks):
            embedding = get_free_embedding(chunk)
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_id": i,
                "chunk_size": len(chunk),
                "total_chunks": len(text_chunks),
            })

            documents.append(chunk)
            embeddings.append(embedding)
            ids.append(f"{base_id}_chunk_{i}")
            metadatas.append(chunk_metadata)

        if not documents:
            raise HTTPException(status_code=500, detail="Failed to process any chunks from the PDF")

        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )

        summary = generate_structured_summary(full_text)

        return {
            "id": base_id,
            "document_id": base_id,
            "filename": file.filename,
            "upload_date": uploaded_at,
            "file_size": len(pdf_content),
            "chunks_processed": len(documents),
            "summary": summary,
            "chroma_collection": config.CHROMA_COLLECTION,
            "embedding_model": "sentence-transformers/all-mpnet-base-v2",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to Chroma Cloud: {str(e)}")