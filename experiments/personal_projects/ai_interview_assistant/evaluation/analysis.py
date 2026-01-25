"""
Evaluation Analysis Layer.

This module provides pure analysis functions to analyze completed EvaluationRun artifacts.
All functions are pure (no LLM calls, no side effects) and operate on EvaluationRun data.

Input: EvaluationRun JSON files
Output: Structured diagnostic reports
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from evaluation.data_contracts import (
    EvaluationRun, TestCase, RetrievalMetrics, AnswerEvaluation
)


# ============================================================================
# Diagnostic Report Data Structures
# ============================================================================

@dataclass(frozen=True)
class RequirementWeakness:
    """Weakness analysis for a specific requirement."""
    requirement_id: str
    test_count: int  # Number of test cases targeting this requirement
    avg_concept_coverage: float  # Average concept coverage across tests
    avg_retrieval_mrr: float  # Average MRR for retrieval
    avg_answer_confidence: float  # Average answer confidence score
    weakness_score: float  # Composite score (lower = weaker)
    test_ids: List[str]  # Test IDs that target this requirement


@dataclass(frozen=True)
class RequirementRanking:
    """Ranked list of weakest requirements."""
    weakest_requirements: List[RequirementWeakness]
    total_requirements_analyzed: int
    avg_weakness_score: float


@dataclass(frozen=True)
class ChunkTypeUsage:
    """Analysis of chunk type usage patterns."""
    chunk_type: str
    expected_count: int  # How many times this type was expected
    actual_count: int  # How many times this type appeared in retrieval
    usage_ratio: float  # actual_count / expected_count (if expected > 0)
    over_used: bool  # True if usage_ratio > 1.2
    under_used: bool  # True if usage_ratio < 0.8 and expected > 0


@dataclass(frozen=True)
class ChunkTypeAnalysis:
    """Analysis of chunk type distribution patterns."""
    chunk_type_usages: List[ChunkTypeUsage]
    overall_distribution: Dict[str, int]  # Total count per chunk type
    recommendations: List[str]  # Text recommendations


@dataclass(frozen=True)
class RetrievalAnswerMismatch:
    """Test case with high retrieval but low answer quality."""
    test_id: str
    question: str
    retrieval_mrr: float
    retrieval_ndcg_at_10: float
    retrieval_concept_coverage: float
    answer_confidence_score: int
    answer_missed_concepts: List[str]
    mismatch_score: float  # Higher = bigger gap between retrieval and answer quality


@dataclass(frozen=True)
class RetrievalAnswerMismatchReport:
    """Report of tests with retrieval-answer quality mismatches."""
    mismatches: List[RetrievalAnswerMismatch]
    total_tests: int
    mismatch_count: int
    avg_mismatch_score: float


@dataclass(frozen=True)
class RegressionMetric:
    """Change in a specific metric between two runs."""
    metric_name: str
    baseline_value: float
    current_value: float
    absolute_change: float
    relative_change: float  # Percentage change
    is_regression: bool  # True if metric got worse
    is_improvement: bool  # True if metric got better


@dataclass(frozen=True)
class RegressionReport:
    """Comparison of two evaluation runs for regression detection."""
    baseline_run_id: str
    current_run_id: str
    metric_changes: List[RegressionMetric]
    requirement_changes: Dict[str, RegressionMetric]  # Per-requirement changes
    regression_count: int
    improvement_count: int
    stable_count: int
    overall_assessment: str  # Text summary


# ============================================================================
# EvaluationRun Loading
# ============================================================================

def load_evaluation_run(filepath: Path) -> EvaluationRun:
    """
    Load an EvaluationRun from a JSON file.
    
    Args:
        filepath: Path to JSON file containing EvaluationRun data
    
    Returns:
        EvaluationRun object
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid or doesn't match EvaluationRun structure
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Evaluation run file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Reconstruct EvaluationRun from dict
    # Note: This is a simplified reconstruction - in production, you'd want
    # a proper from_dict() method on each dataclass
    return _dict_to_evaluation_run(data)


