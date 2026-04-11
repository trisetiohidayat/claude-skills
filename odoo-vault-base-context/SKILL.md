---
name: odoo-vault-base-context
description: >
  ALWAYS activate this skill FIRST before doing anything related to Odoo in a new
  conversation or when encountering a new topic. This gives the AI foundational
  knowledge about Odoo models, workflows, API, and architecture so it does not
  guess or blindly probe APIs.

  TRIGGER when:
  - User asks anything about Odoo (new or existing conversation, any topic)
  - AI is about to query Odoo DB or source code without knowing the topic first
  - AI needs to understand how an Odoo model/field/workflow works
  - AI encounters a topic it does not have confident knowledge of in Odoo
  - User asks for step-by-step guidance on any Odoo operation

  This skill reads the Obsidian vault (documentation) and source code paths
  to build context. It also handles version detection and missing topic gaps.

  Tools: Read, Grep, Glob, Bash
  Output: Structured knowledge context loaded into conversation for use in
  subsequent responses. Does NOT replace domain-specific skills (like odoo-architect,
  odoo-investigate-before-fix, etc.) — it provides BASE context before them.
---

# Odoo Vault Base Context Skill

## Purpose

This skill ensures the AI **always has correct foundational knowledge of Odoo**
before acting — not guessing field names, not blindly probing APIs, not making
assumptions about model structure. It does this by:

1. Loading knowledge from the Obsidian vault (documentation)
2. Cross-checking against source code when needed
3. Handling version detection
4. Identifying and offering to fill knowledge gaps

## Vault & Source Paths

```
VAULT_PATH         = ~/Obsidian Vault/Odoo 19
ODOO_SOURCE_19     = ~/odoo/odoo19/odoo
ODOO_SOURCE_17     = ~/odoo/odoo17/odoo
ODOO_SOURCE_SUQMA  = ~/odoo/odoo19-suqma/odoo
```

## Vault Coverage Map

The vault currently documents:

| Vault Path | Primary Version | Topics Covered |
|---|---|---|
| `Core/*.md` | Odoo 19 | ORM, Fields, API, Controllers, Exceptions |
| `Patterns/*.md` | Odoo 19 | Inheritance, Workflow, Security |
| `Tools/*.md` | Odoo 19 | ORM Operations, Modules Inventory |
| `Modules/Account.md` | Odoo 19 | account.move, invoices, journals |
| `Modules/Purchase.md` | Odoo 19 | purchase.order, PO→invoice |
| `Modules/Stock.md` | Odoo 19 | stock.quant, stock.picking |
| `Modules/Sale.md` | Odoo 19 | sale.order, quotation |
| `Modules/CRM.md`, `MRP.md`, `Product.md`, `HR.md` | Odoo 19 | Per-module docs |
| `New Features/What's New.md` | Odoo 18→19 | Version differences |
| `New Features/API Changes.md` | Odoo 19 | API changes, deprecations |

> Vault primarily covers **Odoo 19 Community Edition**. For other versions
> (15, 17, Enterprise), AI must be cautious and cross-reference with source code.

## Workflow

### Step 0 — Detect Version

Always identify the Odoo version BEFORE loading knowledge:

1. **If user stated a version** → use that version
2. **If not stated** → ask the user:
   ```
   🔍 Versi Odoo berapa yang sedang Anda gunakan?
   Pilihan: Odoo 17, Odoo 19, atau yang lain?
   ```
3. **If vault does NOT have coverage for that version** → tell the user:
   ```
   ⚠️ Vault ini belum memiliki dokumentasi khusus untuk Odoo <version>.
   Opsi:
   [1] Baca langsung dari source code tanpa vault — AI tetap bisa membantu
       dengan membaca kode Odoo yang terinstall.
   [2] Buat vault knowledge baru untuk Odoo <version> — prosesnya
       akan memakan waktu, tapi hasil akhirnya AI akan punya konteks lengkap.
   Mana yang Anda preferensikan?
   ```

### Step 1 — Identify Topic

Parse the user's request to identify the topic area. Use this mapping:

```
Topic                    → Vault File(s)
─────────────────────────────────────────
ORM / model / CRUD       → Core/BaseModel.md
Fields / field types      → Core/Fields.md
API decorators            → Core/API.md
HTTP / controller         → Core/HTTP Controller.md
Exceptions / errors       → Core/Exceptions.md
Inheritance / mixin       → Patterns/Inheritance Patterns.md
Workflow / state machine  → Patterns/Workflow Patterns.md
Security / ACL / ir.rule  → Patterns/Security Patterns.md
Domain / search / browse  → Tools/ORM Operations.md
Modules catalog           → Tools/Modules Inventory.md
Invoice / billing         → Modules/Account.md
Purchase / PO / vendor     → Modules/Purchase.md
Stock / inventory          → Modules/Stock.md
Sale / SO / quotation      → Modules/Sale.md
CRM / lead / opportunity   → Modules/CRM.md
Manufacturing / BOM       → Modules/MRP.md
Product / product.template → Modules/Product.md
HR / employee             → Modules/HR.md
Partner / contact / bank   → Modules/res.partner.md
New in 19 / migration      → New Features/What's New.md
API changes / deprecations → New Features/API Changes.md
```

