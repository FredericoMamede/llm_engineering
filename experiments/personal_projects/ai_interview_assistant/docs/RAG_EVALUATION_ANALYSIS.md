# Evaluation Analysis - Example Usage

> **Purpose**  
> This document shows how to interpret and act on RAG evaluation results using the analysis layer.  
> It does not define metrics or system behavior — see `RAG_EVALUATION_DESIGN.md` for design.

**Status**: ✅ **Implemented** - All analysis functions are available in `evaluation/analysis.py`


## Basic Usage

### 1. Load an Evaluation Run

```python
from pathlib import Path
from evaluation.analysis import load_evaluation_run

# Load a completed evaluation run
run_file = Path("evaluation/runs/run_20250123_143022.json")
evaluation_run = load_evaluation_run(run_file)

print(f"Loaded run: {evaluation_run.run_id}")
print(f"Test cases: {evaluation_run.total_test_cases}")
print(f"Average MRR: {evaluation_run.avg_concept_mrr:.3f}")
```

### 2. Rank Weakest Requirements

```python
from evaluation.analysis import rank_weakest_requirements

# Find weakest requirements
ranking = rank_weakest_requirements(evaluation_run, min_test_count=1)

print(f"Analyzed {ranking.total_requirements_analyzed} requirements")
print(f"Average weakness score: {ranking.avg_weakness_score:.3f}")

# Print top 5 weakest
for i, weakness in enumerate(ranking.weakest_requirements[:5], 1):
    print(f"\n{i}. Requirement {weakness.requirement_id}")
    print(f"   Weakness Score: {weakness.weakness_score:.3f}")
    print(f"   Test Count: {weakness.test_count}")
    print(f"   Avg Coverage: {weakness.avg_concept_coverage:.3f}")
    print(f"   Avg MRR: {weakness.avg_retrieval_mrr:.3f}")
    print(f"   Avg Confidence: {weakness.avg_answer_confidence:.2f}")
```

### 3. Analyze Chunk Type Usage

```python
from evaluation.analysis import analyze_chunk_type_usage

# Detect over/under-used chunk types
analysis = analyze_chunk_type_usage(evaluation_run)

print("Chunk Type Usage Analysis:")
for usage in analysis.chunk_type_usages:
    status = "OVER-USED" if usage.over_used else ("UNDER-USED" if usage.under_used else "Balanced")
    print(f"  {usage.chunk_type}: {status}")
    print(f"    Expected: {usage.expected_count}, Actual: {usage.actual_count}")
    print(f"    Ratio: {usage.usage_ratio:.2f}")

print("\nRecommendations:")
for rec in analysis.recommendations:
    print(f"  - {rec}")
```

### 4. Find Retrieval-Answer Mismatches

```python
from evaluation.analysis import find_retrieval_answer_mismatches

# Find tests with high retrieval but low answer quality
mismatch_report = find_retrieval_answer_mismatches(
    evaluation_run,
    min_retrieval_threshold=0.7,  # MRR/coverage threshold
    max_answer_threshold=3  # Max confidence score
)

print(f"Found {mismatch_report.mismatch_count} mismatches out of {mismatch_report.total_tests} tests")
print(f"Average mismatch score: {mismatch_report.avg_mismatch_score:.3f}")

# Print top mismatches
for mismatch in mismatch_report.mismatches[:5]:
    print(f"\nTest: {mismatch.test_id}")
    print(f"  Question: {mismatch.question[:80]}...")
    print(f"  Retrieval MRR: {mismatch.retrieval_mrr:.3f}")
    print(f"  Retrieval Coverage: {mismatch.retrieval_concept_coverage:.3f}")
    print(f"  Answer Confidence: {mismatch.answer_confidence_score}/5")
    print(f"  Mismatch Score: {mismatch.mismatch_score:.3f}")
    print(f"  Missed Concepts: {len(mismatch.answer_missed_concepts)}")
```

### 5. Compare Two Evaluation Runs (Regression Detection)

