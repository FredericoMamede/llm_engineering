"""
Tool: summarize_text
Summarizes and extracts key points from technical documents.
"""

import re
from typing import Any, List

# Patterns for extracting structure
HEADING_PATTERN = re.compile(r"^(#+)\s+(.+)$", re.MULTILINE)
CODE_BLOCK_PATTERN = re.compile(r"```[\w]*\n[\s\S]*?```", re.MULTILINE)
BULLET_PATTERN = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)
NUMBERED_PATTERN = re.compile(r"^\s*\d+[.)]\s+(.+)$", re.MULTILINE)


def _extract_headings(text: str) -> List[str]:
    """Extract markdown headings from text."""
    matches = HEADING_PATTERN.findall(text)
    return [m[1] for m in matches]


def _count_code_blocks(text: str) -> int:
    """Count code blocks in text."""
    return len(CODE_BLOCK_PATTERN.findall(text))


def _extract_key_points(text: str) -> List[str]:
    """Extract bullet points and numbered lists."""
    bullets = BULLET_PATTERN.findall(text)
    numbered = NUMBERED_PATTERN.findall(text)
    return bullets[:5] + numbered[:5]  # Limit to 10 total


def _estimate_reading_time(text: str) -> str:
    """Estimate reading time based on word count."""
    words = len(text.split())
    minutes = max(1, words // 200)  # ~200 words per minute
    return f"{minutes} min read"


def _detect_document_type(text: str) -> str:
    """Detect the type of document based on content patterns."""
    lower = text.lower()
    
    if "error" in lower or "traceback" in lower or "exception" in lower:
        return "error_log"
    elif "api" in lower and ("endpoint" in lower or "request" in lower or "response" in lower):
        return "api_documentation"
    elif "install" in lower or "setup" in lower or "getting started" in lower:
        return "setup_guide"
    elif "def " in text or "class " in text or "function" in lower:
        return "code_documentation"
    elif "changelog" in lower or "release" in lower or "version" in lower:
        return "changelog"
    else:
        return "general_document"


def summarize_text(text: str, audience: str = "engineer") -> str:
    """
    Summarize a technical document and extract key information.
    
    Args:
        text: The document text to summarize
        audience: Target audience ("engineer", "manager", "beginner")
    
    Returns:
        Structured summary with key points and metadata
    """
    if not text or not text.strip():
        return "No text provided."

    # Basic stats
    word_count = len(text.split())
    line_count = len(text.strip().split("\n"))
    reading_time = _estimate_reading_time(text)
    doc_type = _detect_document_type(text)

    # Extract structure
    headings = _extract_headings(text)
    code_blocks = _count_code_blocks(text)
    key_points = _extract_key_points(text)

    # Build summary
    parts = ["**Document Analysis**\n"]
    parts.append(f"- Type: {doc_type.replace('_', ' ').title()}")
    parts.append(f"- Length: {word_count} words, {line_count} lines")
    parts.append(f"- Estimated reading time: {reading_time}")
    parts.append(f"- Code blocks: {code_blocks}")

    if headings:
        parts.append("\n**Structure (headings):**")
        for h in headings[:8]:  # Limit to 8
            parts.append(f"  - {h}")

    if key_points:
        parts.append("\n**Key points extracted:**")
        for kp in key_points[:6]:  # Limit to 6
            parts.append(f"  - {kp[:80]}{'...' if len(kp) > 80 else ''}")

    # Audience-specific notes
    parts.append(f"\n**For {audience}:**")
    if audience == "engineer":
        parts.append("  - Focus on code blocks and technical details.")
        if code_blocks > 0:
            parts.append(f"  - Review the {code_blocks} code example(s) for implementation details.")
    elif audience == "manager":
        parts.append("  - Focus on headings for high-level overview.")
        parts.append("  - Key decisions and tradeoffs are typically in the first few sections.")
    elif audience == "beginner":
        parts.append("  - Start with any 'Getting Started' or 'Introduction' sections.")
        parts.append("  - Code examples are meant to be copied and modified.")

    # What this means for you
    parts.append("\n**What this means for you:**")
    if doc_type == "error_log":
        parts.append("  This appears to be an error log. Look for the root cause in the traceback.")
    elif doc_type == "api_documentation":
        parts.append("  This is API documentation. Focus on endpoints, request/response formats.")
    elif doc_type == "setup_guide":
        parts.append("  This is a setup guide. Follow steps sequentially; don't skip prerequisites.")
    elif doc_type == "changelog":
        parts.append("  This is a changelog. Look for breaking changes and deprecations.")
    else:
        parts.append("  General technical document. Skim headings first, then dive into relevant sections.")

    return "\n".join(parts)


# Tool metadata for registry
TOOL_NAME = "summarize_text"
TOOL_IMPL = summarize_text
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "summarize_text",
        "description": "Summarize a technical document and extract key information. Returns structured analysis with key points.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The document text to summarize",
                },
                "audience": {
                    "type": "string",
                    "enum": ["engineer", "manager", "beginner"],
                    "description": "Target audience for the summary",
                },
            },
            "required": ["text"],
        },
    },
}
