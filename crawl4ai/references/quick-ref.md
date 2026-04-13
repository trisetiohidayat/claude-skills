# Crawl4AI Quick Reference

## Table of Contents
1. [Installation](#installation)
2. [AsyncWebCrawler](#asyncwebcrawler)
3. [BrowserConfig](#browserconfig)
4. [CrawlerRunConfig](#crawlerrunconfig)
5. [Content Filters](#content-filters)
6. [Extraction Strategies](#extraction-strategies)
7. [Result Object](#result-object)
8. [CLI Reference](#cli-reference)
9. [Environment Variables](#environment-variables)

---

## Installation

```bash
pip install -U crawl4ai
crawl4ai-setup          # First-time browser setup
```

## AsyncWebCrawler

```python
from crawl4ai import AsyncWebCrawler

# Context manager (recommended)
async with AsyncWebCrawler(
    browser_config=BrowserConfig(...),
    verbose=True
) as crawler:
    # Single URL
    result = await crawler.arun(url="...", config=CrawlerRunConfig(...))

    # Multiple URLs
    results = await crawler.arun_many(urls=[...], config=CrawlerRunConfig(...))
```

## BrowserConfig

```python
from crawl4ai import BrowserConfig

BrowserConfig(
    headless=True,              # No GUI (default: True)
    verbose=False,              # Verbose logging
    proxy=None,                 # "http://proxy:port"
    user_agent=None,            # Custom UA string
    cookies=None,               # [{"name": "session", "value": "abc"}]
    headers=None,               # {"Authorization": "Bearer ..."}
    extra_http_headers=None,    # Additional headers
    steal_cookie=False,         # Share cookies across sessions
    word_count_threshold=10,   # Min words to consider non-empty
)
```

## CrawlerRunConfig

```python
from crawl4ai import CrawlerRunConfig, CacheMode

CrawlerRunConfig(
    # ─── Cache ───────────────────────────────────────
    cache_mode=CacheMode.ENABLED,   # ENABLED, BYPASS, ONLY (cache only, no fetch)

    # ─── Content Processing ─────────────────────────
    markdown_generator=None,        # DefaultMarkdownGenerator instance
    content_filter=None,            # Legacy: use markdown_generator.content_filter

    # ─── Extraction ─────────────────────────────────
    extraction_strategy=None,       # JsonCssExtractionStrategy, LLMExtractionStrategy

    # ─── JavaScript ─────────────────────────────────
    js_code=None,                   # JS to execute before capture
    js_only=False,                  # Capture JS-rendered only

    # ─── Timing ─────────────────────────────────────
    delay_before_return_html=0,     # Seconds to wait after JS
    page_timeout=30000,             # Page load timeout (ms)
    scroll_interval=1,              # Scroll interval (seconds)
    max_scroll_height=None,         # None=auto-detect, int=manual

    # ─── Page Constraints ────────────────────────────
    word_count_threshold=10,        # Min words per node
    remove_ads=True,               # Remove ad elements
    targeted_snapshots=None,        # ["div.content", "article.main"]

    # ─── Deep Crawl ─────────────────────────────────
    deep_crawl=False,              # Enable deep crawl mode
    max_pages=10,                  # Max pages for deep crawl
    max_depth=3,                   # Max link depth

    # ─── Robots.txt ─────────────────────────────────
    check_for_robots_txt=True,     # Respect robots.txt

    # ─── Auth ────────────────────────────────────────
    user_agent=None,               # Override browser user agent
    headers=None,                  # Custom HTTP headers

    # ─── Callbacks ───────────────────────────────────
    on_page_started=None,          # async def(url)
    on_page_finished=None,        # def(url, html) -> dict | None
    on_scraped=None,              # def(page_result)

    # ─── Logging ─────────────────────────────────────
    verbose=False,                # Verbose output
)
```

## Content Filters

### PruningContentFilter
```python
from crawl4ai.content_filter_strategy import PruningContentFilter

PruningContentFilter(
    threshold=0.48,           # 0.0 = aggressive prune, 1.0 = keep all
    threshold_type="fixed",   # or "dynamic"
    min_word_threshold=10,    # Min words per node to keep
)
```

### BM25ContentFilter
```python
from crawl4ai.content_filter_strategy import BM25ContentFilter

BM25ContentFilter(
    user_query="...",         # Query for relevance scoring
    bm25_threshold=1.0,      # Min BM25 score
    use_stemmer=True,        # Use Porter stemmer
)
```

### CosineStrategy
```python
from crawl4ai.content_filter_strategy import CosineStrategy

CosineStrategy(
    query="...",
    embedding_provider="openai",       # "openai" | "huggingface" | "ollama"
    embedding_model="text-embedding-3-small",
    embedding_api_key=None,             # Uses OPENAI_API_KEY env var
    semantic_threshold=0.3,            # Cosine similarity threshold
    top_n=10,                           # Top N chunks to keep
)
```

## Extraction Strategies

### JsonCssExtractionStrategy
```python
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

schema = {
    "baseSelector": "CSS selector for container",
    "fields": [
        {
            "name": "field_name",           # Output key
            "selector": "CSS selector",     # Element to target
            "type": "text",                 # "text" | "attribute"
            "attribute": "src",             # Required if type="attribute"
        },
        # ... more fields
    ]
}

strategy = JsonCssExtractionStrategy(schema, verbose=False)
config = CrawlerRunConfig(extraction_strategy=strategy)
```

### LLMExtractionStrategy
```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

strategy = LLMExtractionStrategy(
    api_provider="openai",       # "openai" | "anthropic" | "ollama" | "gemini"
    api_token=None,              # None = use env var
    model="gpt-4o-mini",
    extraction_type="schema",    # "schema" | "dynamic"
    schema={
        "name": "EntityName",
        "baseSelector": "...",
        "fields": [...]
    },
    input_format="markdown",     # "markdown" | "html" | "raw_html"
    temperature=0.1,
    max_tokens=2000,
)
```

## Result Object

```python
result = await crawler.arun(url="...")

result.markdown          # Full markdown (including fit_markdown if filter set)
result.raw_markdown      # Unfiltered markdown
result.fit_markdown      # Filtered markdown
result.html              # Raw HTML
result.url               # Final URL (after redirects)
result.status_code       # HTTP status code
result.success           # True if crawl succeeded
result.error_message     # Error description if failed
result.metadata          # Dict: {title, description, author, keywords, ...}
result.extracted_content # Structured extraction result (list/dict)
result.links             # Dict: {internal: [{url, text, base_url}, ...], external: [...]}
result.images            # List of image URLs
result.media             # Dict: {images, videos, audios}
```

## CLI Reference

```bash
crwl <URL> [OPTIONS]

# Output
-o, --output PATH              # Output file path
--output-type TYPE             # markdown (default) | html | json

# Crawling
--deep-crawl STRATEGY          # bfs | dfs (default: no deep crawl)
--max-pages N                  # Max pages for deep crawl
--max-depth N                  # Max depth for deep crawl

# Content
-q, --query TEXT               # LLM query for extraction
--no-remove-ads                # Don't remove ads

# Browser
--headless                     # Run headless (default)
--browser {chromium|firefox|webkit}
--viewport-width N             # Viewport width in pixels
--viewport-height N            # Viewport height in pixels

# Network
--proxy URL                    # HTTP proxy
-H, --header KEY:VALUE         # Custom header (repeatable)
--user-agent TEXT              # Custom user agent
--no-robots                    # Ignore robots.txt
--timeout N                    # Page timeout in seconds

# JavaScript
--js-code CODE                 # JS to execute before capture
--js-wait N                    # Wait N seconds after JS

# Advanced
--cache                        # Enable caching
--verbose                      # Verbose output
--save-screenshots             # Save page screenshots
--format {markdown|html|text}  # Output format

# Help
crwl --help
```

## Environment Variables

```bash
# API Keys
OPENAI_API_KEY                 # For LLM extraction / embedding
ANTHROPIC_API_KEY             # For Claude extraction
# OLLAMA_BASE_URL              # For local LLM (default: http://localhost:11434)

# Crawl4AI
CRAWL4AI_CACHE_DIR            # Cache directory
CRAWL4AI_HEADLESS             # Force headless mode
CRAWL4AI_VERBOSE              # Verbose logging
```
