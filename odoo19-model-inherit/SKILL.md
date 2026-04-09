---
description: Extend existing Odoo 19 models by inheriting and adding new fields or methods. Use when user wants to extend an existing model.
---


# Odoo 19 Model Inheritance

Extend existing Odoo models by inheriting and adding or modifying functionality.

## Instructions

1. **Inheritance Types:**

### Classical Inheritance (_inherit only)
Extends existing model without creating new table:

```python
class ModelName(models.Model):
    _inherit = 'existing.model'

    # Add new fields
    new_field = fields.Char(string='New Field')

    # Add new methods
    def new_method(self):
        pass

    # Override existing methods
    def existing_method(self):
        # Call original
        result = super().existing_method()
        # Your code
        return result
```

### Prototype Inheritance (_inherit + _name)
Creates new model copying existing model structure:

```python
class NewModel(models.Model):
    _name = 'new.model'
    _inherit = 'existing.model'

    # Override _description
    _description = 'New Model Description'
```

### Delegation Inheritance
Inherits using many2one relation:

```python
class ChildModel(models.Model):
    _name = 'child.model'
    _inherits = {'parent.model': 'parent_id'}

    parent_id = fields.Many2one('parent.model', required=True, ondelete='cascade')
```

2. **Extension Patterns:**

### Add Fields
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_custom_field = fields.Char(string='Custom Field')
    x_notes = fields.Text(string='Notes')
```

### Add Methods
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_custom_action(self):
        for order in self:
            # Your logic
            pass
        return True
```

### Override Methods (Extend)
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Pre-processing
        for order in self:
            if order.x_custom_field:
                # Your logic
                pass

        # Call original method
        result = super().action_confirm()

        # Post-processing
        for order in self:
            order.message_post(_('Order confirmed with custom logic'))

        return result
```

### Override Methods (Replace)
```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_amount(self):
        # Completely replace original logic
        for order in self:
            # Your new logic
            order.amount_total = sum(line.price_subtotal for line in order.order_line)
```

## Usage Examples

### Add Fields to Res Partner

```bash
/model-inherit res.partner add_field custom "Add mobile and website fields to partner"
```

Output:
```python
# models/res_partner.py

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_mobile = fields.Char(string='Mobile')
    x_website = fields.Char(string='Website')
    x_twitter = fields.Char(string='Twitter')
    x_linkedin = fields.Char(string='LinkedIn')
    x_notes = fields.Text(string='Internal Notes')
```

### Add Field with Default Value

```bash
/model-inherit sale.order add_field mycompany "Add delivery instruction field to sale order"
```

Output:
```python
# models/sale_order.py

from odoo import models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_delivery_instructions = fields.Text(
        string='Delivery Instructions',
        help='Special delivery instructions',
        tracking=True
    )
    x_priority = fields.Selection([
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='normal', tracking=True)
```

### Add Computed Field

```bash
/model-inherit product.product add_field custom "Add margin percentage field"
```

Output:
```python
# models/product.py

from odoo import models, fields, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    x_margin_percentage = fields.Float(
        string='Margin %',
        compute='_compute_x_margin_percentage',
        store=True,
        help='Margin percentage based on list price and cost'
    )

    @api.depends('list_price', 'standard_price')
    def _compute_x_margin_percentage(self):
        for product in self:
            if product.list_price > 0:
                margin = ((product.list_price - product.standard_price) / product.list_price) * 100
                product.x_margin_percentage = margin
            else:
                product.x_margin_percentage = 0.0
```

### Add Many2one Relation

```bash
/model-inherit account.move add_field custom "Add salesperson reference to invoice"
```

Output:
```python
# models/account_move.py

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        tracking=True,
        help='Salesperson responsible for this invoice'
    )
    x_branch_id = fields.Many2one(
        'account.analytic.account',
        string='Branch',
        tracking=True
    )
```

### Add One2many Relation

```bash
/model-inherit sale.order add_field custom "Add custom notes to sale order"
```

Output:
```python
# models/sale_order.py

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_custom_note_ids = fields.One2many(
        'sale.order.note',
        'order_id',
        string='Custom Notes'
    )


