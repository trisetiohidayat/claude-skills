---
name: odoo19-field-selection
description: Create Selection field dengan options untuk Odoo 19. Gunakan skill ini ketika user ingin menambahkan field dengan pilihan tetap (dropdown) seperti status, priority, type, category, dll.
---

# Odoo 19 Selection Field Generator

Skill ini digunakan untuk membuat Selection field di Odoo 19 model.

## When to Use

Gunakan skill ini ketika:
- User ingin menambahkan dropdown/select field
- Membuat field status, priority, type, category
- Perlu field dengan pilihan tetap yang tidak berubah

## Input yang Diperlukan

Sebelum generate code, kumpulkan informasi:
1. **Model name**: Contoh `res.partner`, `account.move`, custom model
2. **Field name**: Nama field dalam snake_case, contoh `state`, `priority`, `sale_type`
3. **Field label**: Label yang ditampilkan, contoh "State", "Priority", "Sale Type"
4. **Selection options**: List tuple [('key', 'Display Name')]
5. **Required**: Apakah field wajib diisi (default: False)
6. **Default value**: Nilai default jika ada
7. **Module path**: Path ke module custom

## Selection Field Patterns

### Basic Selection
```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
], string='State', default='draft')
```

### Selection dengan Required
```python
priority = fields.Selection([
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
], string='Priority', required=True, default='medium')
```

### Selection dengan Selection Addition (CE/EE Compatible)
```python
# Di Odoo 19, gunakan selection_add untuk extensibility
state = fields.Selection(selection_add=[
    ('pending', 'Pending'),
    ('approved', 'Approved'),
], string='State')
```

### Selection dengan Widget
```python
# Priority widget untuk kanban
priority = fields.Selection([
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Urgent'),
], string='Priority', default='1')
```

## Field Attributes Reference

| Attribute | Type | Description |
|-----------|------|-------------|
| `string` | str | Field label (wajib) |
| `selection` | list | List of (value, label) tuples |
| `selection_add` | list | Add to existing selection (inheritance) |
| `default` | callable/val | Default value |
| `required` | bool | Mandatory field |
| `readonly` | bool | Read-only field |
| `help` | str | Tooltip text |
| `index` | bool | Create database index |
| `tracking` | bool | Enable mail tracking |
| `copy` | bool | Allow copying (default: True untuk Selection) |

## Generation Steps

1. **Baca existing model** untuk lihat struktur field lain
2. **Tentukan selection options** yang tepat untuk use case
3. **Generate field code** dengan attribute yang sesuai
4. **Update view** jika diperlukan (selection field otomatis render dropdown)
5. **Test** dengan menjalankan Odoo dan cek field muncul dengan benar

## Example Output

### Model Field (Python)
```python
# Add to existing model
sale_type = fields.Selection([
    ('retail', 'Retail'),
    ('wholesale', 'Wholesale'),
    ('export', 'Export'),
], string='Sale Type', default='retail',
   help='Type of sale order')
```

### View Update (XML)
```xml
<!-- Selection fields automatically render as dropdown -->
<field name="sale_type"/>
```

## Common Selection Patterns

### Status Field
```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('submit', 'Submitted'),
    ('approve', 'Approved'),
    ('reject', 'Rejected'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
], string='Status', default='draft', tracking=True)
```

### Priority Field (Kanban-ready)
```python
priority = fields.Selection([
    ('0', 'Low'),
    ('1', 'Normal'),
    ('2', 'High'),
    ('3', 'Very High'),
], string='Priority', default='1')
```

### Type Field
```python
lead_type = fields.Selection([
    ('lead', 'Lead'),
    ('opportunity', 'Opportunity'),
], string='Type', required=True, default='lead')
```

## Best Practices

1. **Gunakan consistent naming**: `state`, `status`, `priority`, `type`
2. **第一位 nilai yang meaningful**: Gunakan slug/short code untuk value
3. **Tambahkan help text**: Supaya user paham pilihan yang ada
4. **Gunakan tracking=True**: Untuk field status penting
5. **Gunakan selection_add**: Untuk inheritance daripada override

## Troubleshooting

**Selection tidak muncul di view?**
- Pastikan field dideklarasikan di model
- Refresh view dengan update module

**Inheritance tidak work?**
- Gunakan `selection_add` bukan `selection` untuk menambah option
- Cek apakah parent field menggunakan selection_add juga

**Value tidak tersimpan?**
- Pastikan value sesuai dengan yang didefinisikan di selection
- Cek apakah ada constraint yang membatasi nilai
