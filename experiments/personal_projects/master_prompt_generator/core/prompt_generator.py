"""
Prompt Generator - Core generation logic with model adaptation.

This module implements the critical path for prompt generation:
1. Build meta-prompt
2. Load model profile
3. Apply model-specific adaptations
4. Generate prompt via LLM
5. Create metadata with lifecycle state
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import yaml
from pathlib import Path

from .model_manager import ModelManager
from .token_economics import TokenEconomics


@dataclass
class PromptWithMetadata:
    """Complete prompt with full metadata schema."""
    # Core content
    system_prompt: Optional[str]
    user_prompt: str
    full_prompt: str
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    parent_prompt_id: Optional[str] = None
    lifecycle_state: str = "generated"
    
    # Context
    use_case: str = ""
    category: str = ""
    complexity_tier: int = 1
    target_model: str = ""
    
    # Evolution tracking
    change_reason: str = ""
    evaluation_score_before: Optional[float] = None
    evaluation_score_after: Optional[float] = None
    evaluation_delta: Optional[float] = None
    
    # Economics
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_cost_per_run: Dict[str, float] = field(default_factory=dict)
    verbosity_efficiency_score: float = 0.0
    cost_quality_tradeoff: str = "balanced"
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    approved_at: Optional[str] = None
    archived_at: Optional[str] = None
    
    # Authorship
    author: str = "ai"
    generated_by: str = ""
    refined_by: Optional[str] = None
    
    # Quality flags
    has_anti_patterns: bool = False
    anti_patterns_detected: List[Dict] = field(default_factory=list)
    model_adaptations_applied: List[str] = field(default_factory=list)


class PromptGenerator:
    """
    Core prompt generation engine.
    
    Generates prompts using meta-prompting, applies model-specific
    adaptations, and creates full metadata.
    """
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        """
        Initialize prompt generator.
        
        Args:
            model_manager: ModelManager instance (creates new if None)
        """
        self.model_manager = model_manager or ModelManager()
        self.token_economics = TokenEconomics()
        self.model_profiles = self._load_model_profiles()
    
    def _load_model_profiles(self) -> Dict:
        """Load model prompt profiles from YAML."""
        config_path = Path(__file__).parent.parent / "config" / "model_prompt_profiles.yaml"
        if not config_path.exists():
            return {}
        
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    def _get_model_profile(self, model_name: str) -> Optional[Dict]:
        """Get profile for a specific model."""
        # Map model name to profile key
        model_lower = model_name.lower()
        
        if "claude" in model_lower:
            return self.model_profiles.get("claude")
        elif "gpt" in model_lower:
            return self.model_profiles.get("gpt")
        elif "gemini" in model_lower:
            return self.model_profiles.get("gemini")
        elif "llama" in model_lower:
            return self.model_profiles.get("llama")
        elif "qwen" in model_lower:
            return self.model_profiles.get("qwen")
        elif "deepseek" in model_lower:
            return self.model_profiles.get("deepseek")
        else:
            return self.model_profiles.get("generic")
    
    def _build_meta_prompt(
        self,
        use_case: str,
        category: str,
        complexity_tier: int,
        context: str,
        requirements: List[str],
        target_model: str,
        model_profile: Optional[Dict]
    ) -> str:
        """Build meta-prompt for generating the actual prompt."""
        meta_prompt = f"""You are an expert prompt engineer. Your task is to generate a production-ready prompt for the following use case.

USE CASE: {use_case}
CATEGORY: {category}
COMPLEXITY TIER: {complexity_tier}

REQUIREMENTS:
"""
        for req in requirements:
            meta_prompt += f"- {req}\n"
        
        meta_prompt += f"""
CONTEXT:
{context}

PROMPT ENGINEERING BEST PRACTICES TO APPLY:
1. Clear role/persona definition (if applicable)
2. Specific task description
3. Explicit output format requirements
4. Examples (if few-shot needed)
5. Constraints and guardrails
6. Step-by-step reasoning (if CoT needed)
7. Delimiters for content separation
8. Positive instructions (what to do, not what not to do)

"""
        
        # Add model-specific preferences
        if model_profile and model_profile.get("prefers"):
            meta_prompt += f"\nMODEL-SPECIFIC PREFERENCES FOR {target_model}:\n"
            for pref in model_profile["prefers"]:
                if isinstance(pref, dict) and "description" in pref:
                    meta_prompt += f"- {pref['description']}\n"
                elif isinstance(pref, str):
                    meta_prompt += f"- {pref}\n"
        
        meta_prompt += """
Generate a prompt that:
- Follows all best practices
- Is optimized for the target model
- Has appropriate length for the complexity tier
- Includes necessary examples
- Has clear structure and formatting
- Is production-ready

