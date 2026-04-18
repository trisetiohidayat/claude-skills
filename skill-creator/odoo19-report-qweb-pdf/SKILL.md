---
name: odoo19-report-qweb-pdf
description: >
  Generate complete Odoo 19 QWeb PDF report modules from PDF files, screenshots, or
  design descriptions. Use this skill whenever the user wants to create, customize, or
  extend any Odoo report — whether they provide a mockup PDF, screenshot of a report
  layout, or simply describe what the report should look like. It generates the full
  module: QWeb XML template(s), ir.actions.report definition, optional report.paperformat,
  ir.model.data CSV, and __manifest__.py. This is the DEFINITIVE skill for ALL Odoo
  QWeb report work in Odoo 19.
  Triggers for: "generate report", "create qweb report", "PDF report template", "custom
  report", "quotation template", "invoice layout", "delivery slip", "stock report",
  "product label", "print button", "report dari PDF", "bikin report Odoo", "extend
  existing report", "add field to sale order report", "customize invoice template",
  "cetak laporan PDF Odoo", "bikin template report".
keywords: [odoo, qweb, pdf, report, template, xml, ir.actions.report, odoo19, bootstrap4, screenshot, mockup, layout]
version: 2.2
author: Claude
---

# Odoo 19 QWeb PDF Report Generator

Generate complete Odoo 19 QWeb PDF report module from PDF mockups, screenshots, or description.

## How It Works

```
Input:  PDF/screenshot/mockup description
Output: my_report_module/
         ├── __manifest__.py
         ├── reports/
         │   ├── __init__.py
         │   ├── ir_actions_report.xml          # ir.actions.report definition
         │   └── ir_actions_report_templates.xml  # QWeb XML templates
         ├── data/
         │   └── ir_model_data.xml             # ir.model.data for external IDs
         └── models/
              └── __init__.py
```

## Odoo 19 Specific Context

> Odoo 19 made significant architectural changes to the report system. Read carefully.

### Web Module Consolidation
All web-related server code is in the `web` module (consolidated from split `web_*` modules in older versions). All report rendering logic, asset bundles, and layout templates live in `web`.

### Bootstrap 4 (not Bootstrap 3)
Odoo 19 uses **Bootstrap 4** throughout reports. Key differences:
| Odoo ≤17 (BS3) | Odoo 19 (BS4) |
|---|---|
| `col-md-6` | `col-6` |
| `text-right` | `text-end` |
| `text-left` | `text-start` |
| `font-weight-bold` | `fw-bold` |
| `mb-3` | `mb-3` (same) |
| `pt-2` | `pt-2` (same) |
| `mx-auto` | `mx-auto` (same) |

### `t-out` Directive (Odoo 16+)
`t-out` is the modern replacement for `t-esc`. Use `t-out` for escaped output. Use `t-raw` only when you intentionally want unescaped HTML (and sanitize first).

### Report Asset Bundles
Two bundles are included in every report via `web.report_layout`:
- `web.report_assets_common` — Common report SCSS
- `web.report_assets_pdf` — PDF-specific reset CSS

### Company Report Customization (Odoo 19 new)
`res.company` has two new fields for report branding:
- `layout_background` — `selection`: `default`, `text`, `company`, `custom`
- `layout_background_image` — `binary`: custom background image

### Odoo 19 html_editor (renamed from web_editor)
For reports that render user-generated HTML content (e.g. notes, terms, policy text), add `html_editor` to depends and use `t-field` instead of `t-out`:
```xml
<div t-field="doc.note"/>   <!-- renders trusted HTML from html_editor widget -->
```
Use `t-out` for plain text fields; use `t-field` for HTML fields.

---

## Report Complexity — Adapt Output to Scope

**ALWAYS assess complexity first**, then scale your output accordingly.

