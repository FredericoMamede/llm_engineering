"""
Performance benchmarking utilities for Python vs C++ code.
"""

import time
import io
import sys
from typing import Dict, Any
from ..core.code_executor import CodeExecutor


def run_python_code(code: str) -> Dict[str, Any]:
    """
    Execute Python code and measure execution time.

    Args:
        code: Python code to execute

    Returns:
        Dictionary with execution time and output
    """
    globals_dict = {"__builtins__": __builtins__}

    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer

    start_time = time.time()
    try:
        exec(code, globals_dict)
        output = buffer.getvalue()
    except Exception as e:
        output = f"Error: {e}"
    finally:
        sys.stdout = old_stdout

    end_time = time.time()
    execution_time = end_time - start_time

    return {
        "execution_time": execution_time,
        "output": output,
        "success": "Error" not in output,
    }


def benchmark_code(
    python_code: str,
    cpp_code: str,
    compile_command: list,
    run_command: list,
    source_file: str = "main.cpp",
) -> Dict[str, Any]:
    """
    Benchmark Python code against generated C++ code.

    Args:
        python_code: Original Python code
        cpp_code: Generated C++ code
        compile_command: Command to compile C++
        run_command: Command to run compiled C++
        source_file: Path to write C++ source

    Returns:
        Dictionary with benchmark results
    """
    # Write C++ code to file
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(cpp_code)

    # Run Python code
    python_result = run_python_code(python_code)

    # Compile and run C++
    executor = CodeExecutor(compile_command, run_command, source_file)
    compile_result, run_result = executor.compile_and_run()

    if not compile_result.success or not run_result or not run_result.success:
        return {
            "python_time": python_result["execution_time"],
            "cpp_time": None,
            "speedup": None,
            "success": False,
            "error": compile_result.error_message or run_result.error_message if run_result else "Unknown error",
        }

    # Parse C++ execution time from output (if available)
    # This assumes the C++ code prints execution time
    cpp_output = run_result.stdout
    cpp_time = None

    # Try to extract time from output
    for line in cpp_output.splitlines():
        if "Execution Time:" in line or "Time:" in line:
            try:
                # Extract number from line
                import re
                match = re.search(r"(\d+\.\d+)", line)
                if match:
                    cpp_time = float(match.group(1))
                    break
            except:
                pass

    # If we can't parse time, we can't calculate speedup
    if cpp_time is None:
        return {
            "python_time": python_result["execution_time"],
            "cpp_time": None,
            "speedup": None,
            "success": True,
            "python_output": python_result["output"],
            "cpp_output": cpp_output,
            "note": "Could not parse execution time from C++ output",
        }

    speedup = python_result["execution_time"] / cpp_time if cpp_time > 0 else None

    return {
        "python_time": python_result["execution_time"],
        "cpp_time": cpp_time,
        "speedup": speedup,
        "success": True,
        "python_output": python_result["output"],
        "cpp_output": cpp_output,
    }
