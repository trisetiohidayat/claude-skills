---
name: odoo-vault-analysis
description: >
  Analisis Odoo 19 menggunakan vault Obsidian + source code cross-reference.
  TRIGGER ketika user bertanya tentang:
  - Cara kerja model/field/API Odoo 19 (e.g. "explain how res.partner.bank works", "apa itu service_tracking")
  - Arsitektur modul Odoo (e.g. "how does sale_project relate to project", "flow SO ke invoice")
  - Source code investigation (e.g. "where is _timesheet_service_generation defined")
  - Best practices Odoo (e.g. "best practice untuk state workflow", "pattern untuk computed field")
  - Dokumentasi modul (e.g. "jelaskan module stock", "purchase order flow")
  - Perbandingan fitur antar modul Odoo
  JANGAN trigger untuk pertanyaan umum yang tidak terkait Odoo 19.
---

# Odoo Vault Analysis Skill

Skill ini menganalisis Odoo 19 dengan membaca **vault Obsidian** (dokumentasi) dan **cross-reference ke source code** untuk memberikan jawaban yang akurat dan berdasar bukti.

## Vault & Source Code Paths

```
VAULT_PATH       = ~/Obsidian Vault/Odoo 19
ODOO_SOURCE_CE   = ~/odoo/odoo19/odoo
ODOO_SOURCE_SUQMA = ~/odoo/odoo19-suqma/odoo
```

## Vault Structure (untuk mapping keyword ke file)

| Kategori | Path | Isi |
|---|---|---|
| Core | `Core/BaseModel.md` | ORM foundation, _name, _inherit, CRUD |
| Core | `Core/Fields.md` | Field types (Char, Many2one, Json, etc.) |
| Core | `Core/API.md` | @api.depends, @api.onchange, @api.constrains |
| Core | `Core/HTTP Controller.md` | @http.route, JSON responses, auth types |
| Core | `Core/Exceptions.md` | ValidationError, UserError, AccessError |
| Patterns | `Patterns/Inheritance Patterns.md` | _inherit vs _inherits vs mixin |
| Patterns | `Patterns/Workflow Patterns.md` | State machine, action methods |
| Patterns | `Patterns/Security Patterns.md` | ACL CSV, ir.rule, field groups |
| Tools | `Tools/ORM Operations.md` | search(), browse(), create(), domain operators |
| Tools | `Tools/Modules Inventory.md` | 304 modules catalog |
| Snippets | `Snippets/Model Snippets.md` | Code templates model |
| Snippets | `Snippets/Controller Snippets.md` | Code templates controller |
| New Features | `New Features/What's New.md` | Odoo 18→19 changes |
| New Features | `New Features/API Changes.md` | Json field, @api.model_create_multi, deprecations |
| Modules | `Modules/Stock.md` | stock.quant, stock.picking, stock.move |
| Modules | `Modules/Purchase.md` | purchase.order, PO→invoice flow |
| Modules | `Modules/Account.md` | account.move, journal entries |
| Modules | `Modules/Sale.md` | sale.order, sale.order.line |
| Modules | `Modules/CRM.md`, `Modules/MRP.md`, `Modules/Product.md`, `Modules/HR.md` | dll |
| Modules | `Modules/res.partner.md` | Partner, bank accounts, addresses |

## Keyword Mapping

Map keyword/topik ke file vault yang relevan:

