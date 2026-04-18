---
name: odoo-vault-base-analysis
description: >
  ALWAYS activate this skill FIRST when analyzing Odoo systems, understanding workflows,
  or investigating issues. This skill builds an accurate, vault-grounded knowledge base
  of Odoo models, field names, method chains, and cross-module flows — essential for
  any Odoo analysis work.

  TRIGGER when:
  - User needs to analyze Odoo behavior, structure, or business logic
  - Investigating Odoo errors, bugs, or unexpected behavior
  - Understanding cross-module workflows (e.g., sale→stock→account)
  - Querying Odoo database or writing code touching Odoo models
  - User asks "how does X work in Odoo", "explain the process of Y", or "analyze Z"
  - Any Odoo debugging, investigation, or deep-dive analysis task

  This skill reads the Obsidian vault (documentation) and source code to build
  an accurate Odoo Knowledge Context. Vault is primary; source code is verification.
  Does NOT replace domain skills — it provides the BASE context before all others.

  Tools: Glob, Read, Grep, mcp__plugin_qmd_qmd__query
---

# Odoo Vault Base Analysis

## Purpose

Build an **Odoo Knowledge Context** before acting. The context is a structured
summary that stays in conversation for all subsequent responses. It contains:
- Key field names, types, and defaults
- Method chains and state transitions
- Cross-module linkages (sale→stock→account, etc.)
- Cross-check notes vs. actual source code

**Source code is ground truth. Vault is reference.**
If they conflict, trust source code and note the discrepancy.

---

## Vault Location

```
VAULT_PATH_19 = ~/odoo-vaults/odoo-19   (primary, comprehensive)
VAULT_PATH_15 = ~/odoo-vaults/odoo-15
VAULT_PATH_17 = ~/odoo-vaults/odoo-17

ODOO_SRC_19 = ~/odoo/odoo19/odoo
ODOO_SRC_17 = ~/odoo/odoo17/odoo
ODOO_SRC_15 = ~/project/roedl/odoo15.0-roedl/odoo
```

---

## qmd Collection Config

qmd must be configured with vault collections in `~/.config/qmd/index.yml`.
Each collection maps a short name to a vault path and glob pattern.

**Currently configured collections:**
```yaml
collections:
  odoo19-vault:
    path: ~/odoo-vaults/odoo-19
    pattern: "**/*.md"
  # odoo15-vault:    # ← add if needed
  #   path: ~/odoo-vaults/odoo-15
  #   pattern: "**/*.md"
```

If a needed collection is missing, add it to `~/.config/qmd/index.yml` and rebuild:
```bash
qmd collection add odoo15-vault ~/odoo-vaults/odoo-15
qmd update          # full reindex (BM25 + vectors)
# OR faster reindex (vectors only, skip BM25 rebuild):
qmd embed -f -c odoo15-vault
```

---

## Step 0 — Detect Version

| If... | Then... |
|-------|---------|
| User stated a version | Use that version |
| User didn't state one | Ask: "Versi Odoo berapa yang Anda gunakan? (Odoo 15, 17, 19, atau lain)" |
| User doesn't know | Offer 3 discovery methods (login page, `odoo.conf`, Odoo URL, MCP) |

Vault covers **Odoo 19** (primary) and **Odoo 15**. For other versions:
load vault as reference, then **always verify with source code** for field names and method signatures.

**Vault path per version:**
```
Odoo 19 → ~/odoo-vaults/odoo-19/   (vault terstruktur lengkap, ada di qmd)
Odoo 17 → ~/odoo-vaults/odoo-17/   (vault terstruktur, cek qmd config)
Odoo 15 → ~/odoo-vaults/odoo-15/   (vault terstruktur, cek qmd config)

Source code per version:
Odoo 19 → ~/odoo/odoo19/odoo/
Odoo 17 → ~/odoo/odoo17/odoo/
Odoo 15 → ~/project/roedl/odoo15.0-roedl/odoo/
```

