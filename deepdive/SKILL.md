---
name: deepdive
description: >
  One-shot deep research session on a specific topic. TRIGGER when user says
  "/deepdive", "deep dive on X", "riset mendalam tentang X", "research X in depth",
  "L4 research on X", "buat halaman komprehensif tentang X", or asks to investigate
  a topic thoroughly in a single focused session.

  Do NOT trigger for "autoresearch", "keep researching", "never stop" — those go to
  /autoresearch (the autonomous loop). This skill runs once, confirms a plan, then stops.

  TOPIC-AGNOSTIC — works for any domain. For Odoo-specific research (Odoo source
  code, Odoo modules, Odoo vault), use the separate odoo-vault-researcher skill
  instead of this one. This skill is for NON-ODOO topics only.
---

# Autoresearch Planner

A general-purpose skill for planning and executing autonomous deep research.
Works with any topic domain. Builds on the karpathy-vault research wiki schema.

## What This Skill Does

When the user asks for autonomous research, this skill:

1. **Plans** — Creates a structured research plan from a seed topic
2. **Discovers** — Identifies what to research (subtopics, entities, concepts)
3. **Executes** — Runs research in depth levels, creating wiki pages as it goes
4. **Tracks** — Maintains a progress log so research can be resumed
5. **Synthesizes** — Produces a final synthesis page pulling everything together

---

## Step 1 — Load Context

Before doing anything else, read the vault's schema and state:

```
1. Read vault/CLAUDE.md         — Understand the schema
2. Read vault/wiki/index.md      — See what's already covered
3. Read vault/wiki/log.md        — Check recent activity
4. Read vault/wiki/_overview.md  — See the big picture (if it exists)
```

These 4 reads give you the foundation. If the vault is empty or new, note that
in your plan — you'll need to build the overview and first pages from scratch.

---

## Step 2 — Generate Research Plan

The research plan answers these questions:

