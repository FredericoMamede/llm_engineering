"""
Extended Python to C++ converter with multi-model support.

This module extends Day 3's converter with support for open-source models
and improved model selection.
"""

from typing import Optional, List
from ..core.system_info import retrieve_system_info
from ..core.model_clients import get_model_clients, get_client_for_model


# Available models across all providers
AVAILABLE_MODELS = [
    "gpt-5",
    "gpt-5-nano",
    "claude-sonnet-4-5-20250929",
    "claude-3-5-haiku-latest",
    "grok-4",
    "grok-4-fast-non-reasoning",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "openai/gpt-oss-120b",
    "qwen2.5-coder",
    "deepseek-coder-v2",
    "gpt-oss:20b",
    "qwen/qwen3-coder-30b-a3b-instruct",
]


def build_system_prompt() -> str:
    """Build the system prompt for code conversion."""
    return """Your task is to convert Python code into high performance C++ code.
Respond only with C++ code. Do not provide any explanation other than occasional comments.
The C++ response needs to produce an identical output in the fastest possible time."""


def build_user_prompt(python_code: str, system_info: dict, compile_command: list) -> str:
    """Build the user prompt for code conversion."""
    return f"""Port this Python code to C++ with the fastest possible implementation that produces identical output in the least time.
The system information is:
{system_info}
Your response will be written to a file called main.cpp and then compiled and executed; the compilation command is:
{compile_command}
Respond only with C++ code.
Python code to port:

```python
{python_code}
```
"""


def convert_python_to_cpp(
    python_code: str,
    model: str = "gpt-5",
    compile_command: Optional[list] = None,
) -> str:
    """
    Convert Python code to C++ using the specified model.

    Args:
        python_code: Python code to convert
        model: Model name to use
        compile_command: Optional compile command

    Returns:
        Generated C++ code

    Raises:
        ValueError: If model is not available or client not found
    """
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model} not in available models: {AVAILABLE_MODELS}")

    system_info = retrieve_system_info()

    if compile_command is None:
        compile_command = [
            "clang++",
            "-std=c++17",
            "-Ofast",
            "-mcpu=native",
            "-flto=thin",
            "-fvisibility=hidden",
            "-DNDEBUG",
            "main.cpp",
            "-o",
            "main",
        ]

    clients = get_model_clients()
    client = get_client_for_model(model, clients)

    if client is None:
        raise ValueError(f"No client available for model: {model}. Check API keys.")

    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": build_user_prompt(python_code, system_info, compile_command)},
    ]

    reasoning_effort = "high" if "gpt" in model.lower() else None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            reasoning_effort=reasoning_effort,
        )

        cpp_code = response.choices[0].message.content
        cpp_code = cpp_code.replace("```cpp", "").replace("```", "").strip()

        return cpp_code
    except Exception as e:
        raise RuntimeError(f"Error calling model {model}: {str(e)}")


def get_available_models() -> List[str]:
    """Get list of available models based on configured API keys."""
    clients = get_model_clients()
    available = []

    for model in AVAILABLE_MODELS:
        client = get_client_for_model(model, clients)
        if client is not None:
            available.append(model)

    return available
