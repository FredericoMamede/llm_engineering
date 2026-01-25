"""
RAG Evaluation Orchestrator.

This module coordinates retrieval, answer generation, and evaluation for RAG quality assessment.
It is orchestration-only: no metric calculation, no test case definitions, no UI logic.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from core.retriever import KnowledgeRetriever, RetrievalResult
from core.answer_generator import AnswerGenerator, GeneratedAnswer
from evaluation.judge import AnswerJudge

from evaluation.data_contracts import (
    TestCase, RetrievalMetrics, AnswerEvaluation, AnswerMetrics, EvaluationRun
)
from evaluation.metrics import (
    calculate_concept_mrr,
    calculate_ndcg_at_k,
    calculate_recall_at_k,
    calculate_concept_coverage,
    calculate_chunk_type_distribution,
    calculate_chunk_type_coverage,
    aggregate_retrieval_metrics,
    aggregate_answer_metrics
)
from evaluation.test_sets import get_test_set

# Setup logging
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """
    Orchestrates RAG evaluation runs.
    
    Responsibilities:
    1. Load test cases from test_sets.py
    2. For each test case: retrieve, generate, evaluate, compute metrics
    3. Aggregate results into EvaluationRun
    4. Persist EvaluationRun to runs/ directory
    
    Does NOT:
    - Calculate metrics (delegates to metrics.py)
    - Define test cases (uses test_sets.py)
    - Provide UI (offline evaluation only)
    """
    
    def __init__(
        self,
        vector_db_dir: Path,
        retrieval_config: Dict[str, Any],
        answer_config: Dict[str, Any],
        judge_config: Dict[str, Any],
        runs_dir: Optional[Path] = None
    ):
        """
        Initialize RAG evaluator.
        
        Args:
            vector_db_dir: Path to vector database directory
            retrieval_config: Configuration for KnowledgeRetriever
                - top_k_original: int
                - top_k_rewritten: int
                - final_k: int
                - enable_query_rewrite: bool
            answer_config: Configuration for AnswerGenerator
                - model: str
                - temperature: float
            judge_config: Configuration for AnswerJudge
                - model: str
                - temperature: float
            runs_dir: Path to directory for persisting evaluation runs (default: evaluation/runs/)
        """
        # Initialize existing components (reusing without modification)
        self.retriever = KnowledgeRetriever(
            vector_db_dir=vector_db_dir,
            backend="local",
            enable_query_rewrite=retrieval_config.get("enable_query_rewrite", True),
            top_k_original=retrieval_config.get("top_k_original", 10),
            top_k_rewritten=retrieval_config.get("top_k_rewritten", 10),
            final_k=retrieval_config.get("final_k", 10)
        )
        
        self.answer_generator = AnswerGenerator(
            model=answer_config.get("model", "openai/gpt-4o-mini"),
            temperature=answer_config.get("temperature", 0)
        )
        
        self.judge = AnswerJudge(
            model=judge_config.get("model", "openai/gpt-4o-mini"),
            temperature=judge_config.get("temperature", 0)
        )
        
        # Store configuration for reproducibility
        self.retrieval_config = retrieval_config
        self.answer_config = answer_config
        self.judge_config = judge_config
        
        # Setup runs directory
        if runs_dir is None:
            runs_dir = Path(__file__).parent / "runs"
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(exist_ok=True)
        
        logger.info(f"RAGEvaluator initialized with runs_dir={self.runs_dir}")
    
    def evaluate_test_set(self, test_set_name: str) -> EvaluationRun:
        """
        Evaluate a complete test set.
        
        Args:
            test_set_name: Name of test set to evaluate (e.g., "core", "system_design")
        
        Returns:
            EvaluationRun object with complete results
        
        Process:
            1. Load test cases from test_set_name
            2. For each test case: retrieve, generate, evaluate, compute metrics
            3. Aggregate results
            4. Create EvaluationRun snapshot
            5. Persist to runs/ directory
        """
        logger.info(f"Starting evaluation of test set: {test_set_name}")
        
        # 1. Load test cases
        test_cases = get_test_set(test_set_name)
        logger.info(f"Loaded {len(test_cases)} test cases")
        
        # 2. Evaluate each test case
        retrieval_metrics_list = []
        answer_evaluations = []
        
        for idx, test_case in enumerate(test_cases, start=1):
            logger.info(f"Evaluating test case {idx}/{len(test_cases)}: {test_case.test_id}")
            
            try:
                retrieval_metrics, answer_eval = self._evaluate_single_test_case(test_case)
                retrieval_metrics_list.append(retrieval_metrics)
                answer_evaluations.append(answer_eval)
                logger.info(f"✓ Completed test case {test_case.test_id}")
            except Exception as e:
                logger.error(f"✗ Error evaluating test case {test_case.test_id}: {e}", exc_info=True)
                # Create error metrics to continue evaluation
                retrieval_metrics = self._create_error_retrieval_metrics(test_case.test_id)
                answer_eval = self._create_error_answer_evaluation(test_case)
                retrieval_metrics_list.append(retrieval_metrics)
                answer_evaluations.append(answer_eval)
        
        # 3. Aggregate results
        logger.info("Aggregating results...")
        answer_metrics = aggregate_answer_metrics(answer_evaluations)
        
        # Calculate summary statistics
        if retrieval_metrics_list:
            avg_concept_mrr = sum(m.mrr for m in retrieval_metrics_list) / len(retrieval_metrics_list)
            avg_ndcg_at_10 = sum(m.ndcg_at_k.get(10, 0.0) for m in retrieval_metrics_list) / len(retrieval_metrics_list)
            avg_recall_at_10 = sum(m.recall_at_k.get(10, 0.0) for m in retrieval_metrics_list) / len(retrieval_metrics_list)
            avg_concept_coverage = sum(m.concept_coverage for m in retrieval_metrics_list) / len(retrieval_metrics_list)
        else:
            avg_concept_mrr = 0.0
            avg_ndcg_at_10 = 0.0
            avg_recall_at_10 = 0.0
            avg_concept_coverage = 0.0
        
        avg_confidence_score = answer_metrics.avg_confidence_score
        
        # 4. Create EvaluationRun
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        run = EvaluationRun(
            run_id=run_id,
            timestamp=timestamp,
            test_set_name=test_set_name,
            retrieval_config=self.retrieval_config.copy(),
            answer_generation_config=self.answer_config.copy(),
            judge_config=self.judge_config.copy(),
            test_cases=test_cases,
            retrieval_metrics=retrieval_metrics_list,
            answer_metrics=answer_metrics,
            total_test_cases=len(test_cases),
            avg_concept_mrr=avg_concept_mrr,
            avg_ndcg_at_10=avg_ndcg_at_10,
            avg_recall_at_10=avg_recall_at_10,
            avg_concept_coverage=avg_concept_coverage,
            avg_confidence_score=avg_confidence_score
        )
        
        # 5. Persist
        filepath = self._persist_run(run)
        logger.info(f"Evaluation complete. Results saved to: {filepath}")
        logger.info(f"Summary: MRR={avg_concept_mrr:.3f}, nDCG@10={avg_ndcg_at_10:.3f}, "
                   f"Recall@10={avg_recall_at_10:.3f}, Coverage={avg_concept_coverage:.3f}, "
                   f"Confidence={avg_confidence_score:.2f}")
        
        return run
    
    def _evaluate_single_test_case(
        self,
        test_case: TestCase
    ) -> Tuple[RetrievalMetrics, AnswerEvaluation]:
        """
        Evaluate a single test case.
        
        Orchestrates: retrieval -> answer generation -> evaluation -> metrics calculation.
        
        Args:
            test_case: TestCase to evaluate
        
        Returns:
            Tuple of (RetrievalMetrics, AnswerEvaluation)
        """
        # 1. Retrieve
        filter_dict = self._build_filter_dict(test_case)
        retrieval_result = self.retriever.retrieve(
            query=test_case.question,
            filter_dict=filter_dict if filter_dict else None,
            debug=False
        )
        
        # 2. Generate answer
        generated_answer = self.answer_generator.generate(retrieval_result)
        
        # 3. Evaluate answer
        answer_eval = self._evaluate_answer(
            test_case=test_case,
            retrieval_result=retrieval_result,
            generated_answer=generated_answer
        )
        
        # 4. Calculate retrieval metrics
        retrieval_metrics = self._calculate_retrieval_metrics(
            test_case=test_case,
            retrieval_result=retrieval_result
        )
        
        return retrieval_metrics, answer_eval
    
    def _build_filter_dict(self, test_case: TestCase) -> Dict[str, Any]:
        """
        Build filter dictionary for retrieval based on test case expectations.
        
        Args:
            test_case: TestCase with expected requirement_ids, company_domains, etc.
        
        Returns:
            Filter dictionary for KnowledgeRetriever.retrieve()
        """
        filter_dict = {}
        
        if test_case.expected_requirement_ids:
            # KnowledgeRetriever expects requirement_id as a single value or list
            if len(test_case.expected_requirement_ids) == 1:
                filter_dict["requirement_id"] = test_case.expected_requirement_ids[0]
            else:
                # For multiple requirement IDs, we'd need to check how retriever handles this
                # For now, use the first one
                filter_dict["requirement_id"] = test_case.expected_requirement_ids[0]
        
        if test_case.expected_company_domains:
            if len(test_case.expected_company_domains) == 1:
                filter_dict["company_domain"] = test_case.expected_company_domains[0]
            else:
                filter_dict["company_domain"] = test_case.expected_company_domains[0]
        
        return filter_dict
    
    def _evaluate_answer(
        self,
        test_case: TestCase,
        retrieval_result: RetrievalResult,
        generated_answer: GeneratedAnswer
    ) -> AnswerEvaluation:
        """
        Evaluate a generated answer using AnswerJudge.
        
        Wraps AnswerJudge.evaluate() and converts to AnswerEvaluation.
        
        Args:
            test_case: Original test case
            retrieval_result: Retrieved chunks used for answer generation
            generated_answer: Generated answer to evaluate
        
        Returns:
            AnswerEvaluation object
        """
        # Call existing judge (no modifications)
        feedback = self.judge.evaluate(
            question=test_case.question,
            candidate_answer=generated_answer.answer_text,
            retrieval_result=retrieval_result,
            reference_answer=generated_answer  # Optional context
        )
        
        # Wrap in AnswerEvaluation with metadata
        return AnswerEvaluation(
            strengths=feedback.strengths,
            gaps=feedback.gaps,
            missed_concepts=feedback.missed_concepts,
            followup_questions=feedback.followup_questions,
            overall_assessment=feedback.overall_assessment,
            confidence_score=feedback.confidence_score,
            test_id=test_case.test_id,
            question=test_case.question,
            generated_answer=generated_answer.answer_text,
            num_retrieved_chunks=len(retrieval_result.retrieved_chunks),
            evaluation_timestamp=datetime.now().isoformat(),
            reference_answer_text=generated_answer.answer_text
        )
    
    def _calculate_retrieval_metrics(
        self,
        test_case: TestCase,
        retrieval_result: RetrievalResult
    ) -> RetrievalMetrics:
        """
        Calculate retrieval metrics for a test case.
        
        Delegates to metrics.py functions.
        
        Args:
            test_case: Test case with expected concepts
            retrieval_result: Retrieved chunks and metadata
        
        Returns:
            RetrievalMetrics object
        """
        # Calculate ranking metrics
        mrr = calculate_concept_mrr(
            expected_concepts=test_case.expected_concepts,
            retrieved_chunks=retrieval_result.retrieved_chunks
        )
        
        ndcg_at_k = {
            5: calculate_ndcg_at_k(test_case.expected_concepts, retrieval_result.retrieved_chunks, 5),
            10: calculate_ndcg_at_k(test_case.expected_concepts, retrieval_result.retrieved_chunks, 10),
            20: calculate_ndcg_at_k(test_case.expected_concepts, retrieval_result.retrieved_chunks, 20)
        }
        
        recall_at_k = {
            5: calculate_recall_at_k(test_case.expected_concepts, retrieval_result.retrieved_chunks, 5),
            10: calculate_recall_at_k(test_case.expected_concepts, retrieval_result.retrieved_chunks, 10),
            20: calculate_recall_at_k(test_case.expected_concepts, retrieval_result.retrieved_chunks, 20)
        }
        
        # Calculate concept coverage
        concept_coverage, concepts_found, concepts_missed = calculate_concept_coverage(
            expected_concepts=test_case.expected_concepts,
            retrieved_chunks=retrieval_result.retrieved_chunks
        )
        
        # Calculate chunk-type distribution
        chunk_type_distribution = calculate_chunk_type_distribution(
            retrieval_result.retrieved_chunks
        )
        
        chunk_type_coverage = {}
        if test_case.expected_chunk_types:
            chunk_type_coverage = calculate_chunk_type_coverage(
                expected_chunk_types=test_case.expected_chunk_types,
                retrieved_chunks=retrieval_result.retrieved_chunks
            )
        
        # Extract query rewriting stats
        original_count = retrieval_result.retrieval_metadata.get("total_candidates", 0) // 2  # Approximate
        rewritten_count = retrieval_result.retrieval_metadata.get("total_candidates", 0) // 2  # Approximate
        merged_count = len(retrieval_result.retrieved_chunks)
        
        # Calculate similarity stats
        if retrieval_result.retrieved_chunks:
            similarity_scores = [chunk.similarity_score for chunk in retrieval_result.retrieved_chunks]
            top_score = max(similarity_scores)
            avg_score = sum(similarity_scores) / len(similarity_scores)
        else:
            top_score = 0.0
            avg_score = 0.0
        
        return RetrievalMetrics(
            test_id=test_case.test_id,
            mrr=mrr,
            ndcg_at_k=ndcg_at_k,
            recall_at_k=recall_at_k,
            concept_coverage=concept_coverage,
            concepts_found=concepts_found,
            concepts_missed=concepts_missed,
            chunk_type_distribution=chunk_type_distribution,
            chunk_type_coverage=chunk_type_coverage,
            original_query_results_count=original_count,
            rewritten_query_results_count=rewritten_count,
            final_merged_count=merged_count,
            total_chunks_retrieved=len(retrieval_result.retrieved_chunks),
            top_similarity_score=top_score,
            avg_similarity_score=avg_score
        )
    
    def _create_error_retrieval_metrics(self, test_id: str) -> RetrievalMetrics:
        """Create error RetrievalMetrics when evaluation fails."""
        return RetrievalMetrics(
            test_id=test_id,
            mrr=0.0,
            ndcg_at_k={5: 0.0, 10: 0.0, 20: 0.0},
            recall_at_k={5: 0.0, 10: 0.0, 20: 0.0},
            concept_coverage=0.0,
            concepts_found=[],
            concepts_missed=[],
            chunk_type_distribution={},
            chunk_type_coverage={},
            original_query_results_count=0,
            rewritten_query_results_count=0,
            final_merged_count=0,
            total_chunks_retrieved=0,
            top_similarity_score=0.0,
            avg_similarity_score=0.0
        )
    
    def _create_error_answer_evaluation(self, test_case: TestCase) -> AnswerEvaluation:
        """Create error AnswerEvaluation when evaluation fails."""
        return AnswerEvaluation(
            strengths=[],
            gaps=["Evaluation failed due to error"],
            missed_concepts=[],
            followup_questions=[],
            overall_assessment="Evaluation failed - see error logs",
            confidence_score=1,
            test_id=test_case.test_id,
            question=test_case.question,
            generated_answer="",
            num_retrieved_chunks=0,
            evaluation_timestamp=datetime.now().isoformat(),
            reference_answer_text=None
        )
    
    def _persist_run(self, run: EvaluationRun) -> Path:
        """
        Persist evaluation run to JSON file.
        
        Args:
            run: EvaluationRun to persist
        
        Returns:
            Path to persisted file
        """
        filepath = self.runs_dir / f"{run.run_id}.json"
        run.to_json(str(filepath))
        return filepath
