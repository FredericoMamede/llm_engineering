"""
Curated test case definitions for RAG evaluation.

This module contains manually curated test cases organized by category and difficulty.
Test cases specify concept-based expectations, not ground truth answers.

These are design sketches - not yet implemented.
"""

from typing import List, Optional
from evaluation.data_contracts import TestCase


# ============================================================================
# Core Test Cases (Direct Facts)
# ============================================================================

CORE_TEST_CASES: List[TestCase] = [
    # Example test case - not a real implementation
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
        tags=["typescript", "javascript", "language_features"],
        notes="Tests retrieval of TypeScript benefits for large-scale development"
    ),
    # TODO: Add more test cases
]


# ============================================================================
# System Design Test Cases
# ============================================================================

SYSTEM_DESIGN_TEST_CASES: List[TestCase] = [
    # Example test case - not a real implementation
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
        tags=["distributed-systems", "rate-limiting"],
        notes="Tests retrieval of system design concepts for rate limiting"
    ),
    # TODO: Add more test cases
]


# ============================================================================
# Company-Specific Test Cases
# ============================================================================

COMPANY_SPECIFIC_TEST_CASES: List[TestCase] = [
    # Example test case - not a real implementation
    TestCase(
        test_id="test_company_001",
        question="What are Eventyr's engineering practices for code review?",
        expected_concepts=[
            "code review process",
            "pull request workflow",
            "engineering culture"
        ],
        expected_company_domains=["eventyr_engineering"],
        category="company_specific",
        difficulty="medium",
        tags=["eventyr", "engineering-practices"],
        notes="Tests retrieval of company-specific knowledge"
    ),
    # TODO: Add more test cases
]


# ============================================================================
# Test Set Loading Functions
# ============================================================================

def get_test_set(name: str) -> List[TestCase]:
    """
    Load a test set by name.
    
    Args:
        name: Test set name (e.g., "core", "system_design", "company_specific")
    
    Returns:
        List of TestCase objects
    
    Raises:
        ValueError: If test set name is not recognized
    """
    test_sets = {
        "core": CORE_TEST_CASES,
        "system_design": SYSTEM_DESIGN_TEST_CASES,
        "company_specific": COMPANY_SPECIFIC_TEST_CASES,
        # TODO: Add more test sets
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
    all_cases = []
    all_cases.extend(CORE_TEST_CASES)
    all_cases.extend(SYSTEM_DESIGN_TEST_CASES)
    all_cases.extend(COMPANY_SPECIFIC_TEST_CASES)
    # TODO: Add more test sets
    return all_cases
