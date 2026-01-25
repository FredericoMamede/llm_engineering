"""
Data ingestion pipeline components for AI Interview Preparation Assistant.
"""

# Import only classes that actually exist
from .chunker import SemanticChunker
from .embedder import ChunkEmbedder

# Optional imports - only if modules exist
try:
    from .discoverer import DocumentFetcher, SourcePlanParser, SourceMetadata
except ImportError:
    pass

__all__ = [
    "SemanticChunker",
    "ChunkEmbedder",
]
