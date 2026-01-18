"""
Orchestrator - End-to-end prompt generation loop.

Coordinates the full workflow:
Generate → Evaluate → (Refine if needed) → Approve
"""

from typing import Optional, List
from .prompt_generator import PromptGenerator, PromptWithMetadata
from .prompt_evaluator import PromptEvaluator, EvaluationResult
from .prompt_refiner import PromptRefiner
from .approval_logic import ApprovalLogic
from .lifecycle_guard import LifecycleGuard
from .version_guard import VersionGuard


class PromptOrchestrator:
    """
    Orchestrates the complete prompt generation workflow.
    
    Manages the full lifecycle:
    1. Generate prompt
    2. Evaluate quality
    3. Refine if needed (loop)
    4. Approve when ready
    """
    
    def __init__(
        self,
        quality_threshold: float = 8.0,
        max_refinement_iterations: int = 3
    ):
        """
        Initialize orchestrator.
        
        Args:
            quality_threshold: Minimum score for approval
            max_refinement_iterations: Maximum refinement attempts
        """
        self.generator = PromptGenerator()
        self.evaluator = PromptEvaluator(quality_threshold=quality_threshold)
        self.refiner = PromptRefiner(self.generator.model_manager)
        self.approval_logic = ApprovalLogic(quality_threshold=quality_threshold)
        self.max_refinement_iterations = max_refinement_iterations
        self.lifecycle_guard = LifecycleGuard()
        self.version_guard = VersionGuard()
    
    def generate_and_approve(
        self,
        use_case: str,
        category: str,
        complexity_tier: int,
        context: str,
        requirements: Optional[List[str]] = None,
        target_model: str = "claude-sonnet",
        generation_model: Optional[str] = None,
        auto_approve: bool = True
    ) -> tuple[PromptWithMetadata, List[PromptWithMetadata], List[EvaluationResult]]:
        """
        Generate prompt and iterate until approval (or max iterations).
        
        Args:
            use_case: Use case description
            category: Category (business, technical, etc.)
            complexity_tier: 1-4 complexity tier
            context: User-provided context
            requirements: Optional specific requirements
            target_model: Model the prompt will be used with
            generation_model: Model for generation (defaults to target)
            auto_approve: If True, automatically approve when ready
        
        Returns:
            (final_prompt, version_history, evaluation_history)
        """
        version_history = []
        evaluation_history = []
        
        # Step 1: Generate initial prompt
        current_prompt = self.generator.generate(
            use_case=use_case,
            category=category,
            complexity_tier=complexity_tier,
            context=context,
            requirements=requirements,
            target_model=target_model,
            generation_model=generation_model
        )
        version_history.append(current_prompt)
        
        # Step 2: Evaluate
        evaluation_result = self.evaluator.score_prompt(current_prompt)
        self.evaluator.update_prompt_metadata(current_prompt, evaluation_result)
        evaluation_history.append(evaluation_result)
        
        # Step 3: Refine loop (if needed)
        previous_prompt = current_prompt
        iteration = 0
        
        while iteration < self.max_refinement_iterations:
            # Check if ready for approval
            can_approve, blockers = self.approval_logic.check_approval_readiness(
                current_prompt,
                evaluation_result,
                previous_prompt if iteration > 0 else None
            )
            
            if can_approve:
                break
            
            # Refine
            current_prompt = self.refiner.refine(
                previous_prompt,
                evaluation_result,
                generation_model
            )
            version_history.append(current_prompt)
            
            # Re-evaluate
            previous_score = evaluation_result.total_score
            evaluation_result = self.evaluator.score_prompt(
                current_prompt,
                previous_score=previous_score
            )
            self.evaluator.update_prompt_metadata(current_prompt, evaluation_result)
            evaluation_history.append(evaluation_result)
            
            previous_prompt = current_prompt
            iteration += 1
        
        # Step 4: Approve if ready and auto_approve is True
        if auto_approve:
            can_approve, blockers = self.approval_logic.check_approval_readiness(
                current_prompt,
                evaluation_result,
                version_history[0] if len(version_history) > 1 else None
            )
            
            if can_approve:
                # Enforce version integrity before approval
                self.version_guard.enforce_version_integrity(
                    current_prompt,
                    parent_lookup=lambda pid: next(
                        (v for v in version_history if v.id == pid), None
                    ) if pid else None,
                    operation="approve"
                )
                current_prompt = self.approval_logic.approve(current_prompt)
        
        return current_prompt, version_history, evaluation_history
