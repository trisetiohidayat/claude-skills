---
description: Create transient models for wizards and temporary data handling in Odoo 19. Use when user wants to create a wizard model.
---


# Odoo 19 Transient Model Creation

Create transient models for wizards and temporary data in Odoo 19.

## Instructions

1. **Transient Model Pattern:**

```python
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class WizardModel(models.TransientModel):
    _name = 'wizard.model.name'
    _description = 'Wizard Description'

    # Fields
    field_name = fields.Char(string='Field', required=True)

    # Methods
    def action_confirm(self):
        """Process wizard data."""
        # Your logic here
        return {'type': 'ir.actions.act_window_close'}
```

2. **Key Characteristics:**
   - Extends `models.TransientModel` (not `models.Model`)
   - Records automatically deleted after specified time
   - Default retention: _transient_max_hours = 2 hours
   - Used for wizards, temporary data, batch operations
   - Cannot be accessed from regular model relations (use Many2one)

3. **Common Use Cases:**
   - Confirmation dialogs
   - Data entry wizards
   - Export/import wizards
   - Batch processing
   - Report generation wizards
   - Multi-step forms

4. **Wizard Structure:**
   - TransientModel definition
   - Form view XML
   - Action window XML
   - Optional: context passing

## Usage Examples

### Simple Confirmation Wizard

```bash
/model-transient wizard.confirm "Confirmation Wizard" confirmation "reason:Text"
```

Output:
```python
# models/wizard_confirm.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardConfirm(models.TransientModel):
    _name = 'wizard.confirm'
    _description = 'Confirmation Wizard'

    reason = fields.Text(string='Reason', required=True)
    cancel_related = fields.Boolean(string='Cancel Related Records', default=False)

    def action_confirm(self):
        """Process the confirmation."""
        self.ensure_one()

        # Get active record from context
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if not active_id or not active_model:
            raise UserError(_('No active record found.'))

        record = self.env[active_model].browse(active_id)

        # Your logic here
        record.write({
            'state': 'cancelled',
            'cancel_reason': self.reason
        })

        if self.cancel_related:
            record.related_ids.write({'state': 'cancelled'})

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Cancel the wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

View XML:
```xml
<odoo>
    <record id="wizard_confirm_form" model="ir.ui.view">
        <field name="name">wizard.confirm.form</field>
        <field name="model">wizard.confirm</field>
        <field name="arch" type="xml">
            <form string="Confirm Action">
                <sheet>
                    <group>
                        <field name="reason" placeholder="Please provide a reason..."/>
                        <field name="cancel_related"/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

### Data Entry Wizard

```bash
/model-transient wizard.invoice.create "Create Invoice Wizard" data_entry "partner_id:Many2one/res.partner,invoice_date:Date,due_date:Date,journal_id:Many2one/account.journal,line_ids:One2many/wizard.invoice.line"
```

Output:
```python
# models/wizard_invoice_create.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class WizardInvoiceCreate(models.TransientModel):
    _name = 'wizard.invoice.create'
    _description = 'Create Invoice Wizard'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, domain=[('is_company', '=', True)])
    invoice_date = fields.Date(string='Invoice Date', required=True, default=fields.Date.context_today)
    due_date = fields.Date(string='Due Date', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type', '=', 'sale')])
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('wizard.invoice.line', 'wizard_id', string='Invoice Lines')
    notes = fields.Text(string='Notes')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Set default journal and due date based on partner."""
        if self.partner_id:
            if self.partner_id.property_payment_term_id:
                # Calculate due date based on payment term
                self.due_date = fields.Date.context_today(self)

    def action_create_invoice(self):
        """Create invoice from wizard data."""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_('Please add at least one invoice line.'))

        # Validate lines
        for line in self.line_ids:
            if not line.product_id or not line.quantity:
                raise ValidationError(_('All lines must have product and quantity.'))

        # Create invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': self.invoice_date,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [],
        }

        # Create invoice lines
        for line in self.line_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'name': line.description,
            }))

        invoice = self.env['account.move'].create(invoice_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_add_line(self):
        """Add a new line."""
        self.line_ids.create({
            'wizard_id': self.id,
            'product_id': False,
            'quantity': 1.0,
            'price_unit': 0.0,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Invoice'),
            'view_mode': 'form',
            'res_model': 'wizard.invoice.create',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }


class WizardInvoiceLine(models.TransientModel):
    _name = 'wizard.invoice.line'
    _description = 'Invoice Wizard Lines'

    wizard_id = fields.Many2one('wizard.invoice.create', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True, default=0.0)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Fill description and price from product."""
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.list_price

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        """Compute subtotal."""
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
```

