"""
Pure, deterministic functions for calculating RAG evaluation metrics.

This module contains only pure functions - no side effects, no LLM calls, no state.
All functions are deterministic: same inputs always produce same outputs.
"""

import math
import re
from typing import List, Dict, Tuple, Any
from core.retriever import RetrievedChunk


# ============================================================================
# Helper Functions for Concept Matching
# ============================================================================

def _normalize_concept(concept: str) -> str:
    """Normalize concept name for matching."""
    return concept.lower().strip()


def _concept_in_text(concept: str, text: str) -> bool:
    """
    Check if concept appears in text using multiple matching strategies.
    
    Strategies (in order):
    1. Case-insensitive substring match
    2. Word-boundary match (concept as whole word)
    """
    if not text or not concept:
        return False
    
    normalized_concept = _normalize_concept(concept)
    normalized_text = text.lower()
    
    # Strategy 1: Case-insensitive substring match
    if normalized_concept in normalized_text:
        return True
    
    # Strategy 2: Word-boundary match (concept as whole word)
    # Escape special regex characters in concept
    escaped_concept = re.escape(normalized_concept)
    pattern = r'\b' + escaped_concept + r'\b'
    if re.search(pattern, normalized_text):
        return True
    
    return False


def _concept_in_chunk(concept: str, chunk: RetrievedChunk) -> bool:
    """
    Check if concept appears in a chunk.
    
    Checks headline, summary, and original_text fields.
    """
    if _concept_in_text(concept, chunk.headline):
        return True
    if _concept_in_text(concept, chunk.summary):
        return True
    if _concept_in_text(concept, chunk.original_text):
        return True
    return False


# ============================================================================
# MRR (Mean Reciprocal Rank)
# ============================================================================

def calculate_concept_mrr(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk]
) -> float:
    """
    Calculate Mean Reciprocal Rank.
    
    Measures how highly ranked the first relevant chunk is.
    
    Args:
        expected_concepts: List of concept names that should be found
        retrieved_chunks: Ranked list of RetrievedChunk objects (sorted by similarity_score)
    
    Returns:
        MRR score (0.0 to 1.0)
    
    Logic:
        1. For each expected concept, find its rank in retrieved chunks
        2. Reciprocal rank = 1 / rank (if found), 0 (if not found)
        3. MRR = average of reciprocal ranks
    """
    if not expected_concepts or not retrieved_chunks:
        return 0.0
    
    reciprocal_ranks = []
    
    for concept in expected_concepts:
        # Find first chunk containing this concept
        rank = None
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            if _concept_in_chunk(concept, chunk):
                rank = idx
                break
        
        if rank is not None:
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
    
    if not reciprocal_ranks:
        return 0.0
    
    return sum(reciprocal_ranks) / len(reciprocal_ranks)


# ============================================================================
# nDCG@K (Normalized Discounted Cumulative Gain at K)
# ============================================================================

def _calculate_relevance_score(concept: str, chunk: RetrievedChunk) -> float:
    """
    Calculate relevance score for a chunk based on concept matches.
    
    Returns:
        Relevance score (0.0 to 1.0)
        - 1.0 if concept appears in headline (most important)
        - 0.7 if concept appears in summary
        - 0.5 if concept appears in original_text
        - 0.0 if concept doesn't appear
    """
    if _concept_in_text(concept, chunk.headline):
        return 1.0
    if _concept_in_text(concept, chunk.summary):
        return 0.7
    if _concept_in_text(concept, chunk.original_text):
        return 0.5
    return 0.0


def _calculate_chunk_relevance(expected_concepts: List[str], chunk: RetrievedChunk) -> float:
    """
    Calculate overall relevance score for a chunk based on all expected concepts.
    
    Returns:
        Relevance score (0.0 to 1.0) - average of best match per concept
    """
    if not expected_concepts:
        return 0.0
    
    max_scores = []
    for concept in expected_concepts:
        score = _calculate_relevance_score(concept, chunk)
        max_scores.append(score)
    
    # Average of best matches (could also use max, but average is more conservative)
    return sum(max_scores) / len(max_scores) if max_scores else 0.0


