"""
Offline RAG Evaluation Runner

This script executes RAG evaluations and generates EvaluationRun artifacts that can be
visualized in the RAG Evaluation Dashboard (UI).

Why Offline?
-----------
RAG evaluations are computationally expensive (multiple LLM calls per test case) and
should be run intentionally, not automatically. This separation ensures:

1. **Explicit Control**: Evaluations run only when explicitly requested
2. **Reproducibility**: Each run is a complete, immutable snapshot
3. **Resource Management**: Avoids accidental API costs or performance impact
4. **Auditability**: Clear separation between evaluation execution and visualization

Workflow:
---------
1. Run this script to execute evaluation: `python evaluation/run_evaluation.py`
2. EvaluationRun JSON artifact is saved to `evaluation/runs/`
3. Open the UI and navigate to "RAG Evaluation" tab
4. Select the run from the dropdown to view metrics and analysis

The UI is read-only and only displays existing evaluation runs. It does not execute
evaluations or modify evaluation logic.

Usage:
------
    python evaluation/run_evaluation.py

The script will:
- Load test cases from the configured test set
- For each test case: retrieve, generate answer, evaluate, compute metrics
- Aggregate results into an EvaluationRun
- Persist to evaluation/runs/run_YYYYMMDD_HHMMSS.json
- Print summary metrics to stdout
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from evaluation.rag_evaluator import RAGEvaluator

# ============================================================================
# Configuration
# ============================================================================

# Test set to evaluate (options: "core", "system_design", "tradeoff", "all")
TEST_SET_NAME = "core"

# Vector database directory
VECTOR_DB_DIR = project_root / "data" / "vector_db"

# Retrieval configuration
RETRIEVAL_CONFIG = {
    "top_k_original": 10,      # Number of chunks from original query
    "top_k_rewritten": 10,      # Number of chunks from rewritten query
    "final_k": 10,              # Final number of chunks after deduplication
    "enable_query_rewrite": True  # Whether to use query rewriting
}

# Answer generation configuration
ANSWER_CONFIG = {
    "model": "openai/gpt-4o-mini",
    "temperature": 0  # Deterministic output
}

# Judge (evaluation) configuration
JUDGE_CONFIG = {
    "model": "openai/gpt-4o-mini",
    "temperature": 0  # Deterministic evaluation
}

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    Execute RAG evaluation and generate EvaluationRun artifact.
    
    This function:
    1. Initializes RAGEvaluator with configured settings
    2. Runs evaluation on the specified test set
    3. Persists results to evaluation/runs/
    4. Prints summary metrics
    """
    # Setup logging for progress visibility
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("RAG Evaluation Runner")
    logger.info("=" * 70)
    logger.info(f"Test Set: {TEST_SET_NAME}")
    logger.info(f"Vector DB: {VECTOR_DB_DIR}")
    logger.info(f"Retrieval Config: {RETRIEVAL_CONFIG}")
    logger.info(f"Answer Config: {ANSWER_CONFIG}")
    logger.info(f"Judge Config: {JUDGE_CONFIG}")
    logger.info("")
    
    # Validate vector DB exists
    if not VECTOR_DB_DIR.exists():
        logger.error(f"Vector database directory not found: {VECTOR_DB_DIR}")
        logger.error("Please run data ingestion first to create the vector database.")
        sys.exit(1)
    
    # Initialize evaluator
    logger.info("Initializing RAGEvaluator...")
    evaluator = RAGEvaluator(
        vector_db_dir=VECTOR_DB_DIR,
        retrieval_config=RETRIEVAL_CONFIG,
        answer_config=ANSWER_CONFIG,
        judge_config=JUDGE_CONFIG
    )
    
    # Run evaluation
    logger.info(f"Starting evaluation of test set: {TEST_SET_NAME}")
    logger.info("This may take several minutes depending on the number of test cases...")
    logger.info("")
    
    try:
        run = evaluator.evaluate_test_set(TEST_SET_NAME)
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        logger.exception("Full error details:")
        sys.exit(1)
    
    # Print summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("Evaluation Complete")
    logger.info("=" * 70)
    logger.info(f"Run ID: {run.run_id}")
    logger.info(f"Timestamp: {run.timestamp}")
    logger.info(f"Test Set: {run.test_set_name}")
    logger.info(f"Total Test Cases: {run.total_test_cases}")
    logger.info("")
    logger.info("Summary Metrics:")
    logger.info(f"  Average Concept MRR:        {run.avg_concept_mrr:.3f}")
    logger.info(f"  Average nDCG@10:            {run.avg_ndcg_at_10:.3f}")
    logger.info(f"  Average Recall@10:          {run.avg_recall_at_10:.3f}")
    logger.info(f"  Average Concept Coverage:   {run.avg_concept_coverage:.3f}")
    logger.info(f"  Average Answer Confidence:  {run.avg_confidence_score:.2f}/5")
    logger.info("")
    logger.info(f"Results saved to: evaluation/runs/{run.run_id}.json")
    logger.info("")
    logger.info("Next Steps:")
    logger.info("  1. Open the UI: python ui/app.py")
    logger.info("  2. Navigate to 'RAG Evaluation' tab")
    logger.info(f"  3. Select run '{run.run_id}' from the dropdown")
    logger.info("  4. Click 'Load Run' to view detailed analysis")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
