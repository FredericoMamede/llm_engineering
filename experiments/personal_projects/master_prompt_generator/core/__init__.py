"""
Core components for Master Prompt Generator.

This module provides the core prompt engineering functionality:
- Generation with model adaptation
- Evaluation with quality metrics
- Refinement with versioning
- Lifecycle management
"""

from .prompt_generator import PromptGenerator, PromptWithMetadata
from .prompt_evaluator import PromptEvaluator, EvaluationResult
from .prompt_refiner import PromptRefiner
from .model_manager import ModelManager
from .prompt_smell_detector import PromptSmellDetector, AntiPattern
from .token_economics import TokenEconomics, TokenEstimate
from .approval_logic import ApprovalLogic
from .orchestrator import PromptOrchestrator
from .lifecycle_guard import LifecycleGuard
from .version_guard import VersionGuard
from .breaking_change_detector import BreakingChangeDetector

__all__ = [
    "PromptGenerator",
    "PromptWithMetadata",
    "PromptEvaluator",
    "EvaluationResult",
    "PromptRefiner",
    "ModelManager",
    "PromptSmellDetector",
    "AntiPattern",
    "TokenEconomics",
    "TokenEstimate",
    "ApprovalLogic",
    "PromptOrchestrator",
    "LifecycleGuard",
    "VersionGuard",
    "BreakingChangeDetector",
]
