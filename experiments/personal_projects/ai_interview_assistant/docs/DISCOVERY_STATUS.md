# Document Discovery Status

**Last Updated:** 2026-01-22  
**Phase:** Document Discovery and Normalization

## Implementation Complete

### Created Components

1. **`ingest/discoverer.py`** - Complete document discovery and normalization system
   - `SourcePlanParser` - Parses SOURCE_PLAN.md to extract all sources with metadata
   - `SourceMetadata` - Data class for source metadata
   - `DocumentFetcher` - Fetches and normalizes documents from URLs
   - Main entry point with progress tracking

### Features

- ✅ Parses all 22 requirements + 7 company context domains from SOURCE_PLAN.md
- ✅ Extracts metadata: requirement_id, company_domain, source_name, source_url, source_type, freshness_year, chunk_types
- ✅ Fetches documents from URLs with retry logic
- ✅ Normalizes HTML to clean Markdown (removes navigation, ads, boilerplate)
- ✅ Adds YAML frontmatter with metadata
- ✅ Generates deterministic filenames
- ✅ Skips placeholder URLs ("or similar")
- ✅ Skips already-fetched files (resume capability)
- ✅ Rate limiting (1 second between requests)
- ✅ Error handling and progress reporting

### Output Structure

Documents are saved to `data/sources/` with format:
```
---
source_name: "TypeScript Official Handbook"
source_url: "https://www.typescriptlang.org/docs/handbook/intro.html"
source_type: "Official documentation"
freshness_year: "2024"
chunk_types:
  - primary
  - interview_question
requirement_id: "req_1"
category: "Experience"
priority: "Required"
---

[Clean Markdown content here]
```

### Filename Format

- Requirements: `req_{N}_{domain}_{path}.md`
- Company domains: `company_domain_{N}_{domain}_{path}.md`

### Next Steps

To run the discovery:

```bash
cd experiments/personal_projects/ai_interview_assistant
python ingest/discoverer.py
```

The script will:
1. Parse SOURCE_PLAN.md
2. Fetch all sources (skipping placeholders)
3. Normalize to Markdown
4. Save with metadata to `data/sources/`

**Expected:** ~95 sources to fetch (some will be placeholders and skipped)

### Fetch Limitations and Known Failures

Some sources returned 403 Forbidden errors due to bot protection mechanisms:

- **OpenAI Documentation** (`platform.openai.com`) - Cloudflare bot protection
- **Eventyr Website** (`eventyr.pro`) - Bot protection/rate limiting
- **Cloudflare-hosted pages** - Various documentation sites using Cloudflare protection

**Resolution:**
- Browser-based fallback using Playwright has been implemented to handle bot-protected pages
- The system attempts HTTP fetch first, then automatically falls back to a real browser (Playwright) when bot protection is detected
- Playwright launches a Chromium browser that behaves like a real user, executing JavaScript and waiting for content to render
- Browser fallback is used only for public pages that require bot protection bypass; it does not attempt to bypass paywalls or authentication
- Previously failing sources (Eventyr website, OpenAI docs) should now be fetchable via the browser fallback

### Notes

- Some URLs contain "(or similar)" - these are placeholders and will be skipped
- The script handles rate limits and errors gracefully
- Already-fetched files are skipped (safe to re-run)
- Processing time: ~2-3 minutes per source (with rate limiting)