def calculate_ndcg_at_k(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk],
    k: int
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K.
    
    Measures ranking quality considering both relevance and position.
    
    Args:
        expected_concepts: List of concept names that should appear
        retrieved_chunks: Ranked list of RetrievedChunk objects
        k: Cutoff rank (e.g., 5, 10, 20)
    
    Returns:
        nDCG@K score (0.0 to 1.0)
    
    Logic:
        1. Assign relevance scores to each chunk based on concept matches
        2. Calculate DCG@K: Sum of (relevance_score / log2(rank + 1)) for top-K chunks
        3. Calculate ideal DCG@K: DCG@K if chunks were perfectly ranked
        4. nDCG@K = DCG@K / ideal_DCG@K
    """
    if not expected_concepts or not retrieved_chunks or k <= 0:
        return 0.0
    
    # Take top-K chunks
    top_k_chunks = retrieved_chunks[:k]
    
    # Calculate DCG@K
    dcg = 0.0
    for rank, chunk in enumerate(top_k_chunks, start=1):
        relevance = _calculate_chunk_relevance(expected_concepts, chunk)
        # Discount: log2(rank + 1) ensures rank 1 gets full weight
        discount = math.log2(rank + 1) if rank > 1 else 1.0
        dcg += relevance / discount
    
    # Calculate ideal DCG@K (perfect ranking: highest relevance first)
    relevance_scores = [_calculate_chunk_relevance(expected_concepts, chunk) for chunk in top_k_chunks]
    ideal_relevance_scores = sorted(relevance_scores, reverse=True)
    
    ideal_dcg = 0.0
    for rank, relevance in enumerate(ideal_relevance_scores, start=1):
        discount = math.log2(rank + 1) if rank > 1 else 1.0
        ideal_dcg += relevance / discount
    
    # Normalize
    if ideal_dcg == 0.0:
        return 0.0
    
    return dcg / ideal_dcg


# ============================================================================
# Recall@K
# ============================================================================

def calculate_recall_at_k(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk],
    k: int
) -> float:
    """
    Calculate Recall at K.
    
    Measures how many expected concepts are found in the top-K retrieved chunks.
    
    Args:
        expected_concepts: List of concept names that should appear
        retrieved_chunks: Ranked list of RetrievedChunk objects
        k: Cutoff rank (e.g., 5, 10, 20)
    
    Returns:
        Recall@K score (0.0 to 1.0)
    
    Logic:
        1. Consider only the top-K chunks from retrieved_chunks
        2. Check which expected concepts appear in those top-K chunks
        3. Recall@K = (concepts found in top-K) / (total expected concepts)
    """
    if not expected_concepts or not retrieved_chunks or k <= 0:
        return 0.0
    
    # Take top-K chunks
    top_k_chunks = retrieved_chunks[:k]
    
    # Find which concepts appear in top-K chunks
    concepts_found = set()
    for concept in expected_concepts:
        for chunk in top_k_chunks:
            if _concept_in_chunk(concept, chunk):
                concepts_found.add(concept)
                break  # Found in at least one chunk, move to next concept
    
    # Calculate recall
    if not expected_concepts:
        return 0.0
    
    return len(concepts_found) / len(expected_concepts)


# ============================================================================
# Concept Coverage
# ============================================================================

def calculate_concept_coverage(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk]
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate concept coverage.
    
    Validates that retrieved chunks cover the expected concepts.
    
    Args:
        expected_concepts: List of concept names that should be found
        retrieved_chunks: List of RetrievedChunk objects
    
    Returns:
        Tuple of (coverage_ratio, concepts_found, concepts_missed)
        - coverage_ratio: Float between 0.0 and 1.0
        - concepts_found: List of concept names that were found
        - concepts_missed: List of concept names that were not found
    """
    if not expected_concepts:
        return 0.0, [], []
    
    concepts_found = []
    concepts_missed = []
    
    for concept in expected_concepts:
        found = False
        for chunk in retrieved_chunks:
            if _concept_in_chunk(concept, chunk):
                concepts_found.append(concept)
                found = True
                break
        
        if not found:
            concepts_missed.append(concept)
    
    coverage_ratio = len(concepts_found) / len(expected_concepts) if expected_concepts else 0.0
    
    return coverage_ratio, concepts_found, concepts_missed


# ============================================================================
# Chunk-Type Distribution
# ============================================================================

def calculate_chunk_type_distribution(
    retrieved_chunks: List[RetrievedChunk]
) -> Dict[str, int]:
    """
    Calculate distribution of chunk types.
    
    Analyzes the diversity and balance of chunk types in retrieved results.
    
    Args:
        retrieved_chunks: List of RetrievedChunk objects
    
    Returns:
        Dictionary mapping chunk_type -> count
    """
    distribution: Dict[str, int] = {}
    
    for chunk in retrieved_chunks:
        chunk_type = chunk.chunk_type
        distribution[chunk_type] = distribution.get(chunk_type, 0) + 1
    
    return distribution


def calculate_chunk_type_coverage(
    expected_chunk_types: List[str],
    retrieved_chunks: List[RetrievedChunk]
) -> Dict[str, float]:
    """
    Calculate coverage of expected chunk types.
    
    Args:
        expected_chunk_types: List of chunk types that should appear
        retrieved_chunks: List of RetrievedChunk objects
    
    Returns:
        Dictionary mapping expected_chunk_type -> coverage ratio (0.0 to 1.0)
        Coverage is 1.0 if type appears, 0.0 if it doesn't
    """
    if not expected_chunk_types:
        return {}
    
    # Get unique chunk types in retrieved chunks
    retrieved_types = set(chunk.chunk_type for chunk in retrieved_chunks)
    
    coverage = {}
    for expected_type in expected_chunk_types:
        coverage[expected_type] = 1.0 if expected_type in retrieved_types else 0.0
    
    return coverage


