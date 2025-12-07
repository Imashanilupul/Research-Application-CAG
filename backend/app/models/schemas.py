from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SummarySection(BaseModel):
    """Schema for a summary section"""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")


class PaperSummary(BaseModel):
    """Schema for complete paper summary"""
    title_and_authors: SummarySection
    abstract: SummarySection
    problem_statement: SummarySection
    methodology: SummarySection
    key_results: SummarySection
    conclusion: SummarySection
    
    class Config:
        json_schema_extra = {
            "example": {
                "title_and_authors": {
                    "title": "Title & Authors",
                    "content": "Sample title and authors"
                },
                "abstract": {
                    "title": "Abstract",
                    "content": "Sample abstract"
                },
                "problem_statement": {
                    "title": "Problem Statement",
                    "content": "Sample problem statement"
                },
                "methodology": {
                    "title": "Methodology",
                    "content": "Sample methodology"
                },
                "key_results": {
                    "title": "Key Results",
                    "content": "Sample key results"
                },
                "conclusion": {
                    "title": "Conclusion",
                    "content": "Sample conclusion"
                }
            }
        }


class PDFUploadResponse(BaseModel):
    """Response schema for PDF upload"""
    id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    upload_date: datetime = Field(..., description="Upload timestamp")
    file_size: int = Field(..., description="File size in bytes")
    summary: PaperSummary = Field(..., description="Generated summary")
    status: str = Field(default="success", description="Upload status")


class QuestionRequest(BaseModel):
    """Schema for question answering request"""
    document_id: str = Field(..., description="ID of the research paper")
    question: str = Field(..., description="User's question")
    top_k: int = Field(default=3, description="Number of similar chunks to retrieve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "question": "What are the main findings?",
                "top_k": 3
            }
        }


class AnswerResponse(BaseModel):
    """Schema for question answering response"""
    document_id: str = Field(..., description="ID of the research paper")
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer from LLM")
    sources: List[str] = Field(default=[], description="Source chunks used")
    confidence: float = Field(default=0.0, description="Confidence score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "question": "What are the main findings?",
                "answer": "The main findings include...",
                "sources": ["Chunk 1 content...", "Chunk 2 content..."],
                "confidence": 0.85
            }
        }


class DocumentMetadata(BaseModel):
    """Schema for document metadata"""
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    upload_date: datetime = Field(..., description="Upload timestamp")
    file_size: int = Field(..., description="File size in bytes")
    chunk_count: int = Field(..., description="Number of chunks in vector DB")
    status: str = Field(default="processed", description="Processing status")


class DocumentListResponse(BaseModel):
    """Schema for list of documents"""
    documents: List[DocumentMetadata] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
