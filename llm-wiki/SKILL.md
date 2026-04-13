---
name: llm-wiki
description: Initialize and maintain a personal LLM Wiki — a persistent, compounding knowledge base. Use when user says "initialize wiki", "set up my knowledge base", "start a wiki project", "build a wiki", or similar. Also use whenever user asks to ingest sources, update cross-references, maintain a wiki, or do any wiki operations (query, lint, file answers back). The LLM Wiki pattern replaces RAG: instead of retrieving raw docs at query time, the wiki is a living artifact the LLM builds and maintains incrementally.
---

# LLM Wiki

A skill for initializing and maintaining a **persistent, compounding wiki** — a structured knowledge base that grows smarter over time, not re-derived from scratch on every query.

The core idea: when you add a source, the LLM reads it, extracts key information, and **integrates it into the existing wiki** — updating entity pages, revising summaries, flagging contradictions, and maintaining cross-references. The wiki keeps getting richer with every source and every question.

---

## When to Use

**You MUST use this skill when:**
- User wants to initialize a new wiki project ("setup my wiki", "initialize wiki for project X")
- User says "ingest" or wants to process a new source/document
- User asks to update, maintain, or lint the wiki
- User asks a question that should be answered from wiki pages and filed back as a new page

**You SHOULD use this skill when:**
- User talks about building a knowledge base, personal wiki, or research notes
- User mentions Obsidian, qmd, or wiki-related tooling
- User is accumulating documents/articles/papers over time and wants them organized

---

## Workflow: Initialize Wiki

### Step 1: Detect or Create Target Directory

Ask the user: "Where should this wiki live? Give me a directory path."

If no path is given, use the current working directory as the wiki root.

Verify the directory exists. If it doesn't, ask for confirmation before creating it.

### Step 2: Check Tooling

Check which tools the user has available:

**Obsidian:**
```bash
# Check if Obsidian is installed
mdfind "kMDItemCFBundleIdentifier == 'md.obsidian'" 2>/dev/null || echo "not_found"
```

**qmd (search engine):**
```bash
which qmd 2>/dev/null || echo "not_found"
```

**Other tools:** Marp, Dataview (Obsidian plugins), etc.

### Step 3: Offer Tooling Setup

For each missing tool, offer to set it up:

> "I see you don't have **qmd** installed — it's a local search engine for markdown files with hybrid BM25/vector search. It works great alongside the wiki's index file at small scale, but becomes essential as the wiki grows past ~100 pages. Want me to set it up? (y/n)"

If yes, provide setup instructions:
- **qmd**: `cargo install qmd` or see https://github.com/tobi/qmd
- **Obsidian**: Download from https://obsidian.md

For Obsidian plugins (Marp, Dataview), explain that the user needs to enable them manually in the app after opening the vault.

### Step 4: Initialize Directory Structure

Create this structure inside the wiki root:

```
wiki-root/
├── CLAUDE.md          # Schema — the most important file
├── index.md           # Content catalog
├── log.md             # Chronological activity log
├── raw/               # Immutable source documents
│   └── .gitkeep
└── wiki/              # LLM-generated wiki pages
    └── .gitkeep
```

Initialize as a git repo if not already one:
```bash
git init
```

### Step 5: Write CLAUDE.md (The Schema)

Write the `CLAUDE.md` file inside the wiki root. This is the schema that guides all future LLM behavior. It is the most important file in the wiki.

**IMPORTANT:** The CLAUDE.md MUST be written inside the wiki root directory (the project directory), not in the skills directory. Every LLM Wiki project needs its own CLAUDE.md.

Include these components:

```markdown
---
description: LLM Wiki maintainer — builds and maintains a persistent, compounding knowledge base. Reads sources, writes and updates wiki pages, maintains cross-references, and keeps the wiki consistent. Use when ingesting sources, answering questions from the wiki, or doing maintenance (lint, update cross-refs).
---

# [Wiki Name] Wiki

## Purpose
[1-2 sentences describing this wiki's domain and goals]

## Structure

### Directory Layout
- `raw/` — immutable source documents (read only, never modify)
- `wiki/` — LLM-generated pages (owned entirely by the LLM)
- `index.md` — catalog of all wiki pages
- `log.md` — chronological activity log
- `CLAUDE.md` — this schema file

### Source Organization
Sources in `raw/` are organized by category. Choose what fits:
- `raw/articles/`
- `raw/papers/`
- `raw/books/`
- `raw/podcasts/`
- `raw/notes/`
- `raw/data/`
- `raw/assets/` (for downloaded images)

## Conventions

### Page Types

**Source Summary Page** (`wiki/sources/`): One page per source
- File: `wiki/sources/[slug].md`
- Frontmatter: `title`, `source`, `date`, `tags`
- Content: key takeaways, claims, questions raised, connections to other sources

**Entity Page** (`wiki/entities/`): People, places, organizations, products
- File: `wiki/entities/[name-slug].md`
- Frontmatter: `type: person|place|org|concept`, `tags`
- Content: brief description, attributes, related entities, links to sources

**Concept Page** (`wiki/concepts/`): Ideas, theories, frameworks
- File: `wiki/concepts/[name-slug].md`
- Frontmatter: `type: concept`, `tags`
- Content: definition, key claims, related concepts, contradictions across sources

**Comparison Page** (`wiki/comparisons/`): Side-by-side analysis of entities or concepts
- File: `wiki/comparisons/[slug].md`
- Frontmatter: `type: comparison`, `subjects: [...]`
- Content: comparison table, key differences, synthesis

**Synthesis Page** (`wiki/synthesis/`): High-level summaries integrating multiple sources
- File: `wiki/synthesis/[slug].md`
- Frontmatter: `type: synthesis`, `tags`
- Content: thesis, supporting evidence, open questions

**Analysis Page** (`wiki/analysis/`): Answers filed from exploratory queries
- File: `wiki/analysis/[slug].md`
- Content: the question, the answer, citations to wiki pages

### Cross-References
- Use wiki links: `[[Entity Page]]`, `[[Concept Page]]`
- Every page should reference at least 2 other wiki pages
- Flag contradictions: `> [!contradiction]` blockquote when new sources challenge old claims

### Frontmatter Standard
Always include on every wiki page:
```yaml
---
title: Page Title
date: YYYY-MM-DD
tags: [tag1, tag2]
sources: 1  # count of raw sources cited
---
```

## Operations

### Ingest
1. Read the source file
2. Discuss key takeaways with user
3. Write a source summary page in `wiki/sources/`
4. Update `index.md`
5. Update or create relevant entity/concept pages
6. Add entry to `log.md` with format: `## [YYYY-MM-DD] ingest | [Title]`