---

## Step 0.5 — qmd Vault Search (Primary Discovery)

**Use `qmd__query` MCP tool first.** This searches the vault using hybrid BM25 + semantic search
and finds relevant files even for topics not in the file mapping.

### Available Collections
| Version | qmd Collection | Notes |
|---------|---------------|-------|
| Odoo 19 | `odoo19-vault` | ✅ Primary — always use |
| Odoo 17 | `odoo17-vault` | ⚠️ Add if needed (see config section) |
| Odoo 15 | `odoo15-vault` | ⚠️ Add if needed (see config section) |

---

### Step 0.5a — Check Index Freshness (Reindex Detection)

**Before searching, always verify the index is fresh.** Run this before using qmd:

```bash
# Get last index time for the collection (from qmd status output)
qmd status

# Get last modified file in the vault
find ~/odoo-vaults/odoo-19 -name "*.md" -type f -printf '%T+\n' | sort -r | head -1
```

**Decision:**
| Condition | Action |
|-----------|--------|
| Vault last modified file **≤** collection "Updated" time in `qmd status` | ✅ Index is fresh — proceed to Step 0.5b |
| Vault last modified file **>** collection "Updated" time | ⚠️ **Reindex needed** |
| Collection missing from `qmd status` | ⚠️ **Add + index first** |

**Reindex command (run once before searching):**
```bash
# Full reindex: BM25 + vectors (slower, most accurate)
qmd update

# Fast reindex: vectors only, skip BM25 rebuild (faster, good enough)
qmd embed -f -c odoo19-vault
```

**Note:** `qmd status` shows "Updated: X ago" per collection — this is the authoritative last index time.

**Example:**
```
qmd status → odoo19-vault: Files: 764 (updated 1d ago)
find ~/odoo-vaults/odoo-19 -name "*.md" -printf '%T+\n' | sort -r | head -1
            → 2026-04-15+14:30:22.0000000000

Last index: 1 day ago (2026-04-14 ~14:30)
Last file modified: 2026-04-15 14:30 (today, newer)
→ ⚠️ Reindex needed before search
```

---

### Step 0.5b — Run qmd Search

After confirming index is fresh, search using the MCP tool:

```
mcp__plugin_qmd_qmd__query({
  searches: [
    { type: 'lex', query: '<keywords>' },
    { type: 'vec', query: '<natural language question>' }
  ],
  collections: ['<collection-name>'],
  intent: '<what the user is trying to do>',
  limit: 10
})
```

**Search strategy:**
- `lex` query: exact Odoo terms (model names, field names, method names)
- `vec` query: what the user is actually asking about in natural language
- Always include `intent` to disambiguate (e.g., "Odoo 19 sale order workflow")

### Decision Tree

```
qmd index fresh?
├─ YES → Search with qmd → use results as primary file list
│         Read top results first (minScore: 0.3), then file mapping as supplement
└─ NO  → Reindex first (qmd update), then search
         If collection missing: add + index → then search
         Only as absolute last resort: fall back to Step 1 (file mapping)
```

### Example
```
User: "Bagaimana proses reconciliation account move dengan payment?"

Index check: odoo19-vault updated 1d ago, latest file modified today
→ ⚠️ Reindex needed first

After reindex:
qmd search:
  lex: 'reconciliation account move payment'
  vec: 'how does payment reconciliation with account move work in Odoo'
  intent: 'Odoo 19 payment reconciliation workflow'

Result: Flows/Account/payment-flow.md (score: 0.95), Modules/Account.md (score: 0.87)
→ Read these files first
→ Then supplement with file mapping for field-level details
```

---

## Step 1 — Map Topic to Vault Files

**Use this as supplement to qmd results, or as primary fallback if qmd unavailable.**

Use this mapping to find relevant files. Read **all matching files**.

