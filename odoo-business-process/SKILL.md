---
name: odoo-business-process
description: |
  Memahami dan menganalisis proses bisnis Odoo secara menyeluruh. Gunakan skill ini ketika:
  - User bertanya tentang modul apa saja yang terinstall dan apa fungsinya
  - User ingin memahami alur bisnis (flow) di Odoo - dari quote sampai invoice, dari purchase sampai receipt
  - User bertanya "bagaimana cara kerja X di Odoo?" atau "apa流程 dari proses ini?"
  - User butuh debugging dengan memahami relasi antar modul dan model
  - User ingin tahu model apa yang terlibat dalam proses bisnis tertentu
  - User bertanya tentang customization point di modul tertentu
  - User ingin dokumentasi bisnis proses dari database yang sedang aktif

  Skill ini wajib digunakan sebelum memberikan jawaban tentang cara kerja Odoo, karena harus tahu dulu modul apa yang terinstall dan bagaimana konfigurasi-nya.
---

# Odoo Business Process Analysis Skill

## Overview

Skill ini digunakan untuk memahami secara menyeluruh proses bisnis Odoo berdasarkan:
1. **Modul yang terinstall** - Apa saja modul di database aktif
2. **Relasi antar modul** - Dependency dan integrasi
3. **Model yang digunakan** - Primary models dalam proses bisnis
4. **Konfigurasi** - Settings dan customization

Tujuan utama: Memberikan jawaban yang akurat tentang cara kerja Odoo berdasarkan state sebenarnya dari database, bukan asumsi.

---

## Step 1: Identify Active Context

### A. Cek Instance dan Database

Selalu tentukan dulu instance Odoo yang aktif:

```python
# Gunakan MCP untuk cek context
# Default: nok-odoo-local untuk development

# Cek installed modules
mcp__odoo-nok__odoo_search_read(
    instance="nok-odoo-local",
    model="ir.module.module",
    domain=[["state", "=", "installed"]],
    fields=["name", "author", "application", "latest_version"],
    limit=200
)
```

### B. Kategorikan Modul

分组 modul yang terinstall berdasarkan kategori:

| Kategori | Contoh Modul | Fungsi |
|----------|--------------|--------|
| **Accounting** | account, account_payment, ark_account | Keuangan & akuntansi |
| **Sales** | sale, sale_stock, ark_sale | Penjualan & quote |
| **Purchase** | purchase, purchase_stock, ark_purchase | Pembelian & PO |
| **Inventory** | stock, stock_account, ark_stock | Gudang & persediaan |
| **Manufacturing** | mrp, mrp_workorder | Produksi |
| **Custom (ark_*)** | ark_dpv, ark_drv, ark_shipment | Kustomisasi NOK |
| **Localization** | l10n_id, l10n_id_efaktur | Lokalisasi Indonesia |

---

## Step 2: Analyze Business Process

### A. Identifikasi Proses yang Ditanyakan

Tanya user atau identifikasi dari pertanyaan:

1. **Sales Cycle**: Quote → Sales Order → Delivery → Invoice → Payment
2. **Purchase Cycle**: RFQ → Purchase Order → Receipt → Bill → Payment
3. **Inventory Flow**: Receipt → Internal Transfer → Delivery
4. **Manufacturing**: BOM → Production → Finished Goods
5. **Custom Processes**: DPV (Down Payment), DRV (Debit Return), Shipment

### B. Trace Model yang Terlibat

Untuk setiap proses, identifikasi model utama:

**Sales Process:**
- `sale.order` - Sales order
- `sale.order.line` - Order lines
- `account.move` (out_invoice) - Customer invoice
- `stock.picking` - Delivery
- `account.payment` - Payment

**Purchase Process:**
- `purchase.order` - Purchase order
- `purchase.order.line` - PO lines
- `account.move` (in_invoice) - Vendor bill
- `stock.picking` - Receipt
- `account.payment` - Payment

**Custom Processes (NOK):**
- `ark.dpv` - Down Payment Voucher
- `ark.drv` - Debit Return Voucher
- `ark.shipment` - Shipment management

### C. Gunakan MCP untuk Detail

```python
# Get model metadata untuk understand fields
mcp__odoo-nok__odoo_get_model_metadata(
    instance="nok-odoo-local",
    model="sale.order"
)

# Search sample records untuk understand data
mcp__odoo-nok__odoo_search_read(
    instance="nok-odoo-local",
    model="sale.order",
    domain=[["state", "=", "sale"]],
    fields=["name", "partner_id", "date_order", "amount_total"],
    limit=5
)

# Get module dependencies
mcp__odoo-nok__odoo_read(
    instance="nok-odoo-local",
    model="ir.module.module",
    ids=[module_id],
    fields=["name", "depends", "description"]
)
```

---

## Step 3: Understand Custom Modules

### A. Cek Custom Modules (ark_*)

Modul kustom NOK yang tersedia:

```python
# List semua ark modules yang terinstall
mcp__odoo-nok__odoo_search_read(
    instance="nok-odoo-local",
    model="ir.module.module",
    domain=[["name", "=like", "ark%"], ["state", "=", "installed"]],
    fields=["name", "version", "depends"]
)
```

