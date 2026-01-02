# Utils Package - Shared components for the Week 2 Exercise
#
# Modules:
#   prompts.py - Dynamic system/user prompts based on expertise level
#   model_registry.py - Multi-model support (GPT + Ollama)
#   tools.py - Tool calling implementation (function registry pattern)

from .prompts import (
    create_system_prompt,
    create_user_prompt,
    EXPERTISE_LEVELS,
    ExpertiseLevel
)

from .model_registry import TechnicalAssistant

from .tools import (
    explain_error,
    suggest_improvements,
    TOOLS,
    TOOL_REGISTRY,
    handle_tool_calls
)

__all__ = [
    "create_system_prompt",
    "create_user_prompt", 
    "EXPERTISE_LEVELS",
    "ExpertiseLevel",
    "TechnicalAssistant",
    "explain_error",
    "suggest_improvements",
    "TOOLS",
    "TOOL_REGISTRY",
    "handle_tool_calls",
]
