---
name: odoo19-account-invoice
description: Create Invoice model dan management untuk Odoo 19. Gunakan skill ini ketika user ingin membuat custom invoice module, extend account.move, atau invoice-related features.
---

# Odoo 19 Account Invoice Generator

Skill ini digunakan untuk membuat Invoice-related models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Membuat custom invoice module
- Extending account.move model
- Invoice FacturX integration
- Invoice-related customizations

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Invoice type**: Customer, Vendor, atau both
3. **Fields yang dibutuhkan**: Custom fields
4. **Dependencies**: account, account_payment

## Extending account.move

### Basic Extension
```python
from odoo import models, fields

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    # Custom fields
    invoice_code = fields.Char(string='Invoice Code')
    custom_field = fields.Char(string='Custom Field')
```

## Complete Invoice Extension

```python
from odoo import models, fields, api

class AccountMoveExtended(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread', 'mail.activity.mixin']
    _description = 'Account Move (Extended)'

    # Invoice Identification
    invoice_code = fields.Char(
        string='Invoice Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Invoice Details
    invoice_date = fields.Date(
        string='Invoice Date',
        default=fields.Date.today,
    )
    invoice_date_due = fields.Date(string='Due Date')

    # Partner Relations
    partner_id = fields.Many2one(tracking=True)
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Delivery Address',
    )

    # Financial
    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount',
        store=True,
    )
    amount_residual = fields.Monetary(
        string='Amount Due',
        compute='_compute_amount',
        store=True,
    )
    amount_tax = fields.Monetary(
        string='Tax',
        compute='_compute_amount',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # Custom Fields
    invoice_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
    ], string='Invoice Type', required=True)

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )

    # Invoice Lines
    invoice_line_ids = fields.One2many(
        'account.move.line',
        'move_id',
        string='Invoice Lines',
    )

    # Payment State
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
    ], string='Payment State', compute='_compute_payment_state', store=True)

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.move_id.payment_state')
    def _compute_amount(self):
        for move in self:
            total = sum(move.invoice_line_ids.mapped('price_subtotal'))
            tax = sum(move.invoice_line_ids.mapped('price_subtotal')) - sum(
                line.price_subtotal for line in move.invoice_line_ids.filtered(lambda l: l.tax_ids)
            )
            move.amount_total = total
            move.amount_tax = tax

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.move_id.payment_state')
    def _compute_payment_state(self):
        for move in self:
            if move.payment_state == 'paid':
                continue

            pay_term_lines = move.invoice_line_ids.filtered(
                lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')
            )
            paid_amount = sum(pay_term_lines.mapped('amount_residual'))
            total = sum(pay_term_lines.mapped('debit'))

            if total == paid_amount:
                move.payment_state = 'paid'
            elif paid_amount > 0:
                move.payment_state = 'partial'
            else:
                move.payment_state = 'not_paid'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('invoice_code', _('New')) == _('New'):
                vals['invoice_code'] = self.env['ir.sequence'].next_by_code(
                    'account.move.invoice'
                ) or _('New')
        return super().create(vals_list)
```

## Invoice Line Extension
```python
class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    # Custom fields for invoice line
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        domain="[('project_id', '=', project_id)]",
    )
```

## View Integration

### Form View Extension
```xml
<record id="view_move_form_extended" model="ir.ui.view">
    <field name="name">account.move.form.extended</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account.view_move_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="invoice_code"/>
            <field name="project_id"/>
        </xpath>
    </field>
</record>
```

## Invoice Workflow Actions

```python
def action_post(self):
    """Post the invoice"""
    for move in self:
        if move.state == 'draft':
            move.write({'state': 'posted'})

def action_invoice_paid(self):
    """Mark invoice as paid"""
    for move in self:
        move.write({'payment_state': 'paid'})

def action_invoice_send(self):
    """Send invoice via email"""
    self.ensure_one()
    template = self.env.ref('account.email_template_edi_invoice')
    self.env['mail.template'].browse(template.id).send_mail(self.id)
```

## Best Practices

1. **Inherit dari account.move** untuk compatibility dengan Accounting app
2. **Use proper invoice types** untuk different scenarios
3. **Leverage account_move_line** untuk line-level details
4. **Consider payment integration** dengan account_payment
5. **Enable tracking** untuk important fields

## Dependencies

- `account` (built-in)
- `account_payment` (for payment handling)
- Optional: `account_peppol` (for e-invoicing)
