"""
Token Economics & Cost Analysis

This module provides cost estimation, token counting, and economic analysis
for prompts to help users make informed decisions about prompt design.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import tiktoken


@dataclass
class TokenEstimate:
    """Token usage estimate for a prompt."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: Dict[str, float]  # Per model
    verbosity_efficiency_score: float  # 0-1, higher is better
    cost_quality_tradeoff: str  # "efficient", "balanced", "expensive"


@dataclass
class ModelPricing:
    """Pricing information for a model."""
    input_cost_per_1k: float
    output_cost_per_1k: float
    model_name: str


class TokenEconomics:
    """
    Analyzes token usage and costs for prompts.
    
    Provides:
    - Token counting (input/output)
    - Cost estimation per model
    - Efficiency scoring
    - Cost-quality tradeoff analysis
    """
    
    # Model pricing (per 1K tokens, as of 2025)
    PRICING = {
        "claude-sonnet": ModelPricing(
            input_cost_per_1k=3.0,
            output_cost_per_1k=15.0,
            model_name="Claude Sonnet 4.5"
        ),
        "claude-haiku": ModelPricing(
            input_cost_per_1k=0.25,
            output_cost_per_1k=1.25,
            model_name="Claude 3.5 Haiku"
        ),
        "gpt-5": ModelPricing(
            input_cost_per_1k=5.0,
            output_cost_per_1k=15.0,
            model_name="GPT-5"
        ),
        "gpt-4o": ModelPricing(
            input_cost_per_1k=2.5,
            output_cost_per_1k=10.0,
            model_name="GPT-4o"
        ),
        "gemini-2.5-pro": ModelPricing(
            input_cost_per_1k=1.25,
            output_cost_per_1k=5.0,
            model_name="Gemini 2.5 Pro"
        ),
        "llama3.2:latest": ModelPricing(
            input_cost_per_1k=0.0,  # Free/local
            output_cost_per_1k=0.0,
            model_name="Llama 3.2"
        ),
        "qwen2.5-coder": ModelPricing(
            input_cost_per_1k=0.0,  # Free/local
            output_cost_per_1k=0.0,
            model_name="Qwen 2.5 Coder"
        ),
    }
    
    def __init__(self):
        # Initialize tokenizers for different models
        try:
            self.gpt_tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.gpt_tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # For Claude and other models, use GPT tokenizer as approximation
        # (Claude uses similar tokenization)
        self.claude_tokenizer = self.gpt_tokenizer
        self.generic_tokenizer = self.gpt_tokenizer
    
    def estimate_tokens(self, text: str, model: str = "gpt-4o") -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to count tokens for
            model: Model name (affects tokenizer choice)
        
        Returns:
            Estimated token count
        """
        # Use appropriate tokenizer
        if "gpt" in model.lower():
            tokenizer = self.gpt_tokenizer
        elif "claude" in model.lower():
            tokenizer = self.claude_tokenizer
        else:
            tokenizer = self.generic_tokenizer
        
        return len(tokenizer.encode(text))
    
    def estimate_output_tokens(
        self, 
        prompt: str, 
        use_case: str,
        complexity_tier: int,
        model: str = "gpt-4o"
    ) -> int:
        """
        Estimate output token count based on prompt and use case.
        
        Uses heuristics based on:
        - Prompt length (longer prompts often generate longer outputs)
        - Use case type (some generate more output)
        - Complexity tier (higher tier = more output)
        
        Args:
            prompt: Input prompt
            use_case: Use case category
            complexity_tier: 1-4 complexity tier
        
        Returns:
            Estimated output tokens
        """
        input_tokens = self.estimate_tokens(prompt, model)
        
        # Base output estimate (rough heuristic)
        base_output = input_tokens * 0.5  # Often outputs are ~50% of input
        
        # Adjust by complexity tier
        tier_multipliers = {1: 0.3, 2: 0.5, 3: 1.0, 4: 1.5}
        base_output *= tier_multipliers.get(complexity_tier, 1.0)
        
        # Adjust by use case
        high_output_cases = ["creative", "analysis", "generation", "writing"]
        if any(case in use_case.lower() for case in high_output_cases):
            base_output *= 1.5
        
        # Cap at reasonable limits
        return min(int(base_output), 4000)  # Max 4K output tokens estimate
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            input_tokens: Input token count
            output_tokens: Output token count
            model: Model name
        
        Returns:
            Total cost in USD
        """
        pricing = self.PRICING.get(model)
        if not pricing:
            # Default to GPT-4 pricing if unknown
            pricing = self.PRICING["gpt-4o"]
        
        input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k
        
        return input_cost + output_cost
    
    def analyze_prompt_economics(
        self,
        prompt: str,
        use_case: str,
        complexity_tier: int,
        models: List[str] = None
    ) -> TokenEstimate:
        """
        Comprehensive economic analysis of a prompt.
        
        Args:
            prompt: Prompt text
            use_case: Use case category
            complexity_tier: 1-4 complexity tier
            models: List of models to analyze (default: all)
        
        Returns:
            TokenEstimate with full economic analysis
        """
        if models is None:
            models = list(self.PRICING.keys())
        
        input_tokens = self.estimate_tokens(prompt)
        output_tokens = self.estimate_output_tokens(prompt, use_case, complexity_tier)
        total_tokens = input_tokens + output_tokens
        
        # Calculate costs for each model
        estimated_costs = {}
        for model in models:
            cost = self.calculate_cost(input_tokens, output_tokens, model)
            estimated_costs[model] = cost
        
        # Calculate verbosity efficiency score
        # Lower token count with same quality = higher efficiency
        # This is a heuristic - assumes optimal prompt length for tier
        optimal_lengths = {1: 100, 2: 300, 3: 800, 4: 1500}
        optimal_tokens = optimal_lengths.get(complexity_tier, 500)
        
        if input_tokens <= optimal_tokens:
            efficiency = 1.0
        else:
            # Penalize excessive length
            excess = input_tokens - optimal_tokens
            efficiency = max(0.0, 1.0 - (excess / optimal_tokens) * 0.5)
        
        # Determine cost-quality tradeoff
        avg_cost = sum(estimated_costs.values()) / len(estimated_costs)
        if avg_cost < 0.01:
            tradeoff = "efficient"
        elif avg_cost < 0.05:
            tradeoff = "balanced"
        else:
            tradeoff = "expensive"
        
        return TokenEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_costs,
            verbosity_efficiency_score=efficiency,
            cost_quality_tradeoff=tradeoff
        )
    
    def compare_prompts(
        self,
        prompt1: str,
        prompt2: str,
        use_case: str,
        complexity_tier: int,
        model: str = "gpt-4o"
    ) -> Dict:
        """
        Compare economics of two prompts.
        
        Returns:
            Dictionary with comparison metrics
        """
        econ1 = self.analyze_prompt_economics(prompt1, use_case, complexity_tier, [model])
        econ2 = self.analyze_prompt_economics(prompt2, use_case, complexity_tier, [model])
        
        cost_diff = econ2.estimated_cost[model] - econ1.estimated_cost[model]
        cost_diff_pct = (cost_diff / econ1.estimated_cost[model] * 100) if econ1.estimated_cost[model] > 0 else 0
        
        return {
            "prompt1": {
                "tokens": econ1.total_tokens,
                "cost": econ1.estimated_cost[model],
                "efficiency": econ1.verbosity_efficiency_score
            },
            "prompt2": {
                "tokens": econ2.total_tokens,
                "cost": econ2.estimated_cost[model],
                "efficiency": econ2.verbosity_efficiency_score
            },
            "difference": {
                "token_delta": econ2.total_tokens - econ1.total_tokens,
                "cost_delta": cost_diff,
                "cost_delta_percent": cost_diff_pct,
                "efficiency_delta": econ2.verbosity_efficiency_score - econ1.verbosity_efficiency_score
            },
            "recommendation": self._generate_recommendation(econ1, econ2, cost_diff_pct)
        }
    
    def _generate_recommendation(
        self,
        econ1: TokenEstimate,
        econ2: TokenEstimate,
        cost_diff_pct: float
    ) -> str:
        """Generate recommendation based on comparison."""
        if abs(cost_diff_pct) < 5:
            return "Both prompts have similar costs. Choose based on quality."
        elif cost_diff_pct > 20:
            return f"Prompt 1 is {abs(cost_diff_pct):.1f}% cheaper. Consider using it if quality is acceptable."
        elif cost_diff_pct < -20:
            return f"Prompt 2 is {abs(cost_diff_pct):.1f}% cheaper. Consider using it if quality is acceptable."
        else:
            return "Cost difference is moderate. Evaluate based on quality vs cost tradeoff."
    
    def suggest_optimizations(
        self,
        prompt: str,
        target_reduction: float = 0.2  # 20% reduction
    ) -> List[str]:
        """
        Suggest optimizations to reduce token count.
        
        Args:
            prompt: Current prompt
            target_reduction: Target token reduction (0.0-1.0)
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        current_tokens = self.estimate_tokens(prompt)
        target_tokens = int(current_tokens * (1 - target_reduction))
        
        # Analyze prompt structure
        if len(prompt.split("\n\n\n")) > 3:
            suggestions.append("Reduce excessive paragraph breaks. Use single line breaks for lists.")
        
        if prompt.count("Example") > 3:
            suggestions.append(f"Reduce examples from {prompt.count('Example')} to 2-3 high-quality ones.")
        
        if len([w for w in prompt.split() if len(w) > 15]) > 10:
            suggestions.append("Replace long words with shorter synonyms where possible.")
        
        redundant_phrases = [
            ("very", "extremely"),
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("at this point in time", "now"),
        ]
        for long_phrase, short_phrase in redundant_phrases:
            if long_phrase in prompt.lower():
                suggestions.append(f"Replace '{long_phrase}' with '{short_phrase}'")
        
        return suggestions