def _dict_to_evaluation_run(data: Dict[str, Any]) -> EvaluationRun:
    """Convert dictionary to EvaluationRun (simplified reconstruction)."""
    # This is a helper - in a real implementation, you'd want proper
    # deserialization methods on each dataclass
    # For now, we'll work with the dict structure directly in analysis functions
    # and reconstruct only what we need
    from evaluation.data_contracts import (
        TestCase, RetrievalMetrics, AnswerMetrics, AnswerEvaluation
    )
    
    # Reconstruct test cases
    test_cases = [
        TestCase(**tc_data) for tc_data in data.get('test_cases', [])
    ]
    
    # Reconstruct retrieval metrics
    retrieval_metrics = [
        RetrievalMetrics(**rm_data) for rm_data in data.get('retrieval_metrics', [])
    ]
    
    # Reconstruct answer evaluations
    answer_metrics_data = data.get('answer_metrics', {})
    evaluations = [
        AnswerEvaluation(**ae_data) for ae_data in answer_metrics_data.get('evaluations', [])
    ]
    
    # Reconstruct answer metrics
    answer_metrics = AnswerMetrics(
        evaluations=evaluations,
        avg_confidence_score=answer_metrics_data.get('avg_confidence_score', 0.0),
        confidence_score_distribution=answer_metrics_data.get('confidence_score_distribution', {}),
        avg_missed_concepts_per_answer=answer_metrics_data.get('avg_missed_concepts_per_answer', 0.0),
        total_unique_missed_concepts=set(answer_metrics_data.get('total_unique_missed_concepts', [])),
        avg_chunks_per_answer=answer_metrics_data.get('avg_chunks_per_answer', 0.0),
        refusal_count=answer_metrics_data.get('refusal_count', 0)
    )
    
    return EvaluationRun(
        run_id=data.get('run_id', ''),
        timestamp=data.get('timestamp', ''),
        test_set_name=data.get('test_set_name', ''),
        retrieval_config=data.get('retrieval_config', {}),
        answer_generation_config=data.get('answer_generation_config', {}),
        judge_config=data.get('judge_config', {}),
        test_cases=test_cases,
        retrieval_metrics=retrieval_metrics,
        answer_metrics=answer_metrics,
        total_test_cases=data.get('total_test_cases', 0),
        avg_concept_mrr=data.get('avg_concept_mrr', 0.0),
        avg_ndcg_at_10=data.get('avg_ndcg_at_10', 0.0),
        avg_recall_at_10=data.get('avg_recall_at_10', 0.0),
        avg_concept_coverage=data.get('avg_concept_coverage', 0.0),
        avg_confidence_score=data.get('avg_confidence_score', 0.0),
        vector_db_version=data.get('vector_db_version'),
        notes=data.get('notes')
    )


# ============================================================================
# Analysis Functions
# ============================================================================