### B. Understand Custom Models

Untuk setiap modul custom, identifikasi:

1. **Primary Model**: Model utama yang dibuat
2. **Extended Models**: Model standard yang di-extend
3. **Custom Fields**: Field tambahan yang ditambahkan
4. **Business Logic**: Method dan computed fields

```python
# Cari custom models di modul tertentu
# Dengan membaca file models/ di module directory
# Contoh: ark_dpv/models/ark_dpv.py
```

---

## Step 4: Analyze Relationships

### A. Model Relationships

Identifikasi bagaimana model saling terhubung:

```
sale.order
    ├── partner_id → res.partner
    ├── order_line → sale.order.line (one2many)
    ├── picking_ids → stock.picking (one2many)
    ├── invoice_ids → account.move (one2many)
    └── payment_ids → account.payment (one2many)
```

### B. Module Dependencies

Pahami bagaimana modul зависит satu sama lain:

```
ark_sale
    ├── depends: [base, sale, ark_base]
    ├── extends: sale.order, sale.order.line
    └── provides: Custom fields untuk sales

ark_account_cashflow
    ├── depends: [base, account, ark_base]
    ├── extends: account.move, account.payment
    └── provides: Cashflow planning
```

---

## Step 5: Provide Comprehensive Answer

### Output Format

Berdasarkan analisis di atas, berikan jawaban dengan format:

```
## [Proses/Business Process yang Ditanyakan]

### Overview
[Penjelasan umum tentang proses]

### Modul yang Terlibat
| Modul | Fungsi |
|-------|--------|
| [nama] | [penjelasan] |

### Model yang Digunakan
| Model | Peran |
|-------|-------|
| [nama] | [penjelasan] |

### Alur/Flow
1. [Langkah 1]
2. [Langkah 2]
3. [Langkah 3]

### Customization Point
[Di mana kustomisasi dilakukan, jika ada]

### Debugging Tips
[Jika ada masalah umum di proses ini]
```

---

## Common Business Process Queries

### 1. Sales Process
**Pertanyaan**: "Bagaimana alur sales di Odoo?"

**Analisis yang diperlukan:**
1. Cek modul sales yang terinstall
2. Identifikasi model: sale.order, sale.order.line
3. Cek custom fields dari ark_sale
4. Trace flow: Quote → Sale Order → Delivery → Invoice

### 2. Purchase Process
**Pertanyaan**: "Bagaimana alur purchase?"

**Analisis yang diperlukan:**
1. Cek modul purchase yang terinstall
2. Identifikasi model: purchase.order, purchase.order.line
3. Cek custom fields dari ark_purchase
4. Trace flow: RFQ → PO → Receipt → Bill

### 3. Down Payment (DPV)
**Pertanyaan**: "Bagaimana cara kerja DPV?"

**Analisis yang diperlukan:**
1. Cek modul ark_dpv terinstall
2. Identifikasi model: ark.dpv
3. Pahami relasi dengan account.move
4. Trace flow: DPV Creation → Invoice → Payment

### 4. Shipment
**Pertanyaan**: "Bagaimana proses shipment?"

**Analisis yang diperlukan:**
1. Cek modul ark_shipment terinstall
2. Identifikasi model: ark.shipment
3. Pahami relasi dengan stock.picking
4. Trace flow: Order → Shipment → Delivery

---

## Quick Reference

### MCP Queries yang Sering Digunakan

```python
# 1. Get all installed modules
mcp__odoo-nok__odoo_search_read(
    instance="nok-odoo-local",
    model="ir.module.module",
    domain=[["state", "=", "installed"]],
    fields=["name", "author", "application"]
)

# 2. Get module details
mcp__odoo-nok__odoo_get_model_metadata(
    instance="nok-odoo-local",
    model="ir.module.module"
)

# 3. Get model fields
mcp__odoo-nok__odoo_get_model_metadata(
    instance="nok-odoo-local",
    model="sale.order"
)

# 4. Search sample data
mcp__odoo-nok__odoo_search_read(
    instance="nok-odoo-local",
    model="sale.order",
    domain=[],
    fields=["name", "state", "partner_id"],
    limit=5
)

# 5. Count records
mcp__odoo-nok__odoo_count(
    instance="nok-odoo-local",
    model="sale.order",
    domain=[["state", "=", "sale"]]
)
```

---

## Important Notes

1. **Selalu cek dulu** apa yang terinstall sebelum menjawab
2. **Tidak mengasumsikan** - Jangan assume fitur ada kalau belum cek
3. **Verify dengan MCP** - Gunakan MCP untuk confirm state database
4. **Sebutkan sumber** - "Berdasarkan modul yang terinstall..."
5. **Tanya konteks** - Jika kurang jelas, minta klarifikasi

---

## Prerequisites

Pastikan:
- MCP instance tersedia (`nok-odoo-local`)
- Database aktif sudah diidentifikasi
- Modul yang ditanyakan sudah terinstall