OUTPUT FORMAT:
Provide the prompt in this structure:
- System Prompt (if applicable): [system prompt]
- User Prompt: [user prompt]
- Notes: [any important considerations]
"""
        
        return meta_prompt
    
    def _apply_model_adaptations(
        self,
        prompt_text: str,
        model_profile: Optional[Dict]
    ) -> tuple[str, List[str]]:
        """
        Apply model-specific adaptations to prompt.
        
        Returns:
            (adapted_prompt, list_of_adaptations_applied)
        """
        if not model_profile:
            return prompt_text, []
        
        adaptations_applied = []
        adapted = prompt_text
        
        # Get adaptation rules
        adaptations = model_profile.get("adaptations", {})
        
        # Apply adaptations based on profile
        if adaptations.get("add_reasoning_framing") and "Let's think" not in adapted:
            adapted = "Let's think through this step by step:\n\n" + adapted
            adaptations_applied.append("added_reasoning_framing")
        
        if adaptations.get("soften_directives"):
            # Replace harsh directives with polite ones
            adapted = adapted.replace("You must", "Please")
            adapted = adapted.replace("You need to", "Consider")
            adaptations_applied.append("softened_directives")
        
        if adaptations.get("enforce_json_schema") and "JSON" not in adapted.upper():
            adapted += "\n\nOutput format: Return ONLY valid JSON, no markdown, no explanations."
            adaptations_applied.append("enforced_json_schema")
        
        if adaptations.get("shorten_instructions"):
            # This is a placeholder - actual shortening would be more complex
            adaptations_applied.append("shortened_instructions")
        
        return adapted, adaptations_applied
    
    def generate(
        self,
        use_case: str,
        category: str,
        complexity_tier: int,
        context: str,
        requirements: Optional[List[str]] = None,
        target_model: str = "claude-sonnet-4-5-20250929",
        generation_model: Optional[str] = None
    ) -> PromptWithMetadata:
        """
        Generate a prompt with full metadata.
        
        Args:
            use_case: Use case description
            category: Category (business, technical, etc.)
            complexity_tier: 1-4 complexity tier
            context: User-provided context
            requirements: Optional list of specific requirements
            target_model: Model the prompt will be used with
            generation_model: Model to use for generation (defaults to target_model)
        
        Returns:
            PromptWithMetadata with lifecycle_state="generated"
        """
        if requirements is None:
            requirements = []
        
        if generation_model is None:
            generation_model = target_model
        
        # Load model profile
        model_profile = self._get_model_profile(target_model)
        
        # Build meta-prompt
        meta_prompt = self._build_meta_prompt(
            use_case=use_case,
            category=category,
            complexity_tier=complexity_tier,
            context=context,
            requirements=requirements,
            target_model=target_model,
            model_profile=model_profile
        )
        
        # Generate prompt using LLM
        client = self.model_manager.get_client(generation_model)
        if not client:
            raise ValueError(f"No client available for model: {generation_model}")
        
        response = client.chat.completions.create(
            model=generation_model,
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer."},
                {"role": "user", "content": meta_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        generated_text = response.choices[0].message.content
        
        # Parse system/user prompts from generated text
        system_prompt = None
        user_prompt = generated_text
        
        if "System Prompt" in generated_text:
            parts = generated_text.split("User Prompt:")
            if len(parts) == 2:
                system_part = parts[0].replace("System Prompt", "").replace(":", "").strip()
                system_prompt = system_part if system_part else None
                user_prompt = parts[1].split("Notes:")[0].strip()
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        
        # Apply model-specific adaptations
        adapted_prompt, adaptations_applied = self._apply_model_adaptations(
            full_prompt,
            model_profile
        )
        
        # Calculate token economics
        economics = self.token_economics.analyze_prompt_economics(
            prompt=adapted_prompt,
            use_case=use_case,
            complexity_tier=complexity_tier,
            models=[target_model]
        )
        
        # Create metadata
        metadata = PromptWithMetadata(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            full_prompt=adapted_prompt,
            version="1.0.0",
            lifecycle_state="generated",
            use_case=use_case,
            category=category,
            complexity_tier=complexity_tier,
            target_model=target_model,
            generated_by=generation_model,
            estimated_input_tokens=economics.input_tokens,
            estimated_output_tokens=economics.output_tokens,
            estimated_cost_per_run=economics.estimated_cost,
            verbosity_efficiency_score=economics.verbosity_efficiency_score,
            cost_quality_tradeoff=economics.cost_quality_tradeoff,
            model_adaptations_applied=adaptations_applied
        )
        
        return metadata
