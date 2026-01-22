"""
Browser-based document fetcher using Playwright.

This module provides a fallback mechanism for fetching documents that are
protected by bot detection mechanisms (Cloudflare, etc.). It uses Playwright
to launch a real browser and fetch content as a human user would.
"""

from typing import Optional
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


class BrowserFetcher:
    """Fetch documents using a real browser to bypass bot protection."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the browser fetcher.
        
        Args:
            headless: Whether to run browser in headless mode (default: True)
        """
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    def _get_browser(self) -> Browser:
        """Get or create browser instance (lazy initialization)."""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                ]
            )
        return self._browser
    
    def fetch(self, url: str, timeout: int = 30000) -> Optional[str]:
        """
        Fetch document content from URL using a real browser.
        
        Args:
            url: URL to fetch
            timeout: Maximum time to wait for page load (milliseconds)
        
        Returns:
            HTML content as string, or None if fetch failed
        """
        try:
            browser = self._get_browser()
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
            )
            
            page = context.new_page()
            
            # Navigate to page
            page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Wait for main content to be ready
            # Try to wait for common content selectors
            try:
                page.wait_for_selector('body', timeout=5000)
            except PlaywrightTimeoutError:
                pass  # Body should already be there
            
            # Get page content
            html_content = page.content()
            
            # Clean up
            page.close()
            context.close()
            
            return html_content
            
        except PlaywrightTimeoutError as e:
            print(f"   ⚠️  Browser timeout for {url}: {e}")
            return None
        except Exception as e:
            print(f"   ⚠️  Browser fetch error for {url}: {e}")
            return None
    
    def close(self):
        """Close browser and cleanup resources."""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.close()
