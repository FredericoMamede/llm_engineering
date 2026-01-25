"""
Vector store abstraction for retrieval.

This module provides a backend-agnostic interface for vector similarity search,
supporting both Chroma and local pickle-based storage.

Phase 4.1 Experiment: Using OpenAI embeddings (text-embedding-3-small)
for query encoding to match the embedding model used during ingestion.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import pickle
import os
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Phase 4.1: Match embedding model used in embedder.py
EMBEDDING_MODEL = "text-embedding-3-small"  # Changed from "all-MiniLM-L6-v2"
USE_OPENAI_EMBEDDINGS = True  # Flag to use OpenAI embeddings

# Use numpy for cosine similarity to avoid sklearn dependency
def cosine_similarity_numpy(query_vec, candidate_vecs):
    """Compute cosine similarity using numpy."""
    # Normalize vectors
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    candidate_norms = candidate_vecs / (np.linalg.norm(candidate_vecs, axis=1, keepdims=True) + 1e-8)
    # Compute dot product
    return np.dot(query_norm, candidate_norms.T).flatten()


class VectorStore(ABC):
    """Abstract interface for vector store operations."""
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query: Query text to search for
            top_k: Number of results to return
            filter_dict: Optional metadata filters (e.g., {"chunk_type": "primary"})
        
        Returns:
            List of dictionaries with keys: chunk_id, chunk_type, text, metadata, score
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Return total number of vectors in store."""
        pass


class LocalVectorStore(VectorStore):
    """Local pickle-based vector store implementation."""
    
    def __init__(self, vector_db_dir: Path, embedding_model_name: Optional[str] = None):
        """
        Initialize local vector store.
        
        Args:
            vector_db_dir: Directory containing vector_db.pkl and vector_db_metadata.json
            embedding_model_name: Name of the embedding model (defaults to EMBEDDING_MODEL constant)
        """
        self.vector_db_dir = vector_db_dir
        self.vector_db_path = vector_db_dir / "vector_db.pkl"
        self.metadata_path = vector_db_dir / "vector_db_metadata.json"
        
        # Use provided model name or default from constant
        self.embedding_model_name = embedding_model_name or EMBEDDING_MODEL
        
        # Load embeddings and metadata
        self.embeddings = []
        self.metadatas = []
        self.documents = []
        self._load()
        
        # Initialize embedding model for query encoding
        if USE_OPENAI_EMBEDDINGS:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
            self.openai_client = OpenAI(api_key=api_key)
            self.embedding_model = None  # Not used for OpenAI
        else:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.openai_client = None
    
    def _load(self):
        """Load embeddings and metadata from disk."""
        if not self.vector_db_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Vector database not found at {self.vector_db_dir}. "
                "Run ingest/embedder.py first."
            )
        
        with open(self.vector_db_path, 'rb') as f:
            self.embeddings = pickle.load(f)
        
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            metadata_data = json.load(f)
            self.metadatas = metadata_data.get('metadatas', [])
            self.documents = metadata_data.get('documents', [])
        
        # Convert to numpy array for efficient computation
        self.embeddings = np.array(self.embeddings)
        
        if len(self.embeddings) != len(self.metadatas) or len(self.embeddings) != len(self.documents):
            raise ValueError(
                f"Mismatch: {len(self.embeddings)} embeddings, "
                f"{len(self.metadatas)} metadatas, {len(self.documents)} documents"
            )
    
    def _apply_filters(self, filter_dict: Optional[Dict[str, Any]]) -> List[int]:
        """
        Apply metadata filters and return indices of matching items.
        
        Args:
            filter_dict: Dictionary of metadata filters
        
        Returns:
            List of indices that match the filters
        """
        if not filter_dict:
            return list(range(len(self.metadatas)))
        
        matching_indices = []
        for idx, metadata in enumerate(self.metadatas):
            match = True
            for key, value in filter_dict.items():
                if metadata.get(key) != value:
                    match = False
                    break
            if match:
                matching_indices.append(idx)
        
        return matching_indices
    
    def _encode_query(self, query: str) -> np.ndarray:
        """
        Encode query text to embedding vector.
        
        Args:
            query: Query text string
            
        Returns:
            Numpy array of shape (1, embedding_dim)
        """
        if USE_OPENAI_EMBEDDINGS:
            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model_name,
                    input=[query]
                )
                embedding = np.array(response.data[0].embedding)
                return embedding.reshape(1, -1)
            except Exception as e:
                raise ValueError(f"Error encoding query with OpenAI: {e}")
        else:
            query_embedding = self.embedding_model.encode([query], show_progress_bar=False)
            return query_embedding.reshape(1, -1)
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity."""
        # Encode query
        query_embedding = self._encode_query(query)
        
        # Apply filters to get candidate indices
        candidate_indices = self._apply_filters(filter_dict)
        
        if not candidate_indices:
            return []
        
        # Get embeddings for candidates
        candidate_embeddings = self.embeddings[candidate_indices]
        
        # Compute cosine similarity
        similarities = cosine_similarity_numpy(query_embedding[0], candidate_embeddings)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            original_idx = candidate_indices[idx]
            results.append({
                'chunk_id': self.metadatas[original_idx].get('chunk_id', ''),
                'chunk_type': self.metadatas[original_idx].get('chunk_type', ''),
                'text': self.documents[original_idx],
                'metadata': self.metadatas[original_idx],
                'score': float(similarities[idx])
            })
        
        return results
    
    def count(self) -> int:
        """Return total number of vectors."""
        return len(self.embeddings)


class ChromaVectorStore(VectorStore):
    """Chroma-based vector store implementation (for future use)."""
    
    def __init__(self, vector_db_dir: Path, collection_name: str = "interview_knowledge"):
        """
        Initialize Chroma vector store.
        
        Args:
            vector_db_dir: Directory for Chroma persistence
            collection_name: Name of the Chroma collection
        """
        # This would be implemented when Chroma is available
        raise NotImplementedError(
            "ChromaVectorStore not yet implemented. "
            "Use LocalVectorStore for now."
        )
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search using Chroma."""
        raise NotImplementedError()
    
    def count(self) -> int:
        """Return count from Chroma."""
        raise NotImplementedError()


def get_vector_store(vector_db_dir: Path, backend: str = "local") -> VectorStore:
    """
    Factory function to get appropriate vector store.
    
    Args:
        vector_db_dir: Directory containing vector database
        backend: "local" or "chroma"
    
    Returns:
        VectorStore instance
    """
    if backend == "local":
        return LocalVectorStore(vector_db_dir)
    elif backend == "chroma":
        return ChromaVectorStore(vector_db_dir)
    else:
        raise ValueError(f"Unknown backend: {backend}")