def rank_weakest_requirements(
    evaluation_run: EvaluationRun,
    min_test_count: int = 1
) -> RequirementRanking:
    """
    Rank requirements by weakness (lowest performance).
    
    Weakness is calculated as a composite score considering:
    - Concept coverage (lower = weaker)
    - Retrieval MRR (lower = weaker)
    - Answer confidence (lower = weaker)
    
    Args:
        evaluation_run: EvaluationRun to analyze
        min_test_count: Minimum number of tests per requirement to include
    
    Returns:
        RequirementRanking with weakest requirements first
    """
    # Group test cases and metrics by requirement_id
    requirement_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'test_ids': [],
        'concept_coverages': [],
        'mrrs': [],
        'confidences': []
    })
    
    # Map test_id to metrics
    metrics_by_test_id = {
        rm.test_id: rm for rm in evaluation_run.retrieval_metrics
    }
    evaluations_by_test_id = {
        ae.test_id: ae for ae in evaluation_run.answer_metrics.evaluations
    }
    
    # Collect data per requirement
    for test_case in evaluation_run.test_cases:
        if not test_case.expected_requirement_ids:
            continue
        
        test_id = test_case.test_id
        retrieval_metrics = metrics_by_test_id.get(test_id)
        answer_eval = evaluations_by_test_id.get(test_id)
        
        if not retrieval_metrics or not answer_eval:
            continue
        
        for req_id in test_case.expected_requirement_ids:
            requirement_data[req_id]['test_ids'].append(test_id)
            requirement_data[req_id]['concept_coverages'].append(retrieval_metrics.concept_coverage)
            requirement_data[req_id]['mrrs'].append(retrieval_metrics.mrr)
            requirement_data[req_id]['confidences'].append(answer_eval.confidence_score)
    
    # Calculate weakness scores
    weaknesses = []
    for req_id, data in requirement_data.items():
        if len(data['test_ids']) < min_test_count:
            continue
        
        avg_coverage = sum(data['concept_coverages']) / len(data['concept_coverages']) if data['concept_coverages'] else 0.0
        avg_mrr = sum(data['mrrs']) / len(data['mrrs']) if data['mrrs'] else 0.0
        avg_confidence = sum(data['confidences']) / len(data['confidences']) if data['confidences'] else 0.0
        
        # Weakness score: lower is worse
        # Normalize each component to 0-1 scale, then average
        # (1 - coverage) + (1 - mrr) + (1 - confidence/5) / 3
        weakness_score = (
            (1.0 - avg_coverage) +
            (1.0 - avg_mrr) +
            (1.0 - avg_confidence / 5.0)
        ) / 3.0
        
        weaknesses.append(RequirementWeakness(
            requirement_id=req_id,
            test_count=len(data['test_ids']),
            avg_concept_coverage=avg_coverage,
            avg_retrieval_mrr=avg_mrr,
            avg_answer_confidence=avg_confidence,
            weakness_score=weakness_score,
            test_ids=data['test_ids']
        ))
    
    # Sort by weakness score (highest = weakest)
    weaknesses.sort(key=lambda w: w.weakness_score, reverse=True)
    
    avg_weakness = sum(w.weakness_score for w in weaknesses) / len(weaknesses) if weaknesses else 0.0
    
    return RequirementRanking(
        weakest_requirements=weaknesses,
        total_requirements_analyzed=len(weaknesses),
        avg_weakness_score=avg_weakness
    )


def analyze_chunk_type_usage(
    evaluation_run: EvaluationRun
) -> ChunkTypeAnalysis:
    """
    Detect over/under-used chunk types.
    
    Compares expected chunk types (from test cases) with actual chunk types
    retrieved to identify imbalances.
    
    Args:
        evaluation_run: EvaluationRun to analyze
    
    Returns:
        ChunkTypeAnalysis with usage patterns and recommendations
    """
    # Count expected chunk types
    expected_counts: Dict[str, int] = defaultdict(int)
    for test_case in evaluation_run.test_cases:
        if test_case.expected_chunk_types:
            for chunk_type in test_case.expected_chunk_types:
                expected_counts[chunk_type] += 1
    
    # Count actual chunk types retrieved
    actual_counts: Dict[str, int] = defaultdict(int)
    for rm in evaluation_run.retrieval_metrics:
        for chunk_type, count in rm.chunk_type_distribution.items():
            actual_counts[chunk_type] += count
    
    # Calculate usage ratios and identify over/under-used types
    chunk_type_usages = []
    for chunk_type in set(list(expected_counts.keys()) + list(actual_counts.keys())):
        expected = expected_counts.get(chunk_type, 0)
        actual = actual_counts.get(chunk_type, 0)
        
        if expected > 0:
            usage_ratio = actual / expected
        else:
            usage_ratio = float('inf') if actual > 0 else 0.0
        
        chunk_type_usages.append(ChunkTypeUsage(
            chunk_type=chunk_type,
            expected_count=expected,
            actual_count=actual,
            usage_ratio=usage_ratio if usage_ratio != float('inf') else 999.0,
            over_used=usage_ratio > 1.2 if expected > 0 else False,
            under_used=usage_ratio < 0.8 and expected > 0
        ))
    
    # Generate recommendations
    recommendations = []
    over_used_types = [ctu for ctu in chunk_type_usages if ctu.over_used]
    under_used_types = [ctu for ctu in chunk_type_usages if ctu.under_used]
    
    if over_used_types:
        recommendations.append(
            f"Over-used chunk types: {', '.join(ctu.chunk_type for ctu in over_used_types)}. "
            f"Consider if retrieval is too biased toward these types."
        )
    
    if under_used_types:
        recommendations.append(
            f"Under-used chunk types: {', '.join(ctu.chunk_type for ctu in under_used_types)}. "
            f"These types are expected but rarely retrieved - may indicate knowledge base gaps."
        )
    
    if not over_used_types and not under_used_types:
        recommendations.append("Chunk type distribution appears balanced.")
    
    return ChunkTypeAnalysis(
        chunk_type_usages=chunk_type_usages,
        overall_distribution=dict(actual_counts),
        recommendations=recommendations
    )


