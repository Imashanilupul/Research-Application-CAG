"""
PDF processing utilities
"""
import PyPDF2
import pdfplumber
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Utility class for PDF processing"""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    @staticmethod
    def extract_text_with_pdfplumber(file_path: str) -> Tuple[str, int]:
        """
        Extract text using pdfplumber with page count
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (extracted text, page count)
        """
        try:
            text = ""
            page_count = 0
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page.page_number} ---\n"
                        text += page_text
            return text, page_count
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    @staticmethod
    def get_pdf_metadata(file_path: str) -> dict:
        """
        Extract metadata from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = pdf.metadata or {}
                return {
                    "title": metadata.get("Title", "Unknown"),
                    "author": metadata.get("Author", "Unknown"),
                    "pages": len(pdf.pages),
                    "subject": metadata.get("Subject", ""),
                    "producer": metadata.get("Producer", "")
                }
        except Exception as e:
            logger.error(f"Error extracting metadata from PDF: {e}")
            raise


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split text into chunks with overlap
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    
    return [c for c in chunks if c]  # Remove empty chunks
