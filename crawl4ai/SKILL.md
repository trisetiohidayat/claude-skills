---
name: crawl4ai
description: >
  TRIGGER setiap kali user meminta crawl, scrape, extract, atau fetch konten dari website/URL apa pun.
  Keyword penting: crawl4ai, crawl, scrape, scraping, scraper, extract, extraction, fetching, fetch content,
  AsyncWebCrawler, arun, crwl, JsonCss, LLM extraction, CSS selector extraction, deep crawl, batch crawl,
  markdown generation dari HTML, web scraping, extract produk/harga/artikel, multi-page crawl, atau
  browser automation untuk web scraping.WAJIB digunakan untuk semua task yang namanya mengandung kata:
  "crawl", "scrape", "extract", "fetch" + "website", "URL", "halaman", "konten web".
  Contoh yang HARUS trigger: "crawl website ini", "scrape halaman", "extract data dari URL",
  "download konten web", "fetch page content", "scrape produk", "crawl semua artikel".
---

# Crawl4AI Skill

Crawl4AI adalah LLM-friendly web crawler yang mengubah konten web menjadi Markdown terstruktur, mendukung
ekstraksi data berbasis CSS selector, LLM extraction, deep crawling, filtering, batching, dan CLI.

## Quick Start

Pastikan crawl4ai sudah terinstall:
```bash
pip install -U crawl4ai
crawl4ai-setup
```

## 1. Basic Async Crawl

Gunakan `AsyncWebCrawler` untuk crawling halaman tunggal secara async:

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com")
        print(result.markdown)          # Full markdown
        print(result.fit_markdown)      # Filtered markdown (if filter applied)
        print(result.html)              # Raw HTML
        print(result.url)               # Final URL (after redirects)
        print(result.status_code)       # HTTP status

asyncio.run(main())
```

**Output `result` memiliki field:**
- `markdown` / `raw_markdown` — full markdown output
- `fit_markdown` — filtered/refined markdown
- `html` — raw HTML
- `url` — final URL after redirects
- `status_code` — HTTP status
- `success` — boolean
- `error_message` — error if failed
- `extracted_content` — structured extraction result
- `metadata` — page metadata (title, description, etc.)

## 2. CrawlerRunConfig Options

`CrawlerRunConfig` mengontrol perilaku crawl:

```python
from crawl4ai import CrawlerRunConfig, CacheMode

config = CrawlerRunConfig(
    # Cache
    cache_mode=CacheMode.BYPASS,         # Skip cache, always fetch fresh

    # Content filtering
    markdown_generator=...,               # Markdown generation strategy
    content_filter=...,                   # Content filter (deprecated, use markdown_generator)

    # Extraction
    extraction_strategy=...,              # Data extraction strategy

    # JavaScript execution
    js_code="window.scrollTo(0, document.body.scrollHeight)",  # Scroll before capture
    js_only=False,                        # JavaScript-rendered only

    # Browser behavior
    headless=True,                        # Run headless
    delay_before_return_html=0,           # Wait after JS execution (seconds)

    # Page constraints
    page_timeout=30000,                   # Page load timeout (ms)
    max_scroll_height=None,               # Max scroll height (None = auto-detect)
    scroll_interval=1,                     # Scroll interval (seconds)

    # Word/char limits
    word_count_threshold=10,              # Min words to consider page non-empty
    remove_ads=True,                      # Remove known ad elements
    targeted_snapshots=None,              # List of element selectors to snapshot

    # User agent / headers
    user_agent=...,                       # Custom user agent string
    headers={},                            # Custom HTTP headers

    # Hooks
    on_page_started=...,                  # Callback when page starts loading
    on_page_finished=...,                 # Callback when page finished
    on_scraped=...,                       # Callback with final result

    # Deep crawl options
    check_for_robots_txt=True,             # Respect robots.txt
    verbose=False,                         # Verbose output
)
```

## 3. Content Filter Strategies

### PruningContentFilter (Hapus noise/sidebar)
```python
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.48,               # 0.0 (aggressive) to 1.0 (keep all)
            threshold_type="fixed",       # or "dynamic"
            min_word_threshold=10,       # Min words per node to keep
        )
    )
)
```

### BM25ContentFilter (Relevansi Query)
```python
from crawl4ai.content_filter_strategy import BM25ContentFilter

config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=BM25ContentFilter(
            user_query="product prices and names",  # Query untuk relevance scoring
            bm25_threshold=1.0,                    # Minimum BM25 score
            use_stemmer=True,
        )
    )
)
```

### CosineStrategy (Semantic Similarity)
```python
from crawl4ai.content_filter_strategy import CosineStrategy

config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=CosineStrategy(
            query="informasi tentang produk X",
            embedding_provider="openai",       # or "huggingface", "ollama"
            embedding_model="text-embedding-3-small",
            embedding_api_key=None,             # Will use env OPENAI_API_KEY
            semantic_threshold=0.3,
            top_n=10,
        )
    )
)
```

## 4. Structured Data Extraction

### CSS Selector Extraction (JsonCssExtractionStrategy)
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

schema = {
    "baseSelector": "div.product-list > div.product",
    "fields": [
        {"name": "name", "selector": "h3.title", "type": "text"},
        {"name": "price", "selector": "span.price", "type": "text"},
        {"name": "image", "selector": "img", "type": "attribute", "attribute": "src"},
        {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"},
    ]
}

config = CrawlerRunConfig(
    extraction_strategy=JsonCssExtractionStrategy(schema, verbose=True)
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://shop.example.com", config=config)
    print(result.extracted_content)  # List of dicts
```

