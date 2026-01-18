"""
Gradio UI for Python to C++ code conversion with multi-model support.
"""

import gradio as gr
from .converter import convert_python_to_cpp, get_available_models
from ..core.code_executor import CodeExecutor
from ..day3_python_to_cpp.benchmark import run_python_code


# Default compile and run commands
COMPILE_COMMAND = [
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

RUN_COMMAND = ["./main"]


def convert_code(model: str, python_code: str) -> str:
    """Convert Python code to C++ using the selected model."""
    if not python_code.strip():
        return "Please provide Python code to convert."

    try:
        cpp_code = convert_python_to_cpp(python_code, model=model)
        return cpp_code
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


def run_cpp(cpp_code: str) -> str:
    """Compile and run C++ code."""
    if not cpp_code.strip():
        return "Please provide C++ code to run."

    # Write code to file
    with open("main.cpp", "w", encoding="utf-8") as f:
        f.write(cpp_code)

    # Compile and run
    executor = CodeExecutor(COMPILE_COMMAND, RUN_COMMAND, "main.cpp")
    compile_result, run_result = executor.compile_and_run()

    if not compile_result.success:
        return f"Compilation error:\n{compile_result.error_message or compile_result.stderr}"

    if not run_result or not run_result.success:
        return f"Execution error:\n{run_result.error_message if run_result else 'Unknown error'}"

    return run_result.stdout


def create_ui():
    """Create and launch the Gradio UI."""
    available_models = get_available_models()
    if not available_models:
        available_models = ["gpt-5"]  # Fallback

    default_python = """import time

def calculate(iterations, param1, param2):
    result = 1.0
    for i in range(1, iterations+1):
        j = i * param1 - param2
        result -= (1/j)
        j = i * param1 + param2
        result += (1/j)
    return result

start_time = time.time()
result = calculate(200_000_000, 4, 1) * 4
end_time = time.time()

print(f"Result: {result:.12f}")
print(f"Execution Time: {(end_time - start_time):.6f} seconds")
"""

    with gr.Blocks(title="Python to C++ Converter") as ui:
        gr.Markdown("# Python to C++ Code Converter")
        gr.Markdown("Convert Python code to optimized C++ using various LLM models.")

        with gr.Row():
            with gr.Column(scale=1):
                python_input = gr.Code(
                    label="Python Code",
                    value=default_python,
                    language="python",
                    lines=20,
                )
                python_run_btn = gr.Button("Run Python", variant="secondary")

            with gr.Column(scale=1):
                cpp_output = gr.Code(
                    label="Generated C++ Code",
                    value="",
                    language="cpp",
                    lines=20,
                )
                cpp_run_btn = gr.Button("Run C++", variant="secondary")

        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=available_models,
                value=available_models[0],
                label="Select Model",
            )
            convert_btn = gr.Button("Convert to C++", variant="primary")

        with gr.Row():
            python_output = gr.TextArea(
                label="Python Output",
                lines=5,
                interactive=False,
            )
            cpp_result = gr.TextArea(
                label="C++ Output",
                lines=5,
                interactive=False,
            )

        convert_btn.click(
            fn=convert_code,
            inputs=[model_dropdown, python_input],
            outputs=[cpp_output],
        )

        python_run_btn.click(
            fn=run_python,
            inputs=[python_input],
            outputs=[python_output],
        )

        cpp_run_btn.click(
            fn=run_cpp,
            inputs=[cpp_output],
            outputs=[cpp_result],
        )

    return ui


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser=True)
