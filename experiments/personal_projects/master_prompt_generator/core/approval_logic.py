"""
Approval Logic - Enforces quality gates before approval.

Checks all conditions that must be met before a prompt can be approved:
- Quality threshold
- No regressions
- No high-severity anti-patterns
- Cost regression check
"""

from typing import Tuple, Optional
from datetime import datetime
from .prompt_evaluator import EvaluationResult
from .prompt_generator import PromptWithMetadata
from .lifecycle_guard import LifecycleGuard


class ApprovalLogic:
    """
    Manages approval logic and quality gates.
    
    Enforces that prompts meet all requirements before approval:
    - Score >= threshold
    - No regressions
    - No high-severity anti-patterns
    - No cost regression without quality gain
    """
    
    def __init__(self, quality_threshold: float = 8.0):
        """
        Initialize approval logic.
        
        Args:
            quality_threshold: Minimum score for approval
        """
        self.quality_threshold = quality_threshold
        self.lifecycle_guard = LifecycleGuard()
    
    def check_approval_readiness(
        self,
        prompt_metadata: PromptWithMetadata,
        evaluation_result: EvaluationResult,
        previous_metadata: Optional[PromptWithMetadata] = None
    ) -> Tuple[bool, List[str]]:
        """
        Check if prompt is ready for approval.
        
        HARD BLOCKS (cannot approve):
        - Regression detected
        - High-severity anti-patterns
        - Cost regression without quality gain
        
        SOFT BLOCKS (warnings, but can approve):
        - Score below threshold
        
        Args:
            prompt_metadata: Current prompt metadata
            evaluation_result: Evaluation results
            previous_metadata: Previous version (for regression check)
        
        Returns:
            (can_approve: bool, blockers: List[str])
        """
        blockers = []
        hard_blockers = []
        
        # HARD BLOCK 1: Regression detection (cannot approve)
        if evaluation_result.has_regression:
            hard_blockers.append(
                f"REGRESSION DETECTED: Score dropped from {previous_metadata.evaluation_score_after} "
                f"to {evaluation_result.total_score}. Cannot approve. "
                f"Recommend reverting to version {previous_metadata.version}."
            )
        
        # HARD BLOCK 2: High-severity anti-patterns (cannot approve)
        if evaluation_result.high_severity_anti_patterns > 0:
            high_severity = [
                p for p in evaluation_result.anti_patterns 
                if p.severity in ["high", "critical"]
            ]
            pattern_names = [p.name for p in high_severity]
            hard_blockers.append(
                f"HIGH-SEVERITY ANTI-PATTERNS: {evaluation_result.high_severity_anti_patterns} "
                f"detected: {', '.join(pattern_names)}. Cannot approve until fixed."
            )
        
        # HARD BLOCK 3: Cost regression without quality gain
        if previous_metadata:
            cost_regression = self._check_cost_regression(
                previous_metadata,
                prompt_metadata,
                evaluation_result
            )
            if cost_regression:
                hard_blockers.append(
                    f"COST REGRESSION: {cost_regression}. Cannot approve."
                )
        
        # SOFT BLOCK: Quality threshold (warning, but not blocking)
        if not evaluation_result.meets_threshold:
            blockers.append(
                f"WARNING: Score {evaluation_result.total_score}/10 below threshold "
                f"{self.quality_threshold}/10 (not blocking)"
            )
        
        # Combine blockers
        all_blockers = hard_blockers + blockers
        
        # Cannot approve if any hard blockers
        can_approve = len(hard_blockers) == 0
        
        return can_approve, all_blockers
    
    def _check_cost_regression(
        self,
        previous: PromptWithMetadata,
        current: PromptWithMetadata,
        evaluation_result: EvaluationResult
    ) -> Optional[str]:
        """
        Check for cost regression without quality gain.
        
        Returns:
            Error message if regression detected, None otherwise
        """
        # Get cost for target model
        target_model = current.target_model
        prev_cost = previous.estimated_cost_per_run.get(target_model, 0.0)
        curr_cost = current.estimated_cost_per_run.get(target_model, 0.0)
        
        if prev_cost == 0:
            return None  # Can't compare
        
        cost_increase_pct = ((curr_cost - prev_cost) / prev_cost) * 100
        
        # Check if cost increased > 20% without quality gain
        if cost_increase_pct > 20:
            prev_score = previous.evaluation_score_after or 0.0
            curr_score = evaluation_result.total_score
            
            if curr_score <= prev_score:
                return (
                    f"Cost increased {cost_increase_pct:.1f}% without quality improvement "
                    f"({prev_cost:.4f} → {curr_cost:.4f})"
                )
        
        return None
    
    def approve(
        self,
        prompt_metadata: PromptWithMetadata
    ) -> PromptWithMetadata:
        """
        Approve a prompt (transition to approved state).
        
        Enforces lifecycle guard: cannot approve without evaluation.
        
        Args:
            prompt_metadata: Prompt to approve
        
        Returns:
            Updated metadata with lifecycle_state="approved"
        
        Raises:
            ValueError: If approval is invalid
        """
        # Enforce lifecycle transition
        self.lifecycle_guard.enforce_transition(
            prompt_metadata,
            "approved",
            "approve"
        )
        
        prompt_metadata.approved_at = datetime.utcnow().isoformat()
        prompt_metadata.updated_at = datetime.utcnow().isoformat()
        
        return prompt_metadata
