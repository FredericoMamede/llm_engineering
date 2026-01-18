"""
Lifecycle Guard - Enforces lifecycle invariants.

Prevents illegal state transitions and ensures lifecycle integrity.
"""

from typing import Tuple
from .prompt_generator import PromptWithMetadata


class LifecycleGuard:
    """
    Enforces lifecycle state machine invariants.
    
    Prevents:
    - Approving unevaluated prompts
    - Refining archived prompts
    - Approving regressed prompts
    - Skipping lifecycle steps
    """
    
    VALID_TRANSITIONS = {
        "draft": ["generated"],
        "generated": ["evaluated", "draft"],
        "evaluated": ["refined", "approved", "draft"],
        "refined": ["evaluated", "approved", "draft"],
        "approved": ["refined", "archived"],
        "archived": ["draft"]
    }
    
    def __init__(self):
        """Initialize lifecycle guard."""
        pass
    
    def can_transition(
        self,
        current_state: str,
        target_state: str
    ) -> Tuple[bool, str]:
        """
        Check if transition is valid.
        
        Args:
            current_state: Current lifecycle state
            target_state: Desired lifecycle state
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if current_state not in self.VALID_TRANSITIONS:
            return False, f"Invalid current state: {current_state}"
        
        if target_state not in self.VALID_TRANSITIONS[current_state]:
            valid_targets = ", ".join(self.VALID_TRANSITIONS[current_state])
            return False, (
                f"Cannot transition from '{current_state}' to '{target_state}'. "
                f"Valid transitions: {valid_targets}"
            )
        
        return True, ""
    
    def validate_evaluation_required(
        self,
        prompt_metadata: PromptWithMetadata,
        target_state: str
    ) -> Tuple[bool, str]:
        """
        Ensure prompt is evaluated before approval.
        
        Args:
            prompt_metadata: Prompt metadata
            target_state: Target state (should be "approved")
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if target_state == "approved":
            if prompt_metadata.lifecycle_state not in ["evaluated", "refined"]:
                return False, (
                    f"Cannot approve prompt in state '{prompt_metadata.lifecycle_state}'. "
                    "Prompt must be evaluated first."
                )
            
            if prompt_metadata.evaluation_score_after is None:
                return False, "Cannot approve prompt without evaluation score."
        
        return True, ""
    
    def validate_not_archived(
        self,
        prompt_metadata: PromptWithMetadata,
        operation: str
    ) -> Tuple[bool, str]:
        """
        Ensure prompt is not archived for operations that require active state.
        
        Args:
            prompt_metadata: Prompt metadata
            operation: Operation name (for error message)
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if prompt_metadata.lifecycle_state == "archived":
            return False, (
                f"Cannot {operation} archived prompt. "
                "Restore to draft state first."
            )
        
        return True, ""
    
    def validate_transition(
        self,
        prompt_metadata: PromptWithMetadata,
        target_state: str,
        operation: str = "transition"
    ) -> Tuple[bool, str]:
        """
        Comprehensive transition validation.
        
        Args:
            prompt_metadata: Current prompt metadata
            target_state: Desired state
            operation: Operation name (for error messages)
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        current_state = prompt_metadata.lifecycle_state
        
        # Check basic transition validity
        can_transition, error = self.can_transition(current_state, target_state)
        if not can_transition:
            return False, error
        
        # Check evaluation requirement for approval
        is_valid, error = self.validate_evaluation_required(prompt_metadata, target_state)
        if not is_valid:
            return False, error
        
        # Check not archived for active operations
        if target_state not in ["archived", "draft"]:
            is_valid, error = self.validate_not_archived(prompt_metadata, operation)
            if not is_valid:
                return False, error
        
        return True, ""
    
    def enforce_transition(
        self,
        prompt_metadata: PromptWithMetadata,
        target_state: str,
        operation: str = "transition"
    ) -> None:
        """
        Enforce transition with exception on failure.
        
        Args:
            prompt_metadata: Prompt metadata
            target_state: Desired state
            operation: Operation name
        
        Raises:
            ValueError: If transition is invalid
        """
        is_valid, error = self.validate_transition(
            prompt_metadata,
            target_state,
            operation
        )
        
        if not is_valid:
            raise ValueError(f"Invalid lifecycle transition: {error}")
        
        # Transition is valid, update state
        prompt_metadata.lifecycle_state = target_state
