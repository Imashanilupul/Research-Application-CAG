from threading import Lock
from typing import Any, Dict, List, Tuple

from cachetools import TTLCache


class SimpleTTLCache:
    """Thread-safe TTL cache used for responses and summaries."""

    def __init__(self, max_size: int = 256, ttl_seconds: int = 600):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self.lock = Lock()

    def get(self, key: str) -> Any:
        with self.lock:
            return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        with self.lock:
            self.cache[key] = value


class MemoryStore:
    """Conversation memory with TTL and message cap per conversation."""

    def __init__(self, max_conversations: int = 256, ttl_seconds: int = 86_400, max_messages: int = 10):
        self.cache = TTLCache(maxsize=max_conversations, ttl=ttl_seconds)
        self.lock = Lock()
        self.max_messages = max_messages

    def get_history(self, conversation_id: str) -> List[Tuple[str, str]]:
        with self.lock:
            return list(self.cache.get(conversation_id, []))

    def append(self, conversation_id: str, role: str, content: str) -> List[Tuple[str, str]]:
        with self.lock:
            history = list(self.cache.get(conversation_id, []))
            history.append((role, content))
            if len(history) > self.max_messages:
                history = history[-self.max_messages :]
            self.cache[conversation_id] = history
            return history


def make_cache_key(*parts: str) -> str:
    """Build a stable cache key from string fragments."""
    normalized = [part.strip().lower() for part in parts if part]
    return "::".join(normalized)
