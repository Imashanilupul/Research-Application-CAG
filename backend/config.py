import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_TENENT = os.getenv("CHROMA_TENENT")
CHROMA_DATABSE = os.getenv("CHROMA_DATABSE")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "documents_collection")