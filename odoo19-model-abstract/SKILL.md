---
name: odoo19-model-abstract
description: Create abstract model (mixin) untuk Odoo 19. Gunakan skill ini ketika user ingin membuat reusable base model yang bisa di-inherit oleh model lain, seperti fields dan methods yang sering dipakai ulang.
---

# Odoo 19 Abstract Model Generator

Skill ini digunakan untuk membuat abstract model (mixin) di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Ingin membuat reusable fields yang bisa digunakan di banyak model
- Ingin membuat common methods yang bisa di-inherit
- Ingin menambahkan functionality ke multiple models
- Membuat mixin seperti `mail.thread`, `mail.activity.mixin`

## Abstract vs Regular Model

| Aspect | Abstract Model | Regular Model |
|--------|---------------|---------------|
| `_abstract` | `True` | `False` (default) |
| Create table | No | Yes |
| Can create records | No | Yes |
| Can be inherited | Yes | Yes |
| Use case | Reusable mixins | Main data models |

## Basic Abstract Model

```python
from odoo import models, fields, api

class AbstractSaleMixin(models.AbstractModel):
    _name = 'sale.abstract.mixin'
    _description = 'Sale Abstract Mixin'

    # Common fields untuk sale documents
    name = fields.Char(string='Document Number', required=True)
    date_order = fields.Datetime(
        string='Order Date',
        required=True,
        default=fields.Datetime.now,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', readonly=True)

    # Common methods
    def action_confirm(self):
        for record in self:
            record.write({'state': 'confirm'})

    def action_done(self):
        for record in self:
            record.write({'state': 'done'})

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancel'})
```

## Inheriting Abstract Model

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'
    _inherit = ['sale.abstract.mixin']  # Inherit abstract mixin

    # Add order-specific fields
    order_line_ids = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
    )
    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount_total',
    )

    @api.depends('order_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(
                line.price_subtotal for line in order.order_line_ids
            )
```

## Common Abstract Mixin Patterns

### With Mail Thread
```python
class AbstractDocument(models.AbstractModel):
    _name = 'document.abstract'
    _description = 'Document Abstract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    date_deadline = fields.Date(string='Deadline', tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
    ], default='1', tracking=True)
```

### With Active Field
```python
class AbstractActive(models.AbstractModel):
    _name = 'abstract.active'
    _description = 'Abstract Active Record'
    _inherit = ['portal.mixin']

    active = fields.Boolean(
        string='Active',
        default=True,
        copy=False,
    )
    active_archived = fields.Boolean(
        string='Active Archived',
        compute='_compute_active_archived',
        store=True,
    )

    @api.depends('active')
    def _compute_active_archived(self):
        for record in self:
            record.active_archived = not record.active
```

### With Company Rule
```python
class AbstractCompany(models.AbstractModel):
    _name = 'abstract.company'
    _description = 'Abstract Company'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    # Automatic ACL based on company
    def _compute_company_display_name(self):
        for record in self:
            record.company_display_name = record.company_id.display_name
```

### With Sequence
```python
class AbstractSequence(models.AbstractModel):
    _name = 'abstract.sequence'
    _description = 'Abstract Sequence'

    name = fields.Char(
        string='Document Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    self._sequence_code or 'default'
                ) or _('New')
        return super().create(vals_list)

    @property
    def _sequence_code(self):
        # Override in child class
        return None
```

## Creating Concrete Model from Abstract

```python
# Concrete model that inherits abstract mixin
class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Project Task'
    _inherit = [
        'document.abstract',      # Mail thread + fields
        'abstract.sequence',      # Sequence numbering
        'abstract.company',       # Company field
    ]

    # Task-specific fields
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
    )
    planned_hours = fields.Float(string='Planned Hours')
    progress = fields.Float(string='Progress', default=0.0)

    @property
    def _sequence_code(self):
        return 'project.task'
```

## Advanced: Multiple Inheritance

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'
    _inherit = [
        'sale.abstract.mixin',    # Sale fields & methods
        'mail.thread',            # Chatter
        'mail.activity.mixin',    # Activities
        'portal.mixin',           # Portal access
    ]
```

## Best Practices

1. **Use meaningful names**: `sale.abstract.mixin`, `document.abstract`
2. **Keep it simple**: Only add fields/methods that are truly reusable
3. **Document the mixin**: Add clear docstrings
4. **Use `_abstract = True`**: Always set explicitly
5. **Consider dependencies**: Some mixins require others (e.g., `mail.thread`)

## Common Odoo Built-in Mixins

| Mixin | Purpose |
|-------|---------|
| `mail.thread` | Chatter, tracking, messages |
| `mail.activity.mixin` | Activity scheduling |
| `portal.mixin` | Portal access control |
| `mail.thread.blacklist` | Email blacklist |
| `mail.thread.cc` | CC field |
| `product.forecast` | Sales forecasting |
| `account.tax.mixin` | Tax computation |

## Error Handling

**"Invalid field 'xxx' on model 'xxx'"**
- Field tidak ada di abstract mixin
- Cek apakah abstract mixin di-inherit dengan benar

**"Cannot create record of transient model"**
- Salah menggunakan `models.TransientModel` untuk abstract
- Gunakan `models.AbstractModel`

**"The model does not inherit from mail.thread"**
- Inherit `mail.thread` bukan hanya mix fields
- Cek `_inherit` list
