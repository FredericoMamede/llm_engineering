"""
LLM Engineering Playground - CLI Entry Point

Main entry point that orchestrates the multi-step LLM pipeline.
Demonstrates clean CLI design with proper argument parsing and error handling.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pipeline import run_pipeline
from scrapper import scrape_url
from utils import validate_text_input, format_output, format_output_json
from config import OUTPUT_FORMATS, DEFAULT_OUTPUT_FORMAT
from logger import logger

# Load environment variable
load_dotenv(override=True)


def parse_args():
    """
    Parse command-line arguments.
    
    Week 1 learning: argparse provides clean, professional CLI interface.
    Mutually exclusive groups ensure only one input method is used.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="LLM Engineering Playground - Multi-step content transformation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url "https://example.com" --model openai --tone professional
  python main.py --text "Your text here" --model ollama --translate nl --show-tokens
        """
    )
    
    # Input group (mutually exclusive - must provide one input method)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--text',
        type=str,
        help='Raw text input to process'
    )
    input_group.add_argument(
        '--url',
        type=str,
        help='URL to scrape and process'
    )
    input_group.add_argument(
        '--file',
        type=str,
        help='Path to text file to process'
    )
    
    # Required arguments
    parser.add_argument(
        '--model',
        choices=['openai', 'ollama'],
        required=True,
        help='Model provider to use (openai or ollama)'
    )
    parser.add_argument(
        '--model-name',
        type=str,
        help='Custom model name (overrides default for provider, e.g., gpt-4o, llama3.1)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--tone',
        choices=['professional', 'casual', 'technical', 'humorous'],
        default='professional',
        help='Tone for rewritten content (default: professional)'
    )
    parser.add_argument(
        '--stream',
        action='store_true',
        default=True,
        help='Stream responses in real-time (default: True)'
    )
    parser.add_argument(
        '--no-stream',
        dest='stream',
        action='store_false',
        help='Disable streaming (get full response at once)'
    )
    parser.add_argument(
        '--translate',
        type=str,
        help='Target language code for translation (e.g., nl for Dutch, es for Spanish)'
    )
    parser.add_argument(
        '--show-analysis',
        action='store_true',
        help='Display analysis results (useful for debugging/learning)'
    )
    parser.add_argument(
        '--show-tokens',
        action='store_true',
        help='Display token usage statistics'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        help='Save output to file (in addition to console)'
    )
    parser.add_argument(
        '--format',
        choices=OUTPUT_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=f'Output format (default: {DEFAULT_OUTPUT_FORMAT})'
    )
    parser.add_argument(
        '--json-mode',
        action='store_true',
        help='Use JSON mode for structured output (OpenAI only, requires --no-stream)'
    )
    parser.add_argument(
        '--no-progress',
        dest='show_progress',
        action='store_false',
        help='Disable progress indicators'
    )
    
    return parser.parse_args()


def read_file_content(file_path: str) -> str:
    """
    Read content from a text file.
    
    Week 1 learning: File input support makes the tool more flexible.
    Users can process large documents without pasting into CLI.
    
    Args:
        file_path: Path to text file
    
    Returns:
        File contents as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or cannot be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    try:
        content = path.read_text(encoding='utf-8')
        if not content.strip():
            raise ValueError(f"File is empty: {file_path}")
        return content
    except UnicodeDecodeError as e:
        raise ValueError(f"Cannot read file (not UTF-8 text): {file_path}. Error: {e}")


def display_results(
    results: Dict[str, Any],
    tone: Optional[str] = None,
    output_file: Optional[str] = None,
    output_format: str = DEFAULT_OUTPUT_FORMAT
) -> None:
    """
    Display pipeline results to console and optionally save to file.
    
    Week 1 learning: Clean output formatting makes results readable.
    Supports multiple output formats (text, JSON) for different use cases.
    
    Args:
        results: Pipeline results dict with summary, bullets, rewritten, etc.
        tone: Tone used for rewriting (for display header)
        output_file: Optional file path to save output
        output_format: Output format ('text', 'json', 'markdown')
    """
    # Week 1 learning: Support multiple output formats
    # JSON is useful for programmatic processing, text for human reading
    if output_format == 'json':
        output_text = format_output_json(results)
    else:
        # Default to text format
        output_text = format_output(results, tone=tone, include_separators=True)
    
    # Print to console
    print(output_text)
    
    # Optionally save to file
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            logger.info(f"Output saved to: {output_file}")
            print(f"\nOutput saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save output to file: {e}")
            print(f"Warning: Failed to save output to file: {e}", file=sys.stderr)


def main():
    """
    Main entry point for CLI tool.
    
    Week 1 learning: This orchestrates the entire pipeline:
    1. Parse CLI arguments
    2. Get content (text or URL)
    3. Validate input
    4. Run pipeline
    5. Display results
    
    Follows fail-fast pattern - validate early, fail clearly.
    """
    args = parse_args()
    
    try:
        # Step 1: Get content (either from text, URL, or file)
        if args.text:
            # Week 1 learning: Validate text input early (fail-fast pattern)
            # This prevents wasted API calls with invalid input
            logger.info("Processing text input")
            validate_text_input(args.text)
            content = args.text
        elif args.url:
            # Week 1 learning: Scraping handles its own validation
            # scrape_url will raise ValueError if URL is invalid
            logger.info(f"Processing URL: {args.url}")
            content = scrape_url(args.url)
        elif args.file:
            # Week 1 learning: File input support for processing documents
            logger.info(f"Processing file: {args.file}")
            content = read_file_content(args.file)
            validate_text_input(content)
        
        # Step 2: Run the multi-step pipeline
        # Week 1 Day 5 learning: This orchestrates Analyze → Transform → (Optional Translate)
        logger.info(f"Starting pipeline with model: {args.model}")
        # Week 1 learning: JSON mode requires non-streaming and OpenAI
        if args.json_mode:
            if args.stream:
                logger.warning("JSON mode requires --no-stream. Disabling streaming.")
                args.stream = False
            if args.model != 'openai':
                logger.warning("JSON mode is only supported for OpenAI models. Disabling JSON mode.")
                args.json_mode = False
        
        results = run_pipeline(
            content=content,
            model_provider=args.model,
            model_name=args.model_name,  # custom model name if provided
            tone=args.tone,
            stream=args.stream,
            translate_to=args.translate,
            show_analysis=args.show_analysis,
            show_tokens=args.show_tokens,
            show_progress=args.show_progress,
            json_mode=args.json_mode
        )
        
        # Step 3: Display results
        display_results(
            results,
            tone=args.tone,
            output_file=args.output_file,
            output_format=args.format
        )
        
        # Step 4: Exit with appropriate code
        # Week 1 learning: Check for errors and exit appropriately
        if results.get('errors'):
            print(f"\nWarning: {len(results['errors'])} error(s) occurred during processing.", file=sys.stderr)
            sys.exit(1)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        # Week 1 learning: Clear error messages for validation failures
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info("Interrupted by user")
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        # Catch-all for unexpected errors
        logger.exception(f"Unexpected error: {type(e).__name__}: {e}")
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()