class SaleOrderNote(models.Model):
    _name = 'sale.order.note'
    _description = 'Sale Order Notes'

    order_id = fields.Many2one('sale.order', required=True, ondelete='cascade')
    note = fields.Text(string='Note', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
```

### Add Method

```bash
/model-inherit sale.order add_method custom "Add method to send custom SMS"
```

Output:
```python
# models/sale_order.py

from odoo import models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_send_custom_sms(self):
        """Send custom SMS notification for order."""
        for order in self:
            if not order.partner_id.mobile:
                raise UserError(_('Partner must have a mobile number.'))

            message = _('Your order %s has been confirmed.') % order.name

            # Your SMS sending logic here
            # order._send_sms(message, order.partner_id.mobile)

            order.message_post(
                body=_('SMS sent to %s: %s') % (order.partner_id.mobile, message)
            )

        return True
```

### Extend Existing Method

```bash
/model-inherit sale.order modify_method mycompany "Add validation to confirm action"
```

Output:
```python
# models/sale_order.py

from odoo import models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Add custom validation before confirming order."""
        for order in self:
            # Custom validation
            if order.amount_total < 100:
                raise UserError(_('Order total must be at least 100.'))

            if not order.x_salesperson_id:
                raise UserError(_('Please assign a salesperson before confirming.'))

        # Call original method
        result = super().action_confirm()

        # Post-processing
        for order in self:
            order.message_post(_('Order confirmed with custom validations.'))

        return result
```

### Override Create Method

```bash
/model-inherit res.partner modify_method custom "Add sequence number when creating partner"
```

Output:
```python
# models/res_partner.py

from odoo import models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        """Add sequence number when creating new partner."""
        # Generate custom reference
        if 'ref' not in vals or not vals['ref']:
            sequence = self.env['ir.sequence'].next_by_code('res.partner.custom')
            vals['ref'] = sequence or _('New')

        # Call original create
        partner = super().create(vals)

        # Post-processing
        partner.message_post(_('Partner created with custom sequence.'))

        return partner
```

### Override Write Method

```bash
/model-inherit stock.picking modify_method custom "Track when pickings are modified"
```

Output:
```python
# models/stock_picking.py

from odoo import models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        """Track important changes to pickings."""
        # Track state changes
        if 'state' in vals:
            for picking in self:
                if picking.state != vals['state']:
                    picking.message_post(
                        body=_('State changed from %s to %s') % (picking.state, vals['state'])
                    )

        # Call original write
        result = super().write(vals)

        return result
```

### Add Constraint

```bash
/model-inherit sale.order add_constraint custom "Prevent orders below minimum amount"
```

Output:
```python
# models/sale_order.py

from odoo import api, models, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('amount_total')
    def _check_minimum_amount(self):
        """Ensure order total meets minimum requirement."""
        for order in self:
            if order.amount_total > 0 and order.amount_total < 50:
                raise ValidationError(_(
                    'Order total (%.2f) is below minimum amount of 50.00.'
                ) % order.amount_total)
```

### Add Onchange Method

```bash
/model-inherit sale.order add_method custom "Auto-fill delivery instructions based on partner"
```

Output:
```python
# models/sale_order.py

from odoo import api, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id_custom(self):
        """Auto-fill custom fields from partner."""
        if self.partner_id:
            self.x_customer_type = self.partner_id.x_customer_type
            self.x_payment_terms = self.partner_id.property_payment_term_id
            self.x_delivery_instructions = self.partner_id.x_delivery_note
```

### Add Search Method

```bash
/model-inherit product.product add_method custom "Search products by supplier"
```

Output:
```python
# models/product.py

from odoo import models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _search_by_supplier(self, supplier_name, operator='ilike'):
        """Search products by supplier name."""
        suppliers = self.env['res.partner'].search([
            ('name', operator, supplier_name),
            ('supplier_rank', '>', 0)
        ])
        if not suppliers:
            return self.browse()

        return self.search([
            ('seller_ids.name', 'in', suppliers.ids)
        ])
```

### Add Computed Related Fields

```bash
/model-inherit sale.order add_field custom "Add customer age and order count fields"
```

Output:
```python
# models/sale_order.py

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_customer_age = fields.Integer(
        string='Customer Age',
        related='partner_id.x_age',
        readonly=True
    )
    x_customer_order_count = fields.Integer(
        string='Customer Orders',
        related='partner_id.sale_order_count',
        readonly=True
    )
    x_customer_credit_limit = fields.Float(
        string='Credit Limit',
        related='partner_id.credit_limit',
        readonly=True
    )
```

### Add State Field

```bash
/model-inherit account.move add_field custom "Add approval state to invoices"
```

Output:
```python
# models/account_move.py

from odoo import models, fields, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Approval State', default='draft', tracking=True)

    def action_submit_approval(self):
        """Submit for approval."""
        self.write({'x_approval_state': 'submitted'})

    def action_approve(self):
        """Approve the invoice."""
        self.write({'x_approval_state': 'approved'})

    def action_reject(self):
        """Reject the invoice."""
        self.write({'x_approval_state': 'rejected'})
```

## Best Practices

1. **Field Naming:**
   - Always use prefix `x_` for custom fields
   - Use descriptive names: `x_customer_type` not `x_field1`
   - Follow Odoo naming conventions

2. **Method Overriding:**
   - Always call `super()` when extending
   - Preserve original behavior unless replacing entirely
   - Document changes in comments

3. **Performance:**
   - Avoid overriding frequently called methods
   - Use computed fields instead of overrides when possible
   - Consider performance implications

4. **Compatibility:**
   - Test with future Odoo versions
   - Avoid depending on private methods
   - Use public APIs when available

5. **Upgradability:**
   - Document customizations
   - Use separate models when appropriate
   - Consider migration path

## Inheritance Order

When multiple modules inherit same model:

1. Dependencies determine order
2. Last module's methods take precedence
3. Use `super()` to call up the chain

## Model Inheritance in Views

Extend views using XPath:

```xml
<odoo>
    <record id="view_order_form_custom" model="ir.ui.view">
        <field name="name">sale.order.form.custom</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="arch" type="xml">
            <!-- Add field after partner_id -->
            <xpath expr="//field[@name='partner_id']" position="after">
                <field name="x_custom_field"/>
            </xpath>

            <!-- Add button to header -->
            <xpath expr="//header" position="inside">
                <button name="action_custom_method" string="Custom Action" type="object"/>
            </xpath>
        </field>
    </record>
</odoo>
```

## Next Steps

After creating model inheritance:
- Update __init__.py imports
- Create view inheritance XML
- Add security rights if needed
- Test with various scenarios
- Document customizations
- Consider upgrade implications