def find_retrieval_answer_mismatches(
    evaluation_run: EvaluationRun,
    min_retrieval_threshold: float = 0.7,
    max_answer_threshold: int = 3
) -> RetrievalAnswerMismatchReport:
    """
    Find test cases with high retrieval quality but low answer quality.
    
    These mismatches indicate potential issues in answer generation or
    evaluation, not retrieval.
    
    Args:
        evaluation_run: EvaluationRun to analyze
        min_retrieval_threshold: Minimum MRR/coverage to consider "high retrieval"
        max_answer_threshold: Maximum confidence score to consider "low answer"
    
    Returns:
        RetrievalAnswerMismatchReport with identified mismatches
    """
    # Map metrics and evaluations by test_id
    metrics_by_test_id = {
        rm.test_id: rm for rm in evaluation_run.retrieval_metrics
    }
    evaluations_by_test_id = {
        ae.test_id: ae for ae in evaluation_run.answer_metrics.evaluations
    }
    test_cases_by_id = {
        tc.test_id: tc for tc in evaluation_run.test_cases
    }
    
    mismatches = []
    
    for test_id, retrieval_metrics in metrics_by_test_id.items():
        answer_eval = evaluations_by_test_id.get(test_id)
        test_case = test_cases_by_id.get(test_id)
        
        if not answer_eval or not test_case:
            continue
        
        # Check if retrieval is high but answer quality is low
        retrieval_score = (
            retrieval_metrics.mrr +
            retrieval_metrics.ndcg_at_k.get(10, 0.0) +
            retrieval_metrics.concept_coverage
        ) / 3.0
        
        is_high_retrieval = retrieval_score >= min_retrieval_threshold
        is_low_answer = answer_eval.confidence_score <= max_answer_threshold
        
        if is_high_retrieval and is_low_answer:
            # Calculate mismatch score (gap between retrieval and answer quality)
            # Higher score = bigger gap
            answer_normalized = answer_eval.confidence_score / 5.0
            mismatch_score = retrieval_score - answer_normalized
            
            mismatches.append(RetrievalAnswerMismatch(
                test_id=test_id,
                question=test_case.question,
                retrieval_mrr=retrieval_metrics.mrr,
                retrieval_ndcg_at_10=retrieval_metrics.ndcg_at_k.get(10, 0.0),
                retrieval_concept_coverage=retrieval_metrics.concept_coverage,
                answer_confidence_score=answer_eval.confidence_score,
                answer_missed_concepts=answer_eval.missed_concepts,
                mismatch_score=mismatch_score
            ))
    
    # Sort by mismatch score (highest first)
    mismatches.sort(key=lambda m: m.mismatch_score, reverse=True)
    
    avg_mismatch = sum(m.mismatch_score for m in mismatches) / len(mismatches) if mismatches else 0.0
    
    return RetrievalAnswerMismatchReport(
        mismatches=mismatches,
        total_tests=len(evaluation_run.test_cases),
        mismatch_count=len(mismatches),
        avg_mismatch_score=avg_mismatch
    )


