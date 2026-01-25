"""
Curated test case definitions for RAG evaluation.

This module contains manually curated test cases organized by category and difficulty.
Test cases specify concept-based expectations, not ground truth answers.
"""

from typing import List, Optional
from evaluation.data_contracts import TestCase


# ============================================================================
# Core Test Cases (Requirements 1-11)
# ============================================================================

CORE_TEST_CASES: List[TestCase] = [
    # Requirement 1: TypeScript fullstack development
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
        expected_requirement_ids=["req_1"],
        category="direct_fact",
        difficulty="medium",
        tags=["typescript", "javascript", "language_features", "fundamentals"],
        notes="Tests retrieval of TypeScript benefits for large-scale development"
    ),
    
    TestCase(
        test_id="test_002",
        question="What are the tradeoffs of using TypeScript's strict mode in a production codebase?",
        expected_concepts=[
            "strict mode",
            "type checking",
            "development velocity",
            "runtime safety",
            "migration complexity",
            "code quality"
        ],
        expected_requirement_ids=["req_1"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["typescript", "tradeoff", "production"],
        notes="Tests retrieval of TypeScript tradeoff concepts"
    ),
    
    TestCase(
        test_id="test_003",
        question="How would you handle type safety when integrating with a third-party JavaScript library that lacks TypeScript definitions?",
        expected_concepts=[
            "type definitions",
            "declaration files",
            "type assertions",
            "any type",
            "type safety",
            "third-party integration"
        ],
        expected_requirement_ids=["req_1"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["typescript", "integration", "failure_mode"],
        notes="Tests retrieval of TypeScript integration patterns and failure handling"
    ),
    
    # Requirement 2: React 18 and modern patterns
    TestCase(
        test_id="test_004",
        question="Explain how React's virtual DOM improves performance.",
        expected_concepts=[
            "virtual DOM",
            "DOM diffing",
            "reconciliation",
            "batch updates",
            "performance optimization",
            "minimal DOM manipulation"
        ],
        expected_requirement_ids=["req_2"],
        category="direct_fact",
        difficulty="medium",
        tags=["react", "frontend", "performance", "fundamentals"],
        notes="Tests retrieval of React core concepts"
    ),
    
    TestCase(
        test_id="test_005",
        question="When should you use React Context vs TanStack Query for state management?",
        expected_concepts=[
            "React Context",
            "TanStack Query",
            "server state",
            "client state",
            "caching",
            "state management patterns"
        ],
        expected_requirement_ids=["req_2"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["react", "tanstack-query", "state-management", "tradeoff"],
        notes="Tests retrieval of React state management tradeoffs"
    ),
    
    TestCase(
        test_id="test_006",
        question="What are common performance pitfalls when using React hooks, and how do you avoid them?",
        expected_concepts=[
            "React hooks",
            "useEffect dependencies",
            "re-renders",
            "memoization",
            "performance pitfalls",
            "optimization patterns"
        ],
        expected_requirement_ids=["req_2"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["react", "hooks", "performance", "failure_mode"],
        notes="Tests retrieval of React hooks failure modes and optimization"
    ),
    
    # Requirement 3: Node.js and NestJS
    TestCase(
        test_id="test_007",
        question="How does NestJS's dependency injection system work, and what benefits does it provide?",
        expected_concepts=[
            "dependency injection",
            "NestJS",
            "inversion of control",
            "testability",
            "modularity",
            "service providers"
        ],
        expected_requirement_ids=["req_3"],
        category="direct_fact",
        difficulty="medium",
        tags=["nestjs", "nodejs", "architecture", "fundamentals"],
        notes="Tests retrieval of NestJS dependency injection concepts"
    ),
    
    TestCase(
        test_id="test_008",
        question="What are the tradeoffs between using NestJS modules vs a more lightweight Node.js framework like Express?",
        expected_concepts=[
            "NestJS",
            "Express",
            "framework overhead",
            "structure",
            "flexibility",
            "development speed",
            "scalability"
        ],
        expected_requirement_ids=["req_3"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["nestjs", "express", "nodejs", "tradeoff"],
        notes="Tests retrieval of Node.js framework tradeoffs"
    ),
    
    TestCase(
        test_id="test_009",
        question="How do you handle uncaught exceptions and promise rejections in a Node.js production application?",
        expected_concepts=[
            "uncaught exceptions",
            "promise rejections",
            "error handling",
            "process events",
            "graceful shutdown",
            "logging",
            "monitoring"
        ],
        expected_requirement_ids=["req_3"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["nodejs", "error-handling", "failure_mode", "production"],
        notes="Tests retrieval of Node.js error handling and failure modes"
    ),
    
    # Requirement 4: PostgreSQL
    TestCase(
        test_id="test_010",
        question="How do you optimize a slow PostgreSQL query that's causing performance issues?",
        expected_concepts=[
            "query optimization",
            "indexing",
            "EXPLAIN ANALYZE",
            "query planning",
            "performance tuning",
            "database optimization"
        ],
        expected_requirement_ids=["req_4"],
        category="system_design",
        difficulty="hard",
        tags=["postgresql", "database", "performance", "optimization"],
        notes="Tests retrieval of PostgreSQL query optimization concepts"
    ),
    
    TestCase(
        test_id="test_011",
        question="What are the tradeoffs between using JSONB vs normalized relational tables in PostgreSQL?",
        expected_concepts=[
            "JSONB",
            "normalized tables",
            "schema flexibility",
            "query performance",
            "data integrity",
            "scalability"
        ],
        expected_requirement_ids=["req_4"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["postgresql", "jsonb", "database-design", "tradeoff"],
        notes="Tests retrieval of PostgreSQL data modeling tradeoffs"
    ),
    
    TestCase(
        test_id="test_012",
        question="How do you handle database migrations safely in a production environment with zero downtime?",
        expected_concepts=[
            "database migrations",
            "zero downtime",
            "backward compatibility",
            "migration strategies",
            "rollback plans",
            "production safety"
        ],
        expected_requirement_ids=["req_4"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["postgresql", "migrations", "production", "failure_mode"],
        notes="Tests retrieval of PostgreSQL migration safety patterns"
    ),
    
    # Requirement 5: Redis
    TestCase(
        test_id="test_013",
        question="How would you implement a distributed rate limiting system using Redis?",
        expected_concepts=[
            "Redis",
            "rate limiting",
            "distributed systems",
            "token bucket",
            "sliding window",
            "atomic operations"
        ],
        expected_requirement_ids=["req_5"],
        category="system_design",
        difficulty="hard",
        tags=["redis", "rate-limiting", "distributed-systems"],
        notes="Tests retrieval of Redis rate limiting patterns"
    ),
    
    TestCase(
        test_id="test_014",
        question="What are the tradeoffs between using Redis pub/sub vs a message queue like BullMQ for job processing?",
        expected_concepts=[
            "Redis pub/sub",
            "BullMQ",
            "message queues",
            "job processing",
            "reliability",
            "scalability",
            "durability"
        ],
        expected_requirement_ids=["req_5"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["redis", "pubsub", "job-queues", "tradeoff"],
        notes="Tests retrieval of Redis vs message queue tradeoffs"
    ),
    
    TestCase(
        test_id="test_015",
        question="How do you handle Redis cache invalidation when data is updated in the primary database?",
        expected_concepts=[
            "cache invalidation",
            "cache consistency",
            "write-through",
            "write-behind",
            "cache-aside",
            "data synchronization"
        ],
        expected_requirement_ids=["req_5"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["redis", "caching", "cache-invalidation", "failure_mode"],
        notes="Tests retrieval of Redis cache invalidation patterns"
    ),
    
    # Requirement 6: REST API and authentication
    TestCase(
        test_id="test_016",
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
        expected_requirement_ids=["req_6"],
        category="direct_fact",
        difficulty="medium",
        tags=["api", "rest", "graphql", "architecture", "fundamentals"],
        notes="Tests retrieval of API design concepts"
    ),
    
    TestCase(
        test_id="test_017",
        question="How do you securely implement JWT token refresh in a stateless REST API?",
        expected_concepts=[
            "JWT",
            "token refresh",
            "access tokens",
            "refresh tokens",
            "stateless authentication",
            "security"
        ],
        expected_requirement_ids=["req_6"],
        category="system_design",
        difficulty="hard",
        tags=["jwt", "authentication", "security", "rest-api"],
        notes="Tests retrieval of JWT authentication patterns"
    ),
    
    TestCase(
        test_id="test_018",
        question="What are common security vulnerabilities in OAuth 2.0 implementations, and how do you prevent them?",
        expected_concepts=[
            "OAuth 2.0",
            "security vulnerabilities",
            "CSRF attacks",
            "token leakage",
            "redirect URI validation",
            "security best practices"
        ],
        expected_requirement_ids=["req_6"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["oauth", "authentication", "security", "failure_mode"],
        notes="Tests retrieval of OAuth security failure modes"
    ),
    
    # Requirement 7: Third-party API integration
    TestCase(
        test_id="test_019",
        question="How do you handle rate limiting and retries when integrating with external payment APIs like Stripe?",
        expected_concepts=[
            "rate limiting",
            "retry logic",
            "exponential backoff",
            "idempotency",
            "payment APIs",
            "error handling"
        ],
        expected_requirement_ids=["req_7"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["api-integration", "stripe", "rate-limiting", "failure_mode"],
        notes="Tests retrieval of third-party API integration patterns"
    ),
    
    TestCase(
        test_id="test_020",
        question="What are the tradeoffs between synchronous vs asynchronous processing when integrating with external services?",
        expected_concepts=[
            "synchronous",
            "asynchronous",
            "webhooks",
            "polling",
            "latency",
            "reliability",
            "complexity"
        ],
        expected_requirement_ids=["req_7"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["api-integration", "async", "webhooks", "tradeoff"],
        notes="Tests retrieval of API integration architecture tradeoffs"
    ),
    
    # Requirement 8: AI/LLM APIs
    TestCase(
        test_id="test_021",
        question="How do you structure prompts for LLM APIs to ensure consistent, reliable outputs in production?",
        expected_concepts=[
            "prompt engineering",
            "LLM APIs",
            "structured outputs",
            "prompt templates",
            "consistency",
            "reliability"
        ],
        expected_requirement_ids=["req_8"],
        category="system_design",
        difficulty="medium",
        tags=["llm", "prompt-engineering", "ai-apis"],
        notes="Tests retrieval of LLM prompt engineering concepts"
    ),
    
    TestCase(
        test_id="test_022",
        question="What are the tradeoffs between using OpenAI's GPT-4 vs GPT-4o-mini for different use cases?",
        expected_concepts=[
            "OpenAI API",
            "model selection",
            "cost",
            "latency",
            "quality",
            "use case optimization"
        ],
        expected_requirement_ids=["req_8"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="medium",
        tags=["openai", "llm", "model-selection", "tradeoff"],
        notes="Tests retrieval of LLM model selection tradeoffs"
    ),
    
    TestCase(
        test_id="test_023",
        question="How do you handle rate limiting and token usage when making multiple LLM API calls in a high-throughput application?",
        expected_concepts=[
            "rate limiting",
            "token usage",
            "API quotas",
            "batching",
            "cost optimization",
            "throughput"
        ],
        expected_requirement_ids=["req_8"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["llm", "api-integration", "rate-limiting", "failure_mode"],
        notes="Tests retrieval of LLM API integration failure modes"
    ),
    
    # Requirement 7: Third-party API integration (additional)
    TestCase(
        test_id="test_024",
        question="How do you ensure idempotency and prevent duplicate charges when processing webhook events from payment gateways?",
        expected_concepts=[
            "idempotency",
            "webhooks",
            "payment processing",
            "duplicate prevention",
            "event deduplication",
            "transaction safety"
        ],
        expected_requirement_ids=["req_7"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="hard",
        tags=["api-integration", "webhooks", "payment", "failure_mode"],
        notes="Tests retrieval of payment API integration safety patterns"
    ),
    
    # Requirement 9: Product thinking
    TestCase(
        test_id="test_025",
        question="How do you decide between building a feature in-house vs using a third-party service when both are technically feasible?",
        expected_concepts=[
            "build vs buy",
            "product decisions",
            "technical feasibility",
            "business value",
            "maintenance cost",
            "vendor lock-in"
        ],
        expected_requirement_ids=["req_9"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["product-thinking", "decision-making", "tradeoff"],
        notes="Tests retrieval of product thinking and technical decision making"
    ),
    
    TestCase(
        test_id="test_026",
        question="What questions should you ask before implementing a new technical feature to ensure it aligns with business goals?",
        expected_concepts=[
            "product requirements",
            "business alignment",
            "user needs",
            "technical feasibility",
            "success metrics",
            "product development"
        ],
        expected_requirement_ids=["req_9"],
        category="direct_fact",
        difficulty="medium",
        tags=["product-thinking", "requirements", "fundamentals"],
        notes="Tests retrieval of product thinking fundamentals"
    ),
    
    TestCase(
        test_id="test_027",
        question="How do you balance technical debt and feature velocity in a fast-moving startup environment?",
        expected_concepts=[
            "technical debt",
            "feature velocity",
            "startup environment",
            "tradeoffs",
            "prioritization",
            "long-term vs short-term"
        ],
        expected_requirement_ids=["req_9"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="hard",
        tags=["product-thinking", "technical-debt", "tradeoff"],
        notes="Tests retrieval of product thinking in startup context"
    ),
    
    # Requirement 10: Autonomous work in startup
    TestCase(
        test_id="test_028",
        question="How do you prioritize tasks when working autonomously on multiple features with competing deadlines?",
        expected_concepts=[
            "task prioritization",
            "autonomous work",
            "deadline management",
            "impact assessment",
            "time management",
            "decision making"
        ],
        expected_requirement_ids=["req_10"],
        category="system_design",
        difficulty="medium",
        tags=["autonomous-work", "prioritization", "startup"],
        notes="Tests retrieval of autonomous work patterns"
    ),
    
    TestCase(
        test_id="test_029",
        question="What strategies help you stay productive and avoid burnout when working in a fast-paced startup with limited resources?",
        expected_concepts=[
            "productivity",
            "burnout prevention",
            "startup environment",
            "resource constraints",
            "work-life balance",
            "sustainable pace"
        ],
        expected_requirement_ids=["req_10"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["autonomous-work", "startup", "failure_mode"],
        notes="Tests retrieval of startup work sustainability patterns"
    ),
    
    TestCase(
        test_id="test_030",
        question="How do you communicate technical progress and blockers effectively when working remotely in a distributed team?",
        expected_concepts=[
            "remote communication",
            "technical updates",
            "blocker reporting",
            "distributed teams",
            "async communication",
            "transparency"
        ],
        expected_requirement_ids=["req_10", "req_11"],
        category="direct_fact",
        difficulty="medium",
        tags=["autonomous-work", "communication", "remote-work"],
        notes="Tests retrieval of autonomous work communication patterns"
    ),
    
    # Requirement 11: English communication
    TestCase(
        test_id="test_031",
        question="How do you write clear technical documentation that's accessible to both technical and non-technical stakeholders?",
        expected_concepts=[
            "technical writing",
            "documentation",
            "clarity",
            "audience awareness",
            "communication",
            "accessibility"
        ],
        expected_requirement_ids=["req_11"],
        category="direct_fact",
        difficulty="medium",
        tags=["communication", "documentation", "technical-writing"],
        notes="Tests retrieval of technical communication concepts"
    ),
    
    TestCase(
        test_id="test_032",
        question="What are common pitfalls in written technical communication when collaborating with an international team?",
        expected_concepts=[
            "written communication",
            "international teams",
            "cultural differences",
            "clarity",
            "miscommunication",
            "best practices"
        ],
        expected_requirement_ids=["req_11"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["communication", "international", "failure_mode"],
        notes="Tests retrieval of international communication failure modes"
    ),
    
    TestCase(
        test_id="test_033",
        question="How do you structure code reviews and pull request descriptions to facilitate effective asynchronous collaboration?",
        expected_concepts=[
            "code reviews",
            "pull requests",
            "asynchronous collaboration",
            "technical communication",
            "code documentation",
            "review clarity"
        ],
        expected_requirement_ids=["req_11"],
        category="direct_fact",
        difficulty="easy",
        tags=["communication", "code-reviews", "collaboration"],
        notes="Tests retrieval of technical communication in code review context"
    ),
    
    # ============================================================================
    # Phase 4.2 Iteration 2: Balance and Stability Additions
    # Focus on weakest requirements (8, 9, 10, 11) with medium-difficulty
    # questions to reduce variance and improve diagnostic value
    # ============================================================================
    
    # Requirement 8: AI/LLM APIs (additional medium-difficulty cases)
    TestCase(
        test_id="test_034",
        question="What are the key considerations when choosing between streaming and non-streaming responses from LLM APIs?",
        expected_concepts=[
            "streaming responses",
            "non-streaming",
            "user experience",
            "latency",
            "API design",
            "response handling"
        ],
        expected_requirement_ids=["req_8"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="medium",
        tags=["llm", "api-design", "tradeoff", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Narrower variant of LLM API design question to reduce variance"
    ),
    
    TestCase(
        test_id="test_035",
        question="How do you implement error handling and fallback strategies when LLM API calls fail or return unexpected responses?",
        expected_concepts=[
            "error handling",
            "fallback strategies",
            "API failures",
            "retry logic",
            "graceful degradation",
            "response validation"
        ],
        expected_requirement_ids=["req_8"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["llm", "error-handling", "failure_mode"],
        notes="Phase 4.2 Iteration 2: Medium-difficulty failure mode question for req_8 to balance hard questions"
    ),
    
    TestCase(
        test_id="test_036",
        question="What prompt engineering techniques help ensure LLM outputs follow a specific format or structure?",
        expected_concepts=[
            "prompt engineering",
            "structured outputs",
            "format constraints",
            "output parsing",
            "prompt design",
            "consistency"
        ],
        expected_requirement_ids=["req_8"],
        category="direct_fact",
        difficulty="medium",
        tags=["llm", "prompt-engineering", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Paraphrased variant of test_021 to test retrieval stability"
    ),
    
    # Requirement 9: Product thinking (additional medium-difficulty cases)
    TestCase(
        test_id="test_037",
        question="How do you evaluate whether a technical solution addresses the actual user problem versus just the stated requirements?",
        expected_concepts=[
            "user problems",
            "requirements analysis",
            "problem validation",
            "user needs",
            "solution evaluation",
            "product thinking"
        ],
        expected_requirement_ids=["req_9"],
        category="system_design",
        difficulty="medium",
        tags=["product-thinking", "requirements", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Medium-difficulty variant of product thinking to balance hard questions"
    ),
    
    TestCase(
        test_id="test_038",
        question="What factors should influence your decision to refactor existing code versus building new features?",
        expected_concepts=[
            "refactoring",
            "feature development",
            "code quality",
            "technical debt",
            "prioritization",
            "product decisions"
        ],
        expected_requirement_ids=["req_9"],
        expected_chunk_types=["primary", "tradeoff"],
        category="tradeoff_analysis",
        difficulty="medium",
        tags=["product-thinking", "refactoring", "tradeoff"],
        notes="Phase 4.2 Iteration 2: Medium-difficulty tradeoff question for req_9 to improve balance"
    ),
    
    TestCase(
        test_id="test_039",
        question="How do you determine the minimum viable scope for a feature when multiple stakeholders have different priorities?",
        expected_concepts=[
            "minimum viable scope",
            "stakeholder priorities",
            "feature scoping",
            "product decisions",
            "prioritization",
            "business alignment"
        ],
        expected_requirement_ids=["req_9"],
        category="direct_fact",
        difficulty="medium",
        tags=["product-thinking", "scoping", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Narrower, medium-difficulty question to reduce variance in req_9 metrics"
    ),
    
    # Requirement 10: Autonomous work (additional medium-difficulty cases)
    TestCase(
        test_id="test_040",
        question="How do you break down a large, ambiguous feature request into actionable tasks when working independently?",
        expected_concepts=[
            "task breakdown",
            "ambiguous requirements",
            "independent work",
            "feature planning",
            "autonomous work",
            "task decomposition"
        ],
        expected_requirement_ids=["req_10"],
        category="system_design",
        difficulty="medium",
        tags=["autonomous-work", "task-management", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Narrower variant of autonomous work question to improve stability"
    ),
    
    TestCase(
        test_id="test_041",
        question="What strategies help you make progress on complex problems when you're blocked and can't immediately get help?",
        expected_concepts=[
            "problem solving",
            "blockers",
            "independent work",
            "research strategies",
            "autonomous work",
            "self-directed learning"
        ],
        expected_requirement_ids=["req_10"],
        expected_chunk_types=["primary", "failure_mode"],
        category="system_design",
        difficulty="medium",
        tags=["autonomous-work", "problem-solving", "failure_mode"],
        notes="Phase 4.2 Iteration 2: Medium-difficulty failure mode question for req_10"
    ),
    
    TestCase(
        test_id="test_042",
        question="How do you estimate and communicate realistic timelines for features when working in a startup with changing priorities?",
        expected_concepts=[
            "time estimation",
            "changing priorities",
            "startup environment",
            "communication",
            "autonomous work",
            "timeline management"
        ],
        expected_requirement_ids=["req_10"],
        category="direct_fact",
        difficulty="medium",
        tags=["autonomous-work", "estimation", "startup", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Paraphrased variant focusing on estimation to reduce variance"
    ),
    
    # Requirement 11: English communication (additional medium-difficulty cases)
    TestCase(
        test_id="test_043",
        question="How do you explain complex technical concepts to non-technical team members or stakeholders?",
        expected_concepts=[
            "technical communication",
            "non-technical audience",
            "concept explanation",
            "clarity",
            "simplification",
            "stakeholder communication"
        ],
        expected_requirement_ids=["req_11"],
        category="direct_fact",
        difficulty="medium",
        tags=["communication", "technical-writing", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Paraphrased variant of test_031 to test retrieval stability"
    ),
    
    TestCase(
        test_id="test_044",
        question="What are effective ways to provide constructive feedback in code reviews without discouraging collaboration?",
        expected_concepts=[
            "code reviews",
            "constructive feedback",
            "collaboration",
            "communication",
            "team dynamics",
            "technical communication"
        ],
        expected_requirement_ids=["req_11"],
        category="system_design",
        difficulty="medium",
        tags=["communication", "code-reviews", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Narrower variant of test_033 to improve balance"
    ),
    
    TestCase(
        test_id="test_045",
        question="How do you write clear commit messages and technical updates that help team members understand changes quickly?",
        expected_concepts=[
            "commit messages",
            "technical updates",
            "clarity",
            "team communication",
            "documentation",
            "written communication"
        ],
        expected_requirement_ids=["req_11"],
        category="direct_fact",
        difficulty="medium",
        tags=["communication", "documentation", "paraphrase"],
        notes="Phase 4.2 Iteration 2: Medium-difficulty question to balance req_11 and reduce variance"
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
