#!/usr/bin/env python3
"""
CLI entry point for meeting intelligence extraction.

Usage:
    python run.py <transcript_file> [--output <output_file>]
"""

import sys
import argparse
from pathlib import Path
from extractor import MeetingExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured information from meeting transcripts"
    )
    parser.add_argument(
        "transcript",
        type=str,
        help="Path to meeting transcript file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path (auto-generated if not provided)"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=0.3,
        help="Generation temperature (default: 0.3)"
    )
    
    args = parser.parse_args()
    
    # Check if transcript file exists
    transcript_path = Path(args.transcript)
    if not transcript_path.exists():
        print(f"Error: Transcript file not found: {args.transcript}")
        sys.exit(1)
    
    # Create extractor
    try:
        extractor = MeetingExtractor(
            model=args.model,
            temperature=args.temperature
        )
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set OPENAI_API_KEY environment variable or create a .env file")
        sys.exit(1)
    
    # Extract
    print(f"Extracting information from: {transcript_path}")
    print(f"Using model: {args.model}")
    print("...")
    
    try:
        output_path = extractor.extract_to_file(
            str(transcript_path),
            args.output
        )
        
        print(f"✅ Extraction complete!")
        print(f"📄 Output saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