def compare_evaluation_runs(
    baseline_run: EvaluationRun,
    current_run: EvaluationRun
) -> RegressionReport:
    """
    Compare two evaluation runs to detect regressions and improvements.
    
    Args:
        baseline_run: Earlier evaluation run (baseline)
        current_run: Later evaluation run (current)
    
    Returns:
        RegressionReport with metric changes and overall assessment
    """
    # Compare overall metrics
    metric_changes = []
    
    metrics_to_compare = [
        ('avg_concept_mrr', 'Average Concept MRR', True),  # Higher is better
        ('avg_ndcg_at_10', 'Average nDCG@10', True),
        ('avg_recall_at_10', 'Average Recall@10', True),
        ('avg_concept_coverage', 'Average Concept Coverage', True),
        ('avg_confidence_score', 'Average Answer Confidence', True),
    ]
    
    for attr_name, display_name, higher_is_better in metrics_to_compare:
        baseline_value = getattr(baseline_run, attr_name, 0.0)
        current_value = getattr(current_run, attr_name, 0.0)
        absolute_change = current_value - baseline_value
        
        if baseline_value != 0:
            relative_change = (absolute_change / baseline_value) * 100.0
        else:
            relative_change = 100.0 if current_value > 0 else 0.0
        
        is_regression = (higher_is_better and absolute_change < -0.01) or (not higher_is_better and absolute_change > 0.01)
        is_improvement = (higher_is_better and absolute_change > 0.01) or (not higher_is_better and absolute_change < -0.01)
        
        metric_changes.append(RegressionMetric(
            metric_name=display_name,
            baseline_value=baseline_value,
            current_value=current_value,
            absolute_change=absolute_change,
            relative_change=relative_change,
            is_regression=is_regression,
            is_improvement=is_improvement
        ))
    
    # Compare per-requirement metrics
    baseline_ranking = rank_weakest_requirements(baseline_run)
    current_ranking = rank_weakest_requirements(current_run)
    
    baseline_by_req = {w.requirement_id: w for w in baseline_ranking.weakest_requirements}
    current_by_req = {w.requirement_id: w for w in current_ranking.weakest_requirements}
    
    requirement_changes: Dict[str, RegressionMetric] = {}
    all_req_ids = set(list(baseline_by_req.keys()) + list(current_by_req.keys()))
    
    for req_id in all_req_ids:
        baseline_req = baseline_by_req.get(req_id)
        current_req = current_by_req.get(req_id)
        
        if baseline_req and current_req:
            # Compare weakness scores (lower is better, so negative change is improvement)
            baseline_score = baseline_req.weakness_score
            current_score = current_req.weakness_score
            change = current_score - baseline_score  # Positive = worse, negative = better
            
            relative_change = (change / baseline_score * 100.0) if baseline_score != 0 else 0.0
            
            requirement_changes[req_id] = RegressionMetric(
                metric_name=f"Requirement {req_id} Weakness",
                baseline_value=baseline_score,
                current_value=current_score,
                absolute_change=change,
                relative_change=relative_change,
                is_regression=change > 0.01,  # Got weaker
                is_improvement=change < -0.01  # Got stronger
            )
    
    # Count regressions and improvements
    regression_count = sum(1 for m in metric_changes if m.is_regression)
    improvement_count = sum(1 for m in metric_changes if m.is_improvement)
    stable_count = len(metric_changes) - regression_count - improvement_count
    
    # Generate overall assessment
    if regression_count > improvement_count:
        assessment = f"⚠️ Regression detected: {regression_count} metrics worsened, {improvement_count} improved."
    elif improvement_count > regression_count:
        assessment = f"✅ Improvement detected: {improvement_count} metrics improved, {regression_count} worsened."
    else:
        assessment = f"➡️ Stable: {stable_count} metrics unchanged, {regression_count} regressions, {improvement_count} improvements."
    
    return RegressionReport(
        baseline_run_id=baseline_run.run_id,
        current_run_id=current_run.run_id,
        metric_changes=metric_changes,
        requirement_changes=requirement_changes,
        regression_count=regression_count,
        improvement_count=improvement_count,
        stable_count=stable_count,
        overall_assessment=assessment
    )


# ============================================================================
# Utility Functions
# ============================================================================

