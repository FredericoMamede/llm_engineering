"""
LLM Engineering Playground - CLI Entry Point

Main entry point that orchestrates the multi-step LLM pipeline.
Demonstrates clean CLI design with proper argument parsing and error handling.
"""
import argparse
import sys
from typing import Optional, Dict, Any
from pipeline import run_pipeline
from scrapper import scrape_url
from utils import validate_text_input, format_output


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
    
    # Input group (mutually exclusive - must provide either text or URL)
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
    
    # Required arguments
    parser.add_argument(
        '--model',
        choices=['openai', 'ollama'],
        required=True,
        help='Model provider to use (openai or ollama)'
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
    
    return parser.parse_args()


def display_results(results: Dict[str, Any], tone: Optional[str] = None, output_file: Optional[str] = None) -> None:
    """
    Display pipeline results to console and optionally save to file.
    
    Week 1 learning: Clean output formatting makes results readable.
    Uses format_output from utils for consistent formatting.
    
    Args:
        results: Pipeline results dict with summary, bullets, rewritten, etc.
        tone: Tone used for rewriting (for display header)
        output_file: Optional file path to save output
    """
    # Week 1 learning: Use format_output utility for consistent formatting
    # This keeps output formatting logic in one place (DRY principle)
    output_text = format_output(results, tone=tone, include_separators=True)
    
    # Print to console
    print(output_text)
    
    # Optionally save to file
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"\nOutput saved to: {output_file}")
        except Exception as e:
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
        # Step 1: Get content (either from text or URL)
        if args.text:
            # Week 1 learning: Validate text input early (fail-fast pattern)
            # This prevents wasted API calls with invalid input
            validate_text_input(args.text, min_length=10)
            content = args.text
        else:
            # Week 1 learning: Scraping handles its own validation
            # scrape_url will raise ValueError if URL is invalid
            content = scrape_url(args.url)
        
        # Step 2: Run the multi-step pipeline
        # Week 1 Day 5 learning: This orchestrates Analyze → Transform → (Optional Translate)
        results = run_pipeline(
            content=content,
            model_provider=args.model,
            tone=args.tone,
            stream=args.stream,
            translate_to=args.translate,
            show_analysis=args.show_analysis,
            show_tokens=args.show_tokens
        )
        
        # Step 3: Display results
        display_results(results, tone=args.tone, output_file=args.output_file)
        
        # Step 4: Exit with appropriate code
        # Week 1 learning: Check for errors and exit appropriately
        if results.get('errors'):
            print(f"\nWarning: {len(results['errors'])} error(s) occurred during processing.", file=sys.stderr)
            sys.exit(1)
        
    except ValueError as e:
        # Week 1 learning: Clear error messages for validation failures
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()