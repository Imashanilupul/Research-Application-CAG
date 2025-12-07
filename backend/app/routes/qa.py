"""
Question answering routes with RAG/CAG
"""
from fastapi import APIRouter, HTTPException
import logging

from app.models import QuestionRequest, AnswerResponse
from app.services import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/qa", tags=["Question Answering"])

# Use same RAG service instance
from app.routes.documents import rag_service


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a research paper
    
    Args:
        request: QuestionRequest with document_id and question
        
    Returns:
        AnswerResponse with generated answer and sources
    """
    try:
        # Validate document exists
        metadata = rag_service.get_document_metadata(request.document_id)
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Document {request.document_id} not found"
            )
        
        # Generate answer using RAG with CAG cache
        answer = rag_service.answer_question(
            document_id=request.document_id,
            question=request.question,
            top_k=request.top_k
        )
        
        return answer
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/batch")
async def ask_multiple_questions(requests: list[QuestionRequest]):
    """
    Ask multiple questions at once
    
    Args:
        requests: List of QuestionRequest objects
        
    Returns:
        List of AnswerResponse objects
    """
    try:
        answers = []
        
        for request in requests:
            # Validate document exists
            metadata = rag_service.get_document_metadata(request.document_id)
            if not metadata:
                logger.warning(f"Document {request.document_id} not found, skipping")
                continue
            
            # Generate answer
            answer = rag_service.answer_question(
                document_id=request.document_id,
                question=request.question,
                top_k=request.top_k
            )
            answers.append(answer)
        
        return {
            "answers": answers,
            "total": len(answers)
        }
    
    except Exception as e:
        logger.error(f"Error processing batch questions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing questions: {str(e)}"
        )