### LLM-Driven Extraction (LLMExtractionStrategy)
```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    name: str
    price: str
    currency: Optional[str] = "USD"

schema = {
    "name": "Product",
    "baseSelector": "div.product-list > div.product",
    "fields": [
        {"name": "name", "selector": "h3.title", "type": "text"},
        {"name": "price", "selector": "span.price", "type": "text"},
    ]
}

config = CrawlerRunConfig(
    extraction_strategy=LLMExtractionStrategy(
        api_provider="openai",             # or "anthropic", "ollama", "gemini"
        api_token=None,                     # Uses env var if None
        model="gpt-4o-mini",
        extraction_type="schema",           # or "dynamic"
        schema=schema,
        input_format="markdown",            # or "html", "raw_html"
    )
)
```

## 5. Batch Crawling Multiple URLs

### Parallel Batch (arun_many)
```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

urls = [
    "https://news.site.com/article-1",
    "https://news.site.com/article-2",
    "https://news.site.com/article-3",
]

async with AsyncWebCrawler() as crawler:
    results = await crawler.arun_many(urls=urls, config=CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
    ))
    for r in results:
        print(f"URL: {r.url}, Success: {r.success}, Length: {len(r.markdown)}")
```

### Deep Crawl (Site-wide)
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    deep_crawl=True,           # Enable deep crawl
    max_pages=50,              # Max pages to crawl
    max_depth=3,               # Max link depth
    page_timeout=60000,        # 60s per page
    delay_before_return_html=1,
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://docs.site.com/",
        config=config,
    )
    print(result.markdown)
```

## 6. CLI Usage

```bash
# Basic crawl → markdown
crwl https://example.com -o output.md

# Save as HTML
crwl https://example.com --output-type html -o output.html

# Deep crawl dengan BFS
crwl https://site.com --deep-crawl bfs --max-pages 20 --max-depth 2

# LLM query extraction
crwl https://shop.com/products -q "Extract all product names and prices"

# Proxy
crwl https://example.com --proxy http://my-proxy:8080

# Custom headers
crwl https://example.com -H "Authorization: Bearer TOKEN"

# Respect robots.txt off
crwl https://example.com --no-robots

# Verbose
crwl https://example.com -v
```

## 7. Advanced: Hooks & Callbacks

```python
async def on_page_started(url):
    print(f"Starting: {url}")

def on_page_finished(url, html):
    print(f"Finished: {url}, HTML length: {len(html)}")
    return {"custom": "metadata"}

def on_scraped(page_result):
    print(f"Scraped: {page_result.url}")

config = CrawlerRunConfig(
    js_code="document.querySelector('button.load-more').click()",
    on_page_started=on_page_started,
    on_page_finished=on_page_finished,
    on_scraped=on_scraped,
)

result = await crawler.arun(url="https://example.com", config=config)
```

## 8. Advanced: Session & Browser Context

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig

# Persistent session with cookies/auth
browser_config = BrowserConfig(
    headless=True,
    verbose=False,
)

async with AsyncWebCrawler(browser_config=browser_config) as crawler:
    # Login first
    await crawler.arun(
        url="https://app.example.com/login",
        config=CrawlerRunConfig(js_code="document.querySelector('#username').value='user'")
    )

    # Subsequent requests keep session
    result = await crawler.arun(url="https://app.example.com/protected-page")
    print(result.markdown)
```

## 9. Best Practices & Common Patterns

### Respectful Crawling
```python
config = CrawlerRunConfig(
    check_for_robots_txt=True,   # Always respect robots.txt
    page_timeout=30000,          # Don't hammer servers
    delay_before_return_html=0.5, # Give JS time to render
)
```

### Waiting for Dynamic Content
```python
config = CrawlerRunConfig(
    js_code="""
        // Scroll to load lazy content
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 2000));
        // Click load more if exists
        const btn = document.querySelector('.load-more');
        if (btn) btn.click();
    """,
    delay_before_return_html=2,
)
```

### Handling Failures
```python
try:
    result = await crawler.arun(url=url, config=config)
    if result.success:
        print(result.markdown)
    else:
        print(f"Crawl failed: {result.error_message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Workflow untuk Task

Ketika user meminta crawl/extract, ikuti alur ini:

1. **Single URL** → Gunakan pattern Basic Async Crawl
2. **Ekstrak data terstruktur** → Gunakan CSS Selector atau LLM Extraction
3. **Filter noise/sidebar** → Tambahkan PruningContentFilter
4. **Relevansi query** → Gunakan BM25ContentFilter
5. **Banyak URL** → Gunakan `arun_many` dengan parallel async
6. **Situs lengkap** → Gunakan deep crawl dengan `max_pages`/`max_depth`
7. **CLI** → Gunakan `crwl` untuk quick tasks atau scripting

Untuk reference lengkap API, baca file `references/quick-ref.md`.