### Query
1. Read `index.md` first to locate relevant pages
2. Read relevant wiki pages
3. Synthesize answer with citations
4. If answer is valuable: offer to file it as a new page in `wiki/analysis/`
5. Add entry to `log.md`: `## [YYYY-MM-DD] query | [Question summary]`

### Lint (periodic health check)
1. Check for orphan pages (no inbound links)
2. Flag stale claims superseded by newer sources
3. Identify concepts mentioned but lacking a page
4. Check for missing cross-references
5. Suggest data gaps fillable via web search
6. Add entry to `log.md`: `## [YYYY-MM-DD] lint | [Findings summary]`

### File Answers Back
When a query answer is valuable enough to keep:
- Write the answer as a new page in `wiki/analysis/`
- Update `index.md`
- Add `[[cross-references]]` to related pages
- This is how the wiki compounds — explorations become permanent knowledge

## index.md Format
```
# Wiki Index

## Pages (N total)

### Sources (n)
[[sources/...]]

### Entities (n)
[[entities/...]]

### Concepts (n)
[[concepts/...]]

### Comparisons (n)
[[comparisons/...]]

### Synthesis (n)
[[synthesis/...]]

### Analysis (n)
[[analysis/...]]
```

## log.md Format
```
# Wiki Log

## [YYYY-MM-DD] ingest | Source Title
...

## [YYYY-MM-DD] query | Question summary
...

## [YYYY-MM-DD] lint | Findings summary
...
```
```

Adjust the page types and conventions to match the user's domain. The above is a starting point — co-evolve this with the user over time.

### Step 6: Initialize index.md and log.md

Create empty `index.md` and `log.md` with the formats above.

### Step 7: Announce Completion

> "Wiki initialized at `[path]`. Here's what was created:
> - `CLAUDE.md` — schema file (read this to understand how the wiki works)
> - `index.md` — page catalog
> - `log.md` — activity log
> - `raw/` — drop your source documents here
> - `wiki/` — your growing knowledge base
>
> Drop a source into `raw/` and say 'ingest' when you're ready to start building the wiki."

---

## Workflow: Ingest a Source

Triggered when user adds a source or says "ingest [filename]".

1. **Confirm source path.** If user just dropped a file, locate it in `raw/`.
2. **Read the source.** Use appropriate tool based on type:
   - PDF: use Read tool with page ranges
   - Markdown/Text: read directly
   - Image: view it
   - Web page: clip first with Obsidian Web Clipper or use defuddle
3. **Discuss with user.** Summarize the key takeaways and ask what to emphasize.
4. **Write summary page** in `wiki/sources/[slug].md`.
5. **Update `index.md`** — add the new page entry.
6. **Update entity/concept pages** — revise relevant existing pages with new info.
7. **Flag contradictions** if new data challenges old claims. Use `> [!contradiction]` blockquote.
8. **Update `log.md`** — append `## [YYYY-MM-DD] ingest | [Title]`.
9. **Announce.** List all files touched and key decisions made.

---

## Workflow: Lint the Wiki

Triggered when user says "lint" or "health check".

1. Read all wiki pages (or scan `index.md` and read in batches for large wikis).
2. Run the checks listed in CLAUDE.md's Lint section.
3. Present findings to user in a readable format.
4. Ask which issues to address, then fix them.
5. Update `log.md`.

---

## Workflow: Answer a Query

Triggered when user asks a question.

1. Read `index.md` to find relevant pages.
2. Read those pages.
3. Synthesize an answer with citations.
4. Offer to file the answer as a new `wiki/analysis/` page if it's valuable.
5. If filed: update `index.md`, add cross-references, update `log.md`.

---

## Tips

- The wiki is just a git repo. You get version history, branching, and collaboration for free.
- If the user has Obsidian open alongside the conversation, they can see real-time updates.
- Use `[[wikilinks]]` instead of full URLs — they work inside Obsidian and many markdown editors.
- When viewing images referenced in markdown, read the text first, then view images separately to gain additional context.
- The `grep "^## \[" log.md | tail -5` command gives the last 5 log entries — useful for quick context.

## Optional Tooling (reference)

These tools are nice-to-have. Check for them and offer to help setup:

| Tool | Purpose | Setup |
|------|---------|-------|
| Obsidian | IDE for browsing the wiki | https://obsidian.md |
| Obsidian Web Clipper | Clip web articles to markdown | Browser extension |
| qmd | Local search engine for wiki pages | `cargo install qmd` |
| Marp | Slide deck generation from markdown | `npm install -g @marp-team/marp-cli` |
| Dataview | Query frontmatter dynamically | Obsidian plugin |

When checking for these tools, explain what each one does and let the user choose.
