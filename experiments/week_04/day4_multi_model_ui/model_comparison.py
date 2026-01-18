"""
Model comparison utilities for Day 4.

This module provides functions to compare model outputs and performance.
"""

from typing import List, Dict, Any
from .converter import convert_python_to_cpp, get_available_models
from ..day3_python_to_cpp.benchmark import benchmark_code


def compare_models(
    python_code: str,
    models: List[str],
    compile_command: list,
    run_command: list,
) -> Dict[str, Any]:
    """
    Compare multiple models on the same Python code.

    Args:
        python_code: Python code to convert
        models: List of model names to compare
        compile_command: C++ compile command
        run_command: C++ run command

    Returns:
        Dictionary with comparison results for each model
    """
    results = {}

    for model in models:
        try:
            # Convert to C++
            cpp_code = convert_python_to_cpp(python_code, model=model)

            # Benchmark
            benchmark_result = benchmark_code(
                python_code, cpp_code, compile_command, run_command
            )

            results[model] = {
                "success": benchmark_result.get("success", False),
                "cpp_code": cpp_code,
                "speedup": benchmark_result.get("speedup"),
                "python_time": benchmark_result.get("python_time"),
                "cpp_time": benchmark_result.get("cpp_time"),
                "error": benchmark_result.get("error"),
            }
        except Exception as e:
            results[model] = {
                "success": False,
                "error": str(e),
            }

    return results


def format_comparison_table(results: Dict[str, Any]) -> str:
    """
    Format comparison results as a markdown table.

    Args:
        results: Results dictionary from compare_models

    Returns:
        Formatted markdown table
    """
    table = "| Model | Success | Speedup | Python Time | C++ Time |\n"
    table += "|-------|---------|---------|-------------|----------|\n"

    for model, result in results.items():
        success = "✅" if result.get("success") else "❌"
        speedup = f"{result.get('speedup', 0):.2f}x" if result.get("speedup") else "N/A"
        py_time = f"{result.get('python_time', 0):.6f}s" if result.get("python_time") else "N/A"
        cpp_time = f"{result.get('cpp_time', 0):.6f}s" if result.get("cpp_time") else "N/A"

        table += f"| {model} | {success} | {speedup} | {py_time} | {cpp_time} |\n"

    return table
