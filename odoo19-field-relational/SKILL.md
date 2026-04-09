---
name: odoo19-field-relational
description: Create Many2one, One2many, Many2many relational fields untuk Odoo 19. Gunakan skill ini ketika user ingin menambahkan relasi antar model seperti partner_id, line_ids, tag_ids, dll.
---

# Odoo 19 Relational Field Generator

Skill ini digunakan untuk membuat relational fields di Odoo 19 model.

## When to Use

Gunakan skill ini ketika:
- User ingin menambahkan relasi ke model lain (Many2one)
- User ingin menambahkan child records (One2many)
- User ingin menambahkan many-to-many relations
- Membuat field seperti `partner_id`, `order_id`, `line_ids`, `tag_ids`

## Input yang Diperlukan

1. **Target model**: Model yang di-reference, contoh `res.partner`, `account.move`, `project.task`
2. **Field name**: Nama field (snake_case)
3. **Field label**: Label untuk display
4. **Relation field name** (untuk One2many/Many2many): Nama inverse field di target model
5. **Module path**: Path ke custom module

## Many2one Field

### Basic Many2one
```python
partner_id = fields.Many2one(
    'res.partner',
    string='Customer',
)
```

### Many2one dengan Required
```python
user_id = fields.Many2one(
    'res.users',
    string='Responsible',
    required=True,
)
```

### Many2one dengan Default
```python
company_id = fields.Many2one(
    'res.company',
    string='Company',
    default=lambda self: self.env.company,
)
```

### Many2one dengan Domain
```python
parent_id = fields.Many2one(
    'project.task',
    string='Parent Task',
    domain="[('project_id', '=', project_id)]",
)
```

### Many2one dengan Ondelete
```python
country_id = fields.Many2one(
    'res.country',
    string='Country',
    ondelete='restrict',  # prevent deletion if records exist
)
```

## One2many Field

### Basic One2many
```python
order_line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    string='Order Lines',
)
```

### One2many dengan Default
```python
line_ids = fields.One2many(
    'account.move.line',
    'move_id',
    string='Journal Items',
    default=lambda self: self._default_line_ids(),
)
```

### One2many dengan Domain
```python
task_ids = fields.One2many(
    'project.task',
    'project_id',
    string='Tasks',
    domain=[('active', '=', True)],
)
```

## Many2many Field

### Basic Many2many
```python
tag_ids = fields.Many2many(
    'project.tags',
    'project_tag_rel',
    'project_id',
    'tag_id',
    string='Tags',
)
```

### Many2many dengan Shortcut Syntax (Odoo 14+)
```python
# Odoo 14+ syntax - lebih简洁
tag_ids = fields.Many2many(
    'project.tags',
    string='Tags',
)
```

### Many2many dengan Relation Table Customization
```python
category_ids = fields.Many2many(
    'product.category',
    'product_category_rel',
    'product_id',
    'category_id',
    string='Categories',
    domain=[('parent_id', '=', False)],
)
```

## Relational Field Attributes Reference

### Many2one Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `comodel_name` | str | Target model name |
| `string` | str | Field label |
| `domain` | str/list | Domain filter |
| `ondelete` | str | On delete action: 'cascade', 'set null', 'restrict' |
| `required` | bool | Mandatory field |
| `readonly` | bool | Read-only field |
| `default` | callable | Default value |
| `help` | str | Tooltip |
| `tracking` | bool | Enable tracking |
| `index` | bool | Create index |

### One2many/Many2many Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `comodel_name` | str | Target model |
| `inverse_name` | str | Field name in target model (One2many) |
| `relation` | str | Relation table name (optional) |
| `column1` | str | Column for current model (Many2many) |
| `column2` | str | Column for target model (Many2many) |
| `string` | str | Field label |
| `domain` | str/list | Domain filter |
| `limit` | int | Default limit for reads |

## Complete Example: Sale Order with Lines

### Parent Model (sale.order)
```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'

    name = fields.Char(string='Order Reference', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        change_default=True,
        tracking=True,
        domain="[('type', '!=', 'private')]",
    )
    date_order = fields.Datetime(
        string='Order Date',
        required=True,
        default=fields.Datetime.now,
    )
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, default='draft')

    order_line_ids = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
        copy=True,
    )

    tag_ids = fields.Many2many(
        'sale.order.tag',
        'sale_order_tag_rel',
        'order_id',
        'tag_id',
        string='Tags',
    )
```

### Child Model (sale.order.line)
```python
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = 'Sales Order Line'

    order_id = fields.Many2one(
        'sale.order',
        string='Order Reference',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain="[('sale_ok', '=', True)]",
    )
    name = fields.Text(string='Description')
    product_uom_qty = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        required=True,
        default=1.0,
    )
    price_unit = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
    )
```

## Common Patterns

### Partner/Customer Relation
```python
partner_id = fields.Many2one(
    'res.partner',
    string='Customer',
    change_default=True,
    tracking=True,
    domain="[('customer_rank', '>', 0)]",
)
```

### User/Responsible Relation
```python
user_id = fields.Many2one(
    'res.users',
    string='Responsible',
    tracking=True,
    default=lambda self: self.env.user,
)
```

### Company Relation (with rules)
```python
company_id = fields.Many2one(
    'res.company',
    string='Company',
    required=True,
    default=lambda self: self.env.company,
)
```

### Tags (Many2many)
```python
tag_ids = fields.Many2many(
    'account.account.tag',
    'account_account_account_move_line_tag_rel',
    'account_move_line_id',
    'account_account_tag_id',
    string='Tags',
    domain="[('applicability', '=', 'model')]",
)
```

## View Integration

### Many2one in Form View
```xml
<field name="partner_id" widget="res_partner_many2one"
       context="{'res_partner_form_view': True}"/>
<!-- atau lebih simple -->
<field name="partner_id"/>
```

### One2many in Form View
```xml
<field name="order_line_ids">
    <tree editable="bottom">
        <field name="product_id"/>
        <field name="product_uom_qty"/>
        <field name="price_unit"/>
        <field name="price_subtotal"/>
    </tree>
    <form>
        <group>
            <field name="product_id"/>
            <field name="product_uom_qty"/>
        </group>
    </form>
</field>
```

### Many2many in Form View
```xml
<field name="tag_ids" widget="many2many_tags"
       options="{'color_field': 'color'}"/>
```

## Best Practices

1. **Always set inverse_name** untuk One2many agar relasi berfungsi
2. **Gunakan ondelete='cascade'** untuk child records
3. **Gunakan domain** untuk filter options yang relevan
4. **Gunakan tracking=True** untuk fields yang penting
5. **Use readonly untuk computed One2many** yang tidak boleh di-edit langsung

## Troubleshooting

**One2many tidak muncul di view?**
- Pastikan inverse_name benar dan ada di target model
- Cek apakah target model sudah di-import

**Many2many tidak bisa select?**
- Pastikan domain benar dan tidak restrictive
- Cek apakah user punya akses ke target model

**Cascade delete tidak work?**
- Pastikan ondelete='cascade' diset di Many2one side
