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

# Allow relative imports - ensure project root is on path
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.orchestrator import Orchestrator
from core.auth import is_auth_enabled, check_auth, require_auth_configured

# Import from local io module (avoid conflict with built-in io module)
# Workaround: import from the package using importlib to avoid built-in io conflict
import importlib.util
_io_loaders_path = os.path.join(project_root, "io", "loaders.py")
_io_audio_path = os.path.join(project_root, "io", "audio.py")

_io_loaders_spec = importlib.util.spec_from_file_location("io_loaders", _io_loaders_path)
_io_loaders = importlib.util.module_from_spec(_io_loaders_spec)
_io_loaders_spec.loader.exec_module(_io_loaders)

_io_audio_spec = importlib.util.spec_from_file_location("io_audio", _io_audio_path)
_io_audio = importlib.util.module_from_spec(_io_audio_spec)
_io_audio_spec.loader.exec_module(_io_audio)

load_file = _io_loaders.load_file
load_url = _io_loaders.load_url
detect_input_type = _io_loaders.detect_input_type
transcribe = _io_audio.transcribe
speak = _io_audio.speak

load_dotenv(override=True)

# Validate auth configuration (secure by default)
require_auth_configured()

# Initialize orchestrator (validates models at startup)
from core.logger import get_logger, log_access, error_logger, log_error

