"""
Prompt Smell Detector - Anti-Pattern Detection

This module identifies common prompt anti-patterns that degrade quality,
explains why they're problematic, and suggests targeted fixes.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import re


@dataclass
class AntiPattern:
    """Represents a detected anti-pattern in a prompt."""
    name: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    why_problematic: str
    location: str  # Where in prompt it was found
    suggestion: str
    confidence: float  # 0.0 to 1.0


class PromptSmellDetector:
    """
    Detects anti-patterns in prompts that indicate quality issues.
    
    Anti-patterns are common mistakes that reduce prompt effectiveness,
    increase token costs, or lead to poor outputs.
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> List[Dict]:
        """Initialize anti-pattern detection rules."""
        return [
            {
                "name": "over_constrained",
                "pattern": r"(must|should|need to|required to).{0,50}(must|should|need to|required to).{0,50}(must|should|need to|required to)",
                "severity": "medium",
                "description": "Excessive constraints in single instruction",
                "why_problematic": "Too many constraints can confuse the model and reduce flexibility. May lead to contradictory requirements.",
                "suggestion": "Break into separate, clear requirements. Use numbered lists for multiple constraints."
            },
            {
                "name": "conflicting_instructions",
                "patterns": [
                    (r"do not", r"must|should|need to"),
                    (r"avoid", r"include|add|use"),
                    (r"never", r"always|must"),
                ],
                "severity": "high",
                "description": "Conflicting positive and negative instructions",
                "why_problematic": "Conflicting instructions create ambiguity. Model may ignore one or produce inconsistent outputs.",
                "suggestion": "Clarify which instruction takes precedence. Use positive framing when possible."
            },
            {
                "name": "excessive_verbosity",
                "pattern": r".{500,}",  # Very long single instruction
                "severity": "low",
                "description": "Excessively verbose prompt without structure",
                "why_problematic": "Long, unstructured prompts waste tokens and reduce clarity. Model may miss key instructions.",
                "suggestion": "Break into sections with clear headers. Use bullet points or numbered lists."
            },
            {
                "name": "examples_overwhelming",
                "pattern": r"Example\s+\d+.*Example\s+\d+.*Example\s+\d+.*Example\s+\d+.*Example\s+\d+",
                "severity": "medium",
                "description": "Too many examples overshadowing instructions",
                "why_problematic": "Excessive examples can make the model focus on pattern matching rather than understanding the task.",
                "suggestion": "Limit to 2-3 high-quality examples. Ensure instructions are clear even without examples."
            },
            {
                "name": "output_format_leakage",
                "patterns": [
                    (r"output.*json", r"markdown|text|plain"),
                    (r"return.*json", r"format.*text"),
                ],
                "severity": "high",
                "description": "Conflicting output format specifications",
                "why_problematic": "Unclear output format leads to parsing errors and inconsistent results.",
                "suggestion": "Specify output format once, clearly. Use explicit format markers (```json, etc.)."
            },
            {
                "name": "redundant_role_definition",
                "pattern": r"(You are|You're|Act as).{0,200}(You are|You're|Act as)",
                "severity": "low",
                "description": "Multiple role definitions in same prompt",
                "why_problematic": "Redundant role definitions waste tokens and may create confusion about primary role.",
                "suggestion": "Define role once, clearly. If multiple roles needed, use structured sections."
            },
            {
                "name": "vague_instructions",
                "patterns": [
                    r"\b(some|few|several|many|various)\b",
                    r"\b(good|better|best|nice|appropriate)\b.*\b(way|manner|style)\b",
                ],
                "severity": "medium",
                "description": "Vague, non-specific instructions",
                "why_problematic": "Vague instructions lead to inconsistent outputs. Model interprets 'some' or 'good' differently each time.",
                "suggestion": "Use specific numbers, clear criteria, and measurable requirements."
            },
            {
                "name": "missing_output_format",
                "pattern": r"^(?!.*(?:output|return|format|structure|json|markdown|xml|yaml)).*$",
                "severity": "high",
                "description": "No explicit output format specified",
                "why_problematic": "Without format specification, model may return inconsistent structures, making parsing difficult.",
                "suggestion": "Always specify output format explicitly: JSON, Markdown, plain text, etc."
            },
            {
                "name": "negative_framing_overuse",
                "pattern": r"(don't|do not|avoid|never|shouldn't|must not).{0,100}(don't|do not|avoid|never|shouldn't|must not).{0,100}(don't|do not|avoid|never|shouldn't|must not)",
                "severity": "medium",
                "description": "Excessive use of negative instructions",
                "why_problematic": "Negative framing is harder for models to process. Positive instructions are clearer and more effective.",
                "suggestion": "Reframe negative instructions as positive requirements. Instead of 'don't include X', say 'include only Y and Z'."
            },
            {
                "name": "nested_conditionals",
                "pattern": r"if.*if.*if",
                "severity": "low",
                "description": "Deeply nested conditional logic",
                "why_problematic": "Complex nested conditionals are hard for models to parse correctly. May lead to missed conditions.",
                "suggestion": "Flatten conditional logic. Use separate, clear instructions for each scenario."
            },
            {
                "name": "token_waste",
                "pattern": r"\b(very|really|quite|extremely|incredibly|absolutely)\b.*\b(very|really|quite|extremely|incredibly|absolutely)\b",
                "severity": "low",
                "description": "Redundant intensifiers wasting tokens",
                "why_problematic": "Redundant words increase token count without adding value, increasing cost.",
                "suggestion": "Remove redundant intensifiers. Use precise, direct language."
            },
            {
                "name": "missing_constraints",
                "pattern": r"generate|create|write|produce",
                "check": lambda m, prompt: self._check_missing_constraints(prompt),
                "severity": "medium",
                "description": "Generation instruction without constraints",
                "why_problematic": "Without constraints, outputs may be too long, off-topic, or in wrong format.",
                "suggestion": "Add constraints: length limits, format requirements, scope boundaries."
            },
        ]
    
    def detect(self, prompt: str, context: Dict = None) -> List[AntiPattern]:
        """
        Detect anti-patterns in a prompt.
        
        Args:
            prompt: The prompt text to analyze
            context: Optional context (model, use case, etc.)
        
        Returns:
            List of detected anti-patterns
        """
        detected = []
        prompt_lower = prompt.lower()
        
        for pattern_def in self.patterns:
            # Handle different pattern types
            if "pattern" in pattern_def:
                try:
                    pattern = pattern_def["pattern"]
                    if pattern and isinstance(pattern, str) and len(pattern) > 0:
                        matches = re.finditer(pattern, prompt_lower, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            detected.append(self._create_anti_pattern(pattern_def, match, prompt))
                except re.error:
                    # Skip invalid regex patterns
                    continue
            
            elif "patterns" in pattern_def:
                # Multiple patterns that must both match (conflicting)
                try:
                    for pattern_pair in pattern_def["patterns"]:
                        if (isinstance(pattern_pair, (list, tuple)) and len(pattern_pair) >= 2 and
                            isinstance(pattern_pair[0], str) and isinstance(pattern_pair[1], str) and
                            len(pattern_pair[0]) > 0 and len(pattern_pair[1]) > 0):
                            if re.search(pattern_pair[0], prompt_lower) and re.search(pattern_pair[1], prompt_lower):
                                detected.append(self._create_anti_pattern(pattern_def, None, prompt, is_conflict=True))
                except re.error:
                    # Skip invalid regex patterns
                    continue
            
            elif "check" in pattern_def:
                # Custom check function
                try:
                    if pattern_def["check"](None, prompt):
                        detected.append(self._create_anti_pattern(pattern_def, None, prompt))
                except Exception:
                    # Skip check functions that fail
                    continue
        
        # Remove duplicates and sort by severity
        detected = self._deduplicate(detected)
        detected.sort(key=lambda x: self._severity_score(x.severity), reverse=True)
        
        return detected
    
    def _create_anti_pattern(
        self, 
        pattern_def: Dict, 
        match: re.Match = None, 
        prompt: str = None,
        is_conflict: bool = False
    ) -> AntiPattern:
        """Create AntiPattern object from detection."""
        location = "unknown"
        if match:
            start, end = match.span()
            location = f"characters {start}-{end}"
            # Get context
            context_start = max(0, start - 50)
            context_end = min(len(prompt), end + 50)
            location += f": ...{prompt[context_start:context_end]}..."
        
        return AntiPattern(
            name=pattern_def["name"],
            severity=pattern_def["severity"],
            description=pattern_def["description"],
            why_problematic=pattern_def["why_problematic"],
            location=location,
            suggestion=pattern_def["suggestion"],
            confidence=self._calculate_confidence(pattern_def, match, prompt)
        )
    
    def _check_missing_constraints(self, prompt: str) -> bool:
        """Check if generation instruction lacks constraints."""
        has_generate = bool(re.search(r"generate|create|write|produce", prompt.lower()))
        has_constraints = bool(re.search(
            r"(length|limit|maximum|minimum|format|structure|constraint|requirement|must|should)",
            prompt.lower()
        ))
        return has_generate and not has_constraints
    
    def _calculate_confidence(self, pattern_def: Dict, match: re.Match, prompt: str) -> float:
        """Calculate confidence score for detection."""
        base_confidence = 0.7
        
        # Increase confidence if pattern is very specific
        if "pattern" in pattern_def and len(pattern_def["pattern"]) > 50:
            base_confidence += 0.1
        
        # Increase if multiple matches
        if match and "pattern" in pattern_def:
            pattern = pattern_def["pattern"]
            if pattern and isinstance(pattern, str) and len(pattern) > 0:
                try:
                    all_matches = list(re.finditer(pattern, prompt.lower()))
                    if len(all_matches) > 1:
                        base_confidence += 0.1
                except re.error:
                    # Invalid regex pattern - skip confidence boost
                    pass
        
        return min(1.0, base_confidence)
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting."""
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return scores.get(severity, 0)
    
    def _deduplicate(self, patterns: List[AntiPattern]) -> List[AntiPattern]:
        """Remove duplicate anti-patterns."""
        seen = set()
        unique = []
        for pattern in patterns:
            key = (pattern.name, pattern.location)
            if key not in seen:
                seen.add(key)
                unique.append(pattern)
        return unique
    
    def generate_report(self, patterns: List[AntiPattern]) -> str:
        """Generate human-readable report of detected anti-patterns."""
        if not patterns:
            return "✅ No anti-patterns detected. Prompt follows best practices."
        
        report = f"⚠️ Detected {len(patterns)} anti-pattern(s):\n\n"
        
        for pattern in patterns:
            report += f"**{pattern.name.upper().replace('_', ' ')}** ({pattern.severity.upper()})\n"
            report += f"- Description: {pattern.description}\n"
            report += f"- Why problematic: {pattern.why_problematic}\n"
            report += f"- Location: {pattern.location}\n"
            report += f"- Suggestion: {pattern.suggestion}\n"
            report += f"- Confidence: {pattern.confidence:.0%}\n\n"
        
        return report
    
    def get_fix_suggestions(self, patterns: List[AntiPattern]) -> List[str]:
        """Get prioritized list of fix suggestions."""
        suggestions = []
        for pattern in sorted(patterns, key=lambda x: self._severity_score(x.severity), reverse=True):
            suggestions.append(f"[{pattern.severity.upper()}] {pattern.suggestion}")
        return suggestions


def detect_prompt_smells(prompt: str, context: Dict = None) -> Tuple[List[AntiPattern], str]:
    """
    Convenience function to detect anti-patterns and generate report.
    
    Returns:
        (patterns, report_string)
    """
    detector = PromptSmellDetector()
    patterns = detector.detect(prompt, context)
    report = detector.generate_report(patterns)
    return patterns, report
