"""
Document discovery and fetching from verified sources.

This module fetches documents from sources listed in SOURCE_PLAN.md,
normalizes them to clean Markdown, and stores them with metadata.
"""

import re
import yaml
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tenacity import retry, stop_after_attempt, wait_exponential

# Handle imports for both script execution and module import
try:
    from .browser_fetcher import BrowserFetcher
except (ImportError, ValueError):
    # When running as script, import directly from file to avoid __init__.py issues
    browser_fetcher_path = Path(__file__).parent / "browser_fetcher.py"
    if browser_fetcher_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("browser_fetcher", browser_fetcher_path)
        browser_fetcher_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(browser_fetcher_module)
        BrowserFetcher = browser_fetcher_module.BrowserFetcher
    else:
        raise ImportError(f"Could not find browser_fetcher.py at {browser_fetcher_path}")


class SourceMetadata:
    """Metadata for a source document."""
    
    def __init__(
        self,
        requirement_id: Optional[str] = None,
        company_domain: Optional[str] = None,
        source_name: str = "",
        source_url: str = "",
        source_type: str = "",
        freshness_year: str = "",
        chunk_types: List[str] = None,
        category: str = "",
        priority: str = "",
    ):
        self.requirement_id = requirement_id
        self.company_domain = company_domain
        self.source_name = source_name
        self.source_url = source_url
        self.source_type = source_type
        self.freshness_year = freshness_year
        self.chunk_types = chunk_types or []
        self.category = category
        self.priority = priority
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for YAML frontmatter."""
        metadata = {
            "source_name": self.source_name,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "freshness_year": self.freshness_year,
            "chunk_types": self.chunk_types,
        }
        
        if self.requirement_id:
            metadata["requirement_id"] = self.requirement_id
            metadata["category"] = self.category
            metadata["priority"] = self.priority
        
        if self.company_domain:
            metadata["company_domain"] = self.company_domain
        
        return metadata
    
    def get_filename(self) -> str:
        """Generate deterministic filename from metadata."""
        if self.requirement_id:
            prefix = f"req_{self.requirement_id}"
        elif self.company_domain:
            prefix = f"company_{self.company_domain}"
        else:
            prefix = "unknown"
        
        # Clean URL to create filename-safe string
        parsed = urlparse(self.source_url)
        domain = parsed.netloc.replace("www.", "").replace(".", "_")
        path = parsed.path.strip("/").replace("/", "_") or "index"
        
        # Limit length
        path = path[:50] if len(path) > 50 else path
        
        filename = f"{prefix}_{domain}_{path}.md"
        # Remove invalid filename characters
        filename = re.sub(r'[<>:"|?*]', '_', filename)
        
        return filename


class SourcePlanParser:
    """Parse SOURCE_PLAN.md to extract source information."""
    
    def __init__(self, source_plan_path: Path):
        self.source_plan_path = source_plan_path
        self.sources: List[SourceMetadata] = []
    
    def parse(self) -> List[SourceMetadata]:
        """Parse SOURCE_PLAN.md and extract all sources."""
        with open(self.source_plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse requirements (1-22)
        self._parse_requirements(content)
        
        # Parse company context domains
        self._parse_company_context(content)
        
        return self.sources
    
    def _parse_requirements(self, content: str):
        """Parse requirement sources."""
        # Split by requirement sections
        req_sections = re.split(r'### Requirement (\d+):', content)[1:]  # Skip first empty part
        
        for i in range(0, len(req_sections), 2):
            if i + 1 >= len(req_sections):
                break
            
            req_num = req_sections[i].strip()
            req_content = req_sections[i + 1]
            
            # Extract category and priority
            category_match = re.search(r'\*\*Category:\*\*\s*(.+)', req_content)
            priority_match = re.search(r'\*\*Priority:\*\*\s*(.+)', req_content)
            category = category_match.group(1).strip() if category_match else ""
            priority = priority_match.group(1).strip() if priority_match else ""
            
            # Find all source sections (Primary, Secondary, Additional)
            source_sections = re.split(r'#### (Primary|Secondary|Additional)', req_content)
            
            for j in range(1, len(source_sections), 2):
                if j + 1 >= len(source_sections):
                    break
                
                source_type_label = source_sections[j]
                source_section = source_sections[j + 1]
                
                # Extract source name
                name_match = re.search(r'- \*\*Source:\*\*\s*(.+?)(?:\n|$)', source_section)
                if not name_match:
                    continue
                source_name = name_match.group(1).strip()
                
                # Extract URL
                url_match = re.search(r'- \*\*URL:\*\*\s*(https?://[^\s\)]+)', source_section)
                if not url_match:
                    continue
                source_url = url_match.group(1).strip()
                
                # Clean URL (remove trailing parentheses, etc.)
                source_url = re.sub(r'[\)\s]+$', '', source_url)
                
                # Extract metadata from the source section
                type_match = re.search(r'- \*\*Type:\*\*\s*(.+)', source_section)
                freshness_match = re.search(r'- \*\*Freshness:\*\*\s*(.+)', source_section)
                chunk_types_match = re.search(r'- \*\*Chunk Types:\*\*\s*(.+)', source_section)
                
                source_type = type_match.group(1).strip() if type_match else ""
                freshness = freshness_match.group(1).strip() if freshness_match else ""
                chunk_types_str = chunk_types_match.group(1).strip() if chunk_types_match else ""
                
                # Extract year from freshness
                year_match = re.search(r'(\d{4})', freshness)
                freshness_year = year_match.group(1) if year_match else "2024"
                
                # Parse chunk types
                chunk_types = [ct.strip() for ct in chunk_types_str.split(',')] if chunk_types_str else []
                
                metadata = SourceMetadata(
                    requirement_id=f"req_{req_num}",
                    source_name=source_name,
                    source_url=source_url,
                    source_type=source_type,
                    freshness_year=freshness_year,
                    chunk_types=chunk_types,
                    category=category,
                    priority=priority,
                )
                
                self.sources.append(metadata)
    
    def _parse_company_context(self, content: str):
        """Parse company context domain sources."""
        # Find company context section
        company_section_match = re.search(r'## COMPANY CONTEXT DOMAINS.*?(?=## SUMMARY|$)', content, re.DOTALL)
        if not company_section_match:
            return
        
        company_section = company_section_match.group(0)
        
        # Split by domain sections
        domain_sections = re.split(r'### Domain (\d+):', company_section)[1:]
        
        for i in range(0, len(domain_sections), 2):
            if i + 1 >= len(domain_sections):
                break
            
            domain_num = domain_sections[i].strip()
            domain_content = domain_sections[i + 1]
            
            # Extract domain name
            domain_name_match = re.search(r'^(.+?)(?:\n|$)', domain_content)
            domain_name = domain_name_match.group(1).strip() if domain_name_match else f"domain_{domain_num}"
            
            # Find all source sections (Primary, Secondary, Additional)
            source_sections = re.split(r'#### (Primary|Secondary|Additional)', domain_content)
            
            for j in range(1, len(source_sections), 2):
                if j + 1 >= len(source_sections):
                    break
                
                source_type_label = source_sections[j]
                source_section = source_sections[j + 1]
                
                # Extract source name
                name_match = re.search(r'- \*\*Source:\*\*\s*(.+?)(?:\n|$)', source_section)
                if not name_match:
                    continue
                source_name = name_match.group(1).strip()
                
                # Extract URL
                url_match = re.search(r'- \*\*URL:\*\*\s*(https?://[^\s\)]+)', source_section)
                if not url_match:
                    continue
                source_url = url_match.group(1).strip()
                
                # Clean URL
                source_url = re.sub(r'[\)\s]+$', '', source_url)
                
                # Extract metadata from the source section
                type_match = re.search(r'- \*\*Type:\*\*\s*(.+)', source_section)
                freshness_match = re.search(r'- \*\*Freshness:\*\*\s*(.+)', source_section)
                chunk_types_match = re.search(r'- \*\*Chunk Types:\*\*\s*(.+)', source_section)
                
                source_type = type_match.group(1).strip() if type_match else ""
                freshness = freshness_match.group(1).strip() if freshness_match else ""
                chunk_types_str = chunk_types_match.group(1).strip() if chunk_types_match else ""
                
                # Extract year
                year_match = re.search(r'(\d{4})', freshness)
                freshness_year = year_match.group(1) if year_match else "2024"
                
                # Parse chunk types
                chunk_types = [ct.strip() for ct in chunk_types_str.split(',')] if chunk_types_str else []
                
                metadata = SourceMetadata(
                    company_domain=f"domain_{domain_num}",
                    source_name=source_name,
                    source_url=source_url,
                    source_type=source_type,
                    freshness_year=freshness_year,
                    chunk_types=chunk_types,
                )
                
                self.sources.append(metadata)


class DocumentFetcher:
    """Fetch and normalize documents from URLs with HTTP and browser fallback."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._browser_fetcher: Optional[BrowserFetcher] = None
    
    def _get_browser_fetcher(self) -> BrowserFetcher:
        """Get or create browser fetcher instance (lazy initialization)."""
        if self._browser_fetcher is None:
            self._browser_fetcher = BrowserFetcher(headless=True)
        return self._browser_fetcher
    
    def _is_bot_protection_error(self, response: requests.Response) -> bool:
        """Check if response indicates bot protection."""
        if response.status_code in (401, 403):
            return True
        
        # Check for common bot protection indicators in response
        content = response.text.lower()
        bot_indicators = [
            'cloudflare',
            'access denied',
            'bot protection',
            'please enable javascript',
            'checking your browser',
        ]
        
        return any(indicator in content for indicator in bot_indicators)
    
    def _fetch_http(self, metadata: SourceMetadata) -> Optional[str]:
        """Fetch document using HTTP requests."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(metadata.source_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check for bot protection
            if self._is_bot_protection_error(response):
                return None  # Signal to try browser fallback
            
            return response.text
            
        except requests.exceptions.HTTPError as e:
            # Check if it's a bot protection error
            if hasattr(e.response, 'status_code') and e.response.status_code in (401, 403):
                return None  # Signal to try browser fallback
            # For other HTTP errors, retry will be handled by the caller
            raise
        except requests.exceptions.RequestException:
            # For network errors, retry will be handled by the caller
            raise
    
    def _fetch_browser(self, metadata: SourceMetadata) -> Optional[str]:
        """Fetch document using browser (fallback for bot-protected pages)."""
        try:
            print(f"   🌐 Using browser fallback for bot-protected page...")
            browser_fetcher = self._get_browser_fetcher()
            html_content = browser_fetcher.fetch(metadata.source_url)
            return html_content
        except Exception as e:
            print(f"   ❌ Browser fetch failed: {e}")
            return None
    
    def _normalize_html(self, html_content: str) -> str:
        """Normalize HTML content to clean Markdown."""
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Convert to Markdown
        markdown = md(str(soup), heading_style="ATX", bullets="-")
        
        # Clean up excessive whitespace
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        markdown = markdown.strip()
        
        return markdown
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self, metadata: SourceMetadata) -> Optional[str]:
        """
        Fetch document from URL and return normalized Markdown.
        
        Tries HTTP first, falls back to browser if bot protection is detected.
        """
        try:
            print(f"📥 Fetching: {metadata.source_name}")
            print(f"   URL: {metadata.source_url}")
            
            # Try HTTP fetch first
            html_content = self._fetch_http(metadata)
            
            # If HTTP fetch failed due to bot protection, try browser
            if html_content is None:
                html_content = self._fetch_browser(metadata)
            
            if html_content is None:
                return None
            
            # Normalize HTML to Markdown
            markdown = self._normalize_html(html_content)
            return markdown
            
        except requests.exceptions.RequestException as e:
            # Try browser fallback for any HTTP error (after retries exhausted)
            print(f"   ⚠️  HTTP fetch failed after retries: {e}")
            html_content = self._fetch_browser(metadata)
            if html_content:
                return self._normalize_html(html_content)
            return None
        except Exception as e:
            print(f"❌ Error processing {metadata.source_url}: {e}")
            return None
    
    def cleanup(self):
        """Cleanup browser resources."""
        if self._browser_fetcher:
            self._browser_fetcher.close()
            self._browser_fetcher = None
    
    def save(self, metadata: SourceMetadata, content: str):
        """Save normalized document with YAML frontmatter."""
        filename = metadata.get_filename()
        filepath = self.output_dir / filename
        
        # Create YAML frontmatter
        frontmatter = yaml.dump(metadata.to_dict(), default_flow_style=False, allow_unicode=True)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(frontmatter)
            f.write("---\n\n")
            f.write(content)
        
        print(f"✅ Saved: {filename}")
    
    def process_source(self, metadata: SourceMetadata) -> Optional[bool]:
        """Fetch and save a single source.
        
        Returns:
            True if successful
            False if failed
            None if skipped (placeholder or already exists)
        """
        # Skip URLs with "(or similar)" - these are placeholders
        if "(or similar" in metadata.source_url.lower() or "or similar" in metadata.source_url.lower():
            print(f"⚠️  Skipping placeholder URL: {metadata.source_url}")
            return None
        
        # Check if file already exists
        filename = metadata.get_filename()
        filepath = self.output_dir / filename
        if filepath.exists():
            print(f"⏭️  Skipping (already exists): {filename}")
            return None
        
        content = self.fetch(metadata)
        if content:
            self.save(metadata, content)
            return True
        return False


def main():
    """Main entry point for document discovery."""
    project_root = Path(__file__).parent.parent
    source_plan_path = project_root / "docs" / "SOURCE_PLAN.md"
    output_dir = project_root / "data" / "sources"
    
    print("🔍 Parsing SOURCE_PLAN.md...")
    parser = SourcePlanParser(source_plan_path)
    sources = parser.parse()
    
    print(f"📋 Found {len(sources)} sources to fetch")
    
    fetcher = DocumentFetcher(output_dir)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, source in enumerate(sources, 1):
        print(f"\n[{i}/{len(sources)}] Processing source...")
        result = fetcher.process_source(source)
        if result:
            successful += 1
        elif result is None:  # Skipped (placeholder or already exists)
            skipped += 1
        else:
            failed += 1
        
        # Rate limiting: wait 1 second between requests
        if i < len(sources):
            time.sleep(1)
    
    print(f"\n✅ Discovery complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Skipped: {skipped}")
    print(f"   Total: {len(sources)}")
    
    # Cleanup browser resources
    fetcher.cleanup()


if __name__ == "__main__":
    main()
