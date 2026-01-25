# RAG Evaluation & Quality Layer - Design Document

> **Status**: Design Phase (Not Implemented)  
> **Purpose**: Internal, offline evaluation harness for measuring RAG retrieval and answer quality  
> **Constraint**: No ground truth answers, no UI, no auto-optimization, no coupling to Interview Simulator

---

## 1. Folder Structure

```
evaluation/
├── __init__.py
├── judge.py                    # Existing: AnswerJudge (reused, not modified)
│
├── rag_evaluator.py            # NEW: Orchestration layer
├── metrics.py                  # NEW: Pure metric calculation functions
├── test_sets.py                # NEW: Curated test case definitions
├── data_contracts.py           # NEW: Dataclass definitions
│
└── runs/                       # NEW: Persisted evaluation artifacts
    ├── run_20250123_143022.json
    ├── run_20250123_143022_retrieval_metrics.json
    └── run_20250123_143022_answer_metrics.json
```

**Design Principles:**
- `rag_evaluator.py`: Orchestration only - coordinates retrieval, answer generation, and evaluation
- `metrics.py`: Pure functions - deterministic, no side effects, no LLM calls
- `test_sets.py`: Static test case definitions - concept-based expectations, not answers
- `data_contracts.py`: Immutable dataclasses - all evaluation data structures
- `runs/`: Immutable snapshots - each run is a complete, reproducible evaluation

---

## 2. Data Contracts

### 2.1 TestCase

**Purpose**: Represents a single test question with concept-based expectations (not ground truth answers).

```python
@dataclass(frozen=True)
class TestCase:
    """A single test case for RAG evaluation."""
    
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
```

**Key Design Decisions:**
- **No `expected_answer` field**: We don't generate ground truth answers
- **Concept-based expectations**: We validate that relevant concepts are retrieved, not that a specific answer is generated
- **Frozen dataclass**: Immutable to prevent accidental modification
- **Optional filters**: Allow test cases to specify requirement/domain/chunk-type expectations

---

### 2.2 RetrievedChunk (Reused)

**Purpose**: Already defined in `core/retriever.py`. We reuse this structure.

**Key Fields for Evaluation:**
- `chunk_id`: For tracking which chunks were retrieved
- `chunk_type`: For chunk-type distribution analysis
- `similarity_score`: For ranking-based metrics (MRR, nDCG)
- `retrieval_path`: For analyzing original vs rewritten query performance
- `inherited_metadata.requirement_id`: For concept coverage analysis
- `inherited_metadata.company_domain`: For domain-specific coverage

**No modifications needed** - we use the existing structure as-is.

---

### 2.3 AnswerEvaluation

**Purpose**: Wraps existing `EvaluationFeedback` from `AnswerJudge` with additional metadata.

```python
@dataclass(frozen=True)
class AnswerEvaluation:
    """Evaluation of a generated answer, wrapping AnswerJudge output."""
    
    # Reused from EvaluationFeedback (from judge.py)
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
```

**Key Design Decisions:**
- **Wraps, doesn't replace**: We reuse `EvaluationFeedback` from `AnswerJudge` without modification
- **Immutable**: Frozen dataclass ensures evaluation results are snapshots
- **No ground truth comparison**: `reference_answer_text` is optional and for context only

---

### 2.4 RetrievalMetrics

**Purpose**: Aggregated metrics for a single test case's retrieval performance.

```python
@dataclass(frozen=True)
class RetrievalMetrics:
    """Retrieval quality metrics for a single test case."""
    
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
```

**Key Design Decisions:**
- **Multiple K values**: nDCG and Recall calculated at multiple K values (5, 10, 20) for flexibility
- **Concept-based validation**: Measures coverage of expected concepts, not exact matches
- **Query rewriting analysis**: Tracks contribution of original vs rewritten queries
- **Chunk-type awareness**: Analyzes distribution and coverage of chunk types

---

### 2.5 AnswerMetrics

**Purpose**: Aggregated metrics for answer quality across multiple test cases.

```python
@dataclass(frozen=True)
class AnswerMetrics:
    """Answer quality metrics aggregated across test cases."""
    
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
```

