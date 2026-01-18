"""
Prompt Refiner - Iterative improvement with versioning.

Refines prompts based on evaluation results, creates new versions,
tracks parent relationships, and manages version increments.
"""

from typing import Optional
from datetime import datetime

from .prompt_generator import PromptGenerator, PromptWithMetadata
from .prompt_evaluator import EvaluationResult
from .model_manager import ModelManager
from .breaking_change_detector import BreakingChangeDetector
from .lifecycle_guard import LifecycleGuard


class PromptRefiner:
    """
    Refines prompts based on evaluation feedback.
    
    Creates new versions with proper versioning, tracks parent
    relationships, and documents change reasons.
    """
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        """
        Initialize refiner.
        
        Args:
            model_manager: ModelManager instance
        """
        self.model_manager = model_manager or ModelManager()
        self.generator = PromptGenerator(model_manager)
        self.breaking_detector = BreakingChangeDetector()
        self.lifecycle_guard = LifecycleGuard()
    
    def _increment_version(
        self,
        current_version: str,
        change_type: str
    ) -> str:
        """
        Increment version based on change type.
        
        Args:
            current_version: Current version string (MAJOR.MINOR.PATCH)
            change_type: "major", "minor", or "patch"
        
        Returns:
            New version string
        """
        parts = current_version.split(".")
        if len(parts) != 3:
            # Default to 1.0.0 if invalid
            parts = ["1", "0", "0"]
        
        major, minor, patch = map(int, parts)
        
        if change_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif change_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def _determine_change_type(
        self,
        original_prompt: PromptWithMetadata,
        refined_prompt_text: str,
        evaluation_result: EvaluationResult
    ) -> str:
        """
        Determine version increment type based on changes.
        
        Uses breaking change detector to identify major changes.
        
        Returns:
            "major", "minor", or "patch"
        """
        # Create temporary metadata for comparison
        temp_metadata = PromptWithMetadata(
            system_prompt=original_prompt.system_prompt,
            user_prompt=refined_prompt_text,  # Use refined text as user prompt for comparison
            full_prompt=refined_prompt_text,
            target_model=original_prompt.target_model,
            version="temp"
        )
        
        # Check for breaking changes
        has_breaking, reasons = self.breaking_detector.requires_major_version(
            original_prompt,
            temp_metadata
        )
        
        if has_breaking:
            return "major"
        
        # Minor: Significant improvements or fixes
        if evaluation_result.high_severity_anti_patterns > 0:
            # Fixing high-severity issues
            return "minor"
        elif (original_prompt.evaluation_score_after and 
              evaluation_result.total_score > original_prompt.evaluation_score_after + 0.5):
            # Significant score improvement
            return "minor"
        else:
            # Small fixes
            return "patch"
    
    def _build_refinement_prompt(
        self,
        original_prompt: PromptWithMetadata,
        evaluation_result: EvaluationResult
    ) -> str:
        """Build prompt for refining the original prompt."""
        refinement_prompt = f"""You are an expert prompt engineer. Your task is to refine and improve the following prompt based on evaluation feedback.

ORIGINAL PROMPT:
{original_prompt.full_prompt}

EVALUATION RESULTS:
- Overall Score: {evaluation_result.total_score}/10
- Clarity: {evaluation_result.clarity}/10
- Completeness: {evaluation_result.completeness}/10
- Structure: {evaluation_result.structure}/10
- Best Practices: {evaluation_result.best_practices}/10
- Specificity: {evaluation_result.specificity}/10
- Reusability: {evaluation_result.reusability}/10

"""
        
        # Add anti-pattern fixes
        if evaluation_result.anti_patterns:
            refinement_prompt += "\nISSUES TO FIX:\n"
            for pattern in evaluation_result.anti_patterns:
                refinement_prompt += f"- [{pattern.severity.upper()}] {pattern.description}\n"
                refinement_prompt += f"  Why: {pattern.why_problematic}\n"
                refinement_prompt += f"  Fix: {pattern.suggestion}\n"
        
        refinement_prompt += """
INSTRUCTIONS:
1. Address all identified issues
2. Improve low-scoring metrics
3. Maintain the core purpose and structure
4. Keep model-specific adaptations
5. Ensure output format is clear
6. Make improvements without breaking existing functionality

OUTPUT:
Provide the refined prompt in the same format as the original:
- System Prompt (if applicable): [system prompt]
- User Prompt: [user prompt]
"""
        
        return refinement_prompt
    
    def refine(
        self,
        prompt_metadata: PromptWithMetadata,
        evaluation_result: EvaluationResult,
        generation_model: Optional[str] = None
    ) -> PromptWithMetadata:
        """
        Refine a prompt based on evaluation results.
        
        Enforces lifecycle guard: cannot refine archived prompts.
        """
        # Enforce lifecycle guard
        is_valid, error = self.lifecycle_guard.validate_not_archived(
            prompt_metadata,
            "refine"
        )
        if not is_valid:
            raise ValueError(error)
        """
        Refine a prompt based on evaluation results.
        
        Args:
            prompt_metadata: Original prompt with metadata
            evaluation_result: Evaluation results with issues identified
            generation_model: Model to use for refinement (defaults to original)
        
        Returns:
            New PromptWithMetadata with:
            - Refined prompt text
            - New version (incremented)
            - parent_prompt_id set to original
            - lifecycle_state = "refined"
            - change_reason documented
        """
        if generation_model is None:
            generation_model = prompt_metadata.generated_by or prompt_metadata.target_model
        
        # Build refinement prompt
        refinement_prompt = self._build_refinement_prompt(
            prompt_metadata,
            evaluation_result
        )
        
        # Generate refined prompt
        client = self.model_manager.get_client(generation_model)
        if not client:
            raise ValueError(f"No client available for model: {generation_model}")
        
        response = client.chat.completions.create(
            model=generation_model,
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer specializing in prompt refinement."},
                {"role": "user", "content": refinement_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        refined_text = response.choices[0].message.content
        
        # Parse system/user prompts
        system_prompt = None
        user_prompt = refined_text
        
        if "System Prompt" in refined_text:
            parts = refined_text.split("User Prompt:")
            if len(parts) == 2:
                system_part = parts[0].replace("System Prompt", "").replace(":", "").strip()
                system_prompt = system_part if system_part else None
                user_prompt = parts[1].strip()
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        
        # Determine change type based on actual changes
        change_type = self._determine_change_type(
            prompt_metadata,
            full_prompt,
            evaluation_result
        )
        new_version = self._increment_version(prompt_metadata.version, change_type)
        
        # Build change reason
        change_reason = f"Refinement to address evaluation feedback (score: {evaluation_result.total_score}/10)"
        if evaluation_result.anti_patterns:
            change_reason += f". Fixed {len(evaluation_result.anti_patterns)} anti-pattern(s)"
        
        # Create new metadata
        refined_metadata = PromptWithMetadata(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            full_prompt=full_prompt,
            id=__import__("uuid").uuid4().hex,
            version=new_version,
            parent_prompt_id=prompt_metadata.id,
            lifecycle_state="refined",
            use_case=prompt_metadata.use_case,
            category=prompt_metadata.category,
            complexity_tier=prompt_metadata.complexity_tier,
            target_model=prompt_metadata.target_model,
            change_reason=change_reason,
            evaluation_score_before=prompt_metadata.evaluation_score_after,
            generated_by=generation_model,
            refined_by=generation_model,
            author="ai"
        )
        
        # Recalculate economics for refined prompt
        economics = self.generator.token_economics.analyze_prompt_economics(
            prompt=full_prompt,
            use_case=prompt_metadata.use_case,
            complexity_tier=prompt_metadata.complexity_tier,
            models=[prompt_metadata.target_model]
        )
        
        refined_metadata.estimated_input_tokens = economics.input_tokens
        refined_metadata.estimated_output_tokens = economics.output_tokens
        refined_metadata.estimated_cost_per_run = economics.estimated_cost
        refined_metadata.verbosity_efficiency_score = economics.verbosity_efficiency_score
        refined_metadata.cost_quality_tradeoff = economics.cost_quality_tradeoff
        
        return refined_metadata
