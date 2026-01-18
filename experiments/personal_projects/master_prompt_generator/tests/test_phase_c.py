"""
Phase C Tests - Lifecycle and Version Integrity.

Tests enforce correctness:
- Illegal lifecycle transitions
- Regression blocking approval
- Breaking change detection
- Version immutability after approval
"""

import pytest
from core import (
    PromptGenerator,
    PromptEvaluator,
    PromptRefiner,
    ApprovalLogic,
    LifecycleGuard,
    VersionGuard,
    BreakingChangeDetector,
    PromptWithMetadata,
    EvaluationResult
)


class TestLifecycleGuard:
    """Test lifecycle transition enforcement."""
    
    def test_cannot_approve_unevaluated(self):
        """Cannot approve prompt that hasn't been evaluated."""
        guard = LifecycleGuard()
        prompt = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Test prompt",
            full_prompt="Test prompt",
            lifecycle_state="generated",
            evaluation_score_after=None
        )
        
        is_valid, error = guard.validate_evaluation_required(prompt, "approved")
        assert not is_valid
        assert "evaluated" in error.lower()
    
    def test_cannot_refine_archived(self):
        """Cannot refine archived prompt."""
        guard = LifecycleGuard()
        prompt = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Test prompt",
            full_prompt="Test prompt",
            lifecycle_state="archived"
        )
        
        is_valid, error = guard.validate_not_archived(prompt, "refine")
        assert not is_valid
        assert "archived" in error.lower()
    
    def test_valid_transitions(self):
        """Valid transitions are allowed."""
        guard = LifecycleGuard()
        
        # Generated -> Evaluated
        is_valid, error = guard.can_transition("generated", "evaluated")
        assert is_valid
        
        # Evaluated -> Refined
        is_valid, error = guard.can_transition("evaluated", "refined")
        assert is_valid
        
        # Evaluated -> Approved
        is_valid, error = guard.can_transition("evaluated", "approved")
        assert is_valid
    
    def test_invalid_transitions(self):
        """Invalid transitions are rejected."""
        guard = LifecycleGuard()
        
        # Cannot skip from generated to approved
        is_valid, error = guard.can_transition("generated", "approved")
        assert not is_valid
        
        # Cannot go backwards from approved to evaluated
        is_valid, error = guard.can_transition("approved", "evaluated")
        assert not is_valid


class TestVersionGuard:
    """Test version integrity enforcement."""
    
    def test_version_format_validation(self):
        """Version format must be MAJOR.MINOR.PATCH."""
        guard = VersionGuard()
        
        # Valid
        is_valid, _ = guard.validate_version_format("1.0.0")
        assert is_valid
        
        # Invalid
        is_valid, _ = guard.validate_version_format("1.0")
        assert not is_valid
        
        is_valid, _ = guard.validate_version_format("v1.0.0")
        assert not is_valid
    
    def test_version_monotonicity(self):
        """Child version must be greater than parent."""
        guard = VersionGuard()
        
        # Valid: 1.0.0 -> 1.1.0
        is_valid, _ = guard.validate_monotonic("1.0.0", "1.1.0")
        assert is_valid
        
        # Invalid: 1.1.0 -> 1.0.0
        is_valid, _ = guard.validate_monotonic("1.1.0", "1.0.0")
        assert not is_valid
        
        # Invalid: 1.0.0 -> 1.0.0
        is_valid, _ = guard.validate_monotonic("1.0.0", "1.0.0")
        assert not is_valid
    
    def test_approved_immutability(self):
        """Approved prompts are immutable."""
        guard = VersionGuard()
        prompt = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Test",
            full_prompt="Test",
            version="1.0.0",
            lifecycle_state="approved"
        )
        
        is_valid, error = guard.validate_immutability(prompt, "edit")
        assert not is_valid
        assert "immutable" in error.lower()


class TestBreakingChangeDetector:
    """Test breaking change detection."""
    
    def test_technique_change_detection(self):
        """Detect technique changes."""
        detector = BreakingChangeDetector()
        
        old = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Generate text. Example 1: ... Example 2: ...",
            full_prompt="Generate text. Example 1: ... Example 2: ...",
            target_model="claude"
        )
        
        new = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Generate text.",
            full_prompt="Generate text.",
            target_model="claude"
        )
        
        has_breaking, reasons = detector.detect_breaking_changes(old, new)
        # Should detect technique change (few-shot -> zero-shot)
        assert has_breaking or len(reasons) > 0
    
    def test_output_format_change_detection(self):
        """Detect output format changes."""
        detector = BreakingChangeDetector()
        
        old = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Generate output in JSON format.",
            full_prompt="Generate output in JSON format.",
            target_model="claude"
        )
        
        new = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Generate output in Markdown format.",
            full_prompt="Generate output in Markdown format.",
            target_model="claude"
        )
        
        has_breaking, reasons = detector.detect_breaking_changes(old, new)
        assert has_breaking
        assert any("format" in r.lower() for r in reasons)


class TestRegressionEnforcement:
    """Test regression blocking approval."""
    
    def test_regression_blocks_approval(self):
        """Regression must block approval."""
        approval = ApprovalLogic(quality_threshold=7.0)
        
        current = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Test",
            full_prompt="Test",
            evaluation_score_after=6.5
        )
        
        previous = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Test",
            full_prompt="Test",
            evaluation_score_after=8.0,
            version="1.0.0"
        )
        
        eval_result = EvaluationResult(
            total_score=6.5,
            clarity=7.0,
            completeness=6.0,
            structure=7.0,
            best_practices=6.0,
            specificity=6.0,
            reusability=6.0,
            has_regression=True
        )
        
        can_approve, blockers = approval.check_approval_readiness(
            current,
            eval_result,
            previous
        )
        
        assert not can_approve
        assert any("regression" in b.lower() for b in blockers)


class TestApprovalImmutability:
    """Test that approved prompts are immutable."""
    
    def test_cannot_modify_approved(self):
        """Cannot modify approved prompt."""
        guard = VersionGuard()
        prompt = PromptWithMetadata(
            system_prompt=None,
            user_prompt="Test",
            full_prompt="Test",
            version="1.0.0",
            lifecycle_state="approved"
        )
        
        is_valid, error = guard.validate_immutability(prompt, "modify")
        assert not is_valid
        assert "immutable" in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
