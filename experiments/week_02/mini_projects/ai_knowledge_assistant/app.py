"""
AI Knowledge Assistant (Weeks 1–2 capstone)

Features:
- Streaming chat with prompt profiles
- Model selector with validation status (GPT, Ollama, DeepSeek, etc.)
- Profile selector (concise_expert / teaching_mode / reviewer_mode)
- File and URL input support
- Tool calling (explain_error, review_code, summarize_text)
- Graceful error handling and fallback
"""

import os
import sys
import uuid

import gradio as gr
from dotenv import load_dotenv

# Allow relative imports
sys.path.insert(0, os.path.dirname(__file__))

from core.orchestrator import Orchestrator
from io.loaders import load_file, load_url, detect_input_type

load_dotenv(override=True)

# Initialize orchestrator (validates models at startup)
print("\nStarting AI Knowledge Assistant...\n")
orchestrator = Orchestrator()
orchestrator.load_prompts(os.path.join(os.path.dirname(__file__), "prompts"))


def process_file(file) -> str:
    """Extract content from uploaded file."""
    if file is None:
        return ""
    result = load_file(file.name)
    if result.get("error"):
        return f"[File Error: {result['error']}]"
    return result.get("content", "")


def process_url(url: str) -> str:
    """Fetch and extract content from URL."""
    if not url or not url.strip():
        return ""
    result = load_url(url.strip())
    if result.get("error"):
        return f"[URL Error: {result['error']}]"
    return result.get("content", "")


def chat_fn(message, history, model, profile, file, url):
    """
    Main chat callback with file/URL support and model validation.
    
    Priority: file > URL > text message
    """
    # Validate model selection first
    is_available, validation_msg = orchestrator.model_registry.validate_selection(model)
    if not is_available:
        yield validation_msg
        return
    
    session_id = "chat-" + str(uuid.uuid4())
    
    # Determine input source
    content = ""
    if file is not None:
        content = process_file(file)
        if content and not content.startswith("["):
            content = f"[Uploaded file: {file.name}]\n\n{content}"
    elif url and url.strip():
        content = process_url(url)
        if content and not content.startswith("["):
            content = f"[URL: {url.strip()}]\n\n{content}"
    
    # Combine with message if both present
    if content:
        if message and message.strip():
            user_text = f"{message.strip()}\n\n---\n\n{content}"
        else:
            input_type = detect_input_type(content)
            if input_type == "error":
                user_text = f"Please explain this error:\n\n{content}"
            elif input_type == "code":
                user_text = f"Please review this code:\n\n{content}"
            else:
                user_text = f"Please summarize and explain:\n\n{content}"
    else:
        user_text = message

    if not user_text or not user_text.strip():
        yield "Please enter a question, paste code, upload a file, or provide a URL."
        return

    # Convert Gradio history to API format
    history_for_api = []
    for h in history or []:
        if isinstance(h, (list, tuple)) and len(h) == 2:
            history_for_api.append({"role": "user", "content": h[0]})
            history_for_api.append({"role": "assistant", "content": h[1]})

    # Stream response
    accumulated = ""
    for chunk in orchestrator.chat_stream(
        user_text=user_text,
        history=history_for_api,
        model_name=model,
        profile_name=profile,
        session_id=session_id,
    ):
        accumulated += chunk
        yield accumulated


def on_model_select(model_name):
    """Handle model selection - show warning if not available."""
    is_available, msg = orchestrator.model_registry.validate_selection(model_name)
    if is_available:
        return gr.update(visible=False)
    else:
        return gr.update(value=msg, visible=True)


def build_ui():
    """Build the Gradio Blocks UI with model status display."""
    # Get UI choices with status indicators
    model_choices = orchestrator.model_registry.get_ui_choices()
    available_models = orchestrator.model_registry.get_available()
    available_profiles = orchestrator.prompt_profiles.available()
    
    # Determine default model (first available)
    default_model = available_models[0] if available_models else (model_choices[0][1] if model_choices else None)

    # Custom CSS for disabled-looking options
    custom_css = """
    .model-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        color: #856404;
    }
    .model-warning.error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    .status-ready { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-error { color: #dc3545; }
    """

    with gr.Blocks(title="AI Knowledge Assistant", theme=gr.themes.Soft(), css=custom_css) as demo:
        gr.Markdown(
            """
            # AI Knowledge Assistant
            
            Ask technical questions, paste code/errors, upload files, or provide URLs.
            Select a model and prompt profile to customize responses.
            """
        )

        # Model status warning (hidden by default)
        model_warning = gr.Markdown(
            "",
            visible=False,
            elem_classes=["model-warning"]
        )

        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=model_choices,
                value=default_model,
                label="Model",
                info="✓ = Ready | ⚠ = Temporary issue | ✗ = Unavailable",
                scale=1,
                interactive=True,
            )
            profile_dropdown = gr.Dropdown(
                choices=available_profiles,
                value=available_profiles[0] if available_profiles else None,
                label="Prompt Profile",
                info="Concise Expert | Teaching Mode | Reviewer Mode",
                scale=1,
            )

        # Update warning when model changes
        model_dropdown.change(
            on_model_select,
            inputs=[model_dropdown],
            outputs=[model_warning],
        )

        with gr.Row():
            file_input = gr.File(
                label="Upload File (optional)",
                file_types=[".txt", ".md", ".py", ".json", ".yaml", ".yml", ".log"],
                scale=1,
            )
            url_input = gr.Textbox(
                label="URL (optional)",
                placeholder="https://example.com/docs",
                scale=1,
            )

        chatbot = gr.Chatbot(label="Conversation", height=400)
        msg_input = gr.Textbox(
            label="Your Question",
            placeholder="Ask a question, paste code/error, or describe what you need...",
            lines=3,
        )
        
        with gr.Row():
            submit_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.ClearButton([msg_input, chatbot, file_input, url_input], value="Clear")

        # Wire up the chat
        def respond(message, history, model, profile, file, url):
            history = history or []
            response = ""
            for chunk in chat_fn(message, history, model, profile, file, url):
                response = chunk
            history.append((message, response))
            return "", history

        submit_btn.click(
            respond,
            inputs=[msg_input, chatbot, model_dropdown, profile_dropdown, file_input, url_input],
            outputs=[msg_input, chatbot],
        )
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot, model_dropdown, profile_dropdown, file_input, url_input],
            outputs=[msg_input, chatbot],
        )

        # Model status accordion (collapsed by default)
        with gr.Accordion("Model Status", open=False):
            status_info = orchestrator.model_registry.info()
            status_lines = []
            for name, info in status_info.items():
                if info["status"] == "not_configured":
                    continue
                icon = "✓" if info["available"] else ("⚠" if info["status"] == "rate_limited" else "✗")
                status_lines.append(f"- **{name}** {icon}: {info['status_message']}")
            
            if status_lines:
                gr.Markdown("\n".join(status_lines))
            else:
                gr.Markdown("No models configured. Add API keys to .env")
            
            refresh_btn = gr.Button("Refresh Model Status", size="sm")
            
            def refresh_models():
                results = orchestrator.model_registry.revalidate_all()
                new_choices = orchestrator.model_registry.get_ui_choices()
                return gr.update(choices=new_choices)
            
            refresh_btn.click(refresh_models, outputs=[model_dropdown])

        gr.Markdown(
            """
            ---
            **Prompt Profiles:**
            - **concise_expert**: Direct answers, root cause + fix, minimal explanation.
            - **teaching_mode**: Step-by-step, explains "why", highlights patterns.
            - **reviewer_mode**: Critical review, flags risks, suggests alternatives.
            """
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch()
