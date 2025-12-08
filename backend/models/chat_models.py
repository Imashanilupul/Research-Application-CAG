from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    document_id: str
    question: str
    conversation_id: Optional[str] = None
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    confidence: Optional[float] = None