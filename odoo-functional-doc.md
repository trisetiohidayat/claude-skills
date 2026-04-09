# Odoo Functional Documentation Generator

Generate comprehensive functional documentation for Odoo modules and business processes. Supports multiple languages including Indonesian (Bahasa Indonesia) and English.

## When to use

Use this skill when you need to:
- Create functional documentation for Odoo modules (ark_*, fsd_*, etc.)
- Document cross-module business processes (Order-to-Cash, Purchase-to-Pay, etc.)
- Generate user guides, training materials, or workflows
- Create bilingual documentation (English + Indonesian)

## Usage

```bash
/odoo-doc <module_name_or_process>
/odoo-doc ark_sale
/odoo-doc order-to-cash
/odoo-doc --both
```

## Features

- **Multi-language Support**: Generate documentation in English, Indonesian, or both
- **Module Documentation**: Comprehensive documentation for individual Odoo modules
- **Business Process Documentation**: End-to-end workflow documentation
- **Structured Format**: Consistent document structure with:
  - Plain language explanations
  - Key concepts and terminology
  - Step-by-step workflows
  - Visual diagrams (Mermaid)
  - Cross-module integration points
  - Common tasks and procedures
  - FAQ sections
  - Best practices

## Document Structure

Each generated document includes:

### 1. Overview
- What is this module/process?
- Business goal and purpose
- Who uses it and when

### 2. Key Concepts
- Important terminology
- Business terms explained simply
- Comparison tables

### 3. Complete Workflow
- Step-by-step numbered process
- Document states and transitions
- Cross-module integration points

### 4. Workflow Diagram
- Mermaid diagram showing document flow
- Visual state transitions

### 5. Cross-Module Integration
- Which modules are involved
- Each module's role in the process

### 6. Common Tasks
- Step-by-step procedures
- Practical how-to guides
- Real business scenarios

### 7. FAQ
- Business Q&A (not technical)
- Common issues and solutions
- Edge cases handling

## Language Options

### English (default)
Professional business English with:
- Clear, concise language
- Standard Odoo terminology
- International business standards

### Indonesian (Bahasa Indonesia)
Formal business Indonesian with:
- Local business terminology
- Cultural adaptation
- Familiar terms for local users

**Key terminology adaptations:**
- Invoice → Tagihan/Invoice
- Payment → Pembayaran
- Vendor → Vendor/Pemasok
- Customer → Pelanggan
- Goods Receipt → Penerimaan Barang
- Approval → Persetujuan
- Workflow → Alur Kerja
- Shipment → Pengiriman

## NOK Project Context

**Database:** nok_live_backup5_20251008-2
**Version:** Odoo 17.0
**Custom Modules:** 28 ark_* modules
**Company:** PT NOK Indonesia (Arkana)

### Available Modules

**Accounting & Finance:**
- ark_dpv - Down Payment Voucher
- ark_drv - Direct Receipt Voucher
- ark_account_asset - Asset Management
- ark_account_cashflow - Cashflow Management
- ark_account - Base Accounting
- ark_tax_rounding - Tax Rounding
- And 8 more accounting modules

**Sales:**
- ark_sale - Sales Customization
- ark_sale_report - Sales Reporting
- ark_priceup_invoice - Price Update on Invoice

**Purchase:**
- ark_purchase - Purchase Customization
- ark_purchase_approval - Purchase Approval Workflow
- ark_purchase_dotmatrix - Dotmatrix Printing
- ark_bill_autocomplete_gr - Auto-complete Bills from GR

**Inventory:**
- ark_stock - Stock Customization
- ark_stock_report - Stock Reporting
- ark_shipment - Shipment Management
- ark_inventory_aging - Inventory Aging Reports

## Output Location

Documentation files are generated in:
```
/Users/tri-mac/project/nok/functional-docs mantap/
```

**File naming:**
- Module docs: `<module_name>.md`
- Process docs (EN): `<PROCESS_NAME>_PROCESSES.md`
- Process docs (ID): `<PROCESS_NAME>_PROCESSES_ID.md`
- Summaries: `<PROCESS_NAME>_SUMMARY.md` or `RINGKASAN_<PROCESS_NAME>.md`

## Examples

### Example 1: Module Documentation (English)

```
User: /odoo-doc ark_dpv

Response: Creates ark_dpv.md with:
- What is DPV?
- Key concepts (voucher, approval, etc.)
- Complete DPV workflow
- Integration with ark_account_cashflow
- Common tasks (create DPV, phone allocation, etc.)
- FAQ section
```

### Example 2: Business Process (Both Languages)

```
User: /odoo-doc --both order-to-cash

Response: Creates two files:
1. ORDER_TO_CASH_PROCESSES.md (English)
2. ORDER_TO_CASH_PROCESSES_ID.md (Indonesian)

Both include:
- Order-to-Cash overview
- Sales → Delivery → Invoice → Payment workflow
- Cross-module integration (ark_sale, ark_stock, ark_account, ark_drv)
- Mermaid workflow diagrams
- Common tasks with step-by-step procedures
- FAQ in respective language
```

### Example 3: User Guide (Indonesian)

```
User: /odoo-doc --id panduan-pengguna-ark-dpv

Response: Creates PANDUAN_PENGGUNA_ARK_DPV_ID.md with:
- Panduan lengkap penggunaan ark_dpv
- Langkah demi langkah
- Tips dan trik
- Pertanyaan umum
```

## Best Practices

### Documentation Quality
- ✅ Use plain business language (no technical jargon)
- ✅ Include visual diagrams (Mermaid)
- ✅ Provide step-by-step procedures
- ✅ Add FAQ sections
- ✅ Include cross-module integration points
- ✅ Add best practices and common pitfalls

### Language Considerations
- ✅ Be consistent with terminology
- ✅ Adapt to local business culture
- ✅ Use formal professional language
- ✅ Maintain technical accuracy

### Structure Consistency
- ✅ Same document structure across all docs
- ✅ Numbered steps for workflows
- ✅ Tables for comparisons and integrations
- ✅ Clear sections with headers

## Integration with Existing Documentation

This skill complements:
- **Module-specific docs** (33 existing files in functional-docs/)
- **Business process docs** (5 major workflows documented)
- **README.md** - Main documentation index

## Version Control

Generated documentation should be:
1. Reviewed for accuracy
2. Added to git with proper commit message
3. Updated README.md with links
4. Committed with conventional commit format

**Example commit:**
```
feat(docs): add ark_dpv functional documentation

- Created comprehensive DPV module documentation
- Includes workflow, integration points, and FAQ
- ~5,000 words in English and Indonesian

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Support

For questions about this skill or generated documentation:
1. Check existing documentation in functional-docs/
2. Review module source code in nok-erp/
3. Contact IT/Support team
4. Update documentation as business processes change

---

**Skill Version:** 1.0
**Last Updated:** 2026-02-12
**Project:** NOK Indonesia ERP Documentation