# ============================================================================
# Aggregation Functions
# ============================================================================

def aggregate_retrieval_metrics(
    metrics_list: List[Any]  # List[RetrievalMetrics]
) -> Dict[str, float]:
    """
    Aggregate retrieval metrics across multiple test cases.
    
    Args:
        metrics_list: List of RetrievalMetrics objects
    
    Returns:
        Dictionary with aggregated statistics:
        - avg_concept_mrr
        - avg_ndcg_at_5, avg_ndcg_at_10, avg_ndcg_at_20
        - avg_recall_at_5, avg_recall_at_10, avg_recall_at_20
        - avg_concept_coverage
    """
    if not metrics_list:
        return {
            'avg_concept_mrr': 0.0,
            'avg_ndcg_at_5': 0.0,
            'avg_ndcg_at_10': 0.0,
            'avg_ndcg_at_20': 0.0,
            'avg_recall_at_5': 0.0,
            'avg_recall_at_10': 0.0,
            'avg_recall_at_20': 0.0,
            'avg_concept_coverage': 0.0
        }
    
    total = len(metrics_list)
    
    # Aggregate MRR
    avg_concept_mrr = sum(m.mrr for m in metrics_list) / total
    
    # Aggregate nDCG@K
    avg_ndcg_at_5 = sum(m.ndcg_at_k.get(5, 0.0) for m in metrics_list) / total
    avg_ndcg_at_10 = sum(m.ndcg_at_k.get(10, 0.0) for m in metrics_list) / total
    avg_ndcg_at_20 = sum(m.ndcg_at_k.get(20, 0.0) for m in metrics_list) / total
    
    # Aggregate Recall@K
    avg_recall_at_5 = sum(m.recall_at_k.get(5, 0.0) for m in metrics_list) / total
    avg_recall_at_10 = sum(m.recall_at_k.get(10, 0.0) for m in metrics_list) / total
    avg_recall_at_20 = sum(m.recall_at_k.get(20, 0.0) for m in metrics_list) / total
    
    # Aggregate concept coverage
    avg_concept_coverage = sum(m.concept_coverage for m in metrics_list) / total
    
    return {
        'avg_concept_mrr': avg_concept_mrr,
        'avg_ndcg_at_5': avg_ndcg_at_5,
        'avg_ndcg_at_10': avg_ndcg_at_10,
        'avg_ndcg_at_20': avg_ndcg_at_20,
        'avg_recall_at_5': avg_recall_at_5,
        'avg_recall_at_10': avg_recall_at_10,
        'avg_recall_at_20': avg_recall_at_20,
        'avg_concept_coverage': avg_concept_coverage
    }


def aggregate_answer_metrics(
    evaluations: List[Any]  # List[AnswerEvaluation]
) -> Any:  # AnswerMetrics
    """
    Aggregate answer evaluation results into AnswerMetrics.
    
    Args:
        evaluations: List of AnswerEvaluation objects
    
    Returns:
        AnswerMetrics object with aggregated statistics
    """
    from evaluation.data_contracts import AnswerMetrics
    
    if not evaluations:
        return AnswerMetrics(
            evaluations=[],
            avg_confidence_score=0.0,
            confidence_score_distribution={},
            avg_missed_concepts_per_answer=0.0,
            total_unique_missed_concepts=set(),
            avg_chunks_per_answer=0.0,
            refusal_count=0
        )
    
    total = len(evaluations)
    
    # Aggregate confidence scores
    confidence_scores = [e.confidence_score for e in evaluations]
    avg_confidence_score = sum(confidence_scores) / total
    
    # Build confidence score distribution
    confidence_score_distribution: Dict[int, int] = {}
    for score in confidence_scores:
        confidence_score_distribution[score] = confidence_score_distribution.get(score, 0) + 1
    
    # Aggregate missed concepts
    all_missed_concepts = []
    for e in evaluations:
        all_missed_concepts.extend(e.missed_concepts)
    
    avg_missed_concepts_per_answer = len(all_missed_concepts) / total if total > 0 else 0.0
    total_unique_missed_concepts = set(all_missed_concepts)
    
    # Aggregate chunks per answer
    avg_chunks_per_answer = sum(e.num_retrieved_chunks for e in evaluations) / total if total > 0 else 0.0
    
    # Count refusals (if reference_answer_text is None, might indicate refusal)
    # Note: This is a heuristic - actual refusal tracking would need to check GeneratedAnswer
    refusal_count = 0  # We don't have direct refusal info in AnswerEvaluation
    
    return AnswerMetrics(
        evaluations=evaluations,
        avg_confidence_score=avg_confidence_score,
        confidence_score_distribution=confidence_score_distribution,
        avg_missed_concepts_per_answer=avg_missed_concepts_per_answer,
        total_unique_missed_concepts=total_unique_missed_concepts,
        avg_chunks_per_answer=avg_chunks_per_answer,
        refusal_count=refusal_count
    )