**Key Design Decisions:**
- **Aggregation layer**: Combines individual `AnswerEvaluation` results
- **Category breakdown**: Optional recursive structure for per-category analysis
- **No ground truth comparison**: Metrics are based on judge evaluation, not answer matching

---

### 2.6 EvaluationRun

**Purpose**: Immutable snapshot of a complete evaluation run.

```python
@dataclass(frozen=True)
class EvaluationRun:
    """Complete, immutable snapshot of an evaluation run."""
    
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
    avg_mrr: float
    avg_ndcg_at_10: float
    avg_recall_at_10: float
    avg_concept_coverage: float
    avg_confidence_score: float
    
    # Metadata
    vector_db_version: Optional[str] = None  # If versioning is tracked
    notes: Optional[str] = None  # Human notes about this run
```

**Key Design Decisions:**
- **Immutable snapshot**: Frozen dataclass ensures run cannot be modified after creation
- **Complete configuration**: Stores all configs used, enabling reproducibility
- **Summary statistics**: Pre-computed aggregates for quick analysis
- **Version tracking**: Optional vector DB version for tracking knowledge base changes

---

## 3. Component Responsibilities

### 3.1 rag_evaluator.py

**Purpose**: Orchestration layer that coordinates retrieval, answer generation, and evaluation.

**Responsibilities:**
1. Load test cases from `test_sets.py`
2. For each test case:
   - Call `KnowledgeRetriever.retrieve()` with the test question
   - Call `AnswerGenerator.generate()` with the retrieval result
   - Call `AnswerJudge.evaluate()` with the generated answer
   - Compute retrieval metrics using `metrics.py`
3. Aggregate results into `EvaluationRun`
4. Persist `EvaluationRun` to `runs/` directory

**Key Design Decisions:**
- **Orchestration only**: No metric calculation, no test case definitions, no UI logic
- **Reuses existing components**: Uses `KnowledgeRetriever`, `AnswerGenerator`, `AnswerJudge` without modification
- **No coupling to Interview Simulator**: Completely independent evaluation flow
- **Error handling**: Gracefully handles failures per test case, continues evaluation

**Pseudocode Structure:**
```python
class RAGEvaluator:
    def __init__(self, vector_db_dir, retrieval_config, answer_config, judge_config):
        # Initialize components (reusing existing classes)
        self.retriever = KnowledgeRetriever(...)
        self.answer_generator = AnswerGenerator(...)
        self.judge = AnswerJudge(...)
        self.metrics_calculator = MetricsCalculator()
    
    def evaluate_test_set(self, test_set_name: str) -> EvaluationRun:
        # Load test cases
        # For each test case: retrieve, generate, evaluate, compute metrics
        # Aggregate results
        # Return EvaluationRun
    
    def _evaluate_single_test_case(self, test_case: TestCase) -> Tuple[RetrievalMetrics, AnswerEvaluation]:
        # Orchestrate retrieval, generation, evaluation
        # Compute metrics
        # Return results
    
    def _persist_run(self, run: EvaluationRun) -> Path:
        # Save to runs/ directory as JSON
```

---

### 3.2 metrics.py

**Purpose**: Pure, deterministic functions for calculating retrieval and answer metrics.

**Responsibilities:**
1. Calculate MRR (Mean Reciprocal Rank)
2. Calculate nDCG@K for multiple K values
3. Calculate Recall@K for multiple K values
4. Calculate concept coverage
5. Calculate chunk-type distribution
6. Aggregate metrics across test cases

**Key Design Decisions:**
- **Pure functions**: No side effects, no LLM calls, no state
- **Deterministic**: Same inputs always produce same outputs
- **No external dependencies**: Only uses standard library and dataclasses
- **Multiple K values**: Calculates metrics at K=5, 10, 20 for flexibility