```
"orm" / "model" / "base model" / "crud" / "create write search"     → Core/BaseModel.md
"field" / "char" / "many2one" / "one2many" / "many2many" / "json"  → Core/Fields.md
"api" / "depends" / "onchange" / "constrains" / "decorator"         → Core/API.md
"controller" / "http" / "route" / "json response" / "auth"           → Core/HTTP Controller.md
"error" / "exception" / "validation error" / "user error"           → Core/Exceptions.md
"inheritance" / "_inherit" / "_inherits" / "mixin"                  → Patterns/Inheritance Patterns.md
"workflow" / "state" / "action_confirm" / "action_done"              → Patterns/Workflow Patterns.md
"security" / "acl" / "ir.rule" / "permission"                       → Patterns/Security Patterns.md
"search" / "browse" / "domain" / "operator" / "filter"              → Tools/ORM Operations.md
"modules" / "catalog" / "available modules"                           → Tools/Modules Inventory.md
"snippet" / "template" / "code template"                             → Snippets/Model Snippets.md atau Controller Snippets.md
"new in 19" / "odoo 19" / "whats new" / "migration"                 → New Features/What's New.md
"api changes" / "deprecated" / "api_create_multi"                    → New Features/API Changes.md
"stock" / "inventory" / "picking" / "quant" / "warehouse"            → Modules/Stock.md
"purchase" / "po" / "vendor" / "rfq"                                 → Modules/Purchase.md
"account" / "invoice" / "journal" / "move" / "payment"               → Modules/Account.md
"sale" / "so" / "sale order" / "quotation"                          → Modules/Sale.md
"crm" / "lead" / "opportunity"                                       → Modules/CRM.md
"mrp" / "bom" / "manufacturing" / "workorder"                       → Modules/MRP.md
"product" / "product.template" / "product.product"                  → Modules/Product.md
"hr" / "employee" / "department"                                     → Modules/HR.md
"partner" / "bank" / "res.partner" / "res.partner.bank"             → Modules/res.partner.md
"project" / "task" / "milestone"                                      → Modules/Project.md (jika ada)
"mail" / "message" / "notification"                                  → Modules/mail.md
"website" / "e-commerce" / "sale.store"                              → Modules/website_sale.md
```

## Workflow

### Step 1: Identifikasi Topik
- Parse pertanyaan user → extract keyword
- Map keyword ke file vault menggunakan tabel di atas
- Jika multiple keywords, baca semua file yang relevan

### Step 2: Baca Vault Files
- Gunakan Read tool untuk baca file vault yang teridentifikasi
- Extract poin-poin penting dari vault (waktu singkat, fokus pada yang relevan)

### Step 3: Cross-Reference ke Source Code
- Identifikasi module path di source code berdasarkan topik
- Gunakan Bash + grep untuk mencari evidence di source code
- Source code priority: `ODOO_SOURCE_SUQMA` (lebih lengkap dengan customizations) > `ODOO_SOURCE_CE`

**Common module paths:**
```
sale_project     → addons/sale_project/models/
account          → addons/account/models/
stock            → addons/stock/models/
purchase         → addons/purchase/models/
project          → addons/project/models/
mrp              → addons/mrp/models/
sale             → addons/sale/models/
crm              → addons/crm/models/
base (res_partner, res_bank) → addons/base/models/
```

### Step 4: Verify & Combine
- Bandingkan penjelasan vault dengan actual source code
- Jika ada discrepancy, **source code WIN** — vault adalah referensi, source code adalah ground truth
- Berikan jawaban yang menggabungkan:
  1. Penjelasan konseptual dari vault
  2. Bukti kode dari source code (file:line)

## Output Format

```
## [Topik] — Analisis dari Vault + Source Code

### 📖 Dari Vault
[Ringkasan relevan dari vault file]

### 🔍 Dari Source Code
[File path]:[line]
```python
[paste relevant code snippet]
```

### ✅ Kesimpulan
[Ringkasan yang menggabungkan keduanya]
```

## Catatan Penting

- Vault adalah **referensi konseptual**, source code adalah **ground truth**
- Jika vault tidak membahas topik tertentu, langsung ke source code
- Gunakan Grep/Bash untuk cari evidence, jangan asumsi
- Mention path file source code: `~/odoo/odoo19-suqma/odoo/addons/.../file.py:line`
- Vault menggunakan Obsidian Flavored Markdown dengan wikilinks (`[[wikilink]]`) — ini adalah link ke file vault lain, follow jika relevan
