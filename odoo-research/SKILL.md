---
name: odoo-research
description: >
  ALWAYS activate when researching Odoo topics, answering questions about Odoo, writing
  Odoo code, or debugging Odoo issues. This skill searches BOTH the Odoo vault knowledge
  base AND official Odoo documentation to give the most comprehensive, accurate answer.

  TRIGGER when:
  - User asks about Odoo features, modules, workflows, or API
  - User needs to understand how something works in Odoo
  - User asks "how do I...", "what is...", "explain...", or "how does X work in Odoo"
  - User needs Odoo code, ORM, fields, or method information
  - User is debugging Odoo errors or writing custom Odoo code
  - User says "check Odoo docs", "search vault", "odoo documentation", or similar

  This skill combines TWO sources for best results:
  1. Odoo Vault (Obsidian vault at ~/odoo-vaults/odoo-19/) — technical deep-dive,
     model/field/method documentation, ORM patterns, source code analysis
  2. Official Odoo Docs (/Users/tri-mac/odoo/documentation/) — user-facing guides,
     step-by-step tutorials, business process explanations, UI/UX documentation

  The vault provides the HOW (implementation details). Official docs provide the WHAT
  (feature description, user steps, screenshots reference). Use BOTH for complete answers.

  Tools: mcp__plugin_qmd_qmd__query, Glob, Read, Grep
---

# Odoo Research — Vault + Official Docs Combined

## Purpose

Search both the Odoo vault AND official documentation to produce the most complete,
accurate answer. Never rely on a single source.

**Vault = technical depth** (models, fields, ORM, source code, method chains)
**Official Docs = conceptual breadth** (user guides, tutorials, UI workflows, feature descriptions)

## Source Locations

```
VAULT_PATH_19     = ~/odoo-vaults/odoo-19/         (primary, technical depth)
VAULT_PATH_18     = ~/odoo-vaults/odoo-18/
VAULT_PATH_17     = ~/odoo-vaults/odoo-17/
VAULT_PATH_15     = ~/odoo-vaults/odoo-15/

DOCS_ROOT         = ~/odoo/documentation/            (official Odoo docs, Sphinx RST)
DOCS_APPLICATIONS = ~/odoo/documentation/content/applications/
DOCS_DEVELOPER    = ~/odoo/documentation/content/developer/
DOCS_ADMIN        = ~/odoo/documentation/content/administration/

ODOO_SOURCE_19    = ~/odoo/odoo19/odoo/            (for source code verification)
```

## Research Workflow

### Step 1 — Parallel Search (BOTH Sources)

Run vault search AND official docs search in parallel:

```
# 1a. Vault search via qmd
mcp__plugin_qmd_qmd__query(
  searches=[
    { type: 'lex', query: '<technical terms>' },
    { type: 'vec', query: '<natural language question>' }
  ],
  collections: ['odoo19-vault'],
  intent: '<topic being researched>',
  limit: 8
)

# 1b. Official docs — glob for relevant RST files
Glob(/Users/tri-mac/odoo/documentation/content/applications/**/<topic>*.rst)
Glob(/Users/tri-mac/odoo/documentation/content/developer/**/<topic>*.rst)
```

### Step 2 — Load Both Sources

```
# From vault (qmd results)
Read: vault file paths from qmd results
Read: Modules/<module>.md, Core/<topic>.md, Flows/<category>/<flow>.md

# From official docs (glob results)
Read: each matching RST file
Extract: key sections, user steps, configuration details
```

### Step 3 — Source Code Verification (When Needed)

Verify vault claims against actual source code:

```
Grep(<field_or_method>, path: ~/odoo/odoo19/odoo/addons/<module>/models/)
```

### Step 4 — Combine Into Complete Answer

Merge findings from both sources:

```
## Odoo Knowledge Context

**Sources:** Vault (technical) + Official Docs (user guide)
**Version:** Odoo 19
**qmd Used:** yes/no

### What It Does (Official Docs — User Perspective)
[From: official RST docs]
- Feature description
- Configuration steps
- UI workflow

### How It Works (Vault — Developer Perspective)
[From: Modules/<module>.md, Core/<topic>.md]
- Model: `model.name`
- Key fields: name (Char), state (Selection), ...
- Key methods: action_confirm(), _compute_amount()
- ORM patterns: @api.depends, @api.onchange

### Implementation Details (Source Code)
[From: addons/<module>/models/*.py — only if needed]
- Exact field definition with parameters
- Method signature and logic

### Answer to User's Question
[Combined synthesis from both sources]
```

## Which Source for What

| User Needs | Use Vault For | Use Official Docs For |
|-----------|---------------|------------------------|
| Feature description | — | ✅ "What does the Sale module do?" |
| Code/ORM reference | ✅ `sale.order` fields/methods | — |
| Step-by-step tutorial | — | ✅ "How to create a quotation" |
| Model relationship diagram | ✅ Flows/, Core/BaseModel | — |
| Configuration guide | Partial | ✅ "How to configure payment providers" |
| API decorator explanation | ✅ Core/API.md | — |
| User permissions setup | — | ✅ "How to set up user groups" |
| Method chain (debug) | ✅ Flows/ files | — |
| New features (v18→v19) | ✅ New Features/API Changes | ✅ administration/upgrade guide |
| Localization setup | ✅ Modules/l10n_id | — |

## Vault File Mapping (Quick Reference)

```
Flows/Cross-Module/sale-stock-account-flow.md  → complete sale→stock→invoice→payment chain
Flows/Account/payment-flow.md                  → reconciliation
Flows/Sale/quotation-to-sale-order-flow.md     → SO lifecycle
Modules/Sale.md, Modules/Account.md, Modules/Stock.md, Modules/Project.md
Core/BaseModel.md, Core/Fields.md, Core/API.md
Patterns/Inheritance Patterns.md, Patterns/Workflow Patterns.md
```

## Official Docs Structure

```
content/applications/sales/        → Sales (quotations, SO, pricing)
content/applications/finance/      → Accounting, invoicing, taxes
content/applications/inventory_and_mrp/ → Stock, manufacturing
content/applications/purchase/     → Purchase orders
content/applications/crm/          → CRM, leads, opportunities
content/applications/services/     → Helpdesk, Project, Timesheets
content/applications/website/      → Website, e-commerce
content/developer/                 → ORM reference, Python API, testing
content/administration/            → Server config, Odoo.sh, upgrades
```

## Anti-Patterns

❌ **Only using one source** — always check both vault AND official docs
❌ **Trusting vault over source code** — source code is ground truth
❌ **Giving code without verifying** — always Grep field/method in source
❌ **User-focused answer for dev question** — distinguish intent
❌ **Skipping vault for simple questions** — even simple questions benefit from model context

✅ **Always run both searches in parallel**
✅ **Read vault's Flows/ for any process/chain question**
✅ **Read official docs for user workflow/trail questions**
✅ **Verify model/field claims with source code**
✅ **Merge both into one coherent answer**

## Output Format

After research, always present:

```
### Summary (from both sources)
[2-3 sentence answer combining vault + official docs]

### Vault Findings (Technical)
- Model: `model.name`
- Key fields: [list]
- Methods: [list]
- Files: [vault paths]

### Official Docs Findings (User Guide)
- Feature: [what it does]
- Steps: [configuration/usage steps]
- Doc file: [path in documentation/]

### Source Code Verification (if applicable)
[verified: field X exists in account_move.py:123]
[note: vault says Y but source shows Z]

### Your Answer
[Complete, merged answer]
```