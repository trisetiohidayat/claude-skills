---
name: odoo-base-understanding
description: |
  Memahami cara kerja kode Odoo secara mendalam. Gunakan skill ini ketika:
  - User bertanya "bagaimana cara kerja X di Odoo?"
  - User ingin tahu alur kode (code flow) dari suatu proses
  - User bertanya "method X bekerja bagaimana?" atau "apa yang terjadi saat Y?"
  - User ingin memahami relasi antar model
  - User ingin tahu di mana harus override jika ingin ubah behavior
  - User bertanya tentang bisnis logic di modul tertentu
  - User ingin tahu cara kerja workflow atau state machine

  Fokus skill ini adalah MEMAHAMI bagaimana Odoo bekerja.
compatibility: "Odoo 12-19"
---

# Odoo Code Understanding Skill

## Path Resolution
GUNAKAN odoo-path-resolver untuk mendapatkan paths. Contoh:
```python
paths = resolve()
# CE modules
ce_path = paths['addons']['ce']
# EE modules
ee_path = paths['addons']['ee']
# Custom modules
custom_path = paths['addons']['custom'][0]
# Find specific module
module_path = find_module('hr_course')
```

## Overview

Skill ini digunakan untuk memahami cara kerja kode Odoo secara mendalam. Tujuannya adalah menjelaskannya dalam bahasa yang mudah dipahami, sehingga developer bisa:
1. Memahami alur kode (code flow)
2. Mengetahui di mana harus mengubah behavior
3. Melacak eksekusi dari mulai hingga akhir

## Workflow: Langkah Sistematis Memahami Kode Odoo

Ikuti langkah-langkah ini secara berurutan:

```
Step 0: Identifikasi Versi Odoo - Tentukan versi yang ditanyakan user
Step 1: Identifikasi Pertanyaan - Apa yang ingin dipahami user?
Step 2: Cari di Custom Addons - Cek apakah sudah ada override
Step 3: Cari di CE (Community Edition) - Temukan base implementation
Step 4: Cari di EE (Enterprise Edition) - Temukan extensions
Step 5: Trace Code Flow - Ikuti urutan method calls
Step 6: Identifikasi Extension Points - Tentukan where to override
Step 7: Dokumentasikan - Jelaskan dengan bahasa manusia
```

## Step 0: Identifikasi Versi Odoo

**PENTING:** Selalu tentukan versi Odoo yang ditanyakan user sebelum mencari kode.

### A. Cek Otomatis dari CLAUDE.md

1. Baca file `CLAUDE.md` di root proyek
2. Cari section "Odoo Configurations" atau "Odoo Versions"
3. Catat versi yang aktif (biasanya ada di "Odoo 19.0 (Active Development)")

### B. Jika Tidak Jelas, Tanyakan ke User

Jika dari konteks tidak jelas versi mana yang dimaksud, tanyakan:
> "Anda bertanya tentang Odoo versi berapa? 15 atau 19?"

### C. PathBerdasarkan Versi

Gunakan path yang sesuai dengan versi:

| Odoo Version | CE Path | EE Path | Custom Addons |
|--------------|---------|---------|---------------|
| **Odoo 15** | `odoo15.0-roedl/odoo/addons/` | `enterprise-roedl-15.0/enterprise/` | `custom_addons_15/roedl/` |
| **Odoo 19** | `odoo19.0-roedl/odoo/addons/` | `enterprise-roedl-19.0/enterprise/` | `custom_addons_19/roedl/` |

### D. Versi-Specific Notes

- **Odoo 15**: Lebih banyak menggunakan `fields.Selection` dengan list tuple
- **Odoo 17+**: Mulai ada perubahan seperti `compute_sudo` tidak wajib
- **Odoo 19**: Beberapa API sudah berubah, cek `__manifest__.py` untuk dependencies

### E. Versi dari Pertanyaan User

Deteksi dari kata kunci:
- "Odoo 15" / "v15" → Odoo 15
- "Odoo 16" / "v16" → Odoo 16
- "Odoo 17" / "v17" → Odoo 17
- "Odoo 18" / "v18" → Odoo 18
- "Odoo 19" / "v19" → Odoo 19
- "Odoo 16+" / "v16+" → gunakan versi tertinggisecara default

---

## Step 1: Identifikasi Pertanyaan

Pahami apa yang ingin diketahui user:

| Jenis Pertanyaan | Contoh | Yang Dicek |
|------------------|--------|------------|
| **Code Flow** | "Bagaimana alur confirm sale order?" | Urutan method calls |
| **Method Explanation** | "Apa yang dilakukan action_confirm?" | Isi method dan efeknya |
| **Model Relationship** | "sale.order terhubung ke model apa saja?" | Foreign keys, one2many |
| **Extension Point** | "Di mana saya bisa override?" | Inheritance, hooks |
| **Business Logic** | "Bagaimana perhitungan harga di SO?" | Computed fields, formulas |
| **Workflow** | "Bagaimana alur dari RFQ sampai Purchase?" | State transitions |