- **What is the seed topic?** (the user's query)
- **What are the key dimensions?** (entities, concepts, processes, regulatory, history)
- **What are the information gaps?** (what's missing from current wiki)
- **What depth level?** (see below)
- **How many pages will this produce?** (rough estimate)
- **What sources will be consulted?** (web search, web fetch, file analysis)
- **Estimated sessions?** (single-shot vs multi-session)

### Research Dimensions (pick what applies)

| Dimension | Questions to Answer |
|-----------|-------------------|
| **Entities** | Who are the key actors/organizations? |
| **Concepts** | What are the core ideas, standards, frameworks? |
| **Processes** | How does something work? Step by step? |
| **History** | How did it evolve? Timeline? |
| **Regulatory** | What rules apply? Who governs? |
| **Landscape** | What tools, products, competitors exist? |
| **Problems** | What are common issues, limitations, edge cases? |
| **Future** | What are trends, upcoming changes, open questions? |

### Depth Levels

**SELALU tanyakan user sebelum memilih depth level.** Jangan gunakan default tanpa persetujuan.

| Level | Name | What to Research |
|-------|------|-----------------|
| **L1** | Survey | High-level overview, definitions, key terms |
| **L2** | Standard | + how things work, key processes, entities involved |
| **L3** | Deep | + edge cases, problems, history, regulations, comparisons |
| **L4** | Expert | + internal details, debates, open questions, future trends |

Tanyakan ke user: "Mau pakai depth level berapa? Berikut opsinya:
- **L1 (Survey):** Overview + definisi + key terms
- **L2 (Standard):** + cara kerja, proses, entities
- **L3 (Deep):** + edge cases, history, regulasi
- **L4 (Expert):** + detail teknis, debates, open questions

Atau kalau topik sudah jelas, minta user menentukan langsung."

Kalau user tidak menjawab dengan angka/L1-L4, default ke **L2** tapi KONFIRMASI lagi dulu.

---

## Step 3 — Present the Plan to the User

**PENTING: Selalu tanyakan depth level di awal sebelum membuat plan.**
Jangan langsung buat plan — minta user memilih depth level terlebih dahulu.

Tampilkan prompt interaktif:
```
Depth level mana yang kamu mau untuk research ini?

L1 (Survey)     — Overview, definisi, key terms saja
L2 (Standard)   — + cara kerja, proses, entities (REKOMENDASI)
L3 (Deep)       — + edge cases, history, regulasi
L4 (Expert)     — + detail teknis, debates, open questions

Ketik angka (1-4) atau nama level.
```

Baru setelah user memilih, output plan dalam format berikut untuk persetujuan:

```markdown
# Autoresearch Plan: [Topic]

**Depth Level:** L2 (Standard) ← sesuai pilihan user
**Estimated Pages:** 8–12
**Sessions:** 1–2

## Research Dimensions
1. **Concepts** — Core ideas and frameworks
2. **Entities** — Key organizations, people, tools
3. **Processes** — How X works step by step
4. **Regulatory** — Applicable rules and standards
5. **History** — Evolution over time
6. **Landscape** — Current ecosystem

## Information Gaps (vs. current wiki)
- ❓ Missing: [gap 1]
- ❓ Missing: [gap 2]
- ❓ Existing but needs update: [gap 3]

## Research Questions
- [ ] Q1: What is X and why does it matter?
- [ ] Q2: How does X work technically?
- [ ] Q3: Who are the key players in the X ecosystem?
- ...

## Execution Order
1. Web search for recent sources on X
2. Create/update entity pages for key organizations
3. Create/update concept pages for core ideas
4. Create synthesis page pulling it all together
5. Update index and log

## Sources to Consult
- [source 1]
- [source 2]
- [file analysis if applicable]

---
**Ready to execute?** Say "go" to start, or modify the plan.
```

**Wait for user confirmation** before proceeding. The user may want to
narrow or expand scope, change depth level, or add specific questions.

---

## Step 4 — Execute the Research

After user says "go" (or equivalent):

### Research Loop

For each research question, follow this loop:

```
FOR each research question:
  1. Web search for relevant sources (use WebSearch tool)
  2. Fetch key pages for deep reading (use WebFetch tool)
  3. Analyze and extract key information
  4. Create or update wiki pages
  5. Add wikilinks to related existing pages
  6. Update index if new pages were created
  7. Log progress to wiki/log.md
```

### Wiki Page Creation

Every new page MUST have frontmatter:

```yaml
---
title: <Page Title>
date: <YYYY-MM-DD>
tags: [tag1, tag2]
sources: [source-id-1, source-id-2]
links: [[entity-name]]
---
```

Follow the [[Page Name]] wikilink convention. Never use bare names.
Use `[[Entities/Name]]` and `[[Concepts/name]]` patterns.

### Cross-linking

After creating a page:
- Check `wiki/index.md` for related pages
- Add wikilinks in both directions (forward AND backward)
- If a related concept exists but is thin, update it with new info
- Flag contradictions: if new info contradicts existing wiki, note it explicitly

### Source Tracking

For each source used:
1. Create `wiki/sources/<source-id>.md` if it's a new source
2. Link it in the page's `sources:` frontmatter
3. Include the source URL and relevant excerpt in the Sources section

---

## Step 5 — Progress Tracking

Update `wiki/log.md` with each milestone:

```markdown
## [YYYY-MM-DD] autoresearch | <Topic>
- Plan: wiki/synthesis/<plan-page>.md (new)
- Pages touched: N
  - wiki/concepts/x.md (new)
  - wiki/entities/y.md (updated)
  - ...
- Sources used: N
  - [Source Title](URL)
- Sessions: 1/N complete
- Notes: <brief user-relevant notes>
```

If the research is large and will span multiple sessions, also create a
`wiki/synthesis/<topic>-research-plan.md` with a checklist of remaining work.

---

## Step 6 — Synthesis

After all research questions are answered, create a synthesis page at:
`wiki/synthesis/<topic>-synthesis.md`

Structure:
```markdown
# <Topic> — Synthesis

**Summary:** One paragraph synthesizing everything researched.

## Key Findings
- Finding 1
- Finding 2
...

## Detailed Analysis
[Body]

## Open Questions
- What remains unknown?
- What needs further research?

## Sources
- [all sources used, with URLs]

## Related
- [[Entity Page]]
- [[Concept Page]]
```

Update `wiki/index.md` to include the synthesis page.

---

## Step 7 — Final Log Entry

Append to `wiki/log.md`:
```markdown
## [YYYY-MM-DD] autoresearch | <Topic> — COMPLETE
- Total pages: N
- New: M
- Updated: K
- Sources: L
- Synthesis: wiki/synthesis/<topic>-synthesis.md
```

---

## Vault Integration Checklist

Before declaring research complete, verify:

- [ ] All new pages have complete frontmatter
- [ ] All pages have at least 3 wikilinks to other pages
- [ ] No page is an orphan (every page links to ≥1 other page)
- [ ] `wiki/index.md` is updated with all new pages
- [ ] `wiki/log.md` has the completion entry
- [ ] Sources are cited in each page's Sources section

---

## Tips for Better Research

- **Start broad, go deep on what's most valuable.** Not every subtopic needs L4.
- **Use parallel research.** When researching independent subtopics, run WebSearch
  and WebFetch calls in parallel.
- **Flag, don't resolve, contradictions.** If sources disagree, note the tension
  in both pages rather than picking a winner.
- **Be specific with wikilinks.** `[[XBRL]]` is vague;
  `[[XBRL-Taxonomy-IDX]]` or `[[Indonesia-Stock-Exchange-IDX]]` is precise.
- **Save interesting outputs.** Charts, tables, and generated files go in
  `wiki/outputs/`. Update `wiki/index.md` accordingly.
- **Batch similar operations.** Creating 3 related concept pages in one pass
  is faster than switching contexts 3 times.

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Web search finds nothing | Broaden search terms, try alternative sources |
| Web fetch fails (403, block) | Use crawl4ai skill or try alternative URL |
| Topic too broad | Suggest narrowing to 2–3 subtopics |
| Wiki page already exists | Update it instead of creating duplicate |
| Source contradicts existing page | Note the contradiction explicitly |
| User interrupts | Save checkpoint to log.md, note what's done |