```python
from evaluation.analysis import compare_evaluation_runs, load_evaluation_run

# Load baseline and current runs
baseline_run = load_evaluation_run(Path("evaluation/runs/run_20250123_143022.json"))
current_run = load_evaluation_run(Path("evaluation/runs/run_20250124_100000.json"))

# Compare for regressions
regression_report = compare_evaluation_runs(baseline_run, current_run)

print(f"Comparison: {regression_report.baseline_run_id} vs {regression_report.current_run_id}")
print(f"\n{regression_report.overall_assessment}")
print(f"\nRegressions: {regression_report.regression_count}")
print(f"Improvements: {regression_report.improvement_count}")
print(f"Stable: {regression_report.stable_count}")

# Print metric changes
print("\nMetric Changes:")
for metric in regression_report.metric_changes:
    change_symbol = "📉" if metric.is_regression else ("📈" if metric.is_improvement else "➡️")
    print(f"{change_symbol} {metric.metric_name}:")
    print(f"  Baseline: {metric.baseline_value:.3f}")
    print(f"  Current: {metric.current_value:.3f}")
    print(f"  Change: {metric.absolute_change:+.3f} ({metric.relative_change:+.1f}%)")

# Print requirement changes
if regression_report.requirement_changes:
    print("\nRequirement Changes:")
    for req_id, change in list(regression_report.requirement_changes.items())[:5]:
        change_symbol = "📉" if change.is_regression else ("📈" if change.is_improvement else "➡️")
        print(f"{change_symbol} Requirement {req_id}:")
        print(f"  Weakness Score Change: {change.absolute_change:+.3f} ({change.relative_change:+.1f}%)")
```

### 6. Generate Complete Analysis Summary

```python
from evaluation.analysis import generate_analysis_summary
from pathlib import Path

# Generate comprehensive summary
summary = generate_analysis_summary(
    evaluation_run,
    output_file=Path("evaluation/analysis_summaries/summary_run_20250123_143022.md")
)

print(summary)
```

## Complete Workflow Example

```python
"""
Complete workflow: Run evaluation, then analyze results.
"""

from pathlib import Path
from evaluation.rag_evaluator import RAGEvaluator
from evaluation.analysis import (
    load_evaluation_run,
    rank_weakest_requirements,
    analyze_chunk_type_usage,
    find_retrieval_answer_mismatches,
    generate_analysis_summary
)

# Step 1: Run evaluation (if not already done)
vector_db_dir = Path("data/vector_db")
evaluator = RAGEvaluator(
    vector_db_dir=vector_db_dir,
    retrieval_config={
        "top_k_original": 10,
        "top_k_rewritten": 10,
        "final_k": 10,
        "enable_query_rewrite": True
    },
    answer_config={"model": "openai/gpt-4o-mini", "temperature": 0},
    judge_config={"model": "openai/gpt-4o-mini", "temperature": 0}
)

# Run evaluation
run = evaluator.evaluate_test_set("core")
print(f"Evaluation complete: {run.run_id}")

# Step 2: Analyze results
run_file = Path(f"evaluation/runs/{run.run_id}.json")
evaluation_run = load_evaluation_run(run_file)

# Analyze weakest requirements
ranking = rank_weakest_requirements(evaluation_run)
print(f"\nTop 3 weakest requirements:")
for weakness in ranking.weakest_requirements[:3]:
    print(f"  - {weakness.requirement_id}: {weakness.weakness_score:.3f}")

# Analyze chunk type usage
chunk_analysis = analyze_chunk_type_usage(evaluation_run)
print(f"\nChunk type issues:")
for usage in chunk_analysis.chunk_type_usages:
    if usage.over_used or usage.under_used:
        print(f"  - {usage.chunk_type}: {'OVER' if usage.over_used else 'UNDER'}-used")

# Find mismatches
mismatches = find_retrieval_answer_mismatches(evaluation_run)
print(f"\nRetrieval-answer mismatches: {mismatches.mismatch_count}")

# Generate summary
summary_file = Path(f"evaluation/analysis_summaries/summary_{run.run_id}.md")
generate_analysis_summary(evaluation_run, output_file=summary_file)
print(f"\nSummary saved to: {summary_file}")
```

## Interpreting Results

### Weakness Score
- **Range**: 0.0 (perfect) to 1.0 (worst)
- **Components**: Concept coverage, retrieval MRR, answer confidence
- **Action**: Lower scores indicate areas needing improvement in knowledge base or retrieval

### Chunk Type Usage Ratio
- **Ratio > 1.2**: Over-used (retrieved more than expected)
- **Ratio < 0.8**: Under-used (retrieved less than expected)
- **Action**: Balance indicates good coverage; imbalances suggest knowledge base gaps

### Mismatch Score
- **High score**: Large gap between retrieval quality and answer quality
- **Indicates**: Potential issues in answer generation or evaluation, not retrieval
- **Action**: Review answer generation prompts or evaluation criteria

### Regression Detection
- **Regression**: Metric got worse (threshold: >1% change)
- **Improvement**: Metric got better (threshold: >1% change)
- **Action**: Investigate regressions to identify what changed