### Cross-Module Flows (start here for processes)
```
Flows/Cross-Module/sale-stock-account-flow.md      ← Sales→Delivery→Invoice→Payment→Reconcile
Flows/Cross-Module/purchase-stock-account-flow.md ← PO→Receipt→Bill→Payment
Flows/Account/invoice-creation-flow.md            ← Draft invoice creation
Flows/Account/invoice-post-flow.md                ← Draft → Posted
Flows/Account/payment-flow.md                     ← Register payment + reconciliation
Flows/Sale/quotation-to-sale-order-flow.md        ← SO confirmation
Flows/Sale/sale-to-invoice-flow.md                ← SO → Invoice
Flows/Sale/sale-to-delivery-flow.md               ← SO → Delivery
Flows/Account/edi-invoice-flow.md                ← EDI/UBL invoicing
```

### Modules
```
Modules/Sale.md              ← sale.order, order lines, states
Modules/Account.md          ← account.move, account.move.line, reconciliation
Modules/Stock.md            ← stock.picking, stock.quant, stock.move
Modules/Purchase.md         ← purchase.order, purchase.order.line
Modules/CRM.md              ← crm.lead, crm.lead.team
Modules/MRP.md              ← mrp.production, mrp.bom
Modules/Product.md          ← product.template, product.product
Modules/res.partner.md      ← partner, address, bank
Modules/payment*.md         ← payment providers (stripe, paypal, etc.)
Modules/l10n_*.md           ← localization (Indonesia: l10n_id.md)
Modules/point_of_sale.md    ← pos.config, pos.order
Modules/hr_holidays.md      ← hr.leave, leave allocation
Modules/spreadsheet*.md     ← spreadsheet/dashboard
Modules/website_sale*.md   ← e-commerce flows
```

### Core
```
Core/BaseModel.md            ← ORM internals, _name, _inherit, environment
Core/Fields.md               ← Field types, parameters, defaults
Core/API.md                 ← @api.model, @api.depends, @api.onchange, @api.constrains
Core/HTTP Controller.md      ← http.Controller, routes, JsonRequest
Core/Exceptions.md          ← ValidationError, UserError, AccessError
Patterns/Inheritance Patterns.md    ← _inherit, mixins, delegation
Patterns/Workflow Patterns.md      ← state machine, _onchange_method
Patterns/Security Patterns.md       ← ir.rule, res.groups, record rules
Patterns/UI-Discovery-Patterns.md   ← **FRONTEND UI discovery rules** (playwright/browser automation)
Tools/ORM Operations.md            ← search(), browse(), read_group(), filtered()
Tools/Modules Inventory.md         ← module list + descriptions
Tools/Export Import Mechanism.md   ← export_data(), load(), __ensure_xml_id(), ir_model_data
```

**For frontend/browser automation, load `Patterns/UI-Discovery-Patterns.md` FIRST** (before other files).

### New Features
```
New Features/What's New.md         ← Odoo 18→19 differences
New Features/API Changes.md       ← API changes and deprecations
```

---

## Step 2 — Load Vault Files

For each identified vault file:
1. `Glob` to confirm it exists
2. `Read` the file (use offset/limit for large files)
3. Extract sections relevant to the user's question

