---
name: odoo-custom-module-docs
description: >
  BUATKAN dokumentasi lengkap untuk Odoo custom module. SELALU gunakan skill ini ketika:
  - User meminta "buat dokumentasi module X"
  - User meminta "document custom module"
  - User meminta "generate module docs"
  - User meminta update dokumentasi setelah ada perubahan code
  - User meminta "buat docs untuk module baru"

  Skill ini menelusuri SELURUH code module (models, views, wizards, controllers),
  menggunakan vault analysis sebagai context base, dan menghasilkan dokumentasi dengan
  template FIXED yang konsisten - selalu terdiri dari SECTION yang SAMA.

  Template FIXED:
  1. Non-Technical (Bahasa Indonesia)
     - Apa Itu [module]?
     - Perbedaan dari Odoo Standard
     - Fitur Utama dan Cara Penggunaan
     - Menu yang Ditambahkan/Dimodifikasi
     - Business Flow Lengkap
     - Kapan Digunakan?
  2. Technical (English)
     - Problem Statement
     - Solution
     - Code Changes
     - Architecture Comparison
     - Requirements
---

# Odoo Custom Module Documentation Skill

## Purpose

Generate comprehensive, consistent documentation for Odoo custom modules using a **FIXED template**.
The output always has the SAME sections regardless of module complexity.

## When to Use

Use this skill when:
- User requests documentation for a specific module
- User requests update of existing documentation after code changes
- User asks to "document" or "generate docs" for Odoo modules
- User asks to "buat dokumentasi" for any Odoo module

## Fixed Template Structure

ALWAYS follow this template exactly. Output ALL sections even if content is minimal.

```markdown
# Module XX: [module_name]

## Non-Technical / Bahasa Indonesia

### Apa Itu `[module_name]`?

[Description of what the module does in Bahasa Indonesia]
[What business problem it solves]

---

### Perbedaan dari Odoo Standard

| Aspek | Odoo Standard | Dengan `[module_name]` |
|-------|---------------|------------------------|
| [aspect 1] | [standard behavior] | [custom behavior] |
| [aspect 2] | [standard behavior] | [custom behavior] |

---

### Fitur Utama dan Cara Penggunaan

#### Fitur 1: [Feature Name]

**Lokasi di Odoo:**
Menu: `Path` -> `To` -> `Menu`

**Step-by-step:**

1. Buka `Path` -> `To` -> `Menu`
2. Klik **[Action]**
3. Isikan:
   - **`Field 1`** - [description]
   - **`Field 2`** - [description]
4. Klik **Save**

**Hasil:** [what happens]

---

#### Fitur 2: [Feature Name]
[Same structure]

---

### Menu yang Ditambahkan/Dimodifikasi

| Menu Original Odoo | Perubahan |
|--------------------|-----------|
| `Menu` -> `Path` | Tambah [description] |
| `Menu` -> `Path` | Modifikasi [description] |

---

### Business Flow Lengkap

```
1. [Step 1 description]
   Menu: `Path` -> `To` -> `Menu`

2. [Step 2 description]
   [Action details]

3. [Step 3 description]
   [Result]
```

---

### Kapan Digunakan?

- [Use case 1]
- [Use case 2]
- [Use case 3]

---

## Technical Documentation / English

### Problem Statement

[What problem does this module solve in Odoo 19 context?]
[What was different/broken in standard Odoo?]

### Solution

[How does this module solve the problem?]
[What approach was taken?]

**Files Modified/Created:**

| File | Type | Purpose |
|------|------|---------|
| `models/xxx.py` | Model | [purpose] |
| `views/xxx.xml` | View | [purpose] |
| `wizards/xxx.py` | Wizard | [purpose] |

### Code Changes

**File: `[relative/path/to/file.py]`**
```python
[Relevant code snippet - 20-30 lines max]
```

**File: `[relative/path/to/file.xml]`**
```xml
[Relevant XML snippet - key elements only]
```

### Architecture Comparison

| Aspect | Standard Odoo 19 | Custom Implementation |
|--------|-----------------|----------------------|
| [aspect 1] | [standard] | [custom] |
| [aspect 2] | [standard] | [custom] |

### Requirements

- [Requirement 1]
- [Requirement 2]
- [Module dependencies]

---

*Generated: [DATE]*
*Odoo Version: 19.0*
```

