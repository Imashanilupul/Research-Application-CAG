"""
Caching utilities for CAG system
"""
import json
import hashlib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        """Initialize cache"""
        self._cache: Dict[str, Any] = {}
    
    @staticmethod
    def generate_key(document_id: str, query: str) -> str:
        """
        Generate cache key from document ID and query
        
        Args:
            document_id: Document ID
            query: Query string
            
        Returns:
            Hash-based cache key
        """
        combined = f"{document_id}:{query}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        logger.debug(f"Cached value for key: {key}")
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache
        
        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache for key: {key}")
    
    def delete_by_document(self, document_id: str) -> None:
        """
        Delete all cache entries for a document
        
        Args:
            document_id: Document ID
        """
        keys_to_delete = [
            k for k in self._cache.keys()
            if k.startswith(document_id)
        ]
        for key in keys_to_delete:
            del self._cache[key]
        logger.debug(f"Deleted {len(keys_to_delete)} cache entries for document: {document_id}")
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        return {
            "total_entries": len(self._cache),
            "size_bytes": sum(
                len(json.dumps(v).encode())
                for v in self._cache.values()
            )
        }


class CAGCache(Cache):
    """Cache specifically for Cache Augmented Generation system"""
    
    def store_qa_result(
        self,
        document_id: str,
        question: str,
        answer: str,
        sources: list
    ) -> str:
        """
        Store Q&A result in cache
        
        Args:
            document_id: Document ID
            question: Question asked
            answer: Generated answer
            sources: Source chunks used
            
        Returns:
            Cache key
        """
        key = self.generate_key(document_id, question)
        value = {
            "question": question,
            "answer": answer,
            "sources": sources
        }
        self.set(key, value)
        return key
    
    def get_qa_result(self, document_id: str, question: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached Q&A result
        
        Args:
            document_id: Document ID
            question: Question asked
            
        Returns:
            Cached Q&A result or None
        """
        key = self.generate_key(document_id, question)
        return self.get(key)


# Global cache instance
cache = Cache()
cag_cache = CAGCache()