### Export Wizard

```bash
/model-transient wizard.product.export "Product Export Wizard" export "date_from:Date,date_to:Date,category_id:Many2one/product.category,include_variants:Boolean,file_format:Selection"
```

Output:
```python
# models/wizard_product_export.py

from odoo import models, fields, api, _
import base64
from io import BytesIO
import csv

class WizardProductExport(models.TransientModel):
    _name = 'wizard.product.export'
    _description = 'Product Export Wizard'

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    category_id = fields.Many2one('product.category', string='Category')
    include_variants = fields.Boolean(string='Include Variants', default=True)
    file_format = fields.Selection([
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ], string='Format', required=True, default='csv')
    export_file = fields.Binary(string='Export File', readonly=True)
    export_filename = fields.Char(string='Filename', readonly=True)

    def action_export(self):
        """Export products to file."""
        self.ensure_one()

        # Build domain
        domain = []
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        if self.category_id:
            domain.append(('categ_id', '=', self.category_id.id))

        # Fetch products
        products = self.env['product.product'].search(domain)

        if not products:
            raise UserError(_('No products found matching the criteria.'))

        # Generate CSV
        output = BytesIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['Name', 'Default Code', 'Category', 'Price', 'Cost', 'Quantity'])

        # Data rows
        for product in products:
            writer.writerow([
                product.name,
                product.default_code or '',
                product.categ_id.name or '',
                product.list_price,
                product.standard_price,
                product.qty_available,
            ])

        # Convert to base64
        file_content = output.getvalue().encode('base64')
        filename = 'products_export_%s.csv' % fields.Date.today().strftime('%Y%m%d')

        # Update wizard
        self.write({
            'export_file': file_content,
            'export_filename': filename
        })

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=wizard.product.export&id=%s&field=export_file&filename=%s' % (self.id, filename),
            'target': 'new',
        }

    def action_cancel(self):
        """Cancel wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

### Batch Process Wizard

```bash
/model-transient wizard.picking.process "Batch Process Pickings" batch_process "picking_ids:Many2many/stock.picking,process_type:Selection,force_availability:Boolean"
```

Output:
```python
# models/wizard_picking_process.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardPickingProcess(models.TransientModel):
    _name = 'wizard.picking.process'
    _description = 'Batch Process Pickings Wizard'

    picking_ids = fields.Many2many('stock.picking', string='Pickings', required=True, domain=[('state', '=', 'assigned')])
    process_type = fields.Selection([
        ('validate', 'Validate'),
        ('check', 'Check Availability'),
        ('print', 'Print'),
        ('cancel', 'Cancel'),
    ], string='Process Type', required=True, default='validate')
    force_availability = fields.Boolean(string='Force Availability', default=False)
    backorder = fields.Boolean(string='Create Backorder', default=True)

    def action_process(self):
        """Process selected pickings."""
        if not self.picking_ids:
            raise UserError(_('Please select at least one picking.'))

        processed = 0
        failed = 0
        messages = []

        for picking in self.picking_ids:
            try:
                if self.process_type == 'validate':
                    picking.with_context(force_availability=self.force_availability).button_validate()
                    processed += 1

                elif self.process_type == 'check':
                    picking.action_assign()
                    processed += 1

                elif self.process_type == 'cancel':
                    picking.action_cancel()
                    processed += 1

                elif self.process_type == 'print':
                    # Print picking operation
                    processed += 1

            except Exception as e:
                failed += 1
                messages.append('%s: %s' % (picking.name, str(e)))

        # Show result
        message = _('Processed: %d\nFailed: %d') % (processed, failed)
        if messages:
            message += '\n\n' + '\n'.join(messages)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success' if failed == 0 else 'warning',
                'sticky': True,
            }
        }