## Step 2: Cari di Custom Addons (Lebih Dulu!)

**PENTING:** Selalu cek custom addons terlebih dahulu karena mungkin sudah ada override.

### Struktur Custom Addons di Proyek Ini

| Path | Kondisi |
|------|---------|
| `custom_addons_19/roedl/` | Production modules |
| `custom_addons_19_new/roedl/` | New development |
| `custom_addons_19_new2/roedl/` | Experimental |

### Cara Mencari (Gunakan Tool GREP)

```bash
paths = resolve()
custom_path = paths['addons']['custom'][0]

# Cari model di custom addons
Grep: pattern="class.*sale.order" path=custom_path

# Cari method tertentu
Grep: pattern="def action_confirm" path=custom_path

# Cari override suatu method
Grep: pattern="_inherit.*sale.order" path=custom_path
```

## Step 3: Cari di CE (Community Edition)

### Lokasi Kode Odoo CE

| Odoo Version | Path |
|--------------|------|
| Odoo 15 | `odoo15.0-roedl/odoo/addons/` |
| Odoo 19 | `odoo19.0-roedl/odoo/addons/` |

### Gunakan Tool GREP (BUKAN bash grep)

```bash
# Cari model - gunakan Grep tool
paths = resolve()
Grep: path=paths['addons']['ce'] + '/sale/models', pattern="class SaleOrder"

# Cari method tertentu
Grep: path=paths['addons']['ce'] + '/sale/models', pattern="def action_confirm"

# Cari semua method di satu file
Grep: path=paths['addons']['ce'] + '/sale/models', pattern="def .*\(self"

# Cari di semua subfolder
Glob: path=paths['addons']['ce'], pattern="**/sale_order.py"
```

## Step 4: Cari di EE (Enterprise Edition)

### Lokasi Kode Odoo EE

| Odoo Version | Path |
|--------------|------|
| Odoo 15 | `enterprise-roedl-15.0/enterprise/` |
| Odoo 19 | `enterprise-roedl-19.0/enterprise/` |

**Catatan:** EE memperluas CE. Jika ada di EE, biasanya lebih lengkap.

```bash
paths = resolve()
Grep: path=paths['addons']['ee'] + '/sale', pattern="def action_confirm"
```

## Step 5: Trace Code Flow

### A. Trace Dari View ke Model

1. **Cari button di XML:**
```xml
<button name="action_confirm" type="object" string="Confirm"/>
```

2. **Cari method di model:**
```python
def action_confirm(self):
    self.write({'state': 'sale'})
    return True
```

3. **Trace lebih dalam:**
```python
def action_confirm(self):
    # Cek apakah ada before/after hooks
    self._action_launch_stock_rule()  # Trigger stock
    self._send_order_email()  # Send email
```

### B. Trace Computed Field

```python
# Dari field definition
amount_total = fields.Float(compute='_compute_amount', store=True)

# Ke compute method
@api.depends('order_line.price_total')
def _compute_amount(self):
    for order in self:
        order.amount_total = sum(order.order_line.mapped('price_total'))
```

### C. Trace Onchange

```python
# Dari field
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.partner_invoice_id = self.partner_id.address_get(['invoice'])
```

## Step 6: Pahami Relasi Model

### A. Dari Model Definition

```python
class SaleOrder(models.Model):
    # Many2one - satu record
    partner_id = fields.Many2one('res.partner', string='Customer')

    # One2many - banyak record
    order_line = fields.One2many('sale.order.line', 'order_id')

    # Many2many - banyak ke banyak
    tag_ids = fields.Many2many('sale.order.tag')
```

### B. Common Relationships

**Sale Order Flow:**
```
sale.order
  ├── partner_id → res.partner
  ├── order_line → sale.order.line (one2many)
  ├── picking_ids → stock.picking (one2many)
  ├── invoice_ids → account.move (one2many)
  └── payment_ids → account.payment (one2many)
```

**Purchase Order Flow:**
```
purchase.order
  ├── partner_id → res.partner
  ├── order_line → purchase.order.line (one2many)
  ├── picking_ids → stock.picking (one2many)
  └── invoice_ids → account.move (one2many)
```

## Step 7: Identifikasi Extension Points

### A. Override Method

```python
# Cara override:
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Custom logic sebelum memanggil parent
        self._custom_before_confirm()

        # Panggil parent method
        result = super().action_confirm()

        # Custom logic setelah parent
        self._custom_after_confirm()

        return result
```

### B. Extend Computed Field

```python
# Tambah depends
@api.depends('order_line.price_total', 'order_line.discount')
def _compute_amount(self):
    # Sekarang juga memperhitungkan discount
    super()._compute_amount()
```