def generate_analysis_summary(
    evaluation_run: EvaluationRun,
    output_file: Optional[Path] = None
) -> str:
    """
    Generate a human-readable summary of all analyses.
    
    Args:
        evaluation_run: EvaluationRun to analyze
        output_file: Optional file path to write summary to
    
    Returns:
        Markdown-formatted summary string
    """
    # Run all analyses
    requirement_ranking = rank_weakest_requirements(evaluation_run)
    chunk_type_analysis = analyze_chunk_type_usage(evaluation_run)
    mismatch_report = find_retrieval_answer_mismatches(evaluation_run)
    
    # Generate summary
    lines = [
        "# Evaluation Run Analysis Summary",
        "",
        f"**Run ID:** {evaluation_run.run_id}",
        f"**Timestamp:** {evaluation_run.timestamp}",
        f"**Test Set:** {evaluation_run.test_set_name}",
        f"**Total Test Cases:** {evaluation_run.total_test_cases}",
        "",
        "## Overall Metrics",
        "",
        f"- Average Concept MRR: {evaluation_run.avg_concept_mrr:.3f}",
        f"- Average nDCG@10: {evaluation_run.avg_ndcg_at_10:.3f}",
        f"- Average Recall@10: {evaluation_run.avg_recall_at_10:.3f}",
        f"- Average Concept Coverage: {evaluation_run.avg_concept_coverage:.3f}",
        f"- Average Answer Confidence: {evaluation_run.avg_confidence_score:.2f}",
        "",
        "## Weakest Requirements",
        "",
        f"Analyzed {requirement_ranking.total_requirements_analyzed} requirements.",
        "",
    ]
    
    if requirement_ranking.weakest_requirements:
        lines.append("Top 5 weakest requirements:")
        lines.append("")
        for i, weakness in enumerate(requirement_ranking.weakest_requirements[:5], 1):
            lines.append(
                f"{i}. **Requirement {weakness.requirement_id}** "
                f"(Weakness Score: {weakness.weakness_score:.3f})"
            )
            lines.append(f"   - Tests: {weakness.test_count}")
            lines.append(f"   - Avg Coverage: {weakness.avg_concept_coverage:.3f}")
            lines.append(f"   - Avg MRR: {weakness.avg_retrieval_mrr:.3f}")
            lines.append(f"   - Avg Confidence: {weakness.avg_answer_confidence:.2f}")
            lines.append("")
    else:
        lines.append("No requirements with sufficient test coverage.")
        lines.append("")
    
    lines.extend([
        "## Chunk Type Usage Analysis",
        "",
    ])
    
    for usage in chunk_type_analysis.chunk_type_usages:
        status = "⚠️ OVER-USED" if usage.over_used else ("⚠️ UNDER-USED" if usage.under_used else "✓ Balanced")
        lines.append(f"- **{usage.chunk_type}**: {status}")
        lines.append(f"  - Expected: {usage.expected_count}, Actual: {usage.actual_count}, Ratio: {usage.usage_ratio:.2f}")
        lines.append("")
    
    lines.extend([
        "### Recommendations",
        "",
    ])
    
    for rec in chunk_type_analysis.recommendations:
        lines.append(f"- {rec}")
        lines.append("")
    
    lines.extend([
        "## Retrieval-Answer Mismatches",
        "",
        f"Found {mismatch_report.mismatch_count} tests with high retrieval but low answer quality.",
        f"Average mismatch score: {mismatch_report.avg_mismatch_score:.3f}",
        "",
    ])
    
    if mismatch_report.mismatches:
        lines.append("Top 3 mismatches:")
        lines.append("")
        for i, mismatch in enumerate(mismatch_report.mismatches[:3], 1):
            lines.append(f"{i}. **{mismatch.test_id}** (Mismatch Score: {mismatch.mismatch_score:.3f})")
            lines.append(f"   - Question: {mismatch.question[:100]}...")
            lines.append(f"   - Retrieval MRR: {mismatch.retrieval_mrr:.3f}")
            lines.append(f"   - Answer Confidence: {mismatch.answer_confidence_score}/5")
            lines.append(f"   - Missed Concepts: {len(mismatch.answer_missed_concepts)}")
            lines.append("")
    else:
        lines.append("No significant mismatches detected.")
        lines.append("")
    
    summary = "\n".join(lines)
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
    
    return summary
