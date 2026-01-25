"""
Curated test case definitions for RAG evaluation.

This module contains manually curated test cases organized by category and difficulty.
Test cases specify concept-based expectations, not ground truth answers.
"""

from typing import List, Optional
from evaluation.data_contracts import TestCase


# ============================================================================
# Core Test Cases (Direct Facts)
# ============================================================================

CORE_TEST_CASES: List[TestCase] = [
    TestCase(
        test_id="test_001",
        question="How does TypeScript help with large-scale JavaScript development?",
        expected_concepts=[
            "static typing",
            "type safety",
            "compile-time error checking",
            "IDE support",
            "refactoring safety",
            "type inference"
        ],
        category="direct_fact",
        difficulty="medium",
        tags=["typescript", "javascript", "language_features"],
        notes="Tests retrieval of TypeScript benefits for large-scale development"
    ),
    
    TestCase(
        test_id="test_002",
        question="What are the key differences between REST and GraphQL APIs?",
        expected_concepts=[
            "REST",
            "GraphQL",
            "over-fetching",
            "under-fetching",
            "single endpoint",
            "multiple endpoints",
            "query flexibility"
        ],
        category="direct_fact",
        difficulty="medium",
        tags=["api", "rest", "graphql", "architecture"],
        notes="Tests retrieval of API design concepts"
    ),
    
    TestCase(
        test_id="test_003",
        question="Explain how React's virtual DOM improves performance.",
        expected_concepts=[
            "virtual DOM",
            "DOM diffing",
            "reconciliation",
            "batch updates",
            "performance optimization",
            "minimal DOM manipulation"
        ],
        category="direct_fact",
        difficulty="medium",
        tags=["react", "frontend", "performance"],
        notes="Tests retrieval of React core concepts"
    ),
]


# ============================================================================
# System Design Test Cases
# ============================================================================

SYSTEM_DESIGN_TEST_CASES: List[TestCase] = [
    TestCase(
        test_id="test_sd_001",
        question="How would you design a distributed rate limiting system?",
        expected_concepts=[
            "distributed systems",
            "rate limiting algorithms",
            "token bucket",
            "sliding window",
            "consistency guarantees",
            "scalability",
            "Redis",
            "distributed coordination"
        ],
        expected_chunk_types=["primary", "tradeoff", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["distributed-systems", "rate-limiting", "scalability"],
        notes="Tests retrieval of system design concepts for rate limiting"
    ),
    
    TestCase(
        test_id="test_sd_002",
        question="What are the tradeoffs between microservices and monolithic architectures?",
        expected_concepts=[
            "microservices",
            "monolithic architecture",
            "scalability",
            "deployment complexity",
            "service boundaries",
            "distributed systems challenges",
            "team autonomy"
        ],
        expected_chunk_types=["primary", "tradeoff"],
        category="system_design",
        difficulty="hard",
        tags=["architecture", "microservices", "tradeoffs"],
        notes="Tests retrieval of architectural tradeoff concepts"
    ),
]


# ============================================================================
# Tradeoff Analysis Test Cases
# ============================================================================

TRADEOFF_TEST_CASES: List[TestCase] = [
    TestCase(
        test_id="test_to_001",
        question="What are the tradeoffs of using NoSQL vs SQL databases?",
        expected_concepts=[
            "NoSQL",
            "SQL",
            "ACID properties",
            "scalability",
            "consistency",
            "schema flexibility",
            "transaction support"
        ],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="medium",
        tags=["database", "nosql", "sql", "tradeoffs"],
        notes="Tests retrieval of database tradeoff concepts"
    ),
]


# ============================================================================
# Test Set Loading Functions
# ============================================================================

def get_test_set(name: str) -> List[TestCase]:
    """
    Load a test set by name.
    
    Args:
        name: Test set name (e.g., "core", "system_design", "tradeoff", "all")
    
    Returns:
        List of TestCase objects
    
    Raises:
        ValueError: If test set name is not recognized
    """
    test_sets = {
        "core": CORE_TEST_CASES,
        "system_design": SYSTEM_DESIGN_TEST_CASES,
        "tradeoff": TRADEOFF_TEST_CASES,
        "all": CORE_TEST_CASES + SYSTEM_DESIGN_TEST_CASES + TRADEOFF_TEST_CASES,
    }
    
    if name not in test_sets:
        raise ValueError(f"Unknown test set: {name}. Available: {list(test_sets.keys())}")
    
    return test_sets[name]


def filter_test_cases(
    test_cases: List[TestCase],
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[TestCase]:
    """
    Filter test cases by criteria.
    
    Args:
        test_cases: List of TestCase objects to filter
        category: Filter by category (e.g., "direct_fact", "system_design")
        difficulty: Filter by difficulty (e.g., "easy", "medium", "hard")
        tags: Filter by tags (test case must have at least one matching tag)
    
    Returns:
        Filtered list of TestCase objects
    """
    filtered = test_cases
    
    if category:
        filtered = [tc for tc in filtered if tc.category == category]
    
    if difficulty:
        filtered = [tc for tc in filtered if tc.difficulty == difficulty]
    
    if tags:
        # Test case must have at least one matching tag
        filtered = [tc for tc in filtered if any(tag in tc.tags for tag in tags)]
    
    return filtered


def get_all_test_cases() -> List[TestCase]:
    """
    Get all test cases from all test sets.
    
    Returns:
        Combined list of all TestCase objects
    """
    return CORE_TEST_CASES + SYSTEM_DESIGN_TEST_CASES + TRADEOFF_TEST_CASES
