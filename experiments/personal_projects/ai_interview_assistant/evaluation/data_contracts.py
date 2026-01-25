"""
Data contracts for RAG evaluation system.

This module defines all dataclasses used for evaluation.
All dataclasses are frozen (immutable) to ensure reproducibility.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set
import json


# ============================================================================
# Test Case Definition
# ============================================================================

@dataclass(frozen=True)
class TestCase:
    """
    A single test case for RAG evaluation.
    
    Represents a question with concept-based expectations (not ground truth answers).
    Frozen to ensure immutability.
    """
    
    # Identity
    test_id: str  # Unique identifier (e.g., "test_001", "typescript_large_scale_001")
    question: str  # The test question
    
    # Concept-based expectations (what concepts should be retrieved/covered)
    expected_concepts: List[str]  # List of concept names that should appear in retrieved chunks
    expected_requirement_ids: Optional[List[str]] = None  # If question targets specific requirements
    expected_company_domains: Optional[List[str]] = None  # If question targets specific company domains
    expected_chunk_types: Optional[List[str]] = None  # Expected chunk types (primary, tradeoff, etc.)
    
    # Metadata
    category: str  # e.g., "direct_fact", "system_design", "tradeoff_analysis"
    difficulty: str  # "easy", "medium", "hard"
    tags: List[str] = field(default_factory=list)  # Additional tags for filtering
    
    # Optional context
    notes: Optional[str] = None  # Human notes about what makes this a good test case
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# ============================================================================
# Answer Evaluation (Wraps AnswerJudge Output)
# ============================================================================

@dataclass(frozen=True)
class AnswerEvaluation:
    """
    Evaluation of a generated answer, wrapping AnswerJudge output.
    
    Reuses EvaluationFeedback from judge.py and adds metadata for tracking.
    Frozen to ensure immutability.
    """
    
    # Reused from EvaluationFeedback (from evaluation/judge.py)
    strengths: List[str]
    gaps: List[str]
    missed_concepts: List[str]
    followup_questions: List[str]
    overall_assessment: str
    confidence_score: int  # 1-5 scale
    
    # Additional metadata for evaluation
    test_id: str  # Which test case this evaluation belongs to
    question: str  # The original question
    generated_answer: str  # The answer that was evaluated
    num_retrieved_chunks: int  # How many chunks were used for answer generation
    evaluation_timestamp: str  # ISO format timestamp
    
    # Optional: reference answer if one was generated (for context only, not comparison)
    reference_answer_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# ============================================================================
# Retrieval Metrics
# ============================================================================

@dataclass(frozen=True)
class RetrievalMetrics:
    """
    Retrieval quality metrics for a single test case.
    
    Contains ranking-based metrics, concept coverage, and chunk-type analysis.
    Frozen to ensure immutability.
    """
    
    test_id: str
    
    # Ranking-based metrics
    mrr: float  # Mean Reciprocal Rank (0.0 to 1.0)
    ndcg_at_k: Dict[int, float]  # nDCG@K for different K values (e.g., {5: 0.75, 10: 0.82})
    recall_at_k: Dict[int, float]  # Recall@K for different K values
    
    # Concept coverage
    concept_coverage: float  # Percentage of expected_concepts found in retrieved chunks (0.0 to 1.0)
    concepts_found: List[str]  # Which expected concepts were found
    concepts_missed: List[str]  # Which expected concepts were not found
    
    # Chunk-type distribution
    chunk_type_distribution: Dict[str, int]  # Count of each chunk_type in retrieved chunks
    chunk_type_coverage: Dict[str, float]  # Coverage of expected_chunk_types (if specified)
    
    # Query rewriting impact
    original_query_results_count: int  # How many results from original query
    rewritten_query_results_count: int  # How many results from rewritten query
    final_merged_count: int  # Final count after deduplication
    
    # Metadata
    total_chunks_retrieved: int
    top_similarity_score: float  # Highest similarity score in retrieved chunks
    avg_similarity_score: float  # Average similarity score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# ============================================================================
# Answer Metrics (Aggregated)
# ============================================================================

@dataclass(frozen=True)
class AnswerMetrics:
    """
    Answer quality metrics aggregated across test cases.
    
    Combines individual AnswerEvaluation results into aggregate statistics.
    Frozen to ensure immutability.
    """
    
    # Per-test-case evaluations
    evaluations: List[AnswerEvaluation]  # One per test case
    
    # Aggregated scores
    avg_confidence_score: float  # Average confidence_score across all evaluations
    confidence_score_distribution: Dict[int, int]  # Count of each score (1-5)
    
    # Coverage analysis
    avg_missed_concepts_per_answer: float  # Average number of missed concepts
    total_unique_missed_concepts: Set[str]  # All unique concepts missed across all answers
    
    # Answer generation statistics
    avg_chunks_per_answer: float  # Average number of chunks used per answer
    refusal_count: int  # How many answers were refused (if tracked)
    
    # Category breakdown (optional)
    metrics_by_category: Optional[Dict[str, 'AnswerMetrics']] = None  # Recursive for category analysis
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Handle Set[str] -> List[str] conversion
        if isinstance(result.get('total_unique_missed_concepts'), set):
            result['total_unique_missed_concepts'] = list(result['total_unique_missed_concepts'])
        # Handle recursive AnswerMetrics
        if result.get('metrics_by_category'):
            result['metrics_by_category'] = {
                k: v.to_dict() if hasattr(v, 'to_dict') else asdict(v)
                for k, v in result['metrics_by_category'].items()
            }
        return result


# ============================================================================
# Evaluation Run (Complete Snapshot)
# ============================================================================

@dataclass(frozen=True)
class EvaluationRun:
    """
    Complete, immutable snapshot of an evaluation run.
    
    Contains all test cases, metrics, and configuration used.
    Frozen to ensure immutability and reproducibility.
    """
    
    # Identity
    run_id: str  # Unique identifier (e.g., "run_20250123_143022")
    timestamp: str  # ISO format timestamp
    
    # Configuration
    test_set_name: str  # Which test set was used
    retrieval_config: Dict[str, Any]  # Snapshot of retrieval configuration
    answer_generation_config: Dict[str, Any]  # Snapshot of answer generation configuration
    judge_config: Dict[str, Any]  # Snapshot of judge configuration
    
    # Results
    test_cases: List[TestCase]  # All test cases that were evaluated
    retrieval_metrics: List[RetrievalMetrics]  # One per test case
    answer_metrics: AnswerMetrics  # Aggregated answer quality metrics
    
    # Summary statistics
    total_test_cases: int
    avg_concept_mrr: float
    avg_ndcg_at_10: float
    avg_recall_at_10: float
    avg_concept_coverage: float
    avg_confidence_score: float
    
    # Metadata
    vector_db_version: Optional[str] = None  # If versioning is tracked
    notes: Optional[str] = None  # Human notes about this run
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert nested dataclasses
        result['test_cases'] = [tc.to_dict() if hasattr(tc, 'to_dict') else asdict(tc) for tc in self.test_cases]
        result['retrieval_metrics'] = [rm.to_dict() if hasattr(rm, 'to_dict') else asdict(rm) for rm in self.retrieval_metrics]
        result['answer_metrics'] = self.answer_metrics.to_dict() if hasattr(self.answer_metrics, 'to_dict') else asdict(self.answer_metrics)
        return result
    
    def to_json(self, filepath: str) -> None:
        """Serialize to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)