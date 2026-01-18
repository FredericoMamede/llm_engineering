"""
Breaking Change Detector - Structural change detection.

Detects breaking changes in prompts:
- Technique changes
- Output format changes
- Semantic similarity drops
- Model compatibility changes
"""

from typing import Tuple, List
from .prompt_generator import PromptWithMetadata


class BreakingChangeDetector:
    """
    Detects structural breaking changes between prompt versions.
    
    Breaking changes require MAJOR version increment.
    """
    
    TECHNIQUES = [
        "zero-shot",
        "few-shot",
        "chain-of-thought",
        "tree-of-thought",
        "role-based",
        "self-consistency",
        "reflection",
        "prompt-chaining"
    ]
    
    OUTPUT_FORMATS = [
        "json",
        "markdown",
        "xml",
        "yaml",
        "plain text",
        "structured"
    ]
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize breaking change detector.
        
        Args:
            similarity_threshold: Minimum semantic similarity (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def _detect_technique(self, prompt: str) -> List[str]:
        """Detect prompt techniques used."""
        detected = []
        prompt_lower = prompt.lower()
        
        if "example" in prompt_lower and prompt_lower.count("example") >= 2:
            detected.append("few-shot")
        else:
            detected.append("zero-shot")
        
        if any(phrase in prompt_lower for phrase in ["step by step", "think through", "reasoning"]):
            detected.append("chain-of-thought")
        
        if any(phrase in prompt_lower for phrase in ["you are", "act as", "role"]):
            detected.append("role-based")
        
        return detected
    
    def _detect_output_format(self, prompt: str) -> str:
        """Detect output format requirement."""
        prompt_lower = prompt.lower()
        
        if "json" in prompt_lower and ("output" in prompt_lower or "format" in prompt_lower):
            return "json"
        elif "markdown" in prompt_lower:
            return "markdown"
        elif "xml" in prompt_lower:
            return "xml"
        elif "yaml" in prompt_lower:
            return "yaml"
        elif "structured" in prompt_lower:
            return "structured"
        else:
            return "plain text"
    
    def _calculate_semantic_similarity(
        self,
        prompt1: str,
        prompt2: str
    ) -> float:
        """
        Calculate rough semantic similarity.
        
        Uses simple heuristics:
        - Word overlap
        - Length similarity
        - Structure similarity
        
        Returns:
            Similarity score (0-1)
        """
        # Simple word-based similarity
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Length similarity
        len1, len2 = len(prompt1), len(prompt2)
        length_sim = 1.0 - abs(len1 - len2) / max(len1, len2, 1)
        
        # Combined similarity (weighted)
        similarity = (jaccard * 0.7) + (length_sim * 0.3)
        
        return similarity
    
    def detect_breaking_changes(
        self,
        old_prompt: PromptWithMetadata,
        new_prompt: PromptWithMetadata
    ) -> Tuple[bool, List[str]]:
        """
        Detect breaking changes between two prompt versions.
        
        Args:
            old_prompt: Previous version
            new_prompt: New version
        
        Returns:
            (has_breaking_changes: bool, reasons: List[str])
        """
        reasons = []
        
        # Check technique change
        old_techniques = set(self._detect_technique(old_prompt.full_prompt))
        new_techniques = set(self._detect_technique(new_prompt.full_prompt))
        
        if old_techniques != new_techniques:
            added = new_techniques - old_techniques
            removed = old_techniques - new_techniques
            if added or removed:
                reasons.append(
                    f"Technique change: {old_techniques} → {new_techniques}"
                )
        
        # Check output format change
        old_format = self._detect_output_format(old_prompt.full_prompt)
        new_format = self._detect_output_format(new_prompt.full_prompt)
        
        if old_format != new_format:
            reasons.append(
                f"Output format change: {old_format} → {new_format}"
            )
        
        # Check semantic similarity
        similarity = self._calculate_semantic_similarity(
            old_prompt.full_prompt,
            new_prompt.full_prompt
        )
        
        if similarity < self.similarity_threshold:
            reasons.append(
                f"Semantic similarity drop: {similarity:.2f} < {self.similarity_threshold}"
            )
        
        # Check model compatibility change
        if old_prompt.target_model != new_prompt.target_model:
            reasons.append(
                f"Target model change: {old_prompt.target_model} → {new_prompt.target_model}"
            )
        
        has_breaking = len(reasons) > 0
        
        return has_breaking, reasons
    
    def requires_major_version(
        self,
        old_prompt: PromptWithMetadata,
        new_prompt: PromptWithMetadata
    ) -> Tuple[bool, List[str]]:
        """
        Determine if major version increment is required.
        
        Args:
            old_prompt: Previous version
            new_prompt: New version
        
        Returns:
            (requires_major: bool, reasons: List[str])
        """
        return self.detect_breaking_changes(old_prompt, new_prompt)
