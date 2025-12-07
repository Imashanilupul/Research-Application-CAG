"""
Application settings and configuration management
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
        env_ignore_empty=True
    )
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    
    # Gemini API
    gemini_api_key: str = ""
    
    # ChromaDB Configuration
    chroma_db_path: str = "./data/chroma_db"
    chroma_collection_name: str = "research_papers"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    use_redis_cache: bool = False
    
    # File Upload Configuration
    max_file_size_mb: int = 50
    upload_folder: str = "./data/uploads"
    allowed_extensions: str = "pdf"  # Changed to string, will be split in code
    
    # LLM Configuration
    llm_model_name: str = "gemini-2.5-flash"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:5173"  # Changed to string
    
    def get_allowed_extensions(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create settings instance
settings = Settings()