If multiple topics are involved, read all relevant files.

### Step 2 — Load Vault Knowledge

1. Use `Glob` to confirm the vault file exists
2. Use `Read` to load the content
3. Extract relevant sections based on the user's specific question
4. Summarize key points for the AI to use

### Step 3 — Cross-Check with Source Code (if needed)

For these situations, always verify vault info against source code:
- Field names that might differ between versions
- Method signatures or API changes
- New or deprecated features
- When vault coverage for the topic is partial

```
Source path mapping:
  addons/account/models/    → Account module
  addons/stock/models/       → Stock module
  addons/purchase/models/     → Purchase module
  addons/sale/models/        → Sale module
  addons/base/models/        → Base models (res.partner, etc.)
  addons/mrp/models/         → Manufacturing
  odoo/models/              → Core ORM (BaseModel, BaseModel._browse)
```

Use `Grep` or `Read` on source files to verify information.
**Source code is ground truth — vault is reference. If they conflict, trust source code.**

### Step 4 — Check for Knowledge Gaps

After loading vault + source:

1. If the topic is **well covered** in vault → provide confident context
2. If the topic is **partially covered** → load what's available, note gaps
3. If the topic is **NOT in vault at all** → follow the **Missing Topic Protocol**:

### Missing Topic Protocol

```
📝 Topik "<topic_name>" belum terdokumentasi di vault.

Vault saat ini mencakup ~80 modul/subtopik dari Odoo 19.
Berikut area yang BELUM terdokumentasi:

[list any gaps identified]

Apakah Anda ingin saya menambahkan dokumentasi untuk topik ini ke vault?

[Jawab Ya] → Gunakan skill "odoo-vault-analysis" untuk membuat
             dokumentasi vault baru. Proses ini akan:
             1. Analisa source code untuk topik tersebut
             2. Buat file vault dengan struktur yang konsisten
             3. Tambahkan ke folder Modules/ atau kategori yang tepat

[Jawab Tidak] → AI tetap membantu berdasarkan:
                1. Knowledge umum Odoo (bukan dari vault)
                2. Source code reading saat diperlukan
                Catatan: response mungkin kurang spesifik dan akurat
                dibanding jika vault sudah ada.
```

### Step 5 — Produce Knowledge Context

Compile all loaded knowledge into a structured context summary that the AI
uses for subsequent responses. Format:

```markdown
## Odoo Knowledge Context

**Version**: Odoo <version>
**Topic**: <topic_name>
**Vault Coverage**: <full | partial | none>
**Source Verified**: <yes | no>

### Key Points from Vault
- ...

### Source Code Verification
- [file:line] — confirmed: ...

### Gaps / Caveats
- ...

### Action Guidance
Based on this context, AI should:
- [do this because...]
- [avoid this because...]
```

This context should be kept concise and focused on what is needed to
answer the user's question accurately.

## Version Handling Rules

| Situation | Action |
|---|---|
| User states version | Use that version |
| User doesn't know | Ask user to confirm |
| Vault covers the version | Load from vault |
| Vault does NOT cover the version | Ask: source code only OR create vault |
| Version not in ~/odoo/ | Cannot cross-verify — use vault + general knowledge |

## Handling "I Don't Know the Version"

If user does not know their Odoo version, offer these discovery methods:
1. Check Odoo login page (shows version number)
2. Check `~/odoo.conf` in project
3. Query MCP instance metadata
4. Look at URL in Odoo frontend (apps version info)

## Special Cases

### For Invoice/Billing Topics
Vault has `Modules/Account.md` which covers `account.move` workflow.
Verify: is this Customer Invoice, Vendor Bill, or Credit Note?
Source: `addons/account/models/account_move.py`

### For Purchase Order Topics
Vault has `Modules/Purchase.md` which covers PO workflow.
Verify: is this RFQ, PO, or Receipt?
Source: `addons/purchase/models/purchase_order.py`

### For Stock/Inventory Topics
Vault has `Modules/Stock.md` which covers `stock.picking` and `stock.quant`.
Verify: is this receipt, delivery, or internal transfer?
Source: `addons/stock/models/stock_picking.py`

### For Multi-Company Environments
Many Odoo installations are multi-company. When discussing data or access:
- Always clarify which company context is relevant
- Record rules may filter data visibility
- The `company_id` field is present on most transactional models

## Anti-Patterns This Skill Prevents

❌ AI tries `groups_id` field on `res.users` without checking vault first
❌ AI assumes field names without verifying against source
❌ AI queries Odoo DB without knowing the model's structure
❌ AI recommends a fix without understanding the workflow state machine
❌ AI gives version-agnostic advice that only applies to a different Odoo version

✅ AI always loads vault knowledge FIRST, then verifies with source, then acts
