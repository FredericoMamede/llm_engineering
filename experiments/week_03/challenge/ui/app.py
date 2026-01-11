"""
Gradio UI for Synthetic Data Generation

Simple, clear interface for generating synthetic datasets.
"""

import os
import gradio as gr
import json
from pathlib import Path
from typing import Optional, List, Tuple

# Load environment variables
from dotenv import load_dotenv

# Import our modules
import sys

# Challenge directory added to path (ui/app.py -> ui/ -> challenge/)
challenge_dir = Path(__file__).parent.parent
sys.path.insert(0, str(challenge_dir))

# Loading .env file from challenge directory
env_path = challenge_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from parent directories
    load_dotenv(dotenv_path=challenge_dir.parent / ".env", override=False)
    load_dotenv(dotenv_path=challenge_dir.parent.parent / ".env", override=False)

from models import create_model, HF_MODELS, OPENAI_MODELS, OLLAMA_MODELS
from models.base import GenerationConfig
from data_generation.generators import DataGenerator
from data_generation.schemas import SchemaType
from data_generation.utils import format_dataset_for_display, save_dataset


# Environment variable keys
HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_available_models() -> Tuple[List[str], List[str], List[str]]:
    """
    Get lists of available models based on authentication.
    
    Returns:
        (hf_models, openai_models, ollama_models)
        Models that require auth but don't have it are marked with [🔒] prefix
    """
    # HuggingFace models
    hf_models = []
    hf_gated = list(HF_MODELS["gated"].values())
    hf_open = list(HF_MODELS["open"].values())
    
    # Open models (always available)
    for model in hf_open:
        hf_models.append(model)
    
    # Gated models (mark if no auth)
    for model in hf_gated:
        if HF_TOKEN:
            hf_models.append(model)
        else:
            hf_models.append(f"{model} [🔒 Auth Required]")
    
    # OpenAI models
    openai_models = []
    for model in OPENAI_MODELS.values():
        if OPENAI_API_KEY:
            openai_models.append(model)
        else:
            openai_models.append(f"{model} [🔒 API Key Required]")
    
    # Ollama models (always available if Ollama is running)
    ollama_models = list(OLLAMA_MODELS.values())
    
    return hf_models, openai_models, ollama_models


# Get model lists
HF_MODEL_LIST, OPENAI_MODEL_LIST, OLLAMA_MODEL_LIST = get_available_models()

SCHEMA_TYPES = [st.value for st in SchemaType]
VARIATION_STRATEGIES = ["default", "formal", "casual", "detailed", "concise", "diverse"]


