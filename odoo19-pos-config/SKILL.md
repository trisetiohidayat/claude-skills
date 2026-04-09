---
name: odoo19-pos-config
description: Create POS (Point of Sale) configuration model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat POS session, order, atau extend pos.config.
---

# Odoo 19 POS Config Generator

Skill ini digunakan untuk membuat POS models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Creating POS configurations
- POS order management
- Extending pos.config or pos.order
- POS session handling

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **POS type**: Retail, Restaurant, etc
3. **Fields yang dibutuhkan**: Custom fields

## Extending pos.order

```python
from odoo import models, fields

class PosOrder(models.Model):
    _name = 'pos.order'
    _inherit = 'pos.order'

    # Custom fields
    order_code = fields.Char(string='Order Code')
```

## Complete POS Order Extension

```python
from odoo import models, fields, api, _

class PosOrderExtended(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order', 'mail.thread']
    _description = 'POS Order (Extended)'

    # Order Identification
    order_code = fields.Char(
        string='Order Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Session
    session_id = fields.Many2one(
        'pos.session',
        string='Session',
        required=True,
    )

    # Partner
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )

    # Date
    date_order = fields.Datetime(
        string='Order Date',
        required=True,
        default=fields.Datetime.now,
    )

    # State
    state = fields.Selection([
        ('draft', 'New'),
        ('paid', 'Paid'),
        ('done', 'Posted'),
        ('invoiced', 'Invoiced'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    # Lines
    lines = fields.One2many(
        'pos.order.line',
        'order_id',
        string='Order Lines',
    )

    # Amount
    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount',
        store=True,
    )
    amount_tax = fields.Monetary(
        string='Tax',
        compute='_compute_amount',
        store=True,
    )
    amount_paid = fields.Monetary(string='Paid')
    amount_return = fields.Monetary(string='Returned')

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
    )

    # Payment
    payment_ids = fields.One2many(
        'pos.payment',
        'order_id',
        string='Payments',
    )

    # Custom Fields
    table_id = fields.Many2one(
        'pos.table',
        string='Table',
    )
    customer_count = fields.Integer(string='Guest Count')

    @api.depends('lines.price_subtotal')
    def _compute_amount(self):
        for order in self:
            total = sum(order.lines.mapped('price_subtotal'))
            order.amount_total = total

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('order_code', _('New')) == _('New'):
                vals['order_code'] = self.env['ir.sequence'].next_by_code(
                    'pos.order.code'
                ) or _('New')
        return super().create(vals_list)
```

## POS Order Line

```python
class PosOrderLine(models.Model):
    _name = 'pos.order.line'
    _inherit = 'pos.order.line'

    # Custom fields
    note = fields.Text(string='Note')
    discount_reason = fields.Char(string='Discount Reason')
```

## Best Practices

1. **Inherit dari pos.order** untuk compatibility
2. **Use proper payment handling**
3. **Consider restaurant features** jika needed
4. **Enable tracking** untuk orders

## Dependencies

- `point_of_sale` (built-in)
- `pos_restaurant` (for restaurant)
