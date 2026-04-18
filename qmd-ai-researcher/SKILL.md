---
name: qmd-ai-researcher
description: |
  AI-powered research skill using QMD semantic search for Odoo 19 vault documentation.
  ACTIVATE whenever user asks about Odoo concepts, models, workflows, patterns,
  or anything that can be answered from the vault documentation.

  TRIGGER when user asks:
  - "what is", "how does", "explain", "describe" about Odoo topics
  - "apa itu", "bagaimana cara", "jelaskan" in Indonesian
  - Any question about Odoo models, fields, decorators, workflows
  - "tell me about X in Odoo" or "compare X vs Y in Odoo"
  - "what happens when", "what is the flow of"
  - Request to research or investigate Odoo topics
  - Questions starting with "kenapa", "why does", "how to"

  DO NOT trigger for:
  - Code generation/creation tasks (use odoo19-model-* skills instead)
  - Direct debugging of actual errors in running Odoo (use odoo-error-analysis)
  - Simple file reads or grep that don't need semantic understanding

  This skill uses QMD vector search to find semantically relevant documentation,
  then synthesizes answers with proper citations. QMD finds 9x more relevant
  results than literal grep by understanding meaning, not just text matching.

  Benchmark: QMD-vector ~950ms warm | Grep ~100ms | QMD finds 18 hits vs Grep 2
  Always prefer QMD for research tasks. Grep only for exact code/debugging.
---

# QMD AI Researcher — Odoo 19 Vault

Use QMD semantic search to answer Odoo 19 questions with grounded citations.

## Quick Decision Tree

```
User question about Odoo?
├─ YES → Use this skill (QMD research)
│         └─ Warm server: ~1s response
│         └─ Cold server: ~15-25s first query (model load)
│
├─ Question is "how to implement/build/create X"?
│   └─ Use this skill first for context, THEN code skill
│
├─ Simple exact code search (filename, class name)?
│   └─ Use Grep instead — faster for literal matches
│
└─ NO → Use other appropriate skill
```

## Research Workflow

### Step 1 — Formulate Semantic Query

Transform user's question into a semantic search query.

**Examples:**
| User Question | Semantic Query |
|---|---|
| "apa itu stock.quant?" | "stock quant inventory" |
| "how does sale order confirm?" | "sale order workflow state" |
| "kenapa ir.rule tidak jalan?" | "ir.rule domain access control" |
| "explain computed field" | "computed field api.depends odoo" |

### Step 2 — Run QMD Search

Use the QMD MCP tool or CLI. **MCP tool preferred** (built-in collection filtering):

**MCP Tool (recommended):**
```
Use mcp__plugin_qmd_qmd__query tool:
- instance: odoo19-vault (or whatever the vault name is)
- query: <semantic query>
- limit: 5
```

**CLI fallback (if MCP unavailable):**
```bash
cd ~/odoo-vaults/odoo-19
qmd vsearch odoo19-vault "<semantic query>" --limit 5
```

### Step 3 — Read Top Results

Fetch the top 2-3 most relevant documents using QMD get:

**MCP:**
```
mcp__plugin_qmd_qmd__get tool
- instance: odoo19-vault
- file: <path from search results>
- limit: 30  # lines of context
```

**CLI:**
```bash
qmd get qmd://odoo19-vault/modules/stock-quant.md -l 50
```

### Step 4 — Synthesize Answer

Build answer from the retrieved context. Follow this format:

```markdown
## [Answer Title]

**Summary:** One sentence answer to the user's question.

### Key Points
- Point 1 (from [Source File](link))
- Point 2 (from [Source File](link))
- Point 3 (from [Source File](link))

### Detail Explanation
[2-3 paragraphs explaining the concept, flow, or mechanism]

### Related Topics
- [[Related Concept]] — brief connection
- [[Another Related]] — brief connection

### Sources
- [File Name](qmd://odoo19-vault/path/to/file.md) — relevance note
```

### Step 5 — Always Cite Sources

Always reference the source files. Format:
- In text: `(via [modules/stock.md](qmd://odoo19-vault/modules/stock.md))`
- At bottom: `Sources: [modules/stock.md], [flows/stock/stock-valuation-flow.md]`

## Query Strategies

### For Model Questions
```
Query: "<model_name> <related_concept>"
Example: "stock.quant inventory valuation"
```

### For Workflow Questions
```
Query: "<business_process> workflow state"
Example: "purchase order receipt workflow"
```

### For API/Decorator Questions
```
Query: "<decorator_name> <usage_example>"
Example: "api.depends computed field odoo"
```

### For Security Questions
```
Query: "<security_concept> access control"
Example: "ir.rule record domain security"
```

### For Pattern Questions
```
Query: "<pattern_type> inheritance extension"
Example: "_inherit delegation odoo inheritance"
```

## Performance Notes

### Speed
- **Warm QMD-vector:** ~950ms average
- **Cold QMD (first query):** ~15-25 seconds (model loading)
- **Grep (comparison):** ~100ms but finds 9x fewer relevant results

### When QMD Returns 0 Results
If QMD returns no hits:
1. Try broader semantic query
2. Fall back to Grep with simplified keywords
3. Check if vault has relevant documentation

### Cross-Vault Results
QMD may return results from other vaults (odoo-minimal-wiki). These are valid
and often complementary. Filter by `qmd://odoo19-vault/` prefix to focus on
the main vault only.

## Vault Reference

```
Vault path:    ~/odoo-vaults/odoo-19
QMD collection: odoo19-vault
Source code:   ~/odoo/odoo19/odoo/addons/
Total docs:    771 files
Indexed:       9521 vectors

Key directories:
  Core/          — ORM, fields, API decorators
  Modules/       — 80+ module documentations
  Patterns/      — Architecture patterns
  Snippets/      — Code templates
  New Features/  — Odoo 18→19 changes
  Tools/         — ORM operations, testing
  flows/         — Business process flows
```

## Example Research Session

**User:** "jelaskan bagaimana stock valuation flow bekerja di Odoo"

**Step 1 — Query:** `stock valuation flow real-time`
**Step 2 — QMD Results:**
- `modules/stock-account.md` (Score: 74%)
- `flows/stock/stock-valuation-flow.md` (Score: 72%)
- `modules/stock-quant.md` (Score: 70%)

**Step 3 — Read top 2 results**
Get snippets from stock-account.md and stock-valuation-flow.md

**Step 4 — Synthesize answer:**

> ## Stock Valuation Flow di Odoo
>
> **Summary:** Odoo secara otomatis membuat journal entries saat inventory moves
> di-validate, dengan dua metode: Real-Time dan Manual.
>
> ### Key Points
> - Trigger: `action_done` pada stock.move → buat `stock.valuation.layer`
>   (via [flows/stock/stock-valuation-flow.md](qmd://odoo19-vault/flows/stock/stock-valuation-flow.md))
> - Config: `property_valuation` field di `product.category`
>   (via [modules/stock-account.md](qmd://odoo19-vault/modules/stock-account.md))
> - Metode: Real-Time (otomatis per move) vs Manual (periodic)
>
> ### Detail
> [synthesized from snippets]
>
> ### Sources
> - [flows/stock/stock-valuation-flow.md](qmd://odoo19-vault/flows/stock/stock-valuation-flow.md)
> - [modules/stock-account.md](qmd://odoo19-vault/modules/stock-account.md)
