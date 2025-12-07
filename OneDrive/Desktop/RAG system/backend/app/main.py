"""
Main FastAPI application
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to allow absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import logging.config

from config.settings import settings
from app.routes import health, documents, qa

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF Research Assistant API",
    description="API for uploading research papers, generating summaries, and answering questions using RAG/CAG",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Include routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(qa.router)


@app.on_event("startup")
async def startup_event():
    """Handle startup events"""
    logger.info("Application started")
    # Create necessary directories
    os.makedirs(settings.upload_folder, exist_ok=True)
    os.makedirs(settings.chroma_db_path, exist_ok=True)
    os.makedirs("logs", exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown events"""
    logger.info("Application shutdown")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF Research Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
