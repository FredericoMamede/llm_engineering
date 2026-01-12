#!/usr/bin/env python3
"""
CLI entry point for meeting intelligence extraction.

Usage:
    python run.py --input sample_inputs/meeting.txt --output sample_outputs/meeting.json
"""

import sys
import argparse
from pathlib import Path
from extractor import MeetingExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured information from meeting transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --input sample_inputs/meeting.txt
  python run.py --input meeting.txt --output output.json
  python run.py --input meeting.txt --max-tokens 2000
        """
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to meeting transcript file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (auto-generated if not provided)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1500,
        help="Maximum tokens to generate (default: 1500)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Generation temperature (default: 0.3, lower = more structured)"
    )
    parser.add_argument(
        "--no-quantization",
        action="store_true",
        help="Disable 4-bit quantization (uses more memory)"
    )
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="HuggingFace token (or use HF_TOKEN env var)"
    )
    
    args = parser.parse_args()
    
    transcript_path = Path(args.input)
    if not transcript_path.exists():
        print(f"Error: Transcript file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    try:
        print(f"Initializing extractor (model: Llama 3.2 3B Instruct)")
        print(f"Quantization: {'disabled' if args.no_quantization else 'enabled (4-bit)'}")
        
        extractor = MeetingExtractor(
            use_quantization=not args.no_quantization,
            temperature=args.temperature,
            max_new_tokens=args.max_tokens,
            hf_token=args.hf_token
        )
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTroubleshooting:", file=sys.stderr)
        print("  - Verify access to meta-llama/Llama-3.2-3B-Instruct", file=sys.stderr)
        print("  - Set HF_TOKEN environment variable or use --hf-token", file=sys.stderr)
        print("  - Ensure GPU is available (or use --no-quantization for CPU)", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\nProcessing transcript: {transcript_path}")
    print(f"Temperature: {args.temperature}, Max tokens: {args.max_tokens}")
    
    try:
        output_path = extractor.extract_to_file(
            str(transcript_path),
            args.output
        )
        
        print(f"Extraction complete. Output saved to: {output_path}")
        extractor.unload()
        
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        print("The model output may not match the expected schema.", file=sys.stderr)
        print("Try adjusting --temperature or --max-tokens", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Extraction failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
