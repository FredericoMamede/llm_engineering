# Tool Calling - Functions the LLM can invoke
#
# Pattern: Function Registry - dictionary maps names to functions
# Why: Scales without if/elif chains, self-documenting, easy to extend
#
# Components:
# 1. Tool implementations (actual Python functions)
# 2. TOOL_REGISTRY (name → function mapping)
# 3. TOOLS (JSON schema for OpenAI API)
# 4. handle_tool_calls() (executes tools from LLM response)

import json
import re
from typing import Dict, Callable, List, Any


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

def explain_error(error_traceback: str) -> str:
    """
    Parse and explain a Python error traceback.
    
    Identifies the error type, explains it in plain language,
    and provides common causes and fixes.
    
    Args:
        error_traceback: The full Python error traceback
    
    Returns:
        Formatted explanation with causes and fixes
    """
    # Knowledge base of common Python errors
    # Each entry has: description, common causes, and fixes
    error_explanations = {
        "TypeError": {
            "description": "You tried to perform an operation on a value of the wrong type.",
            "common_causes": [
                "Adding/concatenating incompatible types (e.g., string + integer)",
                "Calling a non-callable object like a function",
                "Passing wrong number of arguments to a function",
                "Using None where a value was expected"
            ],
            "fixes": [
                "Check the types of your variables using type()",
                "Convert values to compatible types (str(), int(), float())",
                "Check if a variable might be None before using it"
            ]
        },
        "NameError": {
            "description": "You used a variable or function that hasn't been defined.",
            "common_causes": [
                "Typo in variable/function name",
                "Using a variable before it's defined",
                "Variable defined in a different scope (inside a function)",
                "Forgot to import a module"
            ],
            "fixes": [
                "Check spelling of variable/function names",
                "Make sure the variable is defined before use",
                "Check your import statements",
                "Check variable scope (local vs global)"
            ]
        },
        "IndexError": {
            "description": "You tried to access an index that doesn't exist in a list/sequence.",
            "common_causes": [
                "Accessing index beyond list length (off-by-one error)",
                "Empty list but trying to access elements",
                "Using wrong index calculation"
            ],
            "fixes": [
                "Check list length with len() before accessing",
                "Remember Python uses 0-based indexing",
                "Use try/except or check if list is empty"
            ]
        },
        "KeyError": {
            "description": "You tried to access a dictionary key that doesn't exist.",
            "common_causes": [
                "Typo in dictionary key",
                "Key was never added to dictionary",
                "Key was removed or doesn't exist for this data"
            ],
            "fixes": [
                "Use .get() method with a default value",
                "Check if key exists with 'in' operator",
                "Print dictionary keys to see what's available"
            ]
        },
        "AttributeError": {
            "description": "You tried to access an attribute/method that doesn't exist on an object.",
            "common_causes": [
                "Typo in method/attribute name",
                "Object is None (NoneType has no attributes)",
                "Wrong object type (expected different class)",
                "Method exists but with different name"
            ],
            "fixes": [
                "Check if object might be None before accessing",
                "Use dir(object) to see available attributes",
                "Check the documentation for correct method names"
            ]
        },
        "ValueError": {
            "description": "A function received a value of the right type but inappropriate value.",
            "common_causes": [
                "Converting invalid string to number (e.g., int('hello'))",
                "Unpacking wrong number of values",
                "Invalid argument to function (e.g., negative where positive expected)"
            ],
            "fixes": [
                "Validate input before conversion",
                "Check the function documentation for valid values",
                "Use try/except to handle invalid inputs"
            ]
        },
        "SyntaxError": {
            "description": "Your code has a syntax mistake - Python can't understand it.",
            "common_causes": [
                "Missing colon after if/for/def/class",
                "Mismatched parentheses, brackets, or quotes",
                "Invalid Python syntax",
                "Indentation issues"
            ],
            "fixes": [
                "Check for missing colons (:)",
                "Count your parentheses and brackets",
                "Check for unclosed strings",
                "Make sure indentation is consistent"
            ]
        },
        "IndentationError": {
            "description": "Your code has incorrect indentation.",
            "common_causes": [
                "Mixing tabs and spaces",
                "Wrong indentation level",
                "Missing indentation after colon"
            ],
            "fixes": [
                "Use consistent indentation (4 spaces recommended)",
                "Configure your editor to use spaces instead of tabs",
                "Check that code blocks are properly indented"
            ]
        }
    }
    
    # Extract error type from traceback using pattern matching
    error_type = None
    error_message = ""
    
    for known_error in error_explanations.keys():
        if known_error in error_traceback:
            error_type = known_error
            # Extract the specific message after the error type
            match = re.search(f"{known_error}: (.+?)(?:\\n|$)", error_traceback)
            if match:
                error_message = match.group(1)
            break
    
    # Format the response
    if error_type and error_type in error_explanations:
        info = error_explanations[error_type]
        result = f"""
**Error Type:** {error_type}
**Message:** {error_message if error_message else '(no specific message)'}

**What this means:**
{info['description']}

**Common causes:**
{chr(10).join(f'- {cause}' for cause in info['common_causes'])}

**How to fix it:**
{chr(10).join(f'- {fix}' for fix in info['fixes'])}
"""
    else:
        # Fallback for unrecognized errors
        result = f"""
**Error detected in traceback**

Could not identify the specific error type. Here's the traceback for analysis:

```
{error_traceback}
```

**General debugging tips:**
- Read the last line first - it usually has the error type and message
- Look at the line numbers to find where the error occurred
- Check the variables mentioned in the error message
- Use print() statements to debug variable values
"""
    
    return result.strip()


