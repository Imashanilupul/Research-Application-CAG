from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application configuration settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
        env_ignore_empty=True
    )
    
    # API Configuration
    api_host: str = os.getenv("API_HOST")
    api_port: int = int(os.getenv("API_PORT"))
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    log_level: str = os.getenv("LOG_LEVEL")
    
    # Gemini API
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    
    # ChromaDB Configuration
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH")
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME")
    
    
    # File Upload Configuration
    max_file_size_mb: int = os.getenv("MAX_FILE_SIZE_MB")
    upload_folder: str = os.getenv("UPLOAD_FOLDER")
    allowed_extensions: str = os.getenv("ALLOWED_EXTENSIONS")
    
    # LLM Configuration
    llm_model_name: str = os.getenv("LLM_MODEL_NAME")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME")
    max_tokens: int = int(os.getenv("MAX_TOKENS", 1000))
    temperature: float = float(os.getenv("TEMPERATURE", 0.7))
    
    # CORS Configuration
    cors_origins: str = os.getenv("CORS_ORIGINS")
    
    def get_allowed_extensions(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create settings instance
settings = Settings()
