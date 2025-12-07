from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "PDF Research Assistant API is running"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        return {
            "status": "ready",
            "message": "Service is ready to accept requests"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")
