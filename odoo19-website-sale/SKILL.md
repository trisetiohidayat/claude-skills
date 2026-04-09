---
name: odoo19-website-sale
description: Create Website Sale (E-commerce) model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat e-commerce features, online shop, atau extend website sale models.
---

# Odoo 19 Website Sale Generator

Skill ini digunakan untuk membuat Website Sale models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Creating e-commerce features
- Online shop customization
- Extending sale.order untuk website
- Shopping cart customization

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Sale type**: B2B, B2C, etc
3. **Fields yang dibutuhkan**: Custom fields

## Extending sale.order for Website

```python
from odoo import models, fields

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    # Custom fields
    website_order_code = fields.Char(string='Website Order Code')
```

## Complete Website Sale Extension

```python
from odoo import models, fields, api, _

class SaleOrderWebsite(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'mail.thread', 'portal.mixin']
    _description = 'Sale Order (Website)'

    # Website Order Identification
    website_order_code = fields.Char(
        string='Website Order Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Partner (Customer)
    partner_id = fields.Many2one(tracking=True)
    partner_invoice_id = fields.Many2one(
        'res.partner',
        string='Invoice Address',
    )
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Delivery Address',
    )

    # Dates
    date_order = fields.Datetime(
        string='Order Date',
        required=True,
        default=fields.Datetime.now,
    )
    commitment_date = fields.Datetime(string='Commitment Date')

    # State
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    # Lines
    order_line_ids = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
    )

    # Amount
    amount_untaxed = fields.Monetary(string='Untaxed Amount')
    amount_tax = fields.Monetary(string='Tax')
    amount_total = fields.Monetary(string='Total', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency')

    # Website Specific
    website_id = fields.Many2one('website', string='Website')
    cart_recovery_email_sent = fields.Boolean(string='Cart Recovery Email Sent')

    # Payment
    transaction_ids = fields.One2many(
        'payment.transaction',
        'sale_order_id',
        string='Transactions',
    )
    payment_acquirer_id = fields.Many2one(
        'payment.acquirer',
        string='Payment Acquirer',
    )

    # Custom Fields
    delivery_message = fields.Text(string='Delivery Message')
    gift_message = fields.Text(string='Gift Message')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('website_order_code', _('New')) == _('New'):
                vals['website_order_code'] = self.env['ir.sequence'].next_by_code(
                    'sale.order.website'
                ) or _('New')
        return super().create(vals_list)
```

## Website Sale Order Line

```python
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    # Custom fields
    customization_note = fields.Text(string='Customization Note')
```

## Best Practices

1. **Inherit dari sale.order** untuk compatibility
2. **Enable portal access** untuk customer tracking
3. **Integrate dengan payment** untuk checkout
4. **Use tracking** untuk order status

## Dependencies

- `website` (built-in)
- `website_sale` (for e-commerce)
- `payment` (for payment processing)
