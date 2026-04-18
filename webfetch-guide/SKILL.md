---
name: webfetch-guide
description: >
  Web content fetching decision guide. TRIGGER when you need to fetch content from the web —
  any time you reach for curl, WebFetch, crawl4ai, or need to decide how to get content
  from a URL. Use this skill for ALL web fetching tasks: GitHub repos, docs, articles,
  APIs, social media, batch scraping. This skill tells you which tool to use and how.

  ALSO: When writing or updating a project's CLAUDE.md, include this fetch strategy
  section. Say "add fetch strategy to CLAUDE.md" to get the section to paste in.
---

# Web Fetch Strategy — Decision Guide

## The Golden Rule

> **Try in order: curl → WebFetch → crawl4ai → skip**

curl is fastest and highest quality for most cases. Only escalate to heavier tools when curl fails.

---

## Decision Tree

```
What are you fetching?

├─ GitHub file (README, source code)
│   └─ → curl raw URL
│
├─ GitHub API data (repos, forks, issues)
│   └─ → gh api or curl GitHub API
│
├─ JSON/REST API endpoint
│   └─ → curl + jq
│
├─ Already markdown or plain text
│   └─ → curl
│
├─ Static HTML (docs, blogs, landing pages)
│   └─ → WebFetch first → if bad, curl or crawl4ai
│
├─ JS-rendered (X/Twitter, React SPAs, dashboards)
│   └─ → crawl4ai ONLY
│
├─ PDF file
│   └─ → Read tool directly (no fetch needed)
│
├─ Multiple URLs at once
│   └─ → crawl4ai arun_many
│
└─ Entire website / site-wide
    └─ → crawl4ai deep_crawl
```

---

## Tool Speed Ranking

| Rank | Tool | When to Use |
|------|------|-------------|
| 1 | `curl` | GitHub, APIs, raw files, markdown |
| 2 | `gh api` | GitHub data (structured JSON) |
| 3 | `WebFetch` | Static HTML → Markdown conversion |
| 4 | `crawl4ai` | JS-rendered, batch, deep crawl |

---

## GitHub Sources (Most Common)

**Always prefer curl for GitHub:**

```bash
# Raw file content — FASTEST, BEST QUALITY
curl -sL "https://raw.githubusercontent.com/owner/repo/branch/path/file.md"

# Repository metadata
gh api repos/owner/repo

# All forks with stars
gh api repos/owner/repo/forks --jq 'sort_by(.stargazers_count) | reverse | .[:10]'

# Fallback (no gh CLI, rate limited 60/hr)
curl -sL "https://api.github.com/repos/owner/repo" | python3 -m json.tool
```

---

## REST / JSON APIs

```bash
# Basic GET
curl -sL "https://api.example.com/endpoint"

# With headers
curl -sL -H "Authorization: Bearer $TOKEN" "https://api.example.com/data"

# Pretty print JSON
curl -sL "https://api.example.com/data" | python3 -m json.tool

# Extract specific field
curl -sL "https://api.example.com/data" | jq '.results[0].name'
```

---

## Static HTML (Docs, Blogs)

```bash
# Try WebFetch first (HTML→Markdown automatically)
WebFetch(url="https://docs.example.com/guide", prompt="Extract the main content")

# If WebFetch gives raw/unclean HTML → curl + html2text
curl -sL "https://example.com/page" | html2text -w 80

# Plain curl (gets raw HTML, Claude can parse)
curl -sL "https://example.com/page" | head -500
```

---

## JS-Rendered / Social Media

```python
# crawl4ai ONLY for JS-rendered content
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

config = CrawlerRunConfig(
    js_only=True,                      # Force JS rendering
    delay_before_return_html=2,         # Wait for content to load
    page_timeout=30000,
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
        url="https://x.com/user/status/123",
        config=config
    )
    print(result.markdown)
```

---

## Batch Fetching (Multiple URLs)