**Function Signatures (Conceptual):**
```python
def calculate_concept_mrr(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk]
) -> float:
    """
    Calculate Mean Reciprocal Rank.
    
    Inputs:
        - expected_concepts: List of concept names that should be found
        - retrieved_chunks: Ranked list of retrieved chunks
    
    Output:
        - MRR score (0.0 to 1.0)
    
    Logic (conceptual):
        - For each expected concept, find its rank in retrieved chunks
        - Reciprocal rank = 1 / rank (if found), 0 (if not found)
        - MRR = average of reciprocal ranks
    """

def calculate_ndcg_at_k(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk],
    k: int
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K.
    
    Inputs:
        - expected_concepts: List of concept names that should be found
        - retrieved_chunks: Ranked list of retrieved chunks
        - k: Cutoff rank
    
    Output:
        - nDCG@K score (0.0 to 1.0)
    
    Logic (conceptual):
        - Assign relevance scores to chunks based on concept matches
        - Calculate DCG@K (discounted cumulative gain)
        - Calculate ideal DCG@K (perfect ranking)
        - nDCG@K = DCG@K / ideal_DCG@K
    """

def calculate_recall_at_k(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk],
    k: int
) -> float:
    """
    Calculate Recall at K.
    
    Inputs:
        - expected_concepts: List of concept names that should be found
        - retrieved_chunks: Ranked list of retrieved chunks
        - k: Cutoff rank
    
    Output:
        - Recall@K score (0.0 to 1.0)
    
    Logic (conceptual):
        - Count how many expected concepts are found in top-K chunks
        - Recall@K = (concepts found in top-K) / (total expected concepts)
    """

def calculate_concept_coverage(
    expected_concepts: List[str],
    retrieved_chunks: List[RetrievedChunk]
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate concept coverage.
    
    Inputs:
        - expected_concepts: List of concept names that should be found
        - retrieved_chunks: List of retrieved chunks
    
    Output:
        - Tuple of (coverage_ratio, concepts_found, concepts_missed)
    
    Logic (conceptual):
        - Check which expected concepts appear in retrieved chunks (via metadata or text)
        - Coverage = (concepts found) / (total expected concepts)
    """

def calculate_chunk_type_distribution(
    retrieved_chunks: List[RetrievedChunk]
) -> Dict[str, int]:
    """
    Calculate distribution of chunk types.
    
    Inputs:
        - retrieved_chunks: List of retrieved chunks
    
    Output:
        - Dictionary mapping chunk_type -> count
    """
```

---

### 3.3 test_sets.py

**Purpose**: Curated test case definitions organized by category and difficulty.

**Responsibilities:**
1. Define test cases as `TestCase` dataclass instances
2. Organize test cases into test sets (e.g., "core_requirements", "system_design", "company_specific")
3. Provide functions to load test sets by name
4. Provide functions to filter test cases by category, difficulty, tags

**Key Design Decisions:**
- **Static definitions**: Test cases are hardcoded, not generated
- **Concept-based**: Each test case specifies expected concepts, not expected answers
- **Organized by use case**: Test sets for different evaluation scenarios
- **No LLM calls**: Test cases are manually curated, not generated

**Structure (Conceptual):**
```python
# Example test case definitions
CORE_TEST_CASES = [
    TestCase(
        test_id="test_001",
        question="How does TypeScript help with large-scale JavaScript development?",
        expected_concepts=[
            "static typing",
            "type safety",
            "compile-time error checking",
            "IDE support",
            "refactoring safety"
        ],
        expected_requirement_ids=["req_001"],  # If targeting specific requirement
        category="direct_fact",
        difficulty="medium",
        tags=["typescript", "javascript", "language_features"]
    ),
    # ... more test cases
]

SYSTEM_DESIGN_TEST_CASES = [
    TestCase(
        test_id="test_sd_001",
        question="How would you design a distributed rate limiting system?",
        expected_concepts=[
            "distributed systems",
            "rate limiting algorithms",
            "token bucket",
            "sliding window",
            "consistency guarantees",
            "scalability"
        ],
        expected_chunk_types=["primary", "tradeoff", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["distributed-systems", "rate-limiting"]
    ),
    # ... more test cases
]

def get_test_set(name: str) -> List[TestCase]:
    """Load a test set by name."""
    test_sets = {
        "core": CORE_TEST_CASES,
        "system_design": SYSTEM_DESIGN_TEST_CASES,
        # ... more test sets
    }
    return test_sets.get(name, [])

def filter_test_cases(
    test_cases: List[TestCase],
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[TestCase]:
    """Filter test cases by criteria."""
    # Filtering logic
```

