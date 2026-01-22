"""
Strict answer generation using retrieved context.

This module generates interview-grade answers that are fully grounded
in retrieved knowledge chunks, with no hallucination.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from litellm import completion

try:
    from .retriever import RetrievalResult, RetrievedChunk
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.retriever import RetrievalResult, RetrievedChunk

load_dotenv(override=True)

ANSWER_MODEL = "openai/gpt-4o-mini"
TEMPERATURE = 0  # Deterministic output


class ConfidenceLevel(str, Enum):
    """Confidence level for generated answers."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CitedChunk:
    """Reference to a chunk used in the answer."""
    chunk_id: str
    headline: str
    chunk_type: str
    source_url: str


@dataclass
class GeneratedAnswer:
    """Structured answer with citations and confidence."""
    answer_text: str
    cited_chunks: List[CitedChunk]
    confidence_level: ConfidenceLevel
    refusal_reason: Optional[str] = None


class AnswerGenerator:
    """Generate answers strictly from retrieved context."""
    
    def __init__(self, model: str = ANSWER_MODEL, temperature: float = TEMPERATURE):
        """
        Initialize answer generator.
        
        Args:
            model: LLM model to use for generation
            temperature: Temperature for generation (0 for deterministic)
        """
        self.model = model
        self.temperature = temperature
    
    def _format_context(self, chunks: List[RetrievedChunk]) -> str:
        """Format retrieved chunks as context for the prompt."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"""
--- Chunk {i} (ID: {chunk.chunk_id}) ---
Type: {chunk.chunk_type}
Headline: {chunk.headline}
Summary: {chunk.summary}
Original Text: {chunk.original_text}
Source: {chunk.inherited_metadata.get('source_url', 'N/A')}
""")
        
        return "\n".join(context_parts)
    
    def _create_answer_prompt(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        context_text: str
    ) -> str:
        """Create prompt for answer generation."""
        num_chunks = len(chunks)
        
        prompt = f"""You are an AI Interview Preparation Assistant helping a candidate prepare for technical interviews.

CONTEXT:
You have access to {num_chunks} retrieved knowledge chunks that are relevant to the user's question.
These chunks contain authoritative information from official documentation, engineering blogs, and technical resources.

USER QUESTION:
{query}

RETRIEVED CONTEXT:
{context_text}

CRITICAL RULES (NON-NEGOTIABLE):
1. Your answer MUST be constructed ENTIRELY from the retrieved context above.
2. Do NOT use any knowledge outside of the provided chunks - even if you know the answer from training data.
3. Do NOT make assumptions or inferences beyond what is explicitly stated in the chunks.
4. If the context is insufficient to answer the question, you MUST refuse to answer.
5. Every claim you make must be traceable to a specific chunk (cite with "Chunk 1", "Chunk 2", etc.).
6. If you cannot find the answer in the provided chunks, state "I cannot answer this question based on the available context."
7. Do NOT fill gaps with general knowledge or common sense.
8. Do NOT combine information from chunks in ways that create new facts not present in any single chunk.

INTERVIEW CALIBRATION:
- Assume the listener is a senior engineer or hiring manager
- Emphasize reasoning, tradeoffs, and decision criteria
- Avoid tutorial-style explanations unless the question explicitly requests them
- Prefer real-world framing over academic completeness
- Be concise but deep - quality over quantity

ANSWER REQUIREMENTS:
- Ground every statement in the retrieved chunks
- Cite specific chunks when making claims (use chunk IDs: Chunk 1, Chunk 2, etc.)
- If multiple perspectives exist in the context, acknowledge them
- If there are tradeoffs mentioned, explain them clearly
- If the context discusses failure modes or edge cases, include them

If the context is insufficient:
- State clearly that you cannot answer based on the available information
- Explain what specific information is missing
- Suggest what type of knowledge would be needed to answer the question

