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
from summary_extractor import generate_summary_from_first_page

router = APIRouter()
client = get_chroma_client()
collection = client.get_or_create_collection(config.CHROMA_COLLECTION)
summary_collection = client.get_or_create_collection(config.SUMMARIES_COLLECTION)

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
genai.configure(api_key=config.GEMINI_API_KEY)

SUMMARY_MODEL = "gemini-2.5-flash"
SUMMARY_MAX_CHARS = 8000  # Trim very large PDFs to keep prompt size reasonable

def get_free_embedding(text: str):
    """Generate embeddings using free SentenceTransformers"""
    return embedding_model.encode(text).tolist()


def generate_structured_summary(first_page_text: str) -> dict:
    """Generate a structured summary from the first page of the PDF"""
    return generate_summary_from_first_page(first_page_text)


def flatten_summary_for_embedding(summary: dict) -> List[tuple]:
    """Return list of (section_key, section_text) for embedding."""
    sections = []
    for key, value in summary.items():
        title = value.get("title", key)
        content = value.get("content", "")
        text = f"{title}: {content}"
        sections.append((key, text))
    return sections

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

def extract_first_page_from_pdf(pdf_file: bytes) -> str:
    """Extract text from only the first page of the PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        if len(pdf_reader.pages) == 0:
            raise HTTPException(status_code=400, detail="PDF has no pages")
        
        # Extract first page only
        first_page = pdf_reader.pages[0]
        first_page_text = first_page.extract_text()
        
        if not first_page_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from first page")
        
        return first_page_text
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract first page from PDF: {str(e)}")

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

        # Extract first page for summary generation
        first_page_text = extract_first_page_from_pdf(pdf_content)

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

        # Generate summary from first page only
        summary = generate_structured_summary(first_page_text)

        # Store summary embeddings in dedicated collection for faster familiarization
        summary_sections = flatten_summary_for_embedding(summary)
        summary_docs = []
        summary_embeddings = []
        summary_ids = []
        summary_metadatas = []

        for idx, (section_key, section_text) in enumerate(summary_sections):
            summary_docs.append(section_text)
            summary_embeddings.append(get_free_embedding(section_text))
            summary_ids.append(f"{base_id}_summary_{idx}")
            summary_metadatas.append({
                "document_base_id": base_id,
                "section_key": section_key,
                "filename": file.filename,
                "upload_date": uploaded_at,
            })

        if summary_docs:
            summary_collection.add(
                documents=summary_docs,
                embeddings=summary_embeddings,
                ids=summary_ids,
                metadatas=summary_metadatas,
            )

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