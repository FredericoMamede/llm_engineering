"""
Prompt Evaluator - Quality assessment with multi-layered evaluation.

Evaluates prompts on 6 quality criteria, detects anti-patterns,
analyzes token economics, and produces comprehensive evaluation results.
"""

from typing import Dict, List
from dataclasses import dataclass, field

from .prompt_smell_detector import PromptSmellDetector, AntiPattern
from .token_economics import TokenEconomics


@dataclass
class EvaluationResult:
    """Comprehensive evaluation result."""
    # Overall score
    total_score: float  # 0-10, average of 6 metrics
    
    # Individual metrics (0-10 each)
    clarity: float
    completeness: float
    structure: float
    best_practices: float
    specificity: float
    reusability: float
    
    # Anti-patterns
    anti_patterns: List[AntiPattern] = field(default_factory=list)
    has_anti_patterns: bool = False
    high_severity_anti_patterns: int = 0
    
    # Token economics (already in metadata, but included for convenience)
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_cost: Dict[str, float] = field(default_factory=dict)
    verbosity_efficiency_score: float = 0.0
    
    # Quality flags
    meets_threshold: bool = False  # score >= 8.0
    has_regression: bool = False
    can_approve: bool = False  # meets_threshold and no blockers


class PromptEvaluator:
    """
    Evaluates prompt quality using multiple criteria.
    
    Provides:
    - 6 quality metric scores
    - Anti-pattern detection
    - Token economics analysis
    - Approval readiness check
    """
    
    def __init__(self, quality_threshold: float = 8.0):
        """
        Initialize evaluator.
        
        Args:
            quality_threshold: Minimum score for approval (default 8.0)
        """
        self.quality_threshold = quality_threshold
        self.smell_detector = PromptSmellDetector()
        self.token_economics = TokenEconomics()
    
    def _score_clarity(self, prompt: str) -> float:
        """
        Score clarity: Instructions are unambiguous.
        
        Checks:
        - Specific language (not vague)
        - Clear task definition
        - No ambiguous terms
        """
        score = 10.0
        
        # Check for vague terms
        vague_terms = ["some", "few", "several", "many", "various", "appropriate", "good", "better"]
        vague_count = sum(1 for term in vague_terms if term in prompt.lower())
        score -= min(2.0, vague_count * 0.3)
        
        # Check for clear task definition
        task_indicators = ["task is", "your task", "generate", "create", "write", "analyze"]
        has_task = any(indicator in prompt.lower() for indicator in task_indicators)
        if not has_task:
            score -= 1.0
        
        # Check for ambiguous instructions
        if "?" in prompt and prompt.count("?") > 2:
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_completeness(self, prompt: str, requirements: List[str] = None) -> float:
        """
        Score completeness: All requirements addressed.
        
        Checks:
        - Output format specified
        - Constraints defined
        - Examples included (if needed)
        """
        score = 10.0
        
        # Output format
        format_indicators = ["json", "markdown", "xml", "yaml", "format", "output format", "structure"]
        has_format = any(indicator in prompt.lower() for indicator in format_indicators)
        if not has_format:
            score -= 2.0
        
        # Constraints
        constraint_indicators = ["must", "should", "require", "constraint", "limit"]
        has_constraints = any(indicator in prompt.lower() for indicator in constraint_indicators)
        if not has_constraints:
            score -= 1.0
        
        # Examples (check if complex task might need examples)
        if len(prompt) > 500:  # Longer prompts might benefit from examples
            has_examples = "example" in prompt.lower() or "sample" in prompt.lower()
            if not has_examples:
                score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_structure(self, prompt: str) -> float:
        """
        Score structure: Well-organized and formatted.
        
        Checks:
        - Clear sections
        - Proper formatting
        - Readable organization
        """
        score = 10.0
        
        # Check for structure markers
        structure_markers = ["##", "###", "1.", "2.", "-", "*", "•"]
        has_structure = any(marker in prompt for marker in structure_markers)
        if not has_structure and len(prompt) > 200:
            score -= 1.5
        
        # Check for excessive length without breaks
        if len(prompt) > 1000 and prompt.count("\n\n") < 3:
            score -= 1.0
        
        # Check for delimiters (good practice)
        has_delimiters = "```" in prompt or "---" in prompt or "===" in prompt
        if not has_delimiters and len(prompt) > 300:
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_best_practices(self, prompt: str) -> float:
        """
        Score best practices: Follows guidelines.
        
        Checks:
        - Role definition (if applicable)
        - Positive instructions
        - Clear delimiters
        - Proper formatting
        """
        score = 10.0
        
        # Positive instructions (prefer over negative)
        negative_count = sum(1 for word in ["don't", "do not", "avoid", "never", "must not"] 
                            if word in prompt.lower())
        positive_count = sum(1 for word in ["include", "use", "provide", "generate", "create"]
                             if word in prompt.lower())
        
        if negative_count > positive_count:
            score -= 1.0
        
        # Role definition (check if conversational/assistant prompt)
        if any(word in prompt.lower() for word in ["assistant", "help", "you are"]):
            has_role = "you are" in prompt.lower() or "act as" in prompt.lower()
            if not has_role:
                score -= 0.5
        
        # Clear delimiters for content
        if len(prompt) > 300:
            has_delimiters = "```" in prompt or "---" in prompt
            if not has_delimiters:
                score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_specificity(self, prompt: str, complexity_tier: int) -> float:
        """
        Score specificity: Appropriate level of detail.
        
        Checks:
        - Detail matches complexity tier
        - Specific requirements
        - Not too vague, not too verbose
        """
        score = 10.0
        
        # Check detail level matches tier
        prompt_length = len(prompt)
        optimal_lengths = {1: 100, 2: 300, 3: 800, 4: 1500}
        optimal = optimal_lengths.get(complexity_tier, 500)
        
        if prompt_length < optimal * 0.5:
            score -= 1.0  # Too brief
        elif prompt_length > optimal * 2:
            score -= 1.0  # Too verbose
        
        # Check for specific numbers/requirements
        has_specifics = any(char.isdigit() for char in prompt)
        if not has_specifics and complexity_tier >= 2:
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _score_reusability(self, prompt: str) -> float:
        """
        Score reusability: Can be adapted/parameterized.
        
        Checks:
        - Not too specific to one case
        - Can be templated
        - Generalizable structure
        """
        score = 10.0
        
        # Check for hardcoded values that limit reusability
        hardcoded_indicators = ["specific company", "exact date", "precise number"]
        hardcoded_count = sum(1 for indicator in hardcoded_indicators 
                             if indicator in prompt.lower())
        if hardcoded_count > 2:
            score -= 1.0
        
        # Check if structure is generalizable
        has_template_structure = any(marker in prompt for marker in ["{", "[", "placeholder"])
        if has_template_structure:
            score += 0.5  # Bonus for parameterization
        
        return max(0.0, min(10.0, score))
    
    def _calculate_anti_pattern_penalty(self, anti_patterns: List[AntiPattern]) -> float:
        """Calculate score penalty based on anti-patterns."""
        penalty = 0.0
        
        for pattern in anti_patterns:
            severity_scores = {"critical": 2.0, "high": 1.0, "medium": 0.5, "low": 0.2}
            penalty += severity_scores.get(pattern.severity, 0.0) * pattern.confidence
        
        return min(3.0, penalty)  # Cap penalty at 3.0
    
    def score_prompt(
        self,
        prompt_metadata,
        previous_score: Optional[float] = None
    ) -> EvaluationResult:
        """
        Evaluate a prompt and produce comprehensive result.
        
        Args:
            prompt_metadata: PromptWithMetadata object
            previous_score: Score from previous version (for regression detection)
        
        Returns:
            EvaluationResult with all metrics and flags
        """
        prompt = prompt_metadata.full_prompt
        
        # Score 6 quality metrics
        clarity = self._score_clarity(prompt)
        completeness = self._score_completeness(prompt)
        structure = self._score_structure(prompt)
        best_practices = self._score_best_practices(prompt)
        specificity = self._score_specificity(prompt, prompt_metadata.complexity_tier)
        reusability = self._score_reusability(prompt)
        
        # Calculate total score (average of 6 metrics)
        total_score = (clarity + completeness + structure + 
                      best_practices + specificity + reusability) / 6.0
        
        # Detect anti-patterns
        anti_patterns = self.smell_detector.detect(prompt)
        has_anti_patterns = len(anti_patterns) > 0
        high_severity = [p for p in anti_patterns if p.severity in ["high", "critical"]]
        high_severity_count = len(high_severity)
        
        # Apply anti-pattern penalty
        penalty = self._calculate_anti_pattern_penalty(anti_patterns)
        total_score = max(0.0, total_score - penalty)
        
        # Check for regression
        has_regression = False
        if previous_score is not None:
            score_drop = previous_score - total_score
            if score_drop > 0.5:  # More than 0.5 point drop
                has_regression = True
        
        # Check approval readiness
        meets_threshold = total_score >= self.quality_threshold
        can_approve = (meets_threshold and 
                      not has_regression and 
                      high_severity_count == 0)
        
        # Create result
        result = EvaluationResult(
            total_score=round(total_score, 2),
            clarity=round(clarity, 2),
            completeness=round(completeness, 2),
            structure=round(structure, 2),
            best_practices=round(best_practices, 2),
            specificity=round(specificity, 2),
            reusability=round(reusability, 2),
            anti_patterns=anti_patterns,
            has_anti_patterns=has_anti_patterns,
            high_severity_anti_patterns=high_severity_count,
            estimated_input_tokens=prompt_metadata.estimated_input_tokens,
            estimated_output_tokens=prompt_metadata.estimated_output_tokens,
            estimated_cost=prompt_metadata.estimated_cost_per_run,
            verbosity_efficiency_score=prompt_metadata.verbosity_efficiency_score,
            meets_threshold=meets_threshold,
            has_regression=has_regression,
            can_approve=can_approve
        )
        
        return result
    
    def update_prompt_metadata(
        self,
        prompt_metadata,
        evaluation_result: EvaluationResult,
        previous_score: Optional[float] = None
    ) -> None:
        """
        Update prompt metadata with evaluation results.
        
        Args:
            prompt_metadata: PromptWithMetadata to update
            evaluation_result: EvaluationResult
            previous_score: Previous version score (if refining)
        """
        prompt_metadata.lifecycle_state = "evaluated"
        prompt_metadata.evaluation_score_after = evaluation_result.total_score
        
        if previous_score is not None:
            prompt_metadata.evaluation_score_before = previous_score
            prompt_metadata.evaluation_delta = (
                evaluation_result.total_score - previous_score
            )
        
        prompt_metadata.has_anti_patterns = evaluation_result.has_anti_patterns
        prompt_metadata.anti_patterns_detected = [
            {
                "name": p.name,
                "severity": p.severity,
                "description": p.description,
                "suggestion": p.suggestion
            }
            for p in evaluation_result.anti_patterns
        ]
        prompt_metadata.updated_at = __import__("datetime").datetime.utcnow().isoformat()