Generate your answer now. Be precise, grounded, and interview-ready."""

        return prompt
    
    def _extract_citations(self, answer_text: str, chunks: List[RetrievedChunk]) -> List[CitedChunk]:
        """
        Extract cited chunks from answer text.
        
        Looks for references like "Chunk 1", "Chunk 2", etc. in the answer.
        """
        cited_indices = set()
        
        # Look for chunk references in the answer
        for i, chunk in enumerate(chunks, 1):
            # Check for various citation patterns
            patterns = [
                f"Chunk {i}",
                f"chunk {i}",
                f"Chunk {i},",
                f"chunk {i},",
                f"(Chunk {i})",
                f"(chunk {i})",
            ]
            
            for pattern in patterns:
                if pattern in answer_text:
                    cited_indices.add(i - 1)  # Convert to 0-based index
                    break
        
        # If no explicit citations found, assume all chunks were used
        if not cited_indices and chunks:
            cited_indices = set(range(len(chunks)))
        
        # Build cited chunks list
        cited_chunks = []
        for idx in cited_indices:
            if idx < len(chunks):
                chunk = chunks[idx]
                cited_chunks.append(CitedChunk(
                    chunk_id=chunk.chunk_id,
                    headline=chunk.headline,
                    chunk_type=chunk.chunk_type,
                    source_url=chunk.inherited_metadata.get('source_url', '')
                ))
        
        return cited_chunks
    
    def _assess_confidence(
        self,
        answer_text: str,
        chunks: List[RetrievedChunk],
        cited_chunks: List[CitedChunk]
    ) -> ConfidenceLevel:
        """
        Assess confidence level based on answer quality and context coverage.
        
        High: Multiple relevant chunks, clear citations, comprehensive coverage
        Medium: Some relevant chunks, partial citations, adequate coverage
        Low: Few chunks, weak citations, limited coverage
        """
        if not chunks:
            return ConfidenceLevel.LOW
        
        # Check for refusal indicators
        refusal_phrases = [
            "cannot answer",
            "insufficient information",
            "not enough context",
            "unable to answer",
            "missing information"
        ]
        
        answer_lower = answer_text.lower()
        if any(phrase in answer_lower for phrase in refusal_phrases):
            return ConfidenceLevel.LOW
        
        # Assess based on chunk count and citation coverage
        num_chunks = len(chunks)
        num_cited = len(cited_chunks)
        citation_ratio = num_cited / num_chunks if num_chunks > 0 else 0
        
        # Check answer length (very short might indicate low confidence)
        answer_length = len(answer_text.split())
        
        if num_chunks >= 3 and citation_ratio >= 0.6 and answer_length >= 100:
            return ConfidenceLevel.HIGH
        elif num_chunks >= 2 and citation_ratio >= 0.4 and answer_length >= 50:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _check_sufficiency(self, chunks: List[RetrievedChunk], query: str) -> Optional[str]:
        """
        Check if retrieved context is sufficient to answer the query.
        
        Returns:
            None if sufficient, refusal reason string if insufficient
        """
        if not chunks:
            return "No relevant knowledge chunks were retrieved for this query."
        
        # Check if we have very few chunks with low similarity
        if len(chunks) == 1 and chunks[0].similarity_score < 0.3:
            return (
                f"Only one weakly relevant chunk was found (similarity: {chunks[0].similarity_score:.2f}). "
                "This is insufficient to provide a reliable answer."
            )
        
        # Check if all chunks have very low similarity
        if all(chunk.similarity_score < 0.25 for chunk in chunks):
            return (
                f"All retrieved chunks have low similarity scores (max: {max(c.similarity_score for c in chunks):.2f}). "
                "The retrieved context may not be relevant enough to answer the question accurately."
            )
        
        return None  # Context appears sufficient
    
    def generate(
        self,
        retrieval_result: RetrievalResult,
        min_chunks: int = 1,
        min_similarity: float = 0.2
    ) -> GeneratedAnswer:
        """
        Generate an answer from retrieved context.
        
        Args:
            retrieval_result: Result from retrieval pipeline
            min_chunks: Minimum number of chunks required
            min_similarity: Minimum similarity score threshold
        
        Returns:
            GeneratedAnswer with citations and confidence
        """
        chunks = retrieval_result.retrieved_chunks
        
        # Filter chunks by minimum similarity
        filtered_chunks = [c for c in chunks if c.similarity_score >= min_similarity]
        
        # Check sufficiency
        refusal_reason = self._check_sufficiency(filtered_chunks, retrieval_result.original_query)
        
        if refusal_reason:
            return GeneratedAnswer(
                answer_text="",
                cited_chunks=[],
                confidence_level=ConfidenceLevel.LOW,
                refusal_reason=refusal_reason
            )
        
        if len(filtered_chunks) < min_chunks:
            return GeneratedAnswer(
                answer_text="",
                cited_chunks=[],
                confidence_level=ConfidenceLevel.LOW,
                refusal_reason=(
                    f"Only {len(filtered_chunks)} relevant chunk(s) found, "
                    f"but at least {min_chunks} are required for a reliable answer."
                )
            )
        
        # Format context
        context_text = self._format_context(filtered_chunks)
        
        # Create prompt
        prompt = self._create_answer_prompt(
            retrieval_result.original_query,
            filtered_chunks,
            context_text
        )
        
        # Generate answer
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1500
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Extract citations
            cited_chunks = self._extract_citations(answer_text, filtered_chunks)
            
            # Assess confidence
            confidence = self._assess_confidence(answer_text, filtered_chunks, cited_chunks)
            
            return GeneratedAnswer(
                answer_text=answer_text,
                cited_chunks=cited_chunks,
                confidence_level=confidence,
                refusal_reason=None
            )
            
        except Exception as e:
            return GeneratedAnswer(
                answer_text="",
                cited_chunks=[],
                confidence_level=ConfidenceLevel.LOW,
                refusal_reason=f"Error generating answer: {e}"
            )


def main():
    """Test the answer generator."""
    from core.retriever import KnowledgeRetriever
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    vector_db_dir = project_root / "data" / "vector_db"
    
    # Retrieve context
    retriever = KnowledgeRetriever(vector_db_dir=vector_db_dir, backend="local")
    retrieval_result = retriever.retrieve(
        "How does TypeScript help with large-scale JavaScript development?",
        debug=False
    )
    
    # Generate answer
    generator = AnswerGenerator()
    answer = generator.generate(retrieval_result)
    
    print("=" * 80)
    print("QUESTION:")
    print(retrieval_result.original_query)
    print("\n" + "=" * 80)
    
    if answer.refusal_reason:
        print("REFUSAL:")
        print(answer.refusal_reason)
    else:
        print("ANSWER:")
        print(answer.answer_text)
        print("\n" + "=" * 80)
        print(f"CONFIDENCE: {answer.confidence_level.value}")
        print(f"CITATIONS: {len(answer.cited_chunks)} chunks")
        for cited in answer.cited_chunks:
            print(f"  - {cited.headline} ({cited.chunk_type})")
            print(f"    Source: {cited.source_url}")


if __name__ == "__main__":
    main()
