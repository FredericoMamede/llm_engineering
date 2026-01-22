"""
Embedding generation and vector database creation.

This module embeds semantic chunks into a persistent Chroma vector database
for retrieval-augmented generation.
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

load_dotenv(override=True)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_DB_FILE = "vector_db.pkl"
METADATA_FILE = "vector_db_metadata.json"


class ChunkEmbedder:
    """Embed semantic chunks into a vector database."""
    
    def __init__(self, chunks_dir: Path, vector_db_dir: Path):
        self.chunks_dir = chunks_dir
        self.vector_db_dir = vector_db_dir
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings model
        print(f"📥 Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Vector DB file paths
        self.vector_db_path = self.vector_db_dir / VECTOR_DB_FILE
        self.metadata_path = self.vector_db_dir / METADATA_FILE
        
        # Load existing data if available
        self.embeddings = []
        self.metadatas = []
        self.documents = []
        self._load_existing()
    
    def _load_chunk_file(self, chunk_file: Path) -> Dict[str, Any]:
        """Load and parse a chunk JSON file."""
        with open(chunk_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_existing(self):
        """Load existing vector database if it exists."""
        if self.vector_db_path.exists() and self.metadata_path.exists():
            try:
                with open(self.vector_db_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                    self.metadatas = metadata_data.get('metadatas', [])
                    self.documents = metadata_data.get('documents', [])
                print(f"   Loaded {len(self.embeddings)} existing embeddings")
            except Exception as e:
                print(f"   ⚠️  Error loading existing DB: {e}, starting fresh")
                self.embeddings = []
                self.metadatas = []
                self.documents = []
    
    def _save(self):
        """Save vector database to disk."""
        with open(self.vector_db_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadatas': self.metadatas,
                'documents': self.documents
            }, f, indent=2, ensure_ascii=False)
    
    def _get_existing_chunk_ids(self) -> set:
        """Get set of already embedded chunk IDs."""
        return {meta.get('chunk_id') for meta in self.metadatas if meta.get('chunk_id')}
    
    def _prepare_chunk_text(self, chunk: Dict[str, Any]) -> str:
        """Prepare text for embedding: concatenate headline + summary + original_text."""
        headline = chunk.get('headline', '')
        summary = chunk.get('summary', '')
        original_text = chunk.get('original_text', '')
        
        # Concatenate with clear separators
        text_parts = []
        if headline:
            text_parts.append(headline)
        if summary:
            text_parts.append(summary)
        if original_text:
            text_parts.append(original_text)
        
        return '\n\n'.join(text_parts)
    
    def _prepare_chunk_metadata(self, chunk: Dict[str, Any], source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for vector store."""
        inherited = chunk.get('inherited_metadata', {})
        
        metadata = {
            'chunk_id': chunk.get('chunk_id', ''),
            'chunk_type': chunk.get('chunk_type', ''),
            'source_url': inherited.get('source_url', ''),
            'source_type': inherited.get('source_type', ''),
            'freshness_year': inherited.get('freshness_year', '2024'),
            'source_file': source_metadata.get('source_file', ''),
        }
        
        # Add requirement_id or company_domain
        # Chroma metadata should have consistent keys, but we only set the one that exists
        requirement_id = inherited.get('requirement_id')
        company_domain = inherited.get('company_domain')
        
        if requirement_id:
            metadata['requirement_id'] = requirement_id
        if company_domain:
            metadata['company_domain'] = company_domain
        
        return metadata
    
    def _process_chunk_file(self, chunk_file: Path, existing_chunk_ids: set) -> tuple[int, int]:
        """Process a single chunk file and return (embedded_count, skipped_count)."""
        try:
            chunk_data = self._load_chunk_file(chunk_file)
            chunks = chunk_data.get('chunks', [])
            source_metadata = chunk_data.get('source_metadata', {})
            
            if not chunks:
                return 0, 0
            
            # Prepare documents, metadatas, and ids
            documents = []
            metadatas = []
            ids = []
            
            embedded_count = 0
            skipped_count = 0
            
            for chunk in chunks:
                chunk_id = chunk.get('chunk_id', '')
                
                # Skip if already embedded
                if chunk_id in existing_chunk_ids:
                    skipped_count += 1
                    continue
                
                # Prepare text for embedding
                text = self._prepare_chunk_text(chunk)
                if not text.strip():
                    continue
                
                # Prepare metadata
                metadata = self._prepare_chunk_metadata(chunk, source_metadata)
                
                documents.append(text)
                metadatas.append(metadata)
                ids.append(chunk_id)
                embedded_count += 1
            
            # Generate embeddings and add to vector store in batch
            if documents:
                # Generate embeddings
                new_embeddings = self.embedding_model.encode(documents, show_progress_bar=False)
                
                # Add to in-memory storage
                self.embeddings.extend(new_embeddings.tolist())
                self.documents.extend(documents)
                self.metadatas.extend(metadatas)
                
                # Save after each batch
                self._save()
            
            return embedded_count, skipped_count
            
        except Exception as e:
            print(f"   ❌ Error processing {chunk_file.name}: {e}")
            return 0, 0
    
    def embed_all(self):
        """Embed all chunks from chunk files."""
        chunk_files = list(self.chunks_dir.glob("*_chunks.json"))
        
        if not chunk_files:
            print("⚠️  No chunk files found!")
            return
        
        print(f"🔍 Found {len(chunk_files)} chunk files")
        
        # Get existing chunk IDs
        print("📊 Checking existing embeddings...")
        existing_chunk_ids = self._get_existing_chunk_ids()
        print(f"   Found {len(existing_chunk_ids)} already embedded chunks")
        
        # Process all chunk files
        total_embedded = 0
        total_skipped = 0
        requirement_counts = defaultdict(int)
        domain_counts = defaultdict(int)
        
        for chunk_file in tqdm(chunk_files, desc="Embedding chunks"):
            embedded, skipped = self._process_chunk_file(chunk_file, existing_chunk_ids)
            total_embedded += embedded
            total_skipped += skipped
            
            # Track counts by requirement/domain
            try:
                chunk_data = self._load_chunk_file(chunk_file)
                source_metadata = chunk_data.get('source_metadata', {})
                if source_metadata.get('requirement_id'):
                    requirement_counts[source_metadata['requirement_id']] += embedded
                elif source_metadata.get('company_domain'):
                    domain_counts[source_metadata['company_domain']] += embedded
            except Exception:
                pass
        
        # Final statistics
        total_in_db = len(self.embeddings)
        
        print(f"\n✅ Embedding complete!")
        print(f"   Embedded in this run: {total_embedded}")
        print(f"   Skipped (already embedded): {total_skipped}")
        print(f"   Total chunks in vector DB: {total_in_db}")
        
        # Per-requirement counts
        if requirement_counts:
            print(f"\n📊 Chunks by requirement:")
            for req_id in sorted(requirement_counts.keys()):
                print(f"   {req_id}: {requirement_counts[req_id]} chunks")
        
        # Per-domain counts
        if domain_counts:
            print(f"\n📊 Chunks by company domain:")
            for domain in sorted(domain_counts.keys()):
                print(f"   {domain}: {domain_counts[domain]} chunks")
        
        # Verify metadata filtering works
        print(f"\n🔍 Testing metadata filtering...")
        try:
            # Test requirement_id filter
            if requirement_counts:
                test_req = list(requirement_counts.keys())[0]
                filtered = [m for m in self.metadatas if m.get('requirement_id') == test_req]
                if filtered:
                    print(f"   ✅ Filter by requirement_id works ({len(filtered)} chunks found)")
            
            # Test chunk_type filter
            filtered = [m for m in self.metadatas if m.get('chunk_type') == 'primary']
            if filtered:
                print(f"   ✅ Filter by chunk_type works ({len(filtered)} chunks found)")
        except Exception as e:
            print(f"   ⚠️  Metadata filtering test failed: {e}")


def main():
    """Main entry point for embedding generation."""
    project_root = Path(__file__).parent.parent
    chunks_dir = project_root / "data" / "chunks"
    vector_db_dir = project_root / "data" / "vector_db"
    
    embedder = ChunkEmbedder(chunks_dir, vector_db_dir)
    embedder.embed_all()
    
    print("\n✅ Vector database ready for retrieval!")


if __name__ == "__main__":
    main()
