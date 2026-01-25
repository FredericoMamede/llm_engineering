"""
Retrieval pipeline for interview preparation knowledge.

This module implements query normalization, dual retrieval, filtering,
and ranking without generating answers.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from .vector_store import get_vector_store, VectorStore
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.vector_store import get_vector_store, VectorStore

load_dotenv(override=True)

QUERY_REWRITE_MODEL = "openai/gpt-4o-mini"
wait = wait_exponential(multiplier=1, min=2, max=10)

# ============================================================================
# Phase 5: Retrieval Intelligence Constants (Final Tuned)
# ============================================================================
# These constants control deterministic, explainable retrieval adaptations.
# All values are explicitly defined and can be adjusted for experimentation.
# Changes are logged and reversible.
#
# Final tuning (Phase 5 freeze):
# - Softer requirement boost reduces ranking distortion
# - Failure-mode boost disabled to stabilize answer confidence
# - Lower confidence threshold reduces unnecessary depth expansion
# - All intelligence remains deterministic and explainable

# Layer 1: Requirement-aware score boosting
REQUIREMENT_MATCH_BOOST = 1.05  # Multiplicative boost for chunks matching question's requirement_id
# Constraint: Must be ≤ 1.15
# Final tuning: Reduced from 1.10 to 1.05 for stability

# Layer 2: Failure-mode sensitivity
FAILURE_MODE_BOOST = 1.00  # Multiplicative boost for failure_mode chunks when question is tagged
# Constraint: Must be ≤ 1.10
# Final tuning: Disabled (set to 1.00) to stabilize answer confidence

# Layer 3: Weakness-aware retrieval depth
CONFIDENCE_THRESHOLD = 0.60  # Average top-3 similarity threshold for low confidence
DEPTH_INCREASE = 5  # Additional chunks to retrieve when confidence is low
# Constraint: Must not regress recall or precision globally
# Final tuning: Reduced from 0.65 to 0.60 to reduce unnecessary depth expansion


@dataclass
class RetrievedChunk:
    """A retrieved knowledge chunk with full metadata."""
    chunk_id: str
    chunk_type: str
    headline: str
    summary: str
    original_text: str
    inherited_metadata: Dict[str, Any]
    similarity_score: float
    retrieval_path: str  # "original" or "rewritten"


@dataclass
class RetrievalResult:
    """Complete retrieval result with metadata."""
    original_query: str
    rewritten_query: Optional[str]
    retrieved_chunks: List[RetrievedChunk]
    retrieval_metadata: Dict[str, Any] = field(default_factory=dict)


class QueryRewriter:
    """Rewrite queries for better retrieval."""
    
    def __init__(self, model: str = QUERY_REWRITE_MODEL):
        self.model = model
        self.enabled = True
    
    @retry(stop=stop_after_attempt(2), wait=wait)
    def rewrite(self, query: str) -> Optional[str]:
        """
        Rewrite query for better semantic retrieval.
        
        Args:
            query: Original user query
        
        Returns:
            Rewritten query or None if rewriting fails
        """
        if not self.enabled:
            return None
        
        prompt = f"""Rewrite the following query to improve semantic search retrieval for technical interview preparation.

The query will be used to find relevant knowledge chunks about:
- Software engineering concepts
- Technical interview topics
- System design principles
- Framework and tool usage
- Best practices and tradeoffs

Original query: {query}

Rewrite the query to:
1. Preserve the core intent
2. Include relevant technical terms
3. Make it more specific if too vague
4. Keep it concise (1-2 sentences max)