| Complexity | Indicators | Output Scope |
|---|---|---|
| **Simple** | 1 model, ≤4 sections, no custom fields, standard layout | Lean: 1 XML file + lean template ~40-60 lines. Skip separate `ir_actions_report.xml`. |
| **Medium** | 1-2 models, custom fields or computed values, custom paperformat | Standard: full module structure. 3-layer + paperformat. ~80-120 lines. |
| **Complex** | PDF-accurate layout, multiple sections, custom calculations | Full: all optional sections, paperformat, custom styles, notes handling. ~150-300 lines. |

### Lean Module Rules (Simple Reports)
For simple reports, **merge into a single XML file**:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- ir.actions.report definition -->
    <record id="action_report_simple" model="ir.actions.report">
        <field name="name">Simple Report</field>
        <field name="model">my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_module.report_simple</field>
        <field name="binding_model_id" ref="model_my_model"/>
        <field name="bind_filter">True</field>
    </record>

    <!-- Layer 1: entry -->
    <template id="report_simple">
        <t t-call="my_module.report_simple_raw"/>
    </template>

    <!-- Layer 2: raw -->
    <template id="report_simple_raw">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="my_module.report_simple_document" t-lang="doc.partner_id.lang"/>
            </t>
        </t>
    </template>

    <!-- Layer 3: document (lean — only essential sections) -->
    <template id="report_simple_document">
        <t t-call="web.external_layout">
            <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
            <div class="page">
                <!-- header, table, totals only -->
            </div>
        </t>
    </template>
</odoo>
```
**SKIP for simple reports:** `reports/__init__.py`, separate `reports/ir_actions_report.xml`, paperformat (use default), comments, boilerplate.

---

## PDF/Screenshot Input Analysis

When the user provides a PDF or screenshot image:

### Step 1 — Visual Analysis
Before generating code, describe the layout:
1. **Document structure** — how many sections visible? (header, addresses, table, totals, footer)
2. **Column layout** — 1-column or 2-column grid? Header placement?
3. **Table structure** — how many columns, what data in each column?
4. **Typography hints** — font sizes, bold labels, section dividers

### Step 2 — Infer Odoo Model and Fields
Map visual elements to Odoo fields:

| Visual Element | Odoo Field |
|---|---|
| Company name/logo | `doc.company_id` |
| Document number (top) | `doc.name` |
| Date | `doc.date_order` / `doc.invoice_date` |
| Vendor/Customer name | `doc.partner_id.display_name` |
| Address block | `doc.partner_id` with `widget="contact"` |
| Line item rows | `doc.order_line` / `doc.invoice_line_ids` |
| Qty column | `line.product_uom_qty` |
| Unit price | `line.price_unit` with `t-options='{"widget":"monetary"}'` |
| Tax amount | `line.tax_ids` |
| Subtotal | `line.price_subtotal` |
| Subtotal label | `doc.amount_untaxed` |
| Tax total | `doc.amount_tax` |
| Grand total | `doc.amount_total` |
| Notes/terms | `doc.note` or `doc.notes` |
| Signature area | `doc.signature` via `image_data_uri()` |
| Barcode | `line.product_id.barcode` |

### Step 3 — Layout Mapping
- **Header/logo area** → `web.external_layout` provides company logo automatically
- **Top-left text block** → `<div class="col-6">` with `<h2>` title + meta info
- **Top-right block** → `<div class="col-6 text-end">` with date/reference
- **2-column address** → BS4 row with two `col-6` divs
- **Line table** → `<table class="table table-sm table-bordered">` with `<thead>` + `<tbody>`
- **Totals block** → right-aligned `<table>` or BS4 grid on the right side
- **Signature** → two-column BS4 row with border-bottom lines

### Step 4 — Generate Code
Follow the complexity rules above to determine output scope. For **label/grid reports** (multiple items per page), use inline CSS table layout — NOT BS4 col-* grid. BS4 column grid is not reliable in wkhtmltopdf for dense multi-column layouts.

```xml
<!-- Label grid: use HTML table with inline CSS, NOT BS4 col-* -->
<table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
    <tr>
        <td style="width: 50%; padding: 6px; border: 1px solid #ccc;">
            <!-- label 1 content -->
        </td>
        <td style="width: 50%; padding: 6px; border: 1px solid #ccc;">
            <!-- label 2 content -->
        </td>
    </tr>
