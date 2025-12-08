import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_TENENT = os.getenv("CHROMA_TENENT")
CHROMA_DATABSE = os.getenv("CHROMA_DATABSE")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "documents_collection")

# Caching and memory configuration
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))
MEMORY_TTL_SECONDS = int(os.getenv("MEMORY_TTL_SECONDS", "86400"))
MEMORY_MAX_MESSAGES = int(os.getenv("MEMORY_MAX_MESSAGES", "10"))

# Optional external cache (Redis) support
REDIS_URL = os.getenv("REDIS_URL")