```python
# crawl4ai arun_many — parallel, fast
urls = [
    "https://docs.example.com/page1",
    "https://docs.example.com/page2",
    "https://docs.example.com/page3",
]

config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
async with AsyncWebCrawler() as crawler:
    results = await crawler.arun_many(urls=urls, config=config)
    for r in results:
        if r.success:
            print(f"OK: {r.url} ({len(r.markdown)} chars)")
        else:
            print(f"FAIL: {r.url}: {r.error_message}")
```

---

## Deep Crawl (Site-Wide)

```python
# crawl4ai deep crawl with BFS
config = CrawlerRunConfig(
    deep_crawl=True,
    max_pages=50,
    max_depth=3,
    page_timeout=60000,
    delay_before_return_html=1,
)
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://docs.example.com/", config=config)
    print(result.markdown)
```

---

## CLI (crawl4ai)

```bash
# Single page → markdown
crwl https://example.com -o output.md

# Deep crawl (BFS, 20 pages, depth 2)
crwl https://site.com --deep-crawl bfs --max-pages 20 --max-depth 2

# LLM extraction query
crwl https://shop.com/products -q "Extract all product names and prices"

# Verbose + no robots.txt
crwl https://example.com -v --no-robots

# Batch (from file)
crwl $(cat urls.txt | tr '\n' ' ') -o results/
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| curl: 404 | Try alternative URL (raw.githubusercontent.com vs github.com vs blob main) |
| curl: 403 | Add `-H "User-Agent: Mozilla/5.0"` header |
| curl: rate limit | Wait or use gh api (authenticated, higher limit) |
| WebFetch: empty/noise | Fall back to curl or crawl4ai with PruningContentFilter |
| crawl4ai: timeout | Increase `page_timeout=60000`, add `delay_before_return_html=2` |
| All methods fail | Log warning, skip source, continue |

---

## Quick Reference: Which Tool Per Source

| Source | Tool | Command |
|--------|------|---------|
| GitHub README raw | curl | `curl -sL "https://raw.githubusercontent.com/... "` |
| GitHub repo metadata | gh api | `gh api repos/user/repo` |
| GitHub file list | gh api | `gh api repos/user/repo/contents` |
| GitHub forks list | gh api | `gh api repos/user/repo/forks` |
| GitHub raw file | curl | `curl -sL "https://raw.githubusercontent.com/..."` |
| JSON API | curl + jq | `curl -sL "url" \| jq` |
| Markdown file | curl | `curl -sL "url.md"` |
| Static docs | WebFetch | `WebFetch(url="...")` |
| Blog article | crawl4ai | PruningContentFilter |
| JS-rendered page | crawl4ai | `js_only=True` |
| Multiple URLs | crawl4ai | `arun_many(urls=[...])` |
| Full site | crawl4ai | `deep_crawl=True` |
| PDF | Read tool | `Read(file="...pdf", pages="1-10")` |

---

## Embed in CLAUDE.md

To add this fetch strategy to a project's CLAUDE.md, paste this section:

```markdown
## Fetching Strategy

Use this priority order for all web content fetching:

1. **curl** → GitHub, APIs, raw files, markdown (fastest, best quality)
2. **WebFetch** → Static HTML → Markdown (built-in conversion)
3. **crawl4ai** → JS-rendered sites, batch URLs, deep crawl

### GitHub
\`\`\`bash
curl -sL "https://raw.githubusercontent.com/owner/repo/branch/file.md"
gh api repos/owner/repo
\`\`\`

### REST APIs
\`\`\`bash
curl -sL "https://api.example.com/endpoint" | jq .
\`\`\`

### JS-rendered / Social Media
→ Use crawl4ai only (headless browser required)

### Batch URLs
→ Use crawl4ai arun_many()

### Errors
- curl 404 → try alternative URL format
- curl 403 → add \`-H "User-Agent: Mozilla/5.0"\`
- WebFetch empty → fallback to curl or crawl4ai
- All fail → skip, log warning
```