</table>
```

---

## Step-by-Step Workflow

### Step 1 — Analyze the Design + Detect Complexity

Read the PDF/screenshot/mockup. Identify:
1. **Document type** — Invoice, quotation, delivery slip, etc.
2. **Data model** — What Odoo model does it print from?
3. **Sections** — Header info, address block, table, totals, notes, footer
4. **Paper format** — A4 portrait/landscape, US Letter
5. **Loopable sections** — Which parts repeat per record/page?
6. **Complexity level** — Simple, Medium, or Complex (see table above)

If user provides a screenshot, describe what you see before generating code.

### Step 2 — Determine Model and Fields

Confirm with user (or infer from context):
- Model: `sale.order`, `account.move`, `stock.picking`, custom model?
- Key fields: partner, dates, amounts, line items, notes
- Single vs multi-record printing
- Related models: `doc.partner_id`, `doc.company_id`, `doc.currency_id`

### Step 3 — Generate the Complete Module

#### File: `__manifest__.py`
```python
{
    'name': 'My Custom Report',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Custom QWeb PDF report',
    'depends': ['base', 'sale'],
    'data': [
        'reports/ir_actions_report_templates.xml',
        'reports/ir_actions_report.xml',
        # 'data/ir_model_data.xml',  # if external IDs needed
    ],
    'installable': True,
    'application': False,
}
```

#### File: `reports/__init__.py`
```python
from . import ir_actions_report
```
(Only needed if custom Python logic is added.)

#### File: `reports/ir_actions_report.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_report_my_model" model="ir.actions.report">
        <field name="name">My Report</field>
        <field name="model">my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_module.report_my_model</field>
        <field name="report_file">my_module.report_my_model</field>
        <field name="print_report_name">'My Report - %s' % (object.name)</field>
        <field name="binding_model_id" ref="model_my_model"/>
        <field name="binding_type">report</field>
        <field name="bind_filter">True</field>   <!-- Show print wizard with record selection -->
    </record>
</odoo>
```

**Key fields:**
- `model` — technical model name (e.g., `sale.order`, NOT display name)
- `report_name` — **dotted notation**: `<module>.<template_id>`, must match the entry template's `id`
- `binding_model_id` — use `ref="model_<underscored_model>"` (e.g., `model_sale_order`)
- `bind_filter` — set to `True` to show the print wizard (user picks which records to print); omit or set to `False` for direct print
- `print_report_name` — Python expression; `object` = single record being printed

#### File: `reports/ir_actions_report_templates.xml`

**3-LAYER TEMPLATE ARCHITECTURE:**

**Layer 1 — Entry (id matches `report_name`):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="report_my_model">
        <t t-call="my_module.report_my_model_raw"/>
    </template>
```

**Layer 2 — Raw (loops over `docs`, wraps in html_container):**
```xml
    <template id="report_my_model_raw">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="my_module.report_my_model_document"
                   t-lang="doc.partner_id.lang"/>
            </t>
        </t>
    </template>
```

