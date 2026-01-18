"""
Prompt templates for Python to C++ conversion.
"""

SYSTEM_PROMPT = """Your task is to convert Python code into high performance C++ code.
Respond only with C++ code. Do not provide any explanation other than occasional comments.
The C++ response needs to produce an identical output in the fastest possible time."""


def build_user_prompt(python_code: str, system_info: dict, compile_command: list) -> str:
    """Build user prompt for code conversion."""
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
