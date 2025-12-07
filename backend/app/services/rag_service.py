import os
import uuid
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.utils import PDFProcessor, chunk_text, VectorStoreManager, cag_cache
from app.models import PaperSummary, AnswerResponse
from .gemini_service import GeminiService
from config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval Augmented Generation Service with Cache Augmented Generation"""
    
    def __init__(self):
        """Initialize RAG service with ChromaDB and Gemini"""
        self.vector_store = VectorStoreManager(
            settings.chroma_db_path,
            settings.chroma_collection_name
        )
        self.gemini_service = GeminiService(
            api_key=settings.gemini_api_key,
            model_name=settings.llm_model_name
        )
        self.pdf_processor = PDFProcessor()
        self.document_metadata = {}  # In-memory metadata storage
    
    def process_pdf(self, file_path: str, filename: str) -> tuple:
        """
        Process PDF file: extract text, generate summary, and store embeddings
        
        Args:
            file_path: Path to uploaded PDF
            filename: Original filename
            
        Returns:
            Tuple of (document_id, summary, metadata)
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Extract text and metadata
            logger.info(f"Extracting text from {filename}")
            text, page_count = self.pdf_processor.extract_text_with_pdfplumber(file_path)
            pdf_metadata = self.pdf_processor.get_pdf_metadata(file_path)
            
            # Generate summary using Gemini
            logger.info(f"Generating summary for {filename}")
            summary_data = self.gemini_service.generate_summary(text)
            
            # Create summary object
            summary = self._create_summary_object(summary_data)
            
            # Chunk text for vector storage
            logger.info(f"Chunking text for {filename}")
            chunks = chunk_text(text, chunk_size=500, overlap=100)
            
            # Add to vector store with metadata
            metadatas = [
                {
                    "doc_id": document_id,
                    "chunk_index": i,
                    "page_estimate": max(1, (i // 5) + 1),
                    "filename": filename
                }
                for i in range(len(chunks))
            ]
            
            self.vector_store.add_documents(document_id, chunks, metadatas)
            
            # Store metadata
            file_size = os.path.getsize(file_path)
            self.document_metadata[document_id] = {
                "id": document_id,
                "filename": filename,
                "upload_date": datetime.now(),
                "file_size": file_size,
                "chunk_count": len(chunks),
                "page_count": page_count,
                "pdf_metadata": pdf_metadata
            }
            
            logger.info(f"Successfully processed PDF: {document_id}")
            return document_id, summary, self.document_metadata[document_id]
        
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            raise
    
    def answer_question(
        self,
        document_id: str,
        question: str,
        top_k: int = 3
    ) -> AnswerResponse:
        """
        Answer question using RAG with CAG cache
        
        Args:
            document_id: ID of the research paper
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            AnswerResponse with answer and sources
        """
        try:
            # Check cache first (CAG - Cache Augmented Generation)
            cached_result = cag_cache.get_qa_result(document_id, question)
            if cached_result:
                logger.info(f"Cache hit for question in document {document_id}")
                return AnswerResponse(
                    document_id=document_id,
                    question=question,
                    answer=cached_result["answer"],
                    sources=cached_result["sources"],
                    confidence=0.95
                )
            
            # Retrieve relevant chunks from vector store
            logger.info(f"Retrieving chunks for question in document {document_id}")
            search_results = self.vector_store.search(
                query=question,
                top_k=top_k,
                document_id=document_id
            )
            
            # Extract relevant context
            chunks = search_results.get("documents", [[]])[0]
            metadatas = search_results.get("metadatas", [[]])[0]
            
            if not chunks:
                logger.warning(f"No relevant chunks found for document {document_id}")
                return AnswerResponse(
                    document_id=document_id,
                    question=question,
                    answer="No relevant information found in the document.",
                    sources=[],
                    confidence=0.0
                )
            
            # Combine context
            context = "\n\n".join([
                f"Chunk {i}: {chunk}"
                for i, chunk in enumerate(chunks, 1)
            ])
            
            # Generate answer using Gemini
            logger.info(f"Generating answer for question in document {document_id}")
            answer = self.gemini_service.answer_question(
                question=question,
                context=context,
                max_tokens=settings.max_tokens
            )
            
            # Create response
            response = AnswerResponse(
                document_id=document_id,
                question=question,
                answer=answer,
                sources=chunks,
                confidence=self._calculate_confidence(metadatas)
            )
            
            # Store in cache (CAG)
            cag_cache.store_qa_result(
                document_id=document_id,
                question=question,
                answer=answer,
                sources=chunks
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise
    
    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a document
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document metadata or None
        """
        return self.document_metadata.get(document_id)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all documents
        
        Returns:
            List of document metadata
        """
        return list(self.document_metadata.values())
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from vector store and metadata
        
        Args:
            document_id: ID of the document
            
        Returns:
            True if successful
        """
        try:
            self.vector_store.delete_document(document_id)
            if document_id in self.document_metadata:
                del self.document_metadata[document_id]
            cag_cache.delete_by_document(document_id)
            logger.info(f"Deleted document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    @staticmethod
    def _create_summary_object(summary_data: dict) -> PaperSummary:
        """
        Create PaperSummary object from summary data
        
        Args:
            summary_data: Dictionary with summary sections
            
        Returns:
            PaperSummary object
        """
        from app.models import SummarySection
        
        def get_section(data, key, default_title):
            if isinstance(data.get(key), dict):
                return SummarySection(
                    title=data[key].get("title", default_title),
                    content=data[key].get("content", "No content available")
                )
            return SummarySection(
                title=default_title,
                content=str(data.get(key, "No content available"))
            )
        
        return PaperSummary(
            title_and_authors=get_section(summary_data, "title_and_authors", "Title & Authors"),
            abstract=get_section(summary_data, "abstract", "Abstract"),
            problem_statement=get_section(summary_data, "problem_statement", "Problem Statement"),
            methodology=get_section(summary_data, "methodology", "Methodology"),
            key_results=get_section(summary_data, "key_results", "Key Results"),
            conclusion=get_section(summary_data, "conclusion", "Conclusion")
        )
    
    @staticmethod
    def _calculate_confidence(metadatas: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score based on metadata
        
        Args:
            metadatas: List of chunk metadatas
            
        Returns:
            Confidence score between 0 and 1
        """
        if not metadatas:
            return 0.0
        # Simple confidence calculation: more chunks = higher confidence
        return min(0.95, 0.5 + (len(metadatas) * 0.15))
