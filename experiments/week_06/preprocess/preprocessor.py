"""
Day 2 — LLM-based rewriting of product descriptions.

Single-item preprocessing with cost/token tracking.
Toggle: use preprocess() only when preprocessing is ON (cost-aware).
"""

from typing import Any, Dict, Optional

# Default: course used groq/openai/gpt-oss-20b with reasoning_effort.
# We use litellm completion; cost comes from response._hidden_params if present.
DEFAULT_MODEL = "groq/openai/gpt-oss-20b"
DEFAULT_REASONING_EFFORT = "low"

from .prompts import SYSTEM_PROMPT


class Preprocessor:
    """
    Rewrite raw product text to standard format via one LLM call per item.
    Tracks total input/output tokens and cost (when provider reports it).
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        use_preprocessing: bool = True,
    ):
        self.model_name = model_name
        self.reasoning_effort = reasoning_effort
        self.use_preprocessing = use_preprocessing
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def messages_for(self, text: str) -> list[dict]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]

    def preprocess(self, text: str) -> str:
        """
        Return rewritten product description. If preprocessing is OFF, return text unchanged.
        Token usage: system + user (text); cost depends on provider (see litellm).
        """
        if not self.use_preprocessing:
            return text
        try:
            from litellm import completion
        except ImportError:
            return text
        messages = self.messages_for(text)
        kwargs = {"messages": messages, "model": self.model_name}
        if "groq" in self.model_name.lower() or "gpt-oss" in self.model_name.lower():
            kwargs["reasoning_effort"] = self.reasoning_effort
        response = completion(**kwargs)
        self.total_input_tokens += getattr(response.usage, "prompt_tokens", 0) or 0
        self.total_output_tokens += getattr(response.usage, "completion_tokens", 0) or 0
        cost = getattr(getattr(response, "_hidden_params", None) or {}, "response_cost", None)
        if cost is not None:
            self.total_cost += float(cost)
        return response.choices[0].message.content

    def get_cost_summary(self) -> Dict[str, Any]:
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": self.total_cost,
        }