---

## Process

### Step 1: Discover Module Location

Find the module directory:
```
PROJECT_PATH/custom_addons_19_new2/roedl/{module_name}/
PROJECT_PATH/custom_addons_15/{module_name}/
```

Check for:
- `__manifest__.py` (Odoo 17+)
- `__openerp__.py` (Odoo 15-)
- `__init__.py`

### Step 2: Analyze Module Structure

Read ALL of the following (if exists):

```
module/
├── __manifest__.py              # Module metadata
├── __init__.py                   # Imports
├── models/
│   ├── __init__.py
│   ├── model1.py                # All model files
│   └── model2.py
├── views/
│   ├── view1.xml                # All view files
│   └── view2.xml
├── wizards/
│   ├── __init__.py
│   ├── wizard1.py
│   └── wizard1_views.xml
├── controllers/
│   ├── __init__.py
│   └── main.py
├── security/
│   └── ir.model.access.csv
├── data/
│   └── data_file.xml
└── reports/
    ├── report1.xml
    └── report1.py
```

### Step 3: Load Vault Context (odoo-vault-base-analysis)

Before analyzing code, load relevant vault context:

1. Check `~/odoo-vaults/odoo-19/` for relevant module documentation
2. Load `Modules/[related_module].md` files for referenced models
3. Load `Flows/` files for business processes involved

### Step 4: Extract and Analyze

For each file, extract:

**Models (`models/*.py`):**
- Model class names and inheritance (`_name`, `_inherit`)
- All field definitions (name, type, parameters)
- Methods: `create()`, `write()`, `unlink()`, custom methods
- Onchanges: `@api.onchange()`
- Computed fields: `@api.depends()`
- Constraints: `@api.constrains()`

**Views (`views/*.xml`):**
- View types: form, tree, kanban, search, etc.
- View IDs
- Field definitions
- Button definitions
- Inherited views (xpath modifications)

**Wizards (`wizards/*.py`):**
- Wizard model inheritance
- Fields
- Action methods

**Security (`security/*.csv`):**
- Access control lists
- Model permissions

### Step 5: Identify Menu Changes

Search for `ir.ui.menu` in views or check menu definitions:
```bash
grep -r "menu" views/*.xml --include="*.xml"
```

### Step 6: Generate Documentation

Follow the FIXED template exactly. Fill ALL sections even if minimal content.

---

## Analysis Checklist

Use this checklist to ensure complete analysis:

```
[ ] Read __manifest__.py
    [ ] name
    [ ] version
    [ ] description
    [ ] author
    [ ] depends (dependencies)
    [ ] data files

[ ] Read ALL models/*.py
    [ ] Model classes
    [ ] Field definitions
    [ ] Method definitions
    [ ] Onchange methods
    [ ] Computed fields
    [ ] Constraints

[ ] Read ALL views/*.xml
    [ ] View types
    [ ] View inheritance
    [ ] Field positions
    [ ] Button actions

[ ] Read wizards/ (if exists)
    [ ] Wizard models
    [ ] Wizard views
    [ ] Action methods

[ ] Read security/ir.model.access.csv
    [ ] ACL entries

[ ] Check for custom reports (reports/)
[ ] Check for controllers (controllers/)
[ ] Check for data files (data/)

[ ] Identify:
    [ ] What Odoo standard features are modified
    [ ] What new features are added
    [ ] What menus are added/changed
    [ ] What database tables are created
    [ ] What fields are added to existing tables
```