def estimate_max_tokens(num_records: int, schema_type: str) -> int:
    """
    Estimate recommended max_tokens based on number of records and schema complexity.
    
    Complex schemas (with arrays/nested objects) need more tokens per record.
    """
    # Base tokens per record (varies by schema complexity)
    tokens_per_record = {
        "customer_record": 150,      # Simple fields
        "incident_report": 200,      # Medium complexity
        "meeting_summary": 400,      # Complex (arrays, nested objects)
        "business_event": 250,        # Medium complexity
        "product_review": 200,       # Medium complexity
        "employee_record": 180,      # Simple to medium
        "generic_json": 300,         # Variable
    }
    
    base_tokens = tokens_per_record.get(schema_type, 250)
    estimated = base_tokens * num_records
    
    # Buffer for JSON formatting and prompt overhead
    estimated = int(estimated * 1.3)
    
    # Round to nearest 50
    estimated = ((estimated + 25) // 50) * 50
    
    # Clamp to reasonable range
    return max(200, min(estimated, 4000))


def generate_data(
    provider: str,
    model_name: str,
    schema_type: str,
    num_records: int,
    temperature: float,
    max_tokens: int,
    variation_strategy: str,
    use_quantization: bool
) -> tuple[str, str, Optional[str]]:
    """
    Main generation function called by Gradio.
    
    Returns:
        (display_text, json_output, file_path)
    """
    try:
        # Check for authentication requirements
        if provider == "huggingface":
            if not model_name:
                return "Error: Please select a HuggingFace model", "", None
            
            # Check if model requires auth and if we have it
            model_clean = model_name.split(" [🔒")[0]  # Remove auth marker
            is_gated = any(model_clean in models for models in HF_MODELS["gated"].values())
            
            if is_gated and not HF_TOKEN:
                return (
                    "Error: This model requires HuggingFace authentication.\n\n"
                    "Please set HF_TOKEN in your .env file.\n"
                    "Get your token from: https://huggingface.co/settings/tokens",
                    "",
                    None
                )
            
            model = create_model(
                "huggingface",
                model_clean,
                use_quantization=use_quantization,
                hf_token=HF_TOKEN
            )
        elif provider == "openai":
            if not model_name:
                return "Error: Please select an OpenAI model", "", None
            
            # Check if we have API key
            model_clean = model_name.split(" [🔒")[0]  # Remove auth marker
            
            if not OPENAI_API_KEY:
                return (
                    "Error: OpenAI API key is required.\n\n"
                    "Please set OPENAI_API_KEY in your .env file.\n"
                    "Get your key from: https://platform.openai.com/api-keys",
                    "",
                    None
                )
            
            model = create_model(
                "openai",
                model_clean,
                api_key=OPENAI_API_KEY
            )
        elif provider == "ollama":
            if not model_name:
                return "Error: Please select an Ollama model", "", None
            
            model = create_model("ollama", model_name)
        else:
            return f"Error: Unknown provider: {provider}", "", None
        
        # Create generator
        generator = DataGenerator(model)
        
        # Create config
        config = GenerationConfig(
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Generate
        result = generator.generate_dataset(
            schema_type=SchemaType(schema_type),
            num_records=num_records,
            variation_strategy=variation_strategy if variation_strategy != "default" else None,
            config=config
        )
        
        # Check for errors
        if "error" in result:
            return f"Error: {result['error']}", "", None
        
        # Format output
        records = result["records"]
        if not records:
            return "No records generated. Check raw output for details.", result.get("raw_output", ""), None
        
        # Display text
        display_text = format_dataset_for_display(records, max_records=10)
        display_text += f"\n\n--- Metadata ---\n"
        display_text += json.dumps(result["metadata"], indent=2)
        
        # JSON output
        json_output = json.dumps(records, indent=2, ensure_ascii=False)
        
        # Save to file (within challenge directory for Gradio security)
        output_dir = Path(__file__).parent.parent / "outputs" / "generated_samples"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{schema_type}_{timestamp}.json"
        filepath = output_dir / filename
        
        save_dataset(records, str(filepath), format="json")
        
        return display_text, json_output, str(filepath)
        
    except Exception as e:
        error_msg = f"Error during generation: {str(e)}"
        return error_msg, "", None


def update_model_list(provider: str):
    """Update model dropdown based on provider selection"""
    hf_models, openai_models, ollama_models = get_available_models()
    
    if provider == "huggingface":
        # Prefer open models if no auth, otherwise prefer first available
        default_value = None
        if hf_models:
            # Try to find an open model first
            open_models = list(HF_MODELS["open"].values())
            if open_models:
                default_value = open_models[0]
            else:
                default_value = hf_models[0]
        return gr.Dropdown(choices=hf_models, value=default_value)
    elif provider == "openai":
        default_value = openai_models[0] if openai_models else None
        return gr.Dropdown(choices=openai_models, value=default_value)
    elif provider == "ollama":
        default_value = ollama_models[0] if ollama_models else None
        return gr.Dropdown(choices=ollama_models, value=default_value)
    else:
        return gr.Dropdown(choices=[], value=None)


# Create Gradio interface
with gr.Blocks(title="Synthetic Data Generator") as app:
    gr.Markdown("""
    # 🎲 Synthetic Data Generation System
    
    Generate structured synthetic datasets using multiple LLM providers.
    
    **Features:**
    - Multiple providers: HuggingFace, OpenAI, Ollama
    - Multiple schemas: Customer records, incident reports, meeting summaries, and more
    - Prompt variation strategies for diverse outputs
    - Export to JSON files
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Configuration")
            
            provider = gr.Radio(
                choices=["huggingface", "openai", "ollama"],
                value="huggingface",
                label="Provider",
                info="Select model provider"
            )
            
            model_name = gr.Dropdown(
                choices=HF_MODEL_LIST,
                value=HF_MODEL_LIST[0] if HF_MODEL_LIST else None,
                label="Model",
                info="Select model (updates based on provider)"
            )
            
            schema_type = gr.Dropdown(
                choices=SCHEMA_TYPES,
                value=SCHEMA_TYPES[0],
                label="Schema Type",
                info="Type of records to generate"
            )
            
            num_records = gr.Slider(
                minimum=1,
                maximum=50,
                value=5,
                step=1,
                label="Number of Records",
                info="How many records to generate"
            )
            
            variation_strategy = gr.Dropdown(
                choices=VARIATION_STRATEGIES,
                value="default",
                label="Variation Strategy",
                info="Prompt variation approach"
            )
            
            gr.Markdown("### Generation Parameters")
            
            temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=0.7,
                step=0.1,
                label="Temperature",
                info="Higher = more creative, Lower = more deterministic"
            )
            
            max_tokens = gr.Slider(
                minimum=100,
                maximum=4000,
                value=estimate_max_tokens(5, SCHEMA_TYPES[0]),  # Smart default
                step=50,
                label="Max Tokens",
                info="💡 Auto-updates based on records & schema. Adjust manually if needed."
            )
            
            use_quantization = gr.Checkbox(
                value=True,
                label="Use 4-bit Quantization (HF only)",
                info="Reduces memory usage for HF models"
            )
            
            generate_btn = gr.Button("Generate Dataset", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("### Output")
            
            output_display = gr.Textbox(
                label="Generated Records",
                lines=20,
                max_lines=30
            )
            
            json_output = gr.Code(
                label="JSON Output",
                language="json",
                lines=15
            )
            
            file_output = gr.File(
                label="Saved File",
                visible=True
            )
    
    # Update model list when provider changes
    provider.change(
        fn=update_model_list,
        inputs=[provider],
        outputs=[model_name]
    )
    
    # Auto-update max_tokens when num_records or schema_type changes
    def update_max_tokens_value(num_records: int, schema_type: str) -> int:
        """Update max_tokens with suggested value"""
        return estimate_max_tokens(num_records, schema_type)
    
    # Update max_tokens when number of records changes
    num_records.change(
        fn=update_max_tokens_value,
        inputs=[num_records, schema_type],
        outputs=[max_tokens]
    )
    
    # Update max_tokens when schema type changes
    schema_type.change(
        fn=update_max_tokens_value,
        inputs=[num_records, schema_type],
        outputs=[max_tokens]
    )
    
    # Generate button
    generate_btn.click(
        fn=generate_data,
        inputs=[
            provider,
            model_name,
            schema_type,
            num_records,
            temperature,
            max_tokens,
            variation_strategy,
            use_quantization
        ],
        outputs=[output_display, json_output, file_output]
    )
    
    # Authentication status
    auth_status = []
    if HF_TOKEN:
        auth_status.append("✅ HuggingFace token configured")
    else:
        auth_status.append("⚠️ HuggingFace token not set (gated models unavailable)")
    
    if OPENAI_API_KEY:
        auth_status.append("✅ OpenAI API key configured")
    else:
        auth_status.append("⚠️ OpenAI API key not set (OpenAI models unavailable)")
    
    gr.Markdown(f"""
    ---
    ### Authentication Status
    
    {' | '.join(auth_status)}
    
    **Setup:** Create a `.env` file in the challenge directory with:
    ```
    HF_TOKEN=hf_your_token_here
    OPENAI_API_KEY=sk-your_key_here
    ```
    
    ---
    ### Tips
    
    - **Models marked with 🔒**: Require authentication (see status above)
    - **HuggingFace gated models**: Need HF_TOKEN and model access approval
    - **OpenAI models**: Require OPENAI_API_KEY (costs apply per generation)
    - **Ollama models**: Must be running locally (`ollama serve`) and models must be pulled
    - **Quantization**: Reduces memory for HF models but may slightly affect quality
    - **Temperature**: Lower (0.3-0.5) for structured data, higher (0.7-1.0) for variety
    - **Max Tokens**: 💡 **Auto-updates** based on number of records and schema complexity. You can adjust manually if needed.
    """)


if __name__ == "__main__":
    app.launch(share=False, server_name="localhost", server_port=7860, theme=gr.themes.Soft())
