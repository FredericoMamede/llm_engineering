from typing import Optional
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright  # type: ignore
from utils import validate_url

# Headers to mimic a real browser (prevents blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


# Cost management: limit content length for LLM processing
MAX_CONTENT_LENGTH = 2000
# Timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 10
# Timeout for Playwright navigation (milliseconds)
PLAYWRIGHT_TIMEOUT = 30000


class WebsiteScraper:
    """
    Optimized class-based scraper with lazy evaluation pattern.
    
    Optimized from original function-based approach that parsed HTML twice (inefficient).
    This class parses once in __init__, then uses @property decorators for lazy evaluation.
    Only computes what's accessed, caches results. Much faster when accessing multiple attributes.
    
    Pattern: Parse once, access multiple times. Avoids duplicate HTTP requests and parsing.
    """
    def __init__(self, url: str, max_length: int = MAX_CONTENT_LENGTH):
        """
        Initialize scraper with URL and optional content length limit.
        
        Args:
            url: URL to scrape
            max_length: Maximum content length (default: MAX_CONTENT_LENGTH)
        """
        self.url = url
        self.max_length = max_length
        
        # Make HTTP request with browser headers (prevents blocking) and timeout
        # Using constant instead of magic number makes it easy to adjust later
        self.response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        self.response.raise_for_status()  # Raise exception for bad status codes (4xx, 5xx)
        
        # Week 1 learning: Fail-fast validation - check before expensive parsing
        # If response is empty, no point in parsing HTML
        if not self.response.content:
            raise ValueError(f"Empty response from {url}")
        
        # Parse HTML once here - will be reused by title and content properties
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        
        # Lazy evaluation pattern: initialize cache variables as None
        # Will be computed on first access via @property decorators
        self._title = None
        self._content = None
    
    @property
    def title(self) -> str:
        """
        Extract page title using lazy evaluation.
        
        Only computes title when first accessed, then caches result.
        This is the lazy evaluation pattern - compute on demand, not upfront.
        """
        if self._title is None:
            self._title = self.soup.title.string if self.soup.title else "No title found"
        return self._title
    
    @property
    def content(self) -> str:
        """
        Extract clean text content (lazy evaluation).
        
        Removes scripts, styles, images, and inputs for cleaner text extraction.
        Limits to max_length characters for cost management.
        """
        if self._content is None:
            if self.soup.body:
                # Week 1 learning: Remove irrelevant elements for cleaner text extraction
                # Scripts, styles, images, and inputs don't contribute to text content
                # This makes the extracted text more useful for LLM processing
                for irrelevant in self.soup.body(["script", "style", "img", "input"]):
                    irrelevant.decompose()
                text = self.soup.body.get_text(separator="\n", strip=True)
            else:
                text = ""
            
            # Combine title and content, limit length for cost management
            # Week 1 learning: Truncate early to control LLM input costs
            self._content = (self.title + "\n\n" + text)[:self.max_length]
            
            # Edge case handling: if scraping returns empty content, provide fallback
            # This prevents downstream errors in LLM processing (empty input = bad results)
            if not self._content.strip():
                self._content = "No content found on page"
        return self._content


def scrape_static(url: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """
    Scrape static HTML content using requests + BeautifulSoup.
    
    Week 1 learning: This is the fast, lightweight approach for server-side rendered content.
    Works great for traditional websites, but fails on JavaScript-rendered sites (React, Vue, etc.).
    
    Tradeoff: Fast and lightweight vs. doesn't handle modern JS frameworks.
    
    Args:
        url: URL to scrape
        max_length: Maximum content length (default: MAX_CONTENT_LENGTH)
    
    Returns:
        Clean text content (title + body text, limited to max_length)
    
    Raises:
        requests.RequestException: If HTTP request fails
        ValueError: If URL is invalid or response is empty
    """
    validate_url(url)  # Week 1 pattern: Fail fast - validate before expensive operations
    scraper = WebsiteScraper(url, max_length=max_length)
    return scraper.content


def scrape_with_playwright(url: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """
    Scrape JavaScript-rendered content using Playwright.
    
    Week 1 learning: requests only gets static HTML. Playwright runs a real browser,
    executes JavaScript, then extracts the rendered HTML. This handles React, Vue, Angular, SPAs.
    
    Tradeoff: Browser overhead (slower, more resources) vs. compatibility (handles modern web apps).
    Use this as fallback when static scraping fails.
    
    Args:
        url: URL to scrape
        max_length: Maximum content length (default: MAX_CONTENT_LENGTH)
    
    Returns:
        Clean text content (title + body text, limited to max_length)
    
    Raises:
        Exception: If Playwright fails or browser cannot be launched
        ValueError: If URL is invalid
    """
    validate_url(url)  # Fail fast if URL is invalid
    
    # Playwright context manager ensures browser is closed even if errors occur
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless = no visible browser window
        page = browser.new_page()
        
        try:
            # Navigate and wait for network to be idle (all JS loaded)
            # Using constant instead of magic number makes timeout configurable
            page.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
            
            # Get rendered HTML and title after JavaScript execution
            html = page.content()
            title = page.title()
            
        finally:
            browser.close()  # Always close browser, even if navigation fails
    
    # Week 1 pattern: Validate before parsing (fail fast)
    if not html:
        raise ValueError(f"Empty HTML content from {url}")
    
    # Parse with BeautifulSoup using same pattern as static scraper
    # This keeps the text extraction logic consistent between both methods
    soup = BeautifulSoup(html, "html.parser")
    if soup.body:
        # Remove irrelevant elements (same cleanup as static scraper)
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    
    # Combine title and content, limit length for cost management
    content = (title + "\n\n" + text)[:max_length]
    
    # Edge case: if content is empty after extraction, provide fallback
    if not content.strip():
        content = "No content found on page"
    
    return content


def scrape_url(url: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """
    Scrape URL with intelligent fallback strategy.
    
    Strategy:
    1. Try requests + BeautifulSoup (static, fast)
    2. Fallback to Playwright (JavaScript, slower but handles modern sites)
    
    This follows the Week 1 pattern: try lightweight first, fallback to heavier solution.
    
    Args:
        url: URL to scrape
        max_length: Maximum content length (default: MAX_CONTENT_LENGTH)
    
    Returns:
        Clean text content from the webpage
    
    Raises:
        ValueError: If both methods fail or URL is invalid
    """
    # Week 1 learning: More specific exception handling provides better error context
    # Catch specific request exceptions instead of generic Exception
    # This makes debugging easier - know exactly what went wrong
    try:
        return scrape_static(url, max_length=max_length)
    except (requests.RequestException, requests.Timeout, requests.HTTPError, ValueError) as e:
        # Static scraping failed - try Playwright fallback for JavaScript-rendered sites
        # This is the "try lightweight first, fallback to heavier solution" pattern from Week 1
        try:
            return scrape_with_playwright(url, max_length=max_length)
        except Exception as e2:
            # Week 1 learning: Exception chaining preserves full error context
            # The "from e" shows the original exception, making debugging much easier
            # Can see both why static failed AND why Playwright failed
            raise ValueError(
                f"Failed to retrieve content from {url}. "
                f"Static scraping failed: {type(e).__name__}: {str(e)}. "
                f"Playwright fallback failed: {type(e2).__name__}: {str(e2)}. "
                "The page may require JavaScript or block scraping. Try providing raw text instead."
            ) from e  # Exception chaining preserves context