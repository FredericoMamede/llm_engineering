"""
Enhanced Gradio UI for multi-language code conversion (Python → C++/Rust).

This UI extends Day 4's UI with Rust support and enhanced features.
"""

import gradio as gr
from .converter import convert_python_to_language, AVAILABLE_MODELS
from ..core.code_executor import CodeExecutor
from ..day3_python_to_cpp.benchmark import run_python_code


# Default compile and run commands
CPP_COMPILE_COMMAND = [
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

RUST_COMPILE_COMMAND = [
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

RUN_COMMAND = ["./main"]


def convert_code(model: str, language: str, python_code: str) -> str:
    """Convert Python code to target language using the selected model."""
    if not python_code.strip():
        return "Please provide Python code to convert."

    try:
        target_lang = "Rust" if language == "Rust" else "C++"
        code = convert_python_to_language(
            python_code, target_language=target_lang, model=model
        )
        return code
    except Exception as e:
        return f"Error: {str(e)}"


def run_python(python_code: str) -> str:
    """Run Python code and return output."""
    if not python_code.strip():
        return "Please provide Python code to run."

    result = run_python_code(python_code)
    if result["success"]:
        return result["output"]
    else:
        return f"Error: {result['output']}"


def run_compiled(code: str, language: str) -> str:
    """Compile and run C++ or Rust code."""
    if not code.strip():
        return "Please provide code to run."

    if language == "Rust":
        source_file = "main.rs"
        compile_command = RUST_COMPILE_COMMAND
    else:
        source_file = "main.cpp"
        compile_command = CPP_COMPILE_COMMAND

    # Write code to file
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(code)

    # Compile and run
    executor = CodeExecutor(compile_command, RUN_COMMAND, source_file)
    compile_result, run_result = executor.compile_and_run()

    if not compile_result.success:
        return f"Compilation error:\n{compile_result.error_message or compile_result.stderr}"

    if not run_result or not run_result.success:
        return f"Execution error:\n{run_result.error_message if run_result else 'Unknown error'}"

    return run_result.stdout


def create_ui():
    """Create and launch the enhanced Gradio UI."""
    available_models = AVAILABLE_MODELS[:5]  # Use first 5 for UI

    default_python = """# Be careful to support large numbers

def lcg(seed, a=1664525, c=1013904223, m=2**32):
    value = seed
    while True:
        value = (a * value + c) % m
        yield value
        
def max_subarray_sum(n, seed, min_val, max_val):
    lcg_gen = lcg(seed)
    random_numbers = [next(lcg_gen) % (max_val - min_val + 1) + min_val for _ in range(n)]
    max_sum = float('-inf')
    for i in range(n):
        current_sum = 0
        for j in range(i, n):
            current_sum += random_numbers[j]
            if current_sum > max_sum:
                max_sum = current_sum
    return max_sum

def total_max_subarray_sum(n, initial_seed, min_val, max_val):
    total_sum = 0
    lcg_gen = lcg(initial_seed)
    for _ in range(20):
        seed = next(lcg_gen)
        total_sum += max_subarray_sum(n, seed, min_val, max_val)
    return total_sum

# Parameters
n = 10000
initial_seed = 42
min_val = -10
max_val = 10

# Timing
import time
start_time = time.time()
result = total_max_subarray_sum(n, initial_seed, min_val, max_val)
end_time = time.time()

print("Total Maximum Subarray Sum (20 runs):", result)
print("Execution Time: {:.6f} seconds".format(end_time - start_time))
"""

    with gr.Blocks(title="Python to C++/Rust Converter") as ui:
        gr.Markdown("# Python to C++/Rust Code Converter")
        gr.Markdown("Convert Python code to optimized C++ or Rust using various LLM models.")

        with gr.Row():
            with gr.Column(scale=1):
                python_input = gr.Code(
                    label="Python (original)",
                    value=default_python,
                    language="python",
                    lines=26,
                )
                python_run_btn = gr.Button("Run Python", variant="secondary")

            with gr.Column(scale=1):
                compiled_output = gr.Code(
                    label="Generated Code (C++/Rust)",
                    value="",
                    language="cpp",
                    lines=26,
                )
                compiled_run_btn = gr.Button("Run Compiled", variant="secondary")

        with gr.Row():
            language_dropdown = gr.Dropdown(
                choices=["C++", "Rust"],
                value="C++",
                label="Target Language",
            )
            model_dropdown = gr.Dropdown(
                choices=available_models,
                value=available_models[0],
                label="Select Model",
            )
            convert_btn = gr.Button("Convert", variant="primary")

        with gr.Row():
            python_output = gr.TextArea(
                label="Python Result",
                lines=8,
                interactive=False,
            )
            compiled_result = gr.TextArea(
                label="Compiled Result",
                lines=8,
                interactive=False,
            )

        convert_btn.click(
            fn=convert_code,
            inputs=[model_dropdown, language_dropdown, python_input],
            outputs=[compiled_output],
        )

        python_run_btn.click(
            fn=run_python,
            inputs=[python_input],
            outputs=[python_output],
        )

        compiled_run_btn.click(
            fn=run_compiled,
            inputs=[compiled_output, language_dropdown],
            outputs=[compiled_result],
        )

    return ui


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser=True)
