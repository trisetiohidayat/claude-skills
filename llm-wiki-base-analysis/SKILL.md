---
name: llm-wiki-base-analysis
description: >
  ALWAYS activate this skill FIRST when working with the llm-wiki knowledge base —
  for answering questions about its content, researching agent orchestration patterns,
  or building context before doing other work.

  TRIGGER when:
  - User asks about anything documented in llm-wiki (agent orchestrators, MCP, kanban, AI tools)
  - User mentions agent orchestration, Claude Code Studio, Edict, Routa, CrewAI, MCP
  - User wants to add new wiki pages or update existing ones
  - User asks "what do we know about X" where X relates to agent tools or orchestration
  - User asks to research or analyze agent orchestration tools
  - Any task that would benefit from the llm-wiki knowledge base as context

  This skill reads the wiki index, relevant pages, and log to build a structured
  LLM Wiki Context — essential foundation before further analysis or action.

  Tools: Glob, Read, Grep, Bash
---

# LLM Wiki Base Analysis

## Purpose

Build an **LLM Wiki Context** before acting. The context is a structured summary
that stays in conversation for all subsequent responses. It contains:
- All wiki pages and their categories
- Key entities (tools, orgs) and their attributes
- Key concepts (patterns, protocols)
- Synthesis conclusions and research findings
- Recent activity from the log
- Knowledge gaps (pages that don't exist yet but should)

**Wiki is primary source. The CLAUDE.md schema defines the structure.**

---

## Wiki Location

```
LLM_WIKI_PATH = ~/agent-orchest/llm-wiki
LLM_WIKI_PATH_ALT_1 = ~/.claude/llm-wiki
LLM_WIKI_PATH_ALT_2 = ~/my-llm-wiki
LLM_WIKI_PATH_ALT_3 = ~/karpathy-llm-wiki
```

Auto-detect by checking for `CLAUDE.md` in this priority:
1. `/Users/tri-mac/agent-orchest/llm-wiki/CLAUDE.md` (primary)
2. `/Users/tri-mac/.claude/llm-wiki/CLAUDE.md`
3. `/Users/tri-mac/my-llm-wiki/CLAUDE.md`
4. `/Users/tri-mac/karpathy-llm-wiki/CLAUDE.md`

---

## Step 1 — Detect Wiki Path

Use Bash to check existence:
```bash
for path in \
  "/Users/tri-mac/agent-orchest/llm-wiki/CLAUDE.md" \
  "/Users/tri-mac/.claude/llm-wiki/CLAUDE.md" \
  "/Users/tri-mac/my-llm-wiki/CLAUDE.md" \
  "/Users/tri-mac/karpathy-llm-wiki/CLAUDE.md"; do
  if [ -f "$path" ]; then
    WIKI_PATH=$(dirname "$path")
    echo "Found wiki at: $WIKI_PATH"
    break
  fi
done
```

Also check for `WIKI_PATH` environment variable if set.

---

## Step 2 — Load Core Files

Always read these files first (in order):

| File | What it contains |
|------|-------------------|
| `{WIKI_PATH}/CLAUDE.md` | Schema, structure, conventions, page types |
| `{WIKI_PATH}/index.md` | Catalog of all pages — use this to locate topics |
| `{WIKI_PATH}/log.md` | Recent activity — what was researched/added |

**Then read** the specific pages relevant to the user's query, using `index.md` as the map.

---

## Step 3 — Map Topic to Wiki Pages

Use `index.md` to find relevant files. Read **all matching files**.

### Page Type Locations

```
wiki/sources/        ← Source summary pages (from ingested documents)
wiki/entities/       ← People, organizations, products (Claude Code Studio, Edict, Routa, etc.)
wiki/concepts/       ← Ideas, patterns, protocols (mcp-protocol, llm-provider-config, etc.)
wiki/comparisons/    ← Side-by-side analysis of entities or concepts
wiki/synthesis/      ← High-level summaries integrating multiple sources
wiki/analysis/       ← Answers filed from exploratory queries
```

### Topic → File Mapping (common queries)

| Topic | File |
|-------|------|
| Agent orchestrator tools | `wiki/comparisons/agent-orchestrator-tools.md` |
| Kanban + agent orchestration | `wiki/concepts/agent-orchestrator-kanban.md` |
| Claude Code Studio | `wiki/entities/claude-code-studio.md` |
| Edict (12-agent system) | `wiki/entities/edict.md` |
| Routa (5-lane kanban) | `wiki/entities/routa.md` |
| MCP protocol | `wiki/concepts/mcp-protocol.md` |
| LLM provider config | `wiki/concepts/llm-provider-config.md` |
| Odoo + agent orchestrator | `wiki/synthesis/agent-orchestrator-kanban-odoo-module.md` |
| CrewAI + Claude Code | `wiki/synthesis/crewai-claude-code-integration.md` |
| Raw sources | `raw/` directory — read directly |

### Reading Order for Research Tasks

1. `index.md` — find all relevant pages
2. `wiki/synthesis/[topic].md` — bird's-eye view first
3. `wiki/comparisons/[topic].md` — comparison table
4. `wiki/concepts/[topic].md` — concept definitions
5. `wiki/entities/[topic].md` — entity details
6. `raw/` — original source documents if available
7. `log.md` — what was recently researched/added

---

## Step 4 — Check for Knowledge Gaps

After reading wiki + sources:

| Coverage | Action |
|----------|--------|
| **Full** — relevant pages exist | Provide confident, detailed context |
| **Partial** — some pages exist | Load what's available, note gaps |
| **None** — no pages for topic | Offer to create new page via wiki ingest protocol |

### Missing Topic Protocol

```
📝 Topik "<topic>" belum terdokumentasi di llm-wiki.

Wiki mencakup ~14 file di folder entities/, concepts/, synthesis/, comparisons/.

Apakah Anda ingin saya membuat wiki page baru?
  [Ya] → Tentukan jenis page:
    - sources/ → source summary (dari dokumen asli)
    - entities/ → orang/org/produk
    - concepts/ → ide/pola/protokol
    - synthesis/ → ringkasan整合 dari multiple sources
    - comparisons/ → perbandingan side-by-side
  [Tidak] → AI membantu dari general knowledge
```

---

## Step 5 — Produce LLM Wiki Context

Output this structured block at the start of every response:

```markdown
## LLM Wiki Context

**Wiki Path**: <WIKI_PATH>
**Topic**: <topic_name>
**Wiki Coverage**: <full | partial | none>
**Pages Found**: <N matching pages>
**Pages Read**: <list of files>

### Entities (<N>)
- [entity name] — brief description, key attributes

### Concepts (<N>)
- [concept name] — definition, key characteristics

### Synthesis Findings (<N>)
- [finding] — integrated conclusion from multiple sources

### Comparisons
| Tool | Lang | DB | Kanban | Agent Spawn | Key Feature |
|------|------|----|--------|-------------|-------------|

### Cross-References
- [[Entity Page]]
- [[Concept Page]]

### Knowledge Gaps
- [topics that don't have wiki pages yet]

### Action Guidance
Based on this context, AI should:
- [do this because...]
- [avoid this because...]
- [call next skill because...]
```

---

## Step 6 — Wiki Maintenance (when asked)

### Ingest New Source
1. Read the source file from `raw/`
2. Discuss key takeaways with user
3. Write appropriate page type in `wiki/`
4. Update `index.md` catalog
5. Update `log.md` with entry: `## [YYYY-MM-DD] ingest | [Title]`

### Update/Edit Page
1. Read current page
2. Make edits
3. Update `date` in frontmatter
4. Add entry to `log.md`: `## [YYYY-MM-DD] update | [Page Title]`

### Lint (periodic)
1. Check for orphan pages (no inbound links)
2. Flag stale claims
3. Identify concepts mentioned but lacking a page
4. Check for missing cross-references
5. Suggest data gaps
6. Update `log.md`: `## [YYYY-MM-DD] lint | [Findings summary]`

---

## Key Entities the Wiki Documents

### Claude Code Studio
TypeScript/Express app with SQLite. 3-column Kanban (Todo/In Progress/Done). MCP Task Manager. Stars: 94.

### Edict (OpenClaw)
Python app with SQLAlchemy + Redis Streams. Tang Dynasty-inspired 12-agent system. Stars: 15k.

### Routa
Python + Next.js. 5-lane Kanban orchestrator with built-in specialists (ROUTA/CRAFTER/GATE). Stars: 631.

### GPT Researcher
Python. Planner-executor pattern. LangGraph-based. Stars: ~25k.

### MCP Protocol
Model Context Protocol — standard for AI agents accessing tools. Odoo integration via `odoo-toolbox` and `OdooDevMCP`.

---

## Anti-Patterns This Skill Prevents

❌ Answering questions about agent tools without checking the wiki first
❌ Recommending tools not documented or compared in the wiki
❌ Missing cross-references between entities, concepts, and syntheses
❌ Creating duplicate pages for topics that already exist
❌ Forgetting to update `index.md` and `log.md` after adding pages

✅ Always load wiki context FIRST → then act
✅ For research tasks, start with `index.md` → `synthesis/` → `comparisons/`
✅ For entity questions, read `entities/` page + check `log.md` for freshness
✅ Before creating a new page, check `index.md` for existing coverage
