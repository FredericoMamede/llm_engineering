"""
Multi-language code converter (Python → C++ or Rust).

This module extends Day 4's converter with Rust support and language selection.
"""

from typing import Optional, Literal
from ..core.system_info import retrieve_system_info, rust_toolchain_info
from ..core.model_clients import get_model_clients, get_client_for_model
from ..day4_multi_model_ui.converter import AVAILABLE_MODELS


Language = Literal["C++", "Rust"]


def build_system_prompt(language: Language) -> str:
    """Build the system prompt for code conversion."""
    return f"""Your task is to convert Python code into high performance {language} code.
Respond only with {language} code. Do not provide any explanation other than occasional comments.
The {language} response needs to produce an identical output in the fastest possible time."""


def build_user_prompt(
    python_code: str,
    language: Language,
    system_info: dict,
    rust_info: Optional[dict],
    compile_command: list,
) -> str:
    """Build the user prompt for code conversion."""
    prompt = f"""Port this Python code to {language} with the fastest possible implementation that produces identical output in the least time.
The system information is:
{system_info}
"""

    if language == "Rust" and rust_info:
        prompt += f"""
Rust toolchain information:
{rust_info}
"""

    prompt += f"""
Your response will be written to a file called main.{'rs' if language == 'Rust' else 'cpp'} and then compiled and executed; the compilation command is:
{compile_command}
Respond only with {language} code.
Python code to port:

```python
{python_code}
```
"""

    return prompt


def convert_python_to_language(
    python_code: str,
    target_language: Language = "C++",
    model: str = "gpt-5",
    compile_command: Optional[list] = None,
) -> str:
    """
    Convert Python code to C++ or Rust using the specified model.

    Args:
        python_code: Python code to convert
        target_language: Target language ("C++" or "Rust")
        model: Model name to use
        compile_command: Optional compile command

    Returns:
        Generated code in target language

    Raises:
        ValueError: If model is not available or language is invalid
    """
    if target_language not in ["C++", "Rust"]:
        raise ValueError(f"Invalid language: {target_language}. Must be 'C++' or 'Rust'")

    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model} not in available models: {AVAILABLE_MODELS}")

    system_info = retrieve_system_info()
    rust_info = rust_toolchain_info() if target_language == "Rust" else None

    if compile_command is None:
        if target_language == "Rust":
            # Default Rust compile command
            compile_command = [
                "rustc",
                "main.rs",
                "-C", "opt-level=3",
                "-C", "target-cpu=native",
                "-C", "codegen-units=1",
                "-C", "lto=fat",
                "-C", "panic=abort",
                "-C", "strip=symbols",
                "-o", "main",
            ]
        else:
            # Default C++ compile command
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
        {"role": "system", "content": build_system_prompt(target_language)},
        {
            "role": "user",
            "content": build_user_prompt(
                python_code, target_language, system_info, rust_info, compile_command
            ),
        },
    ]

    reasoning_effort = "high" if "gpt" in model.lower() else None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            reasoning_effort=reasoning_effort,
        )

        code = response.choices[0].message.content
        # Clean up markdown code fences
        code = code.replace(f"```{target_language.lower()}", "").replace("```rust", "").replace("```cpp", "").replace("```", "").strip()

        return code
    except Exception as e:
        raise RuntimeError(f"Error calling model {model}: {str(e)}")