---

## 4. Retrieval Metric Definitions (Conceptual)

### 4.1 MRR (Mean Reciprocal Rank)

**Purpose**: Measure how highly ranked the first relevant chunk is.

**Inputs:**
- `expected_concepts`: List of concept names that should appear in retrieved chunks
- `retrieved_chunks`: Ranked list of `RetrievedChunk` objects (sorted by similarity_score)

**Output:**
- `mrr`: Float between 0.0 and 1.0

**Conceptual Logic:**
1. For each expected concept, search through `retrieved_chunks` in order
2. Find the rank (1-indexed) of the first chunk that contains/relates to that concept
3. Reciprocal rank = 1 / rank (if found), 0 (if not found)
4. MRR = average of all reciprocal ranks

**Example:**
- Expected concepts: ["static typing", "type safety"]
- Retrieved chunks: [chunk_about_typescript, chunk_about_react, chunk_about_typescript_types]
- If "static typing" appears in rank 1: reciprocal = 1/1 = 1.0
- If "type safety" appears in rank 3: reciprocal = 1/3 = 0.33
- MRR = (1.0 + 0.33) / 2 = 0.665

---

### 4.2 nDCG@K (Normalized Discounted Cumulative Gain at K)

**Purpose**: Measure ranking quality considering both relevance and position.

**Inputs:**
- `expected_concepts`: List of concept names that should appear
- `retrieved_chunks`: Ranked list of `RetrievedChunk` objects
- `k`: Cutoff rank (e.g., 5, 10, 20)

**Output:**
- `ndcg_at_k`: Float between 0.0 and 1.0

**Conceptual Logic:**
1. Assign relevance scores to each chunk based on how many expected concepts it matches
2. Calculate DCG@K: Sum of (relevance_score / log2(rank + 1)) for top-K chunks
3. Calculate ideal DCG@K: DCG@K if chunks were perfectly ranked (highest relevance first)
4. nDCG@K = DCG@K / ideal_DCG@K

**Key Insight:**
- Higher relevance chunks should be ranked higher
- Position matters: relevant chunks at rank 1 are more valuable than at rank 10
- Normalized to 0-1 scale for comparison across different test cases

---

### 4.3 Recall@K

**Purpose**: Measure how many expected concepts are found in the top-K retrieved chunks.

**Inputs:**
- `expected_concepts`: List of concept names that should appear
- `retrieved_chunks`: Ranked list of `RetrievedChunk` objects
- `k`: Cutoff rank (e.g., 5, 10, 20)

**Output:**
- `recall_at_k`: Float between 0.0 and 1.0

**Conceptual Logic:**
1. Consider only the top-K chunks from `retrieved_chunks`
2. Check which expected concepts appear in those top-K chunks (via metadata or text matching)
3. Recall@K = (number of expected concepts found in top-K) / (total expected concepts)

**Example:**
- Expected concepts: ["static typing", "type safety", "compile-time errors"]
- Top-5 chunks contain: "static typing", "type safety"
- Recall@5 = 2 / 3 = 0.67

---

### 4.4 Chunk-Type Distribution

**Purpose**: Analyze the diversity and balance of chunk types in retrieved results.

**Inputs:**
- `retrieved_chunks`: List of `RetrievedChunk` objects

**Output:**
- `chunk_type_distribution`: Dictionary mapping chunk_type -> count
- `chunk_type_coverage`: Dictionary mapping expected_chunk_type -> coverage ratio (if expected_chunk_types specified)

**Conceptual Logic:**
1. Count occurrences of each `chunk_type` in `retrieved_chunks`
2. If `expected_chunk_types` is specified in test case, calculate coverage:
   - Coverage = (number of expected types found) / (total expected types)

**Example:**
- Retrieved chunks: 5 "primary", 3 "tradeoff", 2 "failure_mode"
- Distribution: {"primary": 5, "tradeoff": 3, "failure_mode": 2}
- If expected: ["primary", "tradeoff"], coverage = 2/2 = 1.0

---

## 5. Concept Coverage Measurement

**Purpose**: Validate that retrieved chunks cover the expected concepts from the test case.

