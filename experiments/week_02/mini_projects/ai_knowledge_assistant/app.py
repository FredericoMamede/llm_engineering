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
import pandas as pd
from dotenv import load_dotenv

# Allow relative imports
sys.path.insert(0, os.path.dirname(__file__))

from core.orchestrator import Orchestrator
from core.auth import is_auth_enabled, check_auth, require_auth_configured
from io.loaders import load_file, load_url, detect_input_type
from io.audio import transcribe, speak

load_dotenv(override=True)

# Validate auth configuration (secure by default)
require_auth_configured()

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


def chat_fn(message, history, model, profile, file, url, session_id):
    """
    Main chat callback with file/URL support and model validation.
    
    Priority: file > URL > text message
    """
    # Validate model selection first
    is_available, validation_msg = orchestrator.model_registry.validate_selection(model)
    if not is_available:
        yield validation_msg
        return
    
    # Generate new session if none exists
    if not session_id:
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

    # Load conversation history from session store if available
    if session_id:
        stored_history = orchestrator.session_store.load_history(session_id)
        if stored_history:
            # Use stored history (more reliable than Gradio's in-memory history)
            history_for_api = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in stored_history
            ]
        else:
            # Convert Gradio history to API format (for new sessions)
            history_for_api = []
            for h in history or []:
                if isinstance(h, (list, tuple)) and len(h) == 2:
                    history_for_api.append({"role": "user", "content": h[0]})
                    history_for_api.append({"role": "assistant", "content": h[1]})
    else:
        # Fallback to Gradio history
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

    # Configure auth (required unless DISABLE_AUTH=true)
    auth_enabled = is_auth_enabled()
    auth_creds = None
    if auth_enabled:
        from core.auth import get_credentials
        username, password = get_credentials()
        auth_creds = (username, password) if username and password else None
    elif not auth_enabled:
        # Auth is disabled (DISABLE_AUTH=true), show warning
        print("\n[WARN] Authentication is DISABLED (DISABLE_AUTH=true).")
        print("       This should only be used for development.\n")
    
    with gr.Blocks(title="AI Knowledge Assistant", theme=gr.themes.Soft(), css=custom_css, auth=auth_creds) as demo:
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
        
        # Audio input (optional, Day 2 feature)
        with gr.Accordion("Voice Input (Optional)", open=False):
            gr.Markdown("Record or upload audio. Transcription will be sent to chat.")
            
            with gr.Tab("Microphone"):
                mic_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Record (click mic, speak, click stop)"
                )
            
            with gr.Tab("Upload Audio"):
                audio_file_input = gr.Audio(
                    sources=["upload"],
                    type="filepath",
                    label="Upload audio file"
                )
            
            audio_path_state = gr.State(None)
            
            def capture_audio(audio):
                return audio
            
            mic_input.change(fn=capture_audio, inputs=[mic_input], outputs=[audio_path_state])
            audio_file_input.change(fn=capture_audio, inputs=[audio_file_input], outputs=[audio_path_state])
            
            transcribe_btn = gr.Button("Transcribe & Send to Chat", variant="primary")
            audio_status = gr.Textbox(
                label="Status",
                placeholder="",
                interactive=False,
                lines=1
            )
            
            def transcribe_and_send(audio_path, history, model, profile, session_id):
                """Transcribe audio and send directly to chat."""
                if audio_path is None:
                    yield history, session_id, "No audio provided. Record or upload first."
                    return
                
                transcribed = transcribe(audio_path)
                
                if transcribed.startswith("Error") or not transcribed.strip():
                    yield history, session_id, transcribed
                    return
                
                yield history, session_id, f"Transcribed: {transcribed}"
                
                # Send transcribed text to chat
                response = ""
                for chunk in chat_fn(transcribed, history, model, profile, None, None, session_id):
                    response = chunk
                    yield history, session_id, f"Transcribed: {transcribed}"
                
                history.append((transcribed, response))
                yield history, session_id, f"Sent: {transcribed}"
            
            transcribe_btn.click(
                fn=transcribe_and_send,
                inputs=[audio_path_state, chatbot, model_dropdown, profile_dropdown, session_state],
                outputs=[chatbot, session_state, audio_status],
                show_progress="full"
            )

        chatbot = gr.Chatbot(label="Conversation", height=400)
        msg_input = gr.Textbox(
            label="Your Question",
            placeholder="Ask a question, paste code/error, or describe what you need...",
            lines=3,
        )
        
        # Session state to maintain conversation across messages
        session_state = gr.State(None)
        
        # Last response for TTS
        last_response_state = gr.State("")
        
        with gr.Row():
            submit_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.ClearButton([msg_input, chatbot, file_input, url_input], value="Clear")
        
        # Wire up the chat
        def respond(message, history, model, profile, file, url, session_id):
            history = history or []
            response = ""
            
            # Show loading state
            if not message.strip() and not file and not url:
                yield "", history, session_id, ""
                return
            
            # Stream response with session persistence
            for chunk in chat_fn(message, history, model, profile, file, url, session_id):
                response = chunk
                yield "", history, session_id, ""
            
            # Update history and return session_id
            history.append((message, response))
            yield "", history, session_id, response

        submit_btn.click(
            respond,
            inputs=[msg_input, chatbot, model_dropdown, profile_dropdown, file_input, url_input, session_state],
            outputs=[msg_input, chatbot, session_state, last_response_state],
        ).then(
            lambda h: h,
            inputs=[chatbot],
            outputs=[chatbot]
        )
        
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot, model_dropdown, profile_dropdown, file_input, url_input, session_state],
            outputs=[msg_input, chatbot, session_state, last_response_state],
        ).then(
            lambda h: h,
            inputs=[chatbot],
            outputs=[chatbot]
        )

        # Voice output (optional, Day 2 feature)
        with gr.Accordion("Voice Output (Optional)", open=False):
            gr.Markdown("Convert the last response to speech.")
            
            with gr.Row():
                tts_voice = gr.Dropdown(
                    choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                    value="nova",
                    label="Voice",
                    scale=1
                )
                speak_btn = gr.Button("Speak Last Response", variant="primary", scale=1)
            
            audio_output = gr.Audio(
                label="Response Audio",
                type="filepath",
                autoplay=True
            )
            
            def speak_last_response(last_response, voice):
                """Convert last response to speech."""
                if not last_response or not last_response.strip():
                    return None
                return speak(last_response, voice=voice)
            
            speak_btn.click(
                fn=speak_last_response,
                inputs=[last_response_state, tts_voice],
                outputs=[audio_output]
            )
        
        # Session management (Day 2 feature)
        with gr.Accordion("Session Management", open=False):
            gr.Markdown("View and manage conversation sessions.")
            
            session_list = gr.Dataframe(
                headers=["Session ID", "Started", "Last Activity", "Messages"],
                label="Recent Sessions",
                interactive=False,
                height=200
            )
            
            def load_sessions():
                sessions = orchestrator.session_store.list_sessions(limit=10)
                if not sessions:
                    return pd.DataFrame(columns=["Session ID", "Started", "Last Activity", "Messages"])
                return pd.DataFrame([
                    {
                        "Session ID": s["session_id"][:20] + "...",
                        "Started": s["started"][:19] if s["started"] else "N/A",
                        "Last Activity": s["last_activity"][:19] if s["last_activity"] else "N/A",
                        "Messages": s["message_count"]
                    }
                    for s in sessions
                ])
            
            refresh_sessions_btn = gr.Button("Refresh Sessions", size="sm")
            refresh_sessions_btn.click(fn=load_sessions, outputs=[session_list])
            
            # Load sessions on accordion open
            session_list.value = load_sessions()
        
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
