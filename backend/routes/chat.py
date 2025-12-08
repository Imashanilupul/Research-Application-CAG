from typing import List, Optional

import google.generativeai as genai
from fastapi import APIRouter, Request
from sentence_transformers import SentenceTransformer

import config
from cache import MemoryStore, SimpleTTLCache, make_cache_key
from db import get_chroma_client
from models.chat_models import ChatRequest, ChatResponse

router = APIRouter(prefix="/qa", tags=["QA"])
client = get_chroma_client()
collection = client.get_or_create_collection(config.CHROMA_COLLECTION)

genai.configure(api_key=config.GEMINI_API_KEY)
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Cache layer
response_cache = SimpleTTLCache(max_size=256, ttl_seconds=config.CACHE_TTL_SECONDS)
memory_store = MemoryStore(
    max_conversations=256,
    ttl_seconds=config.MEMORY_TTL_SECONDS,
    max_messages=config.MEMORY_MAX_MESSAGES,
)


def get_free_embedding(text: str):
    """Generate embeddings using free SentenceTransformers."""
    return embedding_model.encode(text).tolist()


def format_memory(history: List[tuple]) -> str:
    if not history:
        return ""
    formatted = []
    for role, content in history:
        formatted.append(f"{role.capitalize()}: {content}")
    return "\n".join(formatted)


def build_prompt(context_chunks: List[str], history: List[tuple], question: str) -> str:
    context_text = "\n".join(context_chunks)
    memory_text = format_memory(history)
    system_prompt = (
        "You are a concise research assistant. Use provided context chunks to answer the question. "
        "If the answer is not in the context, say you are unsure."
    )

    return (
        f"{system_prompt}\n\n"
        f"Conversation Memory:\n{memory_text}\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )


@router.post("/ask", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, request: Request):
    conversation_id = req.conversation_id or make_cache_key(req.document_id, request.client.host)

    history = memory_store.get_history(conversation_id)
    memory_store.append(conversation_id, "user", req.question)

    cache_key = make_cache_key(req.document_id, req.question)
    cached: Optional[ChatResponse] = response_cache.get(cache_key)
    if cached:
        memory_store.append(conversation_id, "assistant", cached.answer)
        return cached

    query_embedding = get_free_embedding(req.question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=req.top_k,
        where={"document_base_id": req.document_id},
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])[0] if results.get("documents") else []
    distances = results.get("distances", [[]])[0] if results.get("distances") else []

    prompt = build_prompt(docs, history, req.question)

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=400,
            ),
        )

        answer_text = response.text
        # Approximate confidence: inverse of average distance (bounded 0..1)
        confidence = None
        if distances:
            avg_distance = sum(distances) / len(distances)
            confidence = max(0.0, min(1.0, 1 - avg_distance))

        chat_response = ChatResponse(
            answer=answer_text,
            sources=docs,
            confidence=confidence,
        )

        memory_store.append(conversation_id, "assistant", answer_text)
        response_cache.set(cache_key, chat_response)
        return chat_response
    except Exception as exc:  # keep the chat responsive on LLM errors
        fallback = ChatResponse(
            answer=f"Sorry, I hit an error while answering: {exc}",
            sources=docs,
            confidence=None,
        )
        memory_store.append(conversation_id, "assistant", fallback.answer)
        return fallback