**Approach:**
1. **Metadata-based matching**: Check if `requirement_id` or `company_domain` in chunk metadata matches expected values from test case
2. **Text-based matching**: Search for concept names (normalized, case-insensitive) in chunk text fields (`headline`, `summary`, `original_text`)
3. **Fuzzy matching** (optional): Use string similarity (e.g., Levenshtein distance) for concept name variations

**Implementation Strategy:**
```python
def check_concept_in_chunk(concept: str, chunk: RetrievedChunk) -> bool:
    """
    Check if a concept appears in a chunk.
    
    Strategies (in order):
    1. Exact match in chunk.headline, chunk.summary, or chunk.original_text
    2. Case-insensitive match
    3. Word-boundary match (concept as whole word)
    4. Optional: Fuzzy matching for variations
    """
```

**Coverage Calculation:**
- For each expected concept, check if it appears in any retrieved chunk
- Coverage ratio = (concepts found) / (total expected concepts)
- Track which concepts were found and which were missed

**Key Design Decisions:**
- **Multiple matching strategies**: Metadata first, then text matching
- **Normalization**: Case-insensitive, handle variations
- **Per-chunk analysis**: Track which chunks contain which concepts for debugging

---

## 6. Answer Quality Evaluation (Reusing AnswerJudge)

**Purpose**: Evaluate generated answers using the existing `AnswerJudge` without modification.

**Approach:**
1. **Reuse existing component**: Call `AnswerJudge.evaluate()` exactly as it's used in production
2. **No modifications**: Use `AnswerJudge` as-is, with its existing prompt and evaluation logic
3. **Wrap results**: Convert `EvaluationFeedback` to `AnswerEvaluation` by adding metadata

**Flow:**
```python
# In rag_evaluator.py
def _evaluate_answer(
    self,
    test_case: TestCase,
    retrieval_result: RetrievalResult,
    generated_answer: GeneratedAnswer
) -> AnswerEvaluation:
    """
    Evaluate a generated answer using AnswerJudge.
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
        reference_answer_text=generated_answer.answer_text  # For context
    )
```

**Key Design Decisions:**
- **Zero modifications to AnswerJudge**: Reuse existing component as-is
- **No ground truth comparison**: Judge evaluates against retrieved chunks, not expected answers
- **Metadata enrichment**: Add test case ID, timestamps, etc. for tracking

---

## 7. Persisted Artifacts

### 7.1 Evaluation Run JSON

**File**: `runs/run_{run_id}.json`

**Content**: Complete `EvaluationRun` dataclass serialized as JSON.

**Structure:**
```json
{
  "run_id": "run_20250123_143022",
  "timestamp": "2025-01-23T14:30:22",
  "test_set_name": "core",
  "retrieval_config": {
    "top_k_original": 10,
    "top_k_rewritten": 10,
    "final_k": 10,
    "enable_query_rewrite": true
  },
  "answer_generation_config": {
    "model": "openai/gpt-4o-mini",
    "temperature": 0
  },
  "judge_config": {
    "model": "openai/gpt-4o-mini",
    "temperature": 0
  },
  "test_cases": [...],  # Array of TestCase objects
  "retrieval_metrics": [...],  # Array of RetrievalMetrics objects
  "answer_metrics": {...},  # AnswerMetrics object
  "total_test_cases": 50,
  "avg_mrr": 0.75,
  "avg_ndcg_at_10": 0.82,
  "avg_recall_at_10": 0.68,
  "avg_concept_coverage": 0.85,
  "avg_confidence_score": 3.8
}
```

**Purpose**: Complete, reproducible snapshot of evaluation run.

---

### 7.2 Retrieval Metrics JSON (Optional, for analysis)

**File**: `runs/run_{run_id}_retrieval_metrics.json`

**Content**: Detailed retrieval metrics per test case, formatted for easy analysis.

**Purpose**: Separate file for retrieval-focused analysis without loading full run.

---

### 7.3 Answer Metrics JSON (Optional, for analysis)

**File**: `runs/run_{run_id}_answer_metrics.json`

**Content**: Detailed answer evaluation results per test case.

**Purpose**: Separate file for answer-quality-focused analysis.

---

### 7.4 Run Index (Optional, for discovery)

**File**: `runs/index.json`