### C. Extend Onchange

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    # Panggil parent dulu
    super()._onchange_partner()

    # Tambah logic tambahan
    if self.partner_id:
        self.client_order_ref = self.partner_id.ref
```

### D. Track Inheritance Chain

Jika ada multiple inheritance, lacak urutannya:

```python
# Contoh: cek _inherit di model
Grep: path="custom_addons_19/roedl/", pattern="_inherit.*sale.order"
```

## Step 8: Gunakan MCP Odoo untuk Debugging

Jika MCP Odoo tersedia, gunakan untuk eksplorasi langsung:

### A. Buka Odoo Shell via MCP

```python
# Gunakan MCP tool: odoo-rust-mcp-shell atau similar
# Kemudian test langsung:
env['sale.order'].browse(1).action_confirm()
```

### B. Check Metadata

```python
# Lihat field definitions
env['sale.order'].fields_get()

# Lihat model structure
env['sale.order']._fields
```

### C. Trace dengan Logging

```python
def action_confirm(self):
    _logger.info('Starting confirm for orders: %s', self.ids)
    # ... logic
    _logger.info('Confirm completed for orders: %s', self.ids)
```

## Step 9: Jelaskan dengan Bahasa Manusia

### Contoh: Sale Order Confirmation Flow

**Pertanyaan:** "Bagaimana alur confirm sale order?"

**Penjelasan:**

```
1. User klik button "Confirm" di form sale.order
   ↓
2. Button memanggil method action_confirm()
   ↓
3. Di dalam action_confirm():
   - Validasi: Cek apakah ada produk
   - Update state: 'sale' (confirmed)
   - Buat procurement: _action_launch_stock_rule()
   - Buat analytic account jika perlu
   - Trigger email notification: _send_order_email()
   ↓
4. Return ke view dengan reload
```

**Key Points:**
- `action_confirm` adalah entry point
- Ada `_action_*` methods yang di-call di dalamnya
- Bisa override di titik-titik tersebut

## Step 10: Common Code Patterns

### A. Button Actions

```python
# type="object" → memanggil method di model
<button name="action_confirm" type="object"/>

# type="action" → memanggil ir.actions (window action)
<button name="action_view_invoice" type="action"/>
```

**PERHATIAN:** type="action" untuk membuka window/form, type="object" untuk memanggil method.

### B. Workflow States

```python
# State field
state = fields.Selection([
    ('draft', 'Quotation'),
    ('sent', 'Quotation Sent'),
    ('sale', 'Sales Order'),
    ('done', 'Locked'),
    ('cancel', 'Cancelled'),
], string='Status', default='draft')

# State transition via button
def action_confirm(self):
    self.write({'state': 'sale'})
```

### C. Computed Fields dengan Dependencies

```python
# Simple computed
total = fields.Float(compute='_compute_total')

@api.depends('price', 'quantity')
def _compute_total(self):
    for rec in self:
        rec.total = rec.price * rec.quantity

# Computed dengan onchange - akan recalculate saat field2 ini berubah
@api.depends('price', 'quantity', 'tax_id')
def _compute_total(self):
    pass
```

## Quick Reference: Pertanyaan Umum

### Q: Bagaimana cara kerja computed field?
**A:** Field di-compute saat ada perubahan di field yang di-depend. Gunakan `@api.depends` untuk mendefinisikan dependencies.

### Q: Di mana button action_confirm didefinisikan?
**A:** Di model yang sesuai, misalnya `sale.order` punya `action_confirm()` di `sale/models/sale_order.py`

### Q: Bagaimana override onchange?
**A:** Definisikan method dengan nama sama dan panggil `super()`

### Q: Apa bedanya One2many dan Many2many?
**A:** One2many = parent-child (parent punya banyak child, child punya satu parent). Many2many = relasi setara (banyak ke banyak).

### Q: Bagaimana trace alur kode?
**A:** Mulai dari button di XML → method di model → panggil method lain → sampai selesai

### Q: Dimulai dari mana saat ingin memahami kode Odoo?
**A:** Urutan: Custom Addons → CE → EE. Selalu cek custom addons dulu!

---

## Tips Memahami Kode Odoo

1. **Cek versi dulu** - Selalu tentukan versi Odoo (15/19) sebelum mencari kode
2. **Custom first** - Cek custom addons sebelum CE/EE
3. **Mulai dari UI** - Klik button, cek XML, cari method
4. **Follow the flow** - Dari satu method ke method lain
5. **Cari parent** - super() memanggil apa
6. **Cek dependencies** - @api.depends menunjukkan apa yang memicu recalculate
7. **Pahami relasi** - Many2one, One2many, Many2many
8. **Gunakan MCP** - Untuk testing langsung di Odoo shell

---

## Related Skills

- `odoo-debug-tdd`: Untuk debugging masalah
- `odoo-business-process`: Untuk memahami alur bisnis
- `odoo-model-inherit`: Untuk cara inherit/override model