def suggest_improvements(code: str) -> str:
    """
    Analyze code and suggest improvements based on Python best practices.
    
    Uses pattern matching to detect common issues:
    - Bare except clauses
    - Print instead of logging
    - Non-Pythonic comparisons
    - Missing function structure
    - Global variable usage
    - Star imports
    
    Args:
        code: The Python code snippet to analyze
    
    Returns:
        List of improvement suggestions with explanations
    """
    suggestions = []
    
    # Check for bare except clauses - catch specific exceptions instead
    if "except:" in code or "except Exception:" in code:
        suggestions.append("**Specific exceptions:** Consider catching specific exception types instead of bare `except:` or `except Exception:`")
    
    # Check for print in functions - logging module provides more control
    if "print(" in code and "def " in code:
        suggestions.append("**Logging:** Consider using the `logging` module instead of `print()` for better control over output")
    
    # Check for == None - is None is more Pythonic and faster
    if "== None" in code or "!= None" in code:
        suggestions.append("**None comparison:** Use `is None` or `is not None` instead of `== None` (it's more Pythonic and faster)")
    
    # Check for string concatenation - f-strings are cleaner
    if "+" in code and ("'" in code or '"' in code):
        suggestions.append("**String formatting:** Consider using f-strings (`f\"Hello {name}\"`) instead of string concatenation for readability")
    
    # Check for long code without functions - modularity improves maintainability
    if not "def " in code and len(code.split('\n')) > 10:
        suggestions.append("**Functions:** Consider breaking this code into functions for better organization and reusability")
    
    # Check for global keyword - function arguments are preferred
    if "global " in code:
        suggestions.append("**Global variables:** Try to avoid `global` - consider passing values as function arguments instead")
    
    # Check for star imports - pollutes namespace and hides dependencies
    if "import *" in code:
        suggestions.append("**Star imports:** Avoid `from x import *` - it pollutes the namespace and makes code harder to understand")
    
    # If no issues found, provide positive feedback
    if not suggestions:
        suggestions.append("Code looks good. No obvious improvements detected.")
        suggestions.append("For deeper analysis, consider using tools like `pylint`, `flake8`, or `black` for formatting.")
    
    return "\n\n".join(suggestions)


# ============================================================================
# TOOL REGISTRY
# ============================================================================
# Maps function names to function objects
# Why a dictionary? No if/elif chains - scales from 2 to 200 tools
# Adding a new tool = 1 line here + the function implementation

TOOL_REGISTRY: Dict[str, Callable] = {
    "explain_error": explain_error,
    "suggest_improvements": suggest_improvements,
}


# ============================================================================
# TOOL DEFINITIONS (JSON Schema for OpenAI API)
# ============================================================================
# OpenAI needs to know what tools exist and their parameters
# The description helps the LLM decide when to use each tool

TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "explain_error",
            "description": "Parse and explain a Python error traceback, providing a friendly explanation, common causes, and suggested fixes. Use this when the user shares an error message or traceback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "error_traceback": {
                        "type": "string",
                        "description": "The full Python error traceback or error message"
                    }
                },
                "required": ["error_traceback"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_improvements",
            "description": "Analyze a code snippet and suggest improvements based on Python best practices. Use this when the user asks for code review or improvement suggestions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code snippet to analyze"
                    }
                },
                "required": ["code"],
                "additionalProperties": False
            }
        }
    }
]


# ============================================================================
# TOOL CALL HANDLER
# ============================================================================

def handle_tool_calls(message) -> List[Dict[str, Any]]:
    """
    Execute tool calls from an LLM response.
    
    Flow:
    1. Iterate through all tool calls in the message
    2. Parse JSON arguments
    3. Look up function in registry
    4. Execute function with arguments
    5. Return results in OpenAI's expected format
    
    Error handling covers:
    - JSON parsing errors
    - Unknown tool names
    - Invalid arguments
    - Execution errors
    
    Args:
        message: The assistant message containing tool_calls
    
    Returns:
        List of tool response dicts ready to add to conversation
    """
    responses = []
    
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        
        # Parse arguments from JSON string
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            responses.append({
                "role": "tool",
                "content": f"Error: Invalid arguments JSON. {str(e)}",
                "tool_call_id": tool_call.id
            })
            continue
        
        # Look up and execute function from registry
        if function_name in TOOL_REGISTRY:
            func = TOOL_REGISTRY[function_name]
            try:
                result = func(**arguments)
                responses.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call.id
                })
            except TypeError as e:
                # Wrong number or type of arguments
                responses.append({
                    "role": "tool",
                    "content": f"Error: Function {function_name} received invalid arguments. {str(e)}",
                    "tool_call_id": tool_call.id
                })
            except Exception as e:
                # Any other execution error
                responses.append({
                    "role": "tool",
                    "content": f"Error executing {function_name}: {str(e)}",
                    "tool_call_id": tool_call.id
                })
        else:
            responses.append({
                "role": "tool",
                "content": f"Error: Unknown tool '{function_name}'",
                "tool_call_id": tool_call.id
            })
    
    return responses