```

### Update Price Wizard

```bash
/model-transient wizard.product.price "Update Product Prices" data_entry "product_ids:Many2many/product.product,price_type:Selection,price_percentage:Float,apply_to_variants:Boolean"
```

Output:
```python
# models/wizard_product_price.py

from odoo import models, fields, api, _

class WizardProductPrice(models.TransientModel):
    _name = 'wizard.product.price'
    _description = 'Update Product Prices Wizard'

    product_ids = fields.Many2many('product.product', string='Products', required=True, domain=[('sale_ok', '=', True)])
    price_type = fields.Selection([
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('set', 'Set Fixed Price'),
    ], string='Price Type', required=True, default='increase')
    price_percentage = fields.Float(string='Percentage / Value', required=True, default=10.0)
    apply_to_variants = fields.Boolean(string='Apply to Variants', default=True)

    def action_update_prices(self):
        """Update prices for selected products."""
        products = self.product_ids
        if self.apply_to_variants:
            # Include all variants
            products = self.env['product.product'].search([('product_tmpl_id', 'in', products.mapped('product_tmpl_id').ids)])

        updated = 0
        for product in products:
            old_price = product.list_price

            if self.price_type == 'increase':
                product.list_price = old_price * (1 + self.price_percentage / 100)
            elif self.price_type == 'decrease':
                product.list_price = old_price * (1 - self.price_percentage / 100)
            elif self.price_type == 'set':
                product.list_price = self.price_percentage

            updated += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Prices updated for %d products.') % updated,
                'type': 'success',
            }
        }
```

## Wizard View Structure

Standard wizard form view:

```xml
<odoo>
    <record id="view_wizard_form" model="ir.ui.view">
        <field name="name">wizard.name.form</field>
        <field name="model">wizard.name</field>
        <field name="arch" type="xml">
            <form string="Wizard Title">
                <sheet>
                    <group>
                        <!-- Your fields here -->
                        <field name="field1"/>
                        <field name="field2"/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="action_wizard" model="ir.actions.act_window">
        <field name="name">Wizard Action</field>
        <field name="res_model">wizard.name</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

## Calling Wizards

### From Button

```python
def action_open_wizard(self):
    """Open wizard from button."""
    return {
        'type': 'ir.actions.act_window',
        'name': _('Wizard Name'),
        'res_model': 'wizard.name',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_field': self.field,
        }
    }
```

### From Context Menu

```xml
<act_window id="action_wizard"
    name="Wizard Action"
    res_model="wizard.name"
    binding_model="base.model"
    binding_views="list"
    view_mode="form"
    target="new"/>
```

## Best Practices

1. **Transient Model Usage:**
   - Only use for temporary data
   - Keep logic simple and focused
   - Don't create complex relations
   - Remember automatic cleanup

2. **Context Handling:**
   - Use context to pass active_id/active_ids
   - Set default values via context
   - Clean up context before passing

3. **Return Values:**
   - Close wizard: `{'type': 'ir.actions.act_window_close'}`
   - Open record: Return action dict
   - Refresh: Return client action

4. **Security:**
   - Check access rights in wizard
   - Validate user permissions
   - Use proper error handling

5. **Performance:**
   - Batch process large datasets
   - Use background processing for long tasks
   - Show progress to user

## Field Types in Wizards

Common wizard field types:

```python
# Basic fields
name = fields.Char(string='Name', required=True)
description = fields.Text(string='Description')
active = fields.Boolean(string='Active', default=True)

# Date fields
date = fields.Date(string='Date', default=fields.Date.context_today)
datetime = fields.Datetime(string='DateTime')

# Relational fields
partner_id = fields.Many2one('res.partner', string='Partner')
product_ids = fields.Many2many('product.product', string='Products')

# Selection fields
type = fields.Selection([
    ('option1', 'Option 1'),
    ('option2', 'Option 2'),
], string='Type')

# File fields
file = fields.Binary(string='File')
filename = fields.Char(string='Filename')
```

## Next Steps

After creating transient model:
- Create form view XML
- Create action window XML
- Add menu item or button
- Test wizard functionality
- Add validation methods
- Handle errors gracefully