**Layer 3 — Document (actual content, lean example):**
```xml
    <template id="report_my_model_document">
        <t t-call="web.external_layout">
            <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
            <div class="page">

                <!-- Header row: title + meta (BS4 col-6 grid) -->
                <div class="row mb-3">
                    <div class="col-6">
                        <h2 class="fw-bold"><t t-out="doc.name"/></h2>
                    </div>
                    <div class="col-6 text-end">
                        <t t-out="doc.date_order" t-options='{"widget": "date"}'/>
                    </div>
                </div>

                <!-- Partner address via contact widget -->
                <address t-field="doc.partner_id"
                    t-options='{"widget": "contact", "fields": ["address","name","phone"], "no_marker": True}'/>

                <!-- Line items table -->
                <table class="table table-sm table-bordered mt-3">
                    <thead style="display: table-row-group">
                        <tr>
                            <th class="text-start">Product</th>
                            <th class="text-end">Qty</th>
                            <th class="text-end">Unit Price</th>
                            <th class="text-end">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr t-foreach="doc.line_ids" t-as="line">
                            <td><span t-field="line.name"/></td>
                            <td class="text-end"><span t-field="line.product_uom_qty"/></td>
                            <td class="text-end">
                                <span t-field="line.price_unit"
                                      t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                            </td>
                            <td class="text-end">
                                <span t-field="line.price_subtotal"
                                      t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <!-- Totals (right-aligned table) -->
                <div class="row mt-3">
                    <div class="col-6"/>
                    <div class="col-6">
                        <table class="table table-borderless w-auto ms-auto">
                            <tr>
                                <td class="text-end pe-3"><strong>Subtotal:</strong></td>
                                <td class="text-end">
                                    <t t-out="doc.amount_untaxed"
                                       t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                                </td>
                            </tr>
                            <tr>
                                <td class="text-end pe-3"><strong>Tax:</strong></td>
                                <td class="text-end">
                                    <t t-out="doc.amount_tax"
                                       t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                                </td>
                            </tr>
                            <tr class="fw-bold">
                                <td class="text-end pe-3">Total:</td>
                                <td class="text-end">
                                    <t t-out="doc.amount_total"
                                       t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>

                <!-- Notes (conditional) -->
                <div t-if="doc.note" class="mt-3">
                    <strong>Notes:</strong>
                    <p><t t-out="doc.note"/></p>
                </div>

            </div>
        </t>
    </template>
</odoo>
```

**For simple reports:** Omit the table-borderless totals table and use a simpler totals block inside the line table's `<tfoot>`, or a compact right-aligned div. Do not generate verbose templates for simple list-style reports.

**For complex reports:** Add custom paperformat, header styling, tax breakdown rows, installment tables, signature blocks, page-break controls, and conditional display logic as needed.

### Step 4 — Optional: Custom Paperformat

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="paperformat_my_custom" model="report.paperformat">
            <field name="name">Custom A4 Landscape</field>
            <field name="format">A4</field>
            <field name="orientation">Landscape</field>
            <field name="margin_top">40</field>
            <field name="margin_bottom">25</field>
            <field name="margin_left">7</field>
            <field name="margin_right">7</field>
            <field name="header_line" eval="False"/>
            <field name="header_spacing">40</field>
            <field name="dpi">90</field>
        </record>
    </data>
</odoo>
```

Reference in `ir.actions.report`: `<field name="paperformat_id" ref="my_module.paperformat_my_custom"/>`

---

## Extending Existing Reports

### XPath Patterns for Common Odoo 19 Templates

**CRITICAL:** Always inspect the original template before writing XPath. The element `id` attribute is the most reliable anchor.

| Template to Extend | Target Element | XPath | Common Position |
|---|---|---|---|
| `sale.report_saleorder_document` | Information block | `//div[@id='informations']` | `inside` |
| `sale.report_saleorder_document` | Line items table | `//table[hasclass('o_main_table')]/tbody` | `inside` (before `tr` loop) |
| `sale.report_saleorder_document` | After totals | `//div[hasclass('oe_invoice_total')]` | `before` or `after` |
| `purchase.report_purchaseorder_document` | Information block | `//div[@id='informations']` | `inside` |
| `purchase.report_purchaseorder_document` | Line items | `//table[hasclass('o_main_table')]/tbody` | `inside` |
| `account.report_invoice_document` | Invoice info | `//div[@id='informations']` | `inside` |
| `account.report_invoice_document` | Payment terms | `//div[@id='payment_term']` | `after` |
| `stock.report_picking` | Move lines table | `//table[hasclass('o_main_table')]/tbody` | `inside` |

### Adding a field to an existing sale order report:

