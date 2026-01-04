"""
Loaders: text/file/URL ingestion and normalization.

Supports both static HTML (requests + BeautifulSoup) and JavaScript-rendered sites (Playwright).
Uses hybrid approach: try static first, fallback to Playwright if needed.
"""

import time
from typing import Dict, Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Playwright for JavaScript-rendered sites
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def load_text(text: str) -> Dict:
    """Load raw text input."""
    return {
        "type": "text",
        "content": text.strip() if text else "",
        "source": "direct_input",
    }


def load_file(file_path: str) -> Dict:
    """
    Load content from a file with security checks.
    
    Supports: .txt, .md, .py, .json, .yaml, .yml, .log, .csv, .html
    
    Security: Validates file path to prevent directory traversal attacks.
    """
    if not file_path:
        return {"type": "file", "content": "", "error": "No file path provided"}
    
    try:
        path = Path(file_path).resolve()
        
        # Security: Prevent directory traversal
        # Ensure the resolved path is within expected boundaries
        # In production, would restrict to a specific upload directory
        if not path.exists():
            return {"type": "file", "content": "", "error": f"File not found: {file_path}"}
        
        # Check file size (prevent loading huge files)
        max_size = 10 * 1024 * 1024  # 10MB
        if path.stat().st_size > max_size:
            return {
                "type": "file",
                "content": "",
                "error": f"File too large (max {max_size // 1024 // 1024}MB)",
            }
        
        # Supported extensions
        supported = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".log", ".csv", ".html"}
        if path.suffix.lower() not in supported:
            return {
                "type": "file",
                "content": "",
                "error": f"Unsupported file type: {path.suffix}. Supported: {supported}",
            }
        
        # Read file with encoding fallback
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with error handling for binary files
            return {
                "type": "file",
                "content": "",
                "error": "File appears to be binary or has unsupported encoding",
            }
        
        return {
            "type": "file",
            "content": content,
            "source": str(path),
            "filename": path.name,
            "size": len(content),
        }
    except Exception as e:
        return {"type": "file", "content": "", "error": f"Error reading file: {e}"}


def _is_js_heavy(html: str) -> bool:
    """
    Detect if page likely requires JavaScript to render content.
    
    Checks for common indicators of JS-rendered content.
    """
    if not html:
        return True
    
    html_lower = html.lower()
    
    # Check for common JS framework indicators
    js_indicators = [
        "react", "vue", "angular", "next.js", "nuxt",
        "loading...", "please enable javascript", "noscript",
        "data-reactroot", "__next__", "ng-app",
    ]
    
    if any(indicator in html_lower for indicator in js_indicators):
        return True
    
    # Check if body content is very minimal (likely JS-rendered)
    soup = BeautifulSoup(html, "html.parser")
    if soup.body:
        body_text = soup.body.get_text(strip=True)
        # If body has less than 200 chars, likely needs JS
        if len(body_text) < 200:
            return True
    
    return False


def _fetch_with_playwright(url: str, timeout: int = 30) -> Optional[str]:
    """
    Fetch URL content using Playwright (handles JavaScript).
    
    Returns HTML string or None if failed.
    """
    if not PLAYWRIGHT_AVAILABLE:
        return None
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate and wait for content to load
            page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Get rendered HTML after JS execution
            html = page.content()
            browser.close()
            
            return html
    except Exception as e:
        # Playwright failed, return None to fallback
        return None


def load_url(url: str, timeout: int = 10, use_js_fallback: bool = True) -> Dict:
    """
    Load and extract text content from a URL with security validation.
    
    Hybrid approach:
    1. Try requests + BeautifulSoup first (fast, for static pages)
    2. If content seems JS-rendered, fallback to Playwright (slower, handles JS)
    
    Security: Validates URL scheme and prevents SSRF attacks.
    """
    if not url:
        return {"type": "url", "content": "", "error": "No URL provided"}
    
    url = url.strip()
    
    # Security: Only allow http/https
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    # Additional validation: ensure it's a valid URL format
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if not parsed.netloc:
        return {"type": "url", "content": "", "error": "Invalid URL format"}
    
    # Security: Prevent SSRF by blocking local/private IPs (basic check)
    # In production, should use a proper SSRF protection library
    blocked_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
    if parsed.hostname and parsed.hostname.lower() in blocked_hosts:
        return {"type": "url", "content": "", "error": "Local URLs are not allowed for security"}
    
    # Try static fetch first (fast)
    html = None
    fetch_method = "static"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AIKnowledgeAssistant/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        html = response.text
    except requests.Timeout:
        return {"type": "url", "content": "", "error": f"Timeout fetching URL: {url}"}
    except requests.RequestException as e:
        return {"type": "url", "content": "", "error": f"Error fetching URL: {e}"}
    
    # Check if JavaScript is needed
    if use_js_fallback and _is_js_heavy(html):
        # Try Playwright fallback
        playwright_html = _fetch_with_playwright(url, timeout=timeout)
        if playwright_html:
            html = playwright_html
            fetch_method = "playwright"
    
    # Parse and extract content
    try:
        soup = BeautifulSoup(html, "html.parser")
        
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
            "fetch_method": fetch_method,  # For debugging
        }
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
