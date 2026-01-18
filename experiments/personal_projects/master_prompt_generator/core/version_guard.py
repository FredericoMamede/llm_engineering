"""
Version Guard - Enforces version integrity.

Ensures versions are monotonic, parent relationships are valid,
and approved versions are immutable.
"""

from typing import Optional, Tuple, List
from .prompt_generator import PromptWithMetadata
import re


class VersionGuard:
    """
    Enforces version integrity rules.
    
    Ensures:
    - Versions are strictly monotonic
    - Parent references are valid
    - Approved versions are immutable
    - Version format is correct (MAJOR.MINOR.PATCH)
    """
    
    VERSION_PATTERN = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')
    
    def __init__(self):
        """Initialize version guard."""
        pass
    
    def validate_version_format(self, version: str) -> Tuple[bool, str]:
        """
        Validate version format (MAJOR.MINOR.PATCH).
        
        Args:
            version: Version string
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if not self.VERSION_PATTERN.match(version):
            return False, (
                f"Invalid version format: '{version}'. "
                "Must be MAJOR.MINOR.PATCH (e.g., '1.0.0')"
            )
        
        return True, ""
    
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """
        Parse version string to components.
        
        Args:
            version: Version string
        
        Returns:
            (major, minor, patch)
        
        Raises:
            ValueError: If version format is invalid
        """
        match = self.VERSION_PATTERN.match(version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        
        return tuple(map(int, match.groups()))
    
    def compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two versions.
        
        Args:
            v1: First version
            v2: Second version
        
        Returns:
            -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
        """
        major1, minor1, patch1 = self.parse_version(v1)
        major2, minor2, patch2 = self.parse_version(v2)
        
        if major1 != major2:
            return -1 if major1 < major2 else 1
        if minor1 != minor2:
            return -1 if minor1 < minor2 else 1
        if patch1 != patch2:
            return -1 if patch1 < patch2 else 1
        
        return 0
    
    def validate_monotonic(
        self,
        parent_version: str,
        child_version: str
    ) -> Tuple[bool, str]:
        """
        Ensure child version is greater than parent.
        
        Args:
            parent_version: Parent version
            child_version: Child version
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        comparison = self.compare_versions(parent_version, child_version)
        
        if comparison >= 0:
            return False, (
                f"Child version '{child_version}' must be greater than "
                f"parent version '{parent_version}'"
            )
        
        return True, ""
    
    def validate_parent_exists(
        self,
        prompt_metadata: PromptWithMetadata,
        parent_lookup: callable
    ) -> Tuple[bool, str]:
        """
        Ensure parent prompt exists and is valid.
        
        Args:
            prompt_metadata: Child prompt metadata
            parent_lookup: Function to look up parent by ID
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if not prompt_metadata.parent_prompt_id:
            # Root version, no parent required
            return True, ""
        
        parent = parent_lookup(prompt_metadata.parent_prompt_id)
        if not parent:
            return False, (
                f"Parent prompt '{prompt_metadata.parent_prompt_id}' not found. "
                "Invalid parent reference."
            )
        
        # Validate version monotonicity
        is_valid, error = self.validate_monotonic(
            parent.version,
            prompt_metadata.version
        )
        if not is_valid:
            return False, error
        
        return True, ""
    
    def validate_immutability(
        self,
        prompt_metadata: PromptWithMetadata,
        operation: str
    ) -> Tuple[bool, str]:
        """
        Ensure approved prompts are immutable.
        
        Args:
            prompt_metadata: Prompt metadata
            operation: Operation attempting to modify
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if prompt_metadata.lifecycle_state == "approved":
            return False, (
                f"Cannot {operation} approved prompt (version {prompt_metadata.version}). "
                "Approved prompts are immutable. Create a new version instead."
            )
        
        return True, ""
    
    def validate_version_integrity(
        self,
        prompt_metadata: PromptWithMetadata,
        parent_lookup: Optional[callable] = None,
        operation: str = "create"
    ) -> Tuple[bool, List[str]]:
        """
        Comprehensive version integrity validation.
        
        Args:
            prompt_metadata: Prompt metadata to validate
            parent_lookup: Optional function to look up parent
            operation: Operation name
        
        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []
        
        # Validate format
        is_valid, error = self.validate_version_format(prompt_metadata.version)
        if not is_valid:
            errors.append(error)
        
        # Validate parent if exists
        if prompt_metadata.parent_prompt_id and parent_lookup:
            is_valid, error = self.validate_parent_exists(
                prompt_metadata,
                parent_lookup
            )
            if not is_valid:
                errors.append(error)
        
        # Validate immutability for approved prompts
        if operation in ["edit", "modify", "update"]:
            is_valid, error = self.validate_immutability(
                prompt_metadata,
                operation
            )
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors
    
    def enforce_version_integrity(
        self,
        prompt_metadata: PromptWithMetadata,
        parent_lookup: Optional[callable] = None,
        operation: str = "create"
    ) -> None:
        """
        Enforce version integrity with exception on failure.
        
        Args:
            prompt_metadata: Prompt metadata
            parent_lookup: Optional function to look up parent
            operation: Operation name
        
        Raises:
            ValueError: If version integrity is violated
        """
        is_valid, errors = self.validate_version_integrity(
            prompt_metadata,
            parent_lookup,
            operation
        )
        
        if not is_valid:
            error_msg = "Version integrity violations:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)