```xml
<template id="my_extended_report" inherit_id="sale.report_saleorder_document">
    <xpath expr="//div[@id='informations']" position="inside">
        <div class="col" name="custom_field">
            <strong>Custom Field</strong>
            <div t-field="doc.x_custom_field"
                 t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
        </div>
    </xpath>
</template>
```

### Adding a row after totals in invoice report:

```xml
<template id="custom_invoice_total" inherit_id="account.report_invoice_document">
    <xpath expr="//div[@id='total']" position="after">
        <div class="row mt-2">
            <div class="col-6 text-end"><strong>Balance Due:</strong></div>
            <div class="col-6 text-end">
                <t t-out="o.amount_residual"
                   t-options='{"widget": "monetary", "display_currency": o.currency_id}'/>
            </div>
        </div>
    </xpath>
</template>
```

### Completely replacing a template (primary mode):
```xml
<template id="document_tax_totals" inherit_id="account.document_tax_totals_template" primary="True">
    <!-- Full replacement content -->
</template>
```

---

## Sale Order Line Display Types (Odoo 19)

Sale order lines use `display_type` to control rendering:

```xml
<t t-set="is_note"      t-value="line.display_type == 'line_note'"/>
<t t-set="is_section"   t-value="line.display_type == 'line_section'"/>
<t t-set="is_subsection" t-value="line.display_type == 'line_subsection'"/>
<t t-set="is_combo"     t-value="line.combo_item_id"/>

<t t-if="is_section">   <!-- Bold section header with optional total -->   </t>
<t t-elif="is_note">    <!-- Italic note text -->                       </t>
<t t-elif="is_combo">  <!-- Combo product -->                           </t>
<t t-else="">          <!-- Normal product line -->                    </t>
```

---

## Document Variables Reference

| Variable | Type | Description |
|----------|------|-------------|
| `docs` | recordset | All records being printed |
| `doc` | record | Current record (inside t-foreach loop) |
| `data` | dict | Extra data passed from wizard |
| `user` | record | Current user |
| `time` | module | Python `time` module |
| `context` | dict | Odoo context |
| `company` | record | Current company |
| `lang` | str | Current language code |
| `report_type` | str | `'pdf'` or `'html'` |
| `doc.currency_id` | record | Document currency |

---

## QWeb Directive Reference

| Directive | Description |
|-----------|-------------|
| `t-out="expr"` | Escape and output (modern Odoo 16+, preferred over `t-esc`) |
| `t-esc="expr"` | Escape and output (legacy) |
| `t-raw="expr"` | Raw HTML output (sanitize first!) |
| `t-field="rec.field"` | Smart field rendering with automatic translation |
| `t-if="cond"` | Conditional rendering |
| `t-elif="cond"` / `t-else` | Else branches |
| `t-foreach="items" t-as="i"` | Loop; sets `i_index`, `i_first`, `i_last` |
| `t-call="module.template"` | Include another template |
| `t-set="name" t-value="expr"` | Set variable |
| `t-att-class="expr"` | Dynamic attribute |
| `t-options='{"widget": ...}'` | Widget and formatting options |

---

## Widget Options

```xml
<!-- Monetary amount (ALWAYS specify display_currency) -->
t-options='{"widget": "monetary", "display_currency": doc.currency_id}'

<!-- Date -->
t-options='{"widget": "date"}'
t-options='{"widget": "datetime"}'

<!-- Contact/address (combines multiple fields) -->
t-options='{"widget": "contact", "fields": ["address", "name", "phone", "email"], "no_marker": True}'

<!-- Integer (no decimal places) -->
t-options='{"widget": "integer"}'

<!-- Image/logo -->
t-options='{"widget": "image", "max_width": 150, "max_height": 60}'

<!-- Many2one inline (no link) -->
t-options='{"no_open": True, "no_button": True}'

<!-- Many2one with link -->
t-options='{"no_open": False}'
```

---

## Bootstrap 4 Grid & Typography

