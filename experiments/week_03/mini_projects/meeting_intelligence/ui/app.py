"""
Gradio UI for Meeting Intelligence Extractor.

Thin orchestration layer that calls core extraction logic.
No business logic is implemented here.
"""

import json
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv
import gradio as gr

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractor import MeetingExtractor

load_dotenv()


class UIState:
    """Maintains extractor singleton across UI session."""
    
    def __init__(self):
        self.extractor: Optional[MeetingExtractor] = None
    
    def get_extractor(self) -> MeetingExtractor:
        """Returns extractor instance, initializing on first access."""
        if self.extractor is None:
            self.extractor = MeetingExtractor()
        return self.extractor


state = UIState()


def _read_transcript(file_path: Optional[str], text_input: str) -> str:
    """
    Extracts transcript text from file upload or direct text input.
    
    File upload takes priority if both are provided. Returns empty string
    if neither is provided.
    """
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return text_input.strip() if text_input else ""


def _format_error_message(error: Exception) -> str:
    """Translates technical exceptions into user-facing error messages."""
    error_str = str(error)
    
    if "FileNotFoundError" in str(type(error)) or "not found" in error_str.lower():
        return "Transcript file not found. Please check the file path."
    
    if "token" in error_str.lower() and ("limit" in error_str.lower() or "length" in error_str.lower()):
        return "Transcript is too long for the model. Please use a shorter transcript."
    
    if "memory" in error_str.lower() or "cuda" in error_str.lower():
        return "Model ran out of memory. Try using a smaller transcript or restart the application."
    
    if "json" in error_str.lower() or "parse" in error_str.lower():
        return "Failed to parse structured output from the model. The model may have generated invalid JSON."
    
    if "schema" in error_str.lower() or "validation" in error_str.lower():
        return "Model output does not match expected format. Please try again."
    
    return f"Error: {error_str}"


def extract_meeting_intelligence(
    file_input: Optional[str],
    text_input: str
) -> Tuple[str, str, str]:
    """
    Orchestrates extraction workflow for Gradio UI.
    
    Returns tuple of (streaming_output, formatted_json, file_status).
    Handles errors and converts to user-friendly messages.
    """
    try:
        transcript = _read_transcript(file_input, text_input)
        
        if not transcript:
            return "", "", "Error: No transcript provided. Please upload a file or enter text."
        
        extractor = state.get_extractor()
        
        streaming_output = ""
        
        def stream_callback(chunk: str):
            nonlocal streaming_output
            streaming_output += chunk
        
        result = extractor.extract_with_streaming(transcript, stream_callback)
        
        formatted_json = json.dumps(result, indent=2, ensure_ascii=False)
        
        output_dir = Path(__file__).parent.parent / "sample_outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"meeting_{timestamp}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return streaming_output, formatted_json, f"Saved to: {output_path}"
        
    except Exception as e:
        error_msg = _format_error_message(e)
        return "", "", error_msg


def _clear_text_on_file_upload(file_path):
    """Clears text input when file is uploaded."""
    if file_path:
        return gr.update(value="")
    return gr.update()

def _clear_file_on_text_input(text, file_path):
    """Clears file upload when text is entered."""
    if text and text.strip():
        return gr.update(value=None)
    return gr.update()

def create_ui():
    """Builds and returns configured Gradio interface."""
    
    with gr.Blocks(title="Meeting Intelligence Extractor") as app:
        gr.Markdown("# Meeting Intelligence Extractor")
        gr.Markdown("Extract structured insights from meeting transcripts using Llama 3.2 3B Instruct.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Input")
                
                file_input = gr.File(
                    label="Upload Transcript File",
                    file_types=[".txt"],
                    type="filepath"
                )
                
                gr.Markdown("**OR**")
                
                text_input = gr.Textbox(
                    label="Enter Transcript Text",
                    placeholder="Paste meeting transcript here...",
                    lines=10,
                    max_lines=20
                )
                
                extract_btn = gr.Button("Extract Meeting Intelligence", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("## Output")
                
                streaming_output = gr.Textbox(
                    label="Streaming Model Output",
                    lines=8,
                    max_lines=15,
                    interactive=False
                )
                
                structured_json = gr.Code(
                    label="Structured Result (JSON)",
                    language="json",
                    lines=15
                )
                
                file_status = gr.Textbox(
                    label="File Status",
                    interactive=False
                )
        
        file_input.upload(
            fn=_clear_text_on_file_upload,
            inputs=[file_input],
            outputs=[text_input]
        )
        
        text_input.change(
            fn=_clear_file_on_text_input,
            inputs=[text_input, file_input],
            outputs=[file_input]
        )
        
        extract_btn.click(
            fn=extract_meeting_intelligence,
            inputs=[file_input, text_input],
            outputs=[streaming_output, structured_json, file_status]
        )
        
        gr.Markdown("---")
        gr.Markdown("**Note:** The model processes transcripts and extracts summary, decisions, action items, risks, and open questions.")
    
    return app


def main():
    """Entry point for UI server."""
    app = create_ui()
    app.launch(server_name="localhost", share=False)


if __name__ == "__main__":
    main()
