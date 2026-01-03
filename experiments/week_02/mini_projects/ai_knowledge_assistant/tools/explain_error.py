"""
Tool: explain_error
Parses and explains Python tracebacks / logs.
"""

import re
from typing import Any

# Knowledge base of common Python errors
ERROR_EXPLANATIONS = {
    "TypeError": {
        "description": "Operation performed on incompatible type.",
        "common_causes": [
            "Adding/concatenating incompatible types (str + int)",
            "Calling a non-callable object",
            "Wrong number of arguments to function",
        ],
        "fixes": [
            "Check types with type()",
            "Convert values: str(), int(), float()",
            "Verify function signatures",
        ],
    },
    "NameError": {
        "description": "Variable or function not defined.",
        "common_causes": [
            "Typo in variable name",
            "Using before definition",
            "Missing import",
        ],
        "fixes": [
            "Check spelling",
            "Ensure definition precedes use",
            "Add missing import",
        ],
    },
    "KeyError": {
        "description": "Dictionary key does not exist.",
        "common_causes": [
            "Typo in key name",
            "Key never added",
            "Key removed earlier",
        ],
        "fixes": [
            "Use .get() with default",
            "Check key existence with 'in'",
            "Print dict.keys() to inspect",
        ],
    },
    "IndexError": {
        "description": "List index out of range.",
        "common_causes": [
            "Off-by-one error",
            "Empty list access",
            "Wrong index calculation",
        ],
        "fixes": [
            "Check len() before access",
            "Remember 0-based indexing",
            "Use try/except or bounds check",
        ],
    },
    "AttributeError": {
        "description": "Object has no such attribute/method.",
        "common_causes": [
            "Typo in attribute name",
            "Object is None",
            "Wrong object type",
        ],
        "fixes": [
            "Check spelling",
            "Add None check before access",
            "Verify object type with type()",
        ],
    },
    "ValueError": {
        "description": "Function received argument of right type but wrong value.",
        "common_causes": [
            "Invalid literal for int()",
            "Unpacking wrong number of values",
            "Invalid argument to function",
        ],
        "fixes": [
            "Validate input before conversion",
            "Check expected vs actual value count",
            "Read function docs for valid values",
        ],
    },
    "ImportError": {
        "description": "Module or name cannot be imported.",
        "common_causes": [
            "Module not installed",
            "Typo in module name",
            "Circular import",
        ],
        "fixes": [
            "pip install <module>",
            "Check spelling",
            "Restructure imports to break cycle",
        ],
    },
    "FileNotFoundError": {
        "description": "File or directory does not exist.",
        "common_causes": [
            "Wrong file path",
            "File deleted or moved",
            "Relative vs absolute path issue",
        ],
        "fixes": [
            "Verify path with os.path.exists()",
            "Use absolute paths",
            "Check current working directory",
        ],
    },
}


def explain_error(error_traceback: str) -> str:
    """
    Parse a Python traceback and return a structured explanation.
    
    Args:
        error_traceback: The full error traceback text
    
    Returns:
        Formatted explanation with cause, fixes, and context
    """
    if not error_traceback or not error_traceback.strip():
        return "No traceback provided."

    # Extract error type from traceback
    error_type = None
    error_message = ""
    
    # Pattern: ErrorType: message (last line of traceback)
    lines = error_traceback.strip().split("\n")
    for line in reversed(lines):
        match = re.match(r"^(\w+Error|\w+Exception):\s*(.*)$", line.strip())
        if match:
            error_type = match.group(1)
            error_message = match.group(2)
            break

    if not error_type:
        # Try to find any known error type in the text
        for known_error in ERROR_EXPLANATIONS:
            if known_error in error_traceback:
                error_type = known_error
                break

    if not error_type:
        return (
            "Could not identify the error type.\n\n"
            "Tip: Paste the complete traceback starting from 'Traceback (most recent call last):'."
        )

    # Build explanation
    parts = [f"**Error Type:** {error_type}"]
    
    if error_message:
        parts.append(f"**Message:** {error_message}")

    info = ERROR_EXPLANATIONS.get(error_type)
    if info:
        parts.append(f"\n**What it means:** {info['description']}")
        parts.append("\n**Common causes:**")
        for cause in info["common_causes"]:
            parts.append(f"  - {cause}")
        parts.append("\n**How to fix:**")
        for fix in info["fixes"]:
            parts.append(f"  - {fix}")
    else:
        parts.append(
            f"\n{error_type} is not in the knowledge base. "
            "Check Python docs or search for the error message."
        )

    return "\n".join(parts)


# Tool metadata for registry
TOOL_NAME = "explain_error"
TOOL_IMPL = explain_error
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "explain_error",
        "description": "Parse and explain a Python error traceback. Returns structured explanation with causes and fixes.",
        "parameters": {
            "type": "object",
            "properties": {
                "error_traceback": {
                    "type": "string",
                    "description": "The full Python error traceback text",
                }
            },
            "required": ["error_traceback"],
        },
    },
}
