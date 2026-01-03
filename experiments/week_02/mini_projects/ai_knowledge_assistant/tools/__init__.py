"""
Tool registry: centralized access to all tools and their schemas.

Pattern: Dictionary-based registry for scalable tool routing.
"""

import json
from typing import Any, Callable, Dict, List

from .explain_error import (
    explain_error,
    TOOL_NAME as EXPLAIN_ERROR_NAME,
    TOOL_SCHEMA as EXPLAIN_ERROR_SCHEMA,
)
from .review_code import (
    review_code,
    TOOL_NAME as REVIEW_CODE_NAME,
    TOOL_SCHEMA as REVIEW_CODE_SCHEMA,
)
from .summarize_text import (
    summarize_text,
    TOOL_NAME as SUMMARIZE_TEXT_NAME,
    TOOL_SCHEMA as SUMMARIZE_TEXT_SCHEMA,
)

# Registry: name -> function
TOOL_REGISTRY: Dict[str, Callable] = {
    EXPLAIN_ERROR_NAME: explain_error,
    REVIEW_CODE_NAME: review_code,
    SUMMARIZE_TEXT_NAME: summarize_text,
}

# OpenAI-compatible tool definitions
TOOLS: List[Dict[str, Any]] = [
    EXPLAIN_ERROR_SCHEMA,
    REVIEW_CODE_SCHEMA,
    SUMMARIZE_TEXT_SCHEMA,
]


def handle_tool_calls(tool_calls) -> List[Dict[str, Any]]:
    """
    Execute tool calls from LLM response and return results.
    
    Args:
        tool_calls: List of tool call objects from OpenAI response
    
    Returns:
        List of tool response messages for the API
    """
    results = []
    
    for call in tool_calls:
        func_name = call.function.name
        call_id = call.id
        
        try:
            args = json.loads(call.function.arguments)
        except json.JSONDecodeError as e:
            results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": f"Error parsing arguments: {e}",
            })
            continue
        
        func = TOOL_REGISTRY.get(func_name)
        if not func:
            results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": f"Unknown tool: {func_name}",
            })
            continue
        
        try:
            result = func(**args)
            results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": str(result),
            })
        except Exception as e:
            results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": f"Error executing {func_name}: {e}",
            })
    
    return results


__all__ = [
    "TOOL_REGISTRY",
    "TOOLS",
    "handle_tool_calls",
    "explain_error",
    "review_code",
    "summarize_text",
]