---

## Output Location

Save documentation to:
```
PROJECT_PATH/custom_addons_XX/roedl/docs/XX-{module_name}.md
```

Or if documentation already exists:
```
PROJECT_PATH/custom_addons_XX/roedl/docs/{existing-file}.md
```

Update existing documentation, don't delete and recreate.

---

## Example: Feature Description Format

**WRONG (too vague):**
```
Fitur: Invoice signature
Adds signature to invoice
```

**CORRECT (specific with menu path):**
```
#### Fitur 1: Invoice Signature (Tanda Tangan Invoice)

**Lokasi Setup Signature Master:**
Menu: `Settings` -> `Accounting` -> `Signature` (sub-menu baru)

**Step-by-step setup signature:**

1. Buka `Settings` -> `Accounting` -> `Signature` -> **Create**
2. Isikan:
   - **`Employee`** - pilih employee yang signature-nya akan digunakan
   - **`Position`** - isi jabatan, contoh: "Finance Manager", "Director"
3. Klik **Save**

**Hasil:** Saat print invoice, signature akan muncul sesuai dengan signature yang di-assign ke company.
```

---

## Code Snippet Format

**For Python:**
````markdown
**File: `models/account_move.py`**
```python
def _compute_has_facturx_manual_download(self):
    """Docstring explaining purpose."""
    for move in self:
        if not move.journal_id:
            move.has_facturx_manual_download = False
            continue

        # Check module installation
        module_installed = self.env['ir.module.module'].search([
            ('name', '=', 'account_edi_ubl_cii'),
            ('state', '=', 'installed')
        ], limit=1)

        move.has_facturx_manual_download = module_installed and not move.journal_id.embed_edi_to_pdf
```
````

**For XML:**
````markdown
**File: `views/account_journal_views.xml`**
```xml
<xpath expr="//group[@name='group_edi_config']" position="after">
    <group string="Factur-X / EDI Settings" name="group_facturx_config">
        <field name="embed_edi_to_pdf"
                widget="boolean_toggle"
                help="If checked, EDI XML will be embedded in PDF..."/>
    </group>
</xpath>
```
````

---

## Vault Integration

When generating technical documentation, ALWAYS:

1. **Reference vault files** for standard Odoo behavior being modified
2. **Use vault field/method names** accurately
3. **Note discrepancies** if vault says different from actual code

Vault path: `~/odoo-vaults/odoo-19/`

Common vault references:
```
Modules/Account.md          ← for account.move, account.move.line
Modules/Sale.md            ← for sale.order, sale.order.line
Modules/Project.md         ← for project.task, account.analytic.line
Modules/Product.md         ← for product.template
Modules/res.partner.md     ← for res.partner
Flows/Cross-Module/       ← for business processes
```

---

## Version-Specific Notes

### Odoo 19 Specifics

| Old (Odoo 15) | New (Odoo 19) |
|---------------|---------------|
| `<tree>` view | `<list>` view |
| `attrs` attribute | `invisible`/`readonly` attributes |
| `_onchange_price_subtotal()` | `_onchange_amount()` |
| `states='done'` | `stage_id.is_final=True` |
| `account.account.type` model | `account.account.account_type` field |
| `web_progress` wizard | Removed |

Document these differences in "Architecture Comparison" section.

---

## Error Prevention

### DO NOT:
- ❌ Skip sections even if module is simple
- ❌ Use vague descriptions like "adds functionality"
- ❌ Copy-paste without understanding code
- ❌ Miss menu paths (always verify in XML)
- ❌ Ignore wizard/controller files
- ❌ Skip security analysis

### ALWAYS:
- ✅ Follow template exactly
- ✅ Include ALL sections
- ✅ Use specific menu paths from XML
- ✅ Show relevant code snippets (not full files)
- ✅ Document new menu items and changes
- ✅ Note Odoo version differences in technical section

---

*Last Updated: April 2026*