Rewritten query:"""

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            rewritten = response.choices[0].message.content.strip()
            # Remove quotes if present
            rewritten = rewritten.strip('"\'')
            return rewritten if rewritten and rewritten != query else None
        except Exception as e:
            print(f"   ⚠️  Query rewriting failed: {e}")
            return None


class KnowledgeRetriever:
    """Retrieve relevant knowledge chunks for interview preparation."""
    
    def __init__(
        self,
        vector_db_dir: Path,
        backend: str = "local",
        enable_query_rewrite: bool = True,
        top_k_original: int = 10,
        top_k_rewritten: int = 10,
        final_k: int = 10
    ):
        """
        Initialize knowledge retriever.
        
        Args:
            vector_db_dir: Directory containing vector database
            backend: Vector store backend ("local" or "chroma")
            enable_query_rewrite: Whether to rewrite queries
            top_k_original: Top-K results from original query
            top_k_rewritten: Top-K results from rewritten query
            final_k: Final number of results after merging
        """
        self.vector_store = get_vector_store(vector_db_dir, backend)
        self.query_rewriter = QueryRewriter() if enable_query_rewrite else None
        self.top_k_original = top_k_original
        self.top_k_rewritten = top_k_rewritten
        self.final_k = final_k
        self.backend = backend
    
    def _chunk_to_retrieved(self, result: Dict[str, Any], retrieval_path: str) -> RetrievedChunk:
        """Convert vector store result to RetrievedChunk."""
        metadata = result['metadata']
        
        # Extract inherited metadata
        inherited = {
            'requirement_id': metadata.get('requirement_id'),
            'company_domain': metadata.get('company_domain'),
            'source_url': metadata.get('source_url', ''),
            'source_type': metadata.get('source_type', ''),
            'freshness_year': metadata.get('freshness_year', '2024'),
            'source_file': metadata.get('source_file', '')
        }
        
        # Parse text to extract headline, summary, original_text
        # The text is stored as: headline\n\nsummary\n\noriginal_text
        # But we need to get the actual values from the chunk file if possible
        # For now, parse from the stored text
        text = result['text']
        text_parts = text.split('\n\n', 2)
        
        if len(text_parts) >= 3:
            headline = text_parts[0]
            summary = text_parts[1]
            original_text = text_parts[2]
        elif len(text_parts) == 2:
            headline = text_parts[0]
            summary = text_parts[1]
            original_text = text_parts[1]  # Fallback to summary if original_text missing
        else:
            headline = text_parts[0] if text_parts else ""
            summary = ""
            original_text = text
        
        return RetrievedChunk(
            chunk_id=result['chunk_id'],
            chunk_type=result['chunk_type'],
            headline=headline,
            summary=summary,
            original_text=original_text,
            inherited_metadata=inherited,
            similarity_score=result['score'],
            retrieval_path=retrieval_path
        )
    
    def _merge_and_deduplicate(
        self,
        original_results: List[Dict[str, Any]],
        rewritten_results: List[Dict[str, Any]],
        requirement_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        adaptive_log: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Merge results from both queries and deduplicate by chunk_id.
        
        Phase 5: Applies deterministic retrieval intelligence layers:
        - Layer 1: Requirement-aware score boosting
        - Layer 2: Failure-mode sensitivity
        
        Args:
            original_results: Results from original query
            rewritten_results: Results from rewritten query
            requirement_ids: Optional list of requirement IDs from test case
            tags: Optional list of tags from test case (e.g., ["failure_mode"])
            adaptive_log: Optional dict to log adaptive behavior
            
        Returns:
            List of RetrievedChunk, sorted by adjusted similarity score
        """
        seen_chunk_ids = set()
        merged = []
        
        # Add original query results first (they get priority)
        for result in original_results:
            chunk_id = result['chunk_id']
            if chunk_id not in seen_chunk_ids:
                merged.append(self._chunk_to_retrieved(result, "original"))
                seen_chunk_ids.add(chunk_id)
        
        # Add rewritten query results (if not already seen)
        for result in rewritten_results:
            chunk_id = result['chunk_id']
            if chunk_id not in seen_chunk_ids:
                merged.append(self._chunk_to_retrieved(result, "rewritten"))
                seen_chunk_ids.add(chunk_id)
        
        # Phase 5: Apply retrieval intelligence layers
        boosted_chunks = []
        
        # Layer 1: Requirement-aware score boosting
        if requirement_ids:
            for chunk in merged:
                chunk_req_id = chunk.inherited_metadata.get('requirement_id')
                if chunk_req_id and chunk_req_id in requirement_ids:
                    original_score = chunk.similarity_score
                    chunk.similarity_score *= REQUIREMENT_MATCH_BOOST
                    boosted_chunks.append({
                        'chunk_id': chunk.chunk_id,
                        'boost_type': 'requirement_match',
                        'requirement_id': chunk_req_id,
                        'original_score': original_score,
                        'adjusted_score': chunk.similarity_score,
                        'boost_factor': REQUIREMENT_MATCH_BOOST
                    })
        
        # Layer 2: Failure-mode sensitivity
        if tags and 'failure_mode' in tags:
            for chunk in merged:
                if chunk.chunk_type == 'failure_mode':
                    # Only boost if not already boosted by Layer 1
                    if not any(b['chunk_id'] == chunk.chunk_id and b['boost_type'] == 'requirement_match' 
                              for b in boosted_chunks):
                        original_score = chunk.similarity_score
                        chunk.similarity_score *= FAILURE_MODE_BOOST
                        boosted_chunks.append({
                            'chunk_id': chunk.chunk_id,
                            'boost_type': 'failure_mode',
                            'original_score': original_score,
                            'adjusted_score': chunk.similarity_score,
                            'boost_factor': FAILURE_MODE_BOOST
                        })
        
        # Log adaptive behavior if log dict provided
        if adaptive_log is not None:
            adaptive_log['boosts_applied'] = boosted_chunks
            adaptive_log['requirement_ids_provided'] = requirement_ids
            adaptive_log['tags_provided'] = tags
        
        # Sort by adjusted similarity score (descending)
        merged.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Return all merged chunks (final_k applied in retrieve method)
        return merged
    
    def retrieve(
        self,
        query: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        requirement_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> RetrievalResult:
        """
        Retrieve relevant knowledge chunks for a query.
        
        Phase 5: Supports retrieval intelligence through requirement_ids and tags.
        These enable deterministic, explainable adaptations without LLM decision-making.
        
        Args:
            query: User query
            filter_dict: Optional metadata filters
            debug: Enable debug output
            requirement_ids: Optional list of requirement IDs (for Layer 1 boosting)
            tags: Optional list of tags (e.g., ["failure_mode"] for Layer 2 boosting)
        
        Returns:
            RetrievalResult with retrieved chunks and metadata
        """
        original_query = query
        rewritten_query = None
        
        # Step 1: Query normalization/rewriting
        if self.query_rewriter:
            if debug:
                print(f"🔄 Rewriting query...")
            rewritten_query = self.query_rewriter.rewrite(query)
            if debug and rewritten_query:
                print(f"   Original: {original_query}")
                print(f"   Rewritten: {rewritten_query}")
        
        # Step 2: Dual retrieval
        if debug:
            print(f"🔍 Retrieving from original query (top_k={self.top_k_original})...")
        
        original_results = self.vector_store.search(
            query=original_query,
            top_k=self.top_k_original,
            filter_dict=filter_dict
        )
        
        rewritten_results = []
        if rewritten_query:
            if debug:
                print(f"🔍 Retrieving from rewritten query (top_k={self.top_k_rewritten})...")
            rewritten_results = self.vector_store.search(
                query=rewritten_query,
                top_k=self.top_k_rewritten,
                filter_dict=filter_dict
            )
        
        # Step 3: Merge and deduplicate
        if debug:
            print(f"🔗 Merging results...")
            print(f"   Original query: {len(original_results)} results")
            print(f"   Rewritten query: {len(rewritten_results)} results")
        
        # Phase 5: Layer 3 - Weakness-aware retrieval depth
        # Compute retrieval confidence proxy (average top-3 similarity)
        all_candidates = original_results + rewritten_results
        if all_candidates:
            top_scores = sorted([r.get('score', 0.0) for r in all_candidates], reverse=True)[:3]
            avg_top3_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        else:
            avg_top3_score = 0.0
        
        # Adjust final_k if confidence is low
        effective_final_k = self.final_k
        if avg_top3_score < CONFIDENCE_THRESHOLD:
            effective_final_k = self.final_k + DEPTH_INCREASE
            if debug:
                print(f"   [Phase 5 Layer 3] Low confidence ({avg_top3_score:.3f} < {CONFIDENCE_THRESHOLD}), increasing depth: {self.final_k} → {effective_final_k}")
        
        # Phase 5: Adaptive log for tracking
        adaptive_log = {}
        
        # Merge with retrieval intelligence
        merged_chunks = self._merge_and_deduplicate(
            original_results, 
            rewritten_results,
            requirement_ids=requirement_ids,
            tags=tags,
            adaptive_log=adaptive_log
        )
        
        # Apply effective_final_k (Layer 3)
        merged_chunks = merged_chunks[:effective_final_k]
        
        # Log Layer 3 behavior
        if avg_top3_score < CONFIDENCE_THRESHOLD:
            adaptive_log['layer3_applied'] = True
            adaptive_log['confidence_score'] = avg_top3_score
            adaptive_log['original_final_k'] = self.final_k
            adaptive_log['effective_final_k'] = effective_final_k
        else:
            adaptive_log['layer3_applied'] = False
            adaptive_log['confidence_score'] = avg_top3_score
        
        # Step 4: Build result
        retrieval_metadata = {
            'total_candidates': len(original_results) + len(rewritten_results),
            'total_returned': len(merged_chunks),
            'filters_applied': filter_dict or {},
            'backend_used': self.backend,
            'top_k_original': self.top_k_original,
            'top_k_rewritten': self.top_k_rewritten,
            'final_k': self.final_k,
            'effective_final_k': effective_final_k,  # Phase 5: Layer 3
            'phase5_adaptive': adaptive_log  # Phase 5: All adaptive behavior
        }
        
        if debug:
            print(f"✅ Retrieved {len(merged_chunks)} chunks")
            if merged_chunks:
                print(f"   Top score: {merged_chunks[0].similarity_score:.4f}")
                print(f"   Chunk types: {set(c.chunk_type for c in merged_chunks)}")
        
        return RetrievalResult(
            original_query=original_query,
            rewritten_query=rewritten_query,
            retrieved_chunks=merged_chunks,
            retrieval_metadata=retrieval_metadata
        )


def main():
    """Test the retriever."""
    project_root = Path(__file__).parent.parent
    vector_db_dir = project_root / "data" / "vector_db"
    
    retriever = KnowledgeRetriever(
        vector_db_dir=vector_db_dir,
        backend="local",
        enable_query_rewrite=True,
        top_k_original=10,
        top_k_rewritten=10,
        final_k=10
    )
    
    # Test query
    query = "How does TypeScript help with large-scale JavaScript development?"
    result = retriever.retrieve(query, debug=True)
    
    print(f"\n📊 Retrieval Results:")
    print(f"   Query: {result.original_query}")
    if result.rewritten_query:
        print(f"   Rewritten: {result.rewritten_query}")
    print(f"   Retrieved: {len(result.retrieved_chunks)} chunks")
    print(f"\n   Top 3 chunks:")
    for i, chunk in enumerate(result.retrieved_chunks[:3], 1):
        print(f"\n   {i}. {chunk.headline} (score: {chunk.similarity_score:.4f})")
        print(f"      Type: {chunk.chunk_type}")
        print(f"      Source: {chunk.inherited_metadata.get('source_url', 'N/A')}")


if __name__ == "__main__":
    main()
