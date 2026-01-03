"""
Loaders: text/file/URL ingestion and normalization.
"""

import os
from typing import Dict, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def load_text(text: str) -> Dict:
    """Load raw text input."""
    return {
        "type": "text",
        "content": text.strip() if text else "",
        "source": "direct_input",
    }


def load_file(file_path: str) -> Dict:
    """
    Load content from a file.
    
    Supports: .txt, .md, .py, .json, .yaml, .yml, .log
    """
    if not file_path:
        return {"type": "file", "content": "", "error": "No file path provided"}
    
    path = Path(file_path)
    
    if not path.exists():
        return {"type": "file", "content": "", "error": f"File not found: {file_path}"}
    
    # Supported extensions
    supported = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".log", ".csv", ".html"}
    if path.suffix.lower() not in supported:
        return {
            "type": "file",
            "content": "",
            "error": f"Unsupported file type: {path.suffix}. Supported: {supported}",
        }
    
    try:
        content = path.read_text(encoding="utf-8")
        return {
            "type": "file",
            "content": content,
            "source": str(path),
            "filename": path.name,
            "size": len(content),
        }
    except Exception as e:
        return {"type": "file", "content": "", "error": f"Error reading file: {e}"}


def load_url(url: str, timeout: int = 10) -> Dict:
    """
    Load and extract text content from a URL.
    
    Uses requests + BeautifulSoup for static pages.
    """
    if not url:
        return {"type": "url", "content": "", "error": "No URL provided"}
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AIKnowledgeAssistant/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML and extract text
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        content = "\n".join(lines)
        
        # Truncate if too long (context window consideration)
        max_chars = 50000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated...]"
        
        return {
            "type": "url",
            "content": content,
            "source": url,
            "title": soup.title.string if soup.title else None,
            "size": len(content),
        }
    
    except requests.Timeout:
        return {"type": "url", "content": "", "error": f"Timeout fetching URL: {url}"}
    except requests.RequestException as e:
        return {"type": "url", "content": "", "error": f"Error fetching URL: {e}"}
    except Exception as e:
        return {"type": "url", "content": "", "error": f"Error processing URL: {e}"}


def detect_input_type(text: str) -> str:
    """
    Detect the type of input based on content patterns.
    
    Returns: "error", "code", "url", "document", or "question"
    """
    if not text:
        return "question"
    
    lower = text.lower().strip()
    
    # URL detection
    if lower.startswith(("http://", "https://", "www.")):
        return "url"
    
    # Error/traceback detection
    if "traceback" in lower or "error:" in lower or "exception" in lower:
        return "error"
    
    # Code detection (Python-focused)
    code_indicators = ["def ", "class ", "import ", "from ", "if __name__", "print(", "return "]
    if any(ind in text for ind in code_indicators):
        return "code"
    
    # Document detection (markdown-ish)
    if text.startswith("#") or "```" in text or text.count("\n") > 10:
        return "document"
    
    return "question"


__all__ = ["load_text", "load_file", "load_url", "detect_input_type"]
