"""
PDF upload and document management routes
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from typing import List
import os
import logging
from datetime import datetime

from app.services import RAGService
from app.models import PDFUploadResponse, DocumentMetadata, DocumentListResponse
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# Initialize RAG service (singleton pattern)
rag_service = RAGService()


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF document
    
    Args:
        file: PDF file to upload
        
    Returns:
        PDFUploadResponse with document ID and summary
    """
    try:
        # Validate file
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum of {settings.max_file_size_mb}MB"
            )
        
        # Create upload directory
        os.makedirs(settings.upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(settings.upload_folder, file.filename)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Uploaded file: {file.filename}")
        
        # Process PDF
        document_id, summary, metadata = rag_service.process_pdf(file_path, file.filename)
        
        return PDFUploadResponse(
            id=document_id,
            filename=file.filename,
            upload_date=metadata["upload_date"],
            file_size=metadata["file_size"],
            summary=summary,
            status="success"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents
    
    Returns:
        List of documents with metadata
    """
    try:
        documents = rag_service.get_all_documents()
        
        # Convert to DocumentMetadata format
        doc_list = [
            DocumentMetadata(
                id=doc["id"],
                filename=doc["filename"],
                upload_date=doc["upload_date"],
                file_size=doc["file_size"],
                chunk_count=doc["chunk_count"],
                status="processed"
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=doc_list,
            total=len(doc_list)
        )
    
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving documents"
        )


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str):
    """
    Get document metadata
    
    Args:
        document_id: ID of the document
        
    Returns:
        Document metadata
    """
    try:
        metadata = rag_service.get_document_metadata(document_id)
        
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        return DocumentMetadata(
            id=metadata["id"],
            filename=metadata["filename"],
            upload_date=metadata["upload_date"],
            file_size=metadata["file_size"],
            chunk_count=metadata["chunk_count"],
            status="processed"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document metadata: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving document"
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Success message
    """
    try:
        success = rag_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        return {
            "status": "success",
            "message": f"Document {document_id} deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting document"
        )