**Reading order for a cross-module process question:**
1. `Flows/Cross-Module/[topic].md` (bird's-eye method chain)
2. `Modules/[topic].md` (field-level details)
3. `Core/[topic].md` if ORM/API question
4. `Patterns/[topic].md` if workflow/security question

---

## Step 3 — Source Cross-Check (when needed)

Always verify with source code when:
- User mentions a specific field name
- User mentions a method or API
- Vault coverage for the topic is **partial or unknown**
- Version is not Odoo 19

**Source paths:**
```
addons/account/models/account_move.py        ← invoice, reconciliation
addons/account/models/account_payment.py    ← payment model
addons/sale/models/sale_order.py            ← sale.order, confirmation
addons/sale_stock/models/stock.py           ← sale→stock linkage
addons/stock/models/stock_picking.py        ← picking, delivery
addons/purchase/models/purchase_order.py    ← PO, receipt
addons/base/models/res_partner.py           ← partner
odoo/models/base.py                        ← BaseModel, environment
```

**How to verify:**
- `Grep` for the field/method name in the relevant source file
- Confirm field type, parameters, default, and compute chain
- Note any differences from vault

---

## Step 4 — Check for Knowledge Gaps

After reading vault + source:

| Coverage | Action |
|----------|--------|
| **Full** — relevant vault file exists | Provide confident, detailed context |
| **Partial** — some vault files exist | Load what's available, note what's missing |
| **None** — no vault file for topic | Apply Missing Topic Protocol (below) |

### Missing Topic Protocol

```
📝 Topik "<topic>" belum terdokumentasi di vault.

Vault mencakup ~300+ file di folder Modules/, Flows/, Core/, Patterns/, Tools/.

Apakah Anda ingin saya membuat dokumentasi vault baru untuk topik ini?
  [Ya] → Buat file vault baru dengan menganalisa source code
          Lokasi: Modules/[topic].md atau Flows/[category]/[flow].md
  [Tidak] → AI membantu berdasarkan general Odoo knowledge + source code
```

---

## Step 5 — Produce Odoo Knowledge Context

Output this structured block at the start of every response:

```markdown
## Odoo Knowledge Context

**Version**: Odoo <version>
**Topic**: <topic_name>
**Vault Coverage**: <full | partial | none>
**Source Verified**: <yes | no | not_needed>
**qmd Used**: <yes (collection: ...) | no | not_available>
**Key Vault Files**: <list of files read>

### Key Points from Vault
- [field/method/state important to the question]

### Cross-Module Flow (if applicable)
[For process questions, include the method chain from Flows/ file]

### Source Code Verification
- [file:line] — confirmed: [what was verified]

### Gaps / Caveats
- [what vault doesn't cover, what needs source verification]

### Action Guidance
Based on this context, AI should:
- [do this because...]
- [avoid this because...]
- [call domain skill next because...]
```

---

## Key Patterns the Vault Documents

### Cross-Module Flow for Sales-to-Reconcile
The vault's `Flows/Cross-Module/sale-stock-account-flow.md` documents the complete chain:
```
sale.order.action_confirm()
  ├─► procurement_group created → stock.picking created
  ├─► _action_launch_stock_rule → delivery confirmed
  └─► sale.order._create_invoices() → account.move (draft)
        └─► account.move.action_post() → posted invoice
              └─► account.payment.action_post() → reconcile
```

### Reconciliation in Account
`Flows/Account/payment-flow.md` + `Modules/Account.md` (L305-L415):
- `account.move.line.amount_residual` — remaining due
- `full_reconcile_id` — full reconciliation record
- `matched_debit_ids` / `matched_credit_ids` — partial reconciliation
- `reconcile` field on `account.account` — must be `True` for auto-reconcile
- Account types: `asset_receivable` (AR) and `liability_payable` (AP) are **enforced reconcile=True**

### Sale Order States (Odoo 19)
```
draft → sent → sale → locked     (no more "done" state)
         └─► cancel
```
Odoo 18 `done` state replaced by `locked` boolean in Odoo 19.

---

## Anti-Patterns This Skill Prevents

❌ Guessing field names without checking vault/source
❌ Recommending fixes without understanding the workflow state machine
❌ Querying Odoo DB without knowing model structure
❌ Giving version-agnostic advice for a different Odoo version
❌ Missing cross-module linkages (e.g., thinking invoice is independent from SO)

✅ Always qmd search first → then file mapping supplement → source verify
✅ For any multi-step process, always start with the Flows/ cross-module file
✅ For any field/method question, always read Modules/[topic].md first