**Content**: List of all evaluation runs with metadata.

**Structure:**
```json
{
  "runs": [
    {
      "run_id": "run_20250123_143022",
      "timestamp": "2025-01-23T14:30:22",
      "test_set_name": "core",
      "total_test_cases": 50,
      "avg_mrr": 0.75,
      "avg_confidence_score": 3.8
    },
    ...
  ]
}
```

**Purpose**: Quick discovery of available evaluation runs without loading full files.

---

## 8. Assumptions and Non-Goals

### 8.1 Assumptions

1. **Test cases are manually curated**: Test cases in `test_sets.py` are written by humans, not generated
2. **Concept matching is approximate**: Concept coverage uses text matching, not exact semantic equivalence
3. **AnswerJudge is stable**: We assume `AnswerJudge` behavior is consistent across runs
4. **Vector DB is static during run**: We assume the vector DB doesn't change during a single evaluation run
5. **No ground truth answers**: We never compare generated answers to "correct" answers

---

### 8.2 Non-Goals

1. **No UI**: This is an offline evaluation harness, no Gradio UI or visualization
2. **No auto-optimization**: Does not automatically tune retrieval parameters or suggest improvements
3. **No training/fine-tuning**: Does not generate training data or fine-tune models
4. **No ground truth generation**: Does not generate expected answers or golden datasets
5. **No coupling to Interview Simulator**: Completely independent evaluation flow
6. **No real-time evaluation**: This is for offline batch evaluation, not live monitoring
7. **No A/B testing framework**: Does not compare different configurations automatically
8. **No metric aggregation across runs**: Each run is independent; no built-in trend analysis

This system diagnoses failure modes but does not prescribe fixes; improvement decisions remain human-led.
---

## 9. Usage Example (Conceptual)

```python
# In a separate script or notebook
from evaluation.rag_evaluator import RAGEvaluator
from pathlib import Path

# Initialize evaluator
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

# Access results
print(f"Average MRR: {run.avg_mrr}")
print(f"Average nDCG@10: {run.avg_ndcg_at_10}")
print(f"Average Confidence Score: {run.avg_confidence_score}")

# Analyze specific test case
test_case_metrics = run.retrieval_metrics[0]
print(f"MRR for test_001: {test_case_metrics.mrr}")
print(f"Concepts found: {test_case_metrics.concepts_found}")
print(f"Concepts missed: {test_case_metrics.concepts_missed}")
```

---

## 10. Implementation Notes

### 10.1 Dataclass Serialization

- Use `dataclasses.asdict()` for JSON serialization
- Handle `frozen=True` dataclasses (they're still serializable)
- Use custom JSON encoder for `Set` and other non-JSON types

### 10.2 Error Handling

- **Per-test-case errors**: If one test case fails, log error and continue with others
- **Component errors**: If retrieval fails, mark test case as failed but continue
- **Metric calculation errors**: If metric calculation fails, use default values (0.0) and log warning

### 10.3 Performance Considerations

- **Parallelization**: Consider parallelizing test case evaluation (but be careful with LLM rate limits)
- **Caching**: Consider caching retrieval results if same question is evaluated multiple times
- **Progress tracking**: Use tqdm or similar for progress bars during long runs

### 10.4 Extensibility

- **Custom metrics**: `metrics.py` functions can be extended with new metric types
- **Custom test sets**: New test sets can be added to `test_sets.py`
- **Custom data contracts**: New dataclasses can be added to `data_contracts.py` without breaking existing code

---

## Summary

This design provides a **complete, production-ready evaluation harness** that:

1. ✅ Measures retrieval quality (MRR, nDCG, Recall@K, chunk-type distribution)
2. ✅ Measures answer quality (reusing AnswerJudge)
3. ✅ Uses concept-based test cases (no ground truth answers)
4. ✅ Reuses existing components without modification
5. ✅ Persists complete evaluation runs as immutable snapshots
6. ✅ Is completely independent of Interview Simulator
7. ✅ Has no UI, no auto-optimization, no training/fine-tuning
8. ✅ Is designed for offline batch evaluation

The design is **ready for implementation** with clear separation of concerns, explicit data contracts, and well-defined responsibilities.
