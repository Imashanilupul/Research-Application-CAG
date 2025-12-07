import chromadb
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manager for ChromaDB vector store operations"""
    
    def __init__(self, db_path: str, collection_name: str):
        """
        Initialize ChromaDB vector store
        
        Args:
            db_path: Path to ChromaDB directory
            collection_name: Name of the collection
        """
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        document_id: str,
        chunks: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> None:
        """
        Add document chunks to vector store
        
        Args:
            document_id: Unique document ID
            chunks: List of text chunks
            metadatas: List of metadata dicts for each chunk
        """
        try:
            if metadatas is None:
                metadatas = [{"doc_id": document_id, "chunk_index": i} 
                           for i in range(len(chunks))]
            
            # Generate unique IDs for chunks
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            
            self.collection.add(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        document_id: str = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents in vector store
        
        Args:
            query: Search query
            top_k: Number of top results to return
            document_id: Optional filter by document ID
            
        Returns:
            Dictionary with search results
        """
        try:
            where_filter = None
            if document_id:
                where_filter = {"doc_id": {"$eq": document_id}}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter
            )
            
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete all chunks of a document from vector store
        
        Args:
            document_id: ID of document to delete
        """
        try:
            self.collection.delete(
                where={"doc_id": {"$eq": document_id}}
            )
            logger.info(f"Deleted document {document_id} from vector store")
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        
        Returns:
            Dictionary with collection info
        """
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise
    
    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