```xml
<!-- 2-column row -->
<div class="row mb-3">
    <div class="col-6">Left content</div>
    <div class="col-6">Right content</div>
</div>

<!-- Auto-width columns -->
<div class="row">
    <div class="col">Auto</div>
    <div class="col">Auto</div>
</div>

<!-- Responsive -->
<div class="col-sm-4 col-md-6">Responsive</div>

<!-- Typography -->
<span class="fw-bold">Bold</span>
<span class="fst-italic">Italic</span>
<span class="text-muted small">Muted small</span>
<span class="text-end">Right aligned</span>
<span class="text-nowrap">No wrap</span>

<!-- Spacing -->
<div class="mt-3 mb-2">         <!-- margin -->
<div class="pt-2 pb-3">        <!-- padding -->
<div class="mx-auto">           <!-- centering -->
<div class="ms-auto">           <!-- push right -->
```

---

## Common Patterns

### Company Logo
```xml
<div t-field="doc.company_id.logo"
     t-options='{"widget": "image", "max_width": 150, "max_height": 60}'/>
```

### Signature Block
```xml
<div t-if="doc.signature" class="mt-4">
    <div class="offset-8 text-center">
        <img t-att-src="image_data_uri(doc.signature)"
             style="max-height: 4cm; max-width: 8cm;"/>
    </div>
    <div class="offset-8 text-center">
        <span t-field="doc.signed_by">Signee Name</span>
    </div>
</div>
```

### Conditional Table Row
```xml
<tr t-if="line.discount">
    <td>Discount</td>
    <td class="text-end"><t t-out="line.discount"/>%</td>
</tr>
```

### Page Break Control
```xml
<div style="page-break-before: always;"/>   <!-- page break BEFORE -->
<div style="page-break-after: always;"/>     <!-- page break AFTER -->
<div style="page-break-inside: avoid;">      <!-- don't break INSIDE -->
```

### Tax Totals (shared template)
```xml
<t t-call="sale.document_tax_totals">
    <t t-set="tax_totals" t-value="doc.tax_totals"/>
    <t t-set="currency" t-value="doc.currency_id"/>
</t>
```

---

## Validation Checklist

- [ ] `ir.actions.report` `model` uses technical name (`sale.order` not `Sale Order`)
- [ ] `report_name` uses dotted notation: `<module>.report_<id>`
- [ ] `binding_model_id` uses `ref="model_<underscored_model>"`
- [ ] Entry template `id` matches `report_name`
- [ ] Raw template loops `docs` with `t-foreach="docs" t-as="doc"`
- [ ] Document template sets `doc` with `t-value="doc.with_context(...)"`
- [ ] `t-lang="doc.partner_id.lang"` passed when calling document template
- [ ] Monetary fields use `t-options='{"widget": "monetary", "display_currency": ...}'`
- [ ] Bootstrap 4 classes (no `col-md-*`, no `text-right`, no `font-weight-bold`)
- [ ] `t-out` used for escaped output (not `t-esc` unless legacy)
- [ ] `__manifest__.py` includes all XML files in correct data order
- [ ] `noupdate="1"` on paperformat records (they should not be auto-updated)

---

## Important Notes

**Single vs Multi-Record**: The raw template always loops `docs`. Each `doc` is a single record. The report engine handles merging multiple PDFs into one download.

**Inheritance First**: If a similar report exists, extend it with `inherit_id` + `xpath` rather than rewriting. This preserves existing features (tax totals, section grouping, combo items).

**Wkhtmltopdf Performance**: Keep tables under ~500 rows per `<table>`. Odoo auto-splits large tables. Complex nested tables can cause rendering failures.

**XSS Safety**: Use `t-out` (escaped) for user-provided content. Use `t-raw` only for trusted HTML (e.g., from computed fields that have been sanitized).

**Studio Customization**: Odoo Studio uses `copy_qweb_template()` to copy report templates for per-record customization. Customizations generated by Studio use standard inheritance and are upgrade-safe.