logger = get_logger(__name__)
logger.info("Starting AI Knowledge Assistant...")

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
    
    If both file and URL are present, both are processed and combined.
    This ensures that inputs are processed based on what's currently in the inputs,
    and inputs are cleared after processing to avoid confusion.
    
    Yields: response chunks (strings)
    """
    # Validate model selection first
    is_available, validation_msg = orchestrator.model_registry.validate_selection(model)
    if not is_available:
        yield validation_msg
        return
    
    # Generate new session if none exists
    if not session_id:
        session_id = "chat-" + str(uuid.uuid4())
        log_access("session_created", session_id=session_id)
    
    # Log access
    log_access(
        "chat_request",
        session_id=session_id,
        model=model,
        profile=profile,
        has_file=file is not None,
        has_url=bool(url and url.strip()),
        has_message=bool(message and message.strip()),
    )
    
    # Determine input source - can process both file and URL if both are present
    content_parts = []
    
    if file is not None:
        # Process file
        file_content = process_file(file)
        if file_content and not file_content.startswith("["):
            content_parts.append(f"[Uploaded file: {file.name}]\n\n{file_content}")
        elif file_content:
            content_parts.append(file_content)
    
    if url and url.strip():
        # Process URL
        url_content = process_url(url)
        if url_content and not url_content.startswith("["):
            content_parts.append(f"[URL: {url.strip()}]\n\n{url_content}")
        elif url_content:
            content_parts.append(url_content)
    
    # Combine all content parts
    if content_parts:
        content = "\n\n---\n\n".join(content_parts)
    else:
        content = ""
    
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
            # Convert Gradio 6.0 messages format to API format (for new sessions)
            history_for_api = []
            for h in history or []:
                if isinstance(h, dict) and "role" in h and "content" in h:
                    # Already in correct format
                    history_for_api.append({"role": h["role"], "content": h["content"]})
                elif isinstance(h, (list, tuple)) and len(h) == 2:
                    # Old tuple format (shouldn't happen with type="messages", but handle it)
                    history_for_api.append({"role": "user", "content": h[0]})
                    history_for_api.append({"role": "assistant", "content": h[1]})
    else:
        # Fallback to Gradio history
        history_for_api = []
        for h in history or []:
            if isinstance(h, dict) and "role" in h and "content" in h:
                history_for_api.append({"role": h["role"], "content": h["content"]})
            elif isinstance(h, (list, tuple)) and len(h) == 2:
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
        log_access("model_selected", model=model_name)
        return gr.update(visible=False)
    else:
        log_access("model_selection_failed", model=model_name, reason=msg)
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
    .input-info {
        background-color: #e7f3ff;
        border-left: 3px solid #2196F3;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9em;
        color: #1565C0;
    }
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
    
    # Gradio 6.0+ requires auth, theme, and css in launch(), not Blocks()
    with gr.Blocks(title="AI Knowledge Assistant") as demo:
        # Store launch parameters for later
        demo._launch_auth = auth_creds
        demo._launch_theme = gr.themes.Soft()
        demo._launch_css = custom_css
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

        gr.Markdown(
            "**Note:** File and URL inputs are automatically cleared after processing. "
            "If both are provided in the same message, both will be processed together.",
            elem_classes=["input-info"]
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

        # Chatbot and session state must be defined before audio handlers
        # Gradio Chatbot uses messages format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        chatbot = gr.Chatbot(label="Conversation", height=400)
        session_state = gr.State(None)
        
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
                # Normalize history to messages format
                formatted_history = []
                for h in (history or []):
                    if isinstance(h, dict) and "role" in h and "content" in h:
                        # Already in correct format
                        formatted_history.append({"role": h["role"], "content": h["content"]})
                    elif isinstance(h, (list, tuple)) and len(h) == 2:
                        # Legacy tuple format - convert to messages format
                        formatted_history.append({"role": "user", "content": str(h[0])})
                        formatted_history.append({"role": "assistant", "content": str(h[1])})
                
                if audio_path is None:
                    yield formatted_history, session_id, "No audio provided. Record or upload first."
                    return
                
                transcribed = transcribe(audio_path)
                
                if transcribed.startswith("Error") or not transcribed.strip():
                    yield formatted_history, session_id, transcribed
                    return
                
                yield formatted_history, session_id, f"Transcribed: {transcribed}"
                
                # Convert to API format for chat_fn
                history_for_api = []
                for h in formatted_history:
                    history_for_api.append({"role": h["role"], "content": h["content"]})
                
                # Send transcribed text to chat
                response = ""
                current_history = formatted_history.copy()
                # Add user message
                current_history.append({"role": "user", "content": transcribed})
                
                for chunk in chat_fn(transcribed, history_for_api, model, profile, None, None, session_id):
                    response = chunk
                    # Update history as we stream
                    if current_history and len(current_history) > 0 and current_history[-1]["role"] == "user":
                        # Add assistant response
                        current_history.append({"role": "assistant", "content": response})
                    elif current_history and len(current_history) > 0 and current_history[-1]["role"] == "assistant":
                        # Update existing assistant response
                        current_history[-1] = {"role": "assistant", "content": response}
                    yield current_history, session_id, f"Transcribed: {transcribed}"
                
                # Final update
                if current_history and len(current_history) > 0 and current_history[-1]["role"] == "assistant":
                    current_history[-1] = {"role": "assistant", "content": response}
                elif current_history and len(current_history) > 0 and current_history[-1]["role"] == "user":
                    current_history.append({"role": "assistant", "content": response})
                else:
                    current_history.append({"role": "assistant", "content": response})
                
                yield current_history, session_id, f"Sent: {transcribed}"
            
            transcribe_btn.click(
                fn=transcribe_and_send,
                inputs=[audio_path_state, chatbot, model_dropdown, profile_dropdown, session_state],
                outputs=[chatbot, session_state, audio_status],
                show_progress="full"
            )

        msg_input = gr.Textbox(
            label="Your Question",
            placeholder="Ask a question, paste code/error, or describe what you need...",
            lines=3,
        )
        
        # Last response for TTS
        last_response_state = gr.State("")
        
        with gr.Row():
            submit_btn = gr.Button("Send", variant="primary")
            # ClearButton automatically clears listed components when clicked - no explicit wiring needed
            gr.ClearButton([msg_input, chatbot, file_input, url_input], value="Clear")

        # Wire up the chat
        def respond(message, history, model, profile, file, url, session_id):
            """Handle user message and stream response - messages format.
            
            Clears file/URL inputs after processing to ensure only new inputs are considered.
            If both file and URL are present, both are processed and combined.
            """
            try:
                # Gradio Chatbot uses messages format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
                # Normalize history to list of message dicts
                if not isinstance(history, list):
                    history = []
                
                formatted_history = []
                for h in history:
                    if isinstance(h, dict) and "role" in h and "content" in h:
                        # Already in correct format
                        formatted_history.append({"role": h["role"], "content": h["content"]})
                    elif isinstance(h, (list, tuple)) and len(h) == 2:
                        # Legacy tuple format - convert to messages format
                        formatted_history.append({"role": "user", "content": str(h[0])})
                        formatted_history.append({"role": "assistant", "content": str(h[1])})
                
                # Show loading state - ignore empty messages
                if not message.strip() and not file and not url:
                    yield "", formatted_history, session_id, "", None, ""  # msg_input, chatbot, session_state, last_response_state, file_input, url_input
                    return
                
                # Determine what inputs are present (both can be present)
                has_file = file is not None
                has_url = bool(url and url.strip())
                
                # Build user display text showing what will be processed
                input_parts = []
                if has_file:
                    input_parts.append(f"📎 {file.name}")
                if has_url:
                    input_parts.append(f"🔗 {url.strip()}")
                
                if input_parts:
                    input_info = " + ".join(input_parts)
                    if message and message.strip():
                        user_display_text = f"{message.strip()} ({input_info})"
                    else:
                        user_display_text = f"Processing: {input_info}"
                else:
                    user_display_text = message.strip() if message else "User"
                
                # Convert history to API format (dicts) for chat_fn
                history_for_api = []
                for h in formatted_history:
                    history_for_api.append({"role": h["role"], "content": h["content"]})
                
                # Stream response - update history as we go
                current_history = formatted_history.copy()
                # Add user message to history
                current_history.append({"role": "user", "content": user_display_text})
                response = ""
                
                for chunk in chat_fn(message, history_for_api, model, profile, file, url, session_id):
                    response = chunk
                    if not isinstance(response, str):
                        response = str(response) if response else ""
                    
                    # Update assistant message in history
                    if current_history and len(current_history) > 0 and current_history[-1]["role"] == "user":
                        # Add assistant response
                        current_history.append({"role": "assistant", "content": response})
                    elif current_history and len(current_history) > 0 and current_history[-1]["role"] == "assistant":
                        # Update existing assistant response
                        current_history[-1] = {"role": "assistant", "content": response}
                    
                    # Yield updated history (messages format) - keep inputs for now, clear at end
                    yield "", current_history, session_id, "", file, url
                
                # Final yield with complete response - CLEAR INPUTS after processing
                if current_history and len(current_history) > 0 and current_history[-1]["role"] == "assistant":
                    current_history[-1] = {"role": "assistant", "content": response}
                elif current_history and len(current_history) > 0 and current_history[-1]["role"] == "user":
                    current_history.append({"role": "assistant", "content": response})
                else:
                    current_history.append({"role": "assistant", "content": response})
                
                # Clear file and URL inputs after processing
                yield "", current_history, session_id, response, None, ""
                
            except Exception as e:
                # Log error
                log_error(error_logger, e, context={
                    "function": "respond",
                    "message": message[:100] if message else None,
                })
                # Return error in proper format - clear inputs on error too
                error_msg = f"Error: {str(e)}"
                error_history = formatted_history.copy() if 'formatted_history' in locals() else []
                user_msg = user_display_text if 'user_display_text' in locals() else (message.strip() if message else "User")
                error_history.append({"role": "user", "content": str(user_msg)})
                error_history.append({"role": "assistant", "content": str(error_msg)})
                yield "", error_history, session_id, error_msg, None, ""

        submit_btn.click(
            respond,
            inputs=[msg_input, chatbot, model_dropdown, profile_dropdown, file_input, url_input, session_state],
            outputs=[msg_input, chatbot, session_state, last_response_state, file_input, url_input],
        ).then(
            lambda h: h,
            inputs=[chatbot],
            outputs=[chatbot]
        )
        
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot, model_dropdown, profile_dropdown, file_input, url_input, session_state],
            outputs=[msg_input, chatbot, session_state, last_response_state, file_input, url_input],
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
            
            # Gradio 6.0+ doesn't support height parameter for Dataframe
            session_list = gr.Dataframe(
                headers=["Session ID", "Started", "Last Activity", "Messages"],
                label="Recent Sessions",
                interactive=False
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
    import sys
    
    # Set up global exception handler to log all uncaught exceptions
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Global exception handler to log all uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={
                "type": "uncaught_exception",
                "exception_type": exc_type.__name__,
            }
        )
    
    sys.excepthook = exception_handler
    
    try:
        app = build_ui()
        # Gradio 6.0+ requires auth, theme, and css in launch()
        launch_kwargs = {}
        if hasattr(app, "_launch_auth") and app._launch_auth:
            launch_kwargs["auth"] = app._launch_auth
        if hasattr(app, "_launch_theme"):
            launch_kwargs["theme"] = app._launch_theme
        if hasattr(app, "_launch_css"):
            launch_kwargs["css"] = app._launch_css
        app.launch(**launch_kwargs)
    except Exception as e:
        log_error(error_logger, e, context={"function": "__main__", "stage": "app_launch"})
        raise
