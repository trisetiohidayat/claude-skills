---
description: Create complete transient model wizard with form view and action window for data entry in Odoo 19. Use when user wants to create a wizard.
---


# Odoo 19 Wizard Creation

Create complete transient model wizards with form view and action window for data entry, export, or batch processing in Odoo 19.

## Instructions

1. **Parse the wizard requirements:**
   - Extract wizard technical name (e.g., 'wizard.product.export')
   - Parse wizard description
   - Parse field list with types
   - Determine confirm action method name
   - Check if One2many lines are needed

2. **Create the transient model** (`models/wizard_name.py`):

   ```python
   from odoo import models, fields, api, _
   from odoo.exceptions import UserError, ValidationError

   class WizardName(models.TransientModel):
       _name = 'wizard.name'
       _description = 'Wizard Description'

       # Fields from user input
       field_name = fields.FieldType(string='Field Label', required=True)

       # Context fields
       active_id = fields.Integer(string='Active ID', readonly=True)
       active_model = fields.Char(string='Active Model', readonly=True)

       def action_confirm(self):
           """Process wizard data and execute action."""
           self.ensure_one()

           # Get active record from context
           active_id = self.env.context.get('active_id')
           active_model = self.env.context.get('active_model')

           if not active_id or not active_model:
               raise UserError(_('No active record found.'))

           record = self.env[active_model].browse(active_id)

           # Your wizard logic here
           # Example: Create records, update records, export data, etc.

           # Close wizard
           return {'type': 'ir.actions.act_window_close'}

       def action_cancel(self):
           """Cancel the wizard."""
           return {'type': 'ir.actions.act_window_close'}
   ```

3. **Create the form view** (`views/wizard_view.xml`):

   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <odoo>
       <record id="view_wizard_name_form" model="ir.ui.view">
           <field name="name">wizard.name.form</field>
           <field name="model">wizard.name</field>
           <field name="arch" type="xml">
               <form string="Wizard Title">
                   <sheet>
                       <group>
                           <group string="Configuration">
                               <field name="field1" required="1"/>
                               <field name="field2"/>
                           </group>
                           <group string="Options">
                               <field name="field3"/>
                               <field name="field4"/>
                           </group>
                       </group>
                   </sheet>
                   <footer>
                       <button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
                       <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                   </footer>
               </form>
           </field>
       </record>

       <!-- Action Window -->
       <record id="action_wizard_name" model="ir.actions.act_window">
           <field name="name">Wizard Action</field>
           <field name="res_model">wizard.name</field>
           <field name="view_mode">form</field>
           <field name="target">new</field>
           <field name="context">{}</field>
       </record>
   </odoo>
   ```

4. **Key characteristics of transient models:**
   - Extend `models.TransientModel` (NOT `models.Model`)
   - Records automatically deleted after 2 hours (configurable via `_transient_max_hours`)
   - Cannot have normal Many2one relations pointing to them
   - Perfect for wizards, temporary forms, batch operations
   - Superuser access bypasses some security checks

5. **Common field types in wizards:**

   ```python
   # Basic fields
   name = fields.Char(string='Name', required=True)
   description = fields.Text(string='Description')
   notes = fields.Html(string='Notes')

   # Date fields
   date_from = fields.Date(string='From Date', default=fields.Date.context_today)
   date_to = fields.Date(string='To Date')

   # Relational fields
   partner_id = fields.Many2one('res.partner', string='Partner', required=True)
   product_ids = fields.Many2many('product.product', string='Products')
   line_ids = fields.One2many('wizard.line', 'wizard_id', string='Lines')

   # Selection fields
   export_format = fields.Selection([
       ('csv', 'CSV'),
       ('excel', 'Excel'),
       ('pdf', 'PDF'),
   ], string='Format', required=True, default='csv')

   # Boolean fields
   include_details = fields.Boolean(string='Include Details', default=True)

   # File fields
   export_file = fields.Binary(string='File', readonly=True)
   filename = fields.Char(string='Filename', readonly=True)
   ```

6. **Add One2many line support** (if has_lines=true):

   ```python
   # Main wizard
   line_ids = fields.One2many('wizard.name.line', 'wizard_id', string='Lines')

   # Line model
   class WizardNameLine(models.TransientModel):
       _name = 'wizard.name.line'
       _description = 'Wizard Lines'

       wizard_id = fields.Many2one('wizard.name', required=True, ondelete='cascade')
       sequence = fields.Integer(string='Sequence', default=10)
       product_id = fields.Many2one('product.product', string='Product')
       quantity = fields.Float(string='Quantity', default=1.0)
       price_unit = fields.Float(string='Price')
   ```

7. **Context handling**:
   - Use `active_id` for single record operations
   - Use `active_ids` for multi-record operations
   - Use `active_model` to know the source model
   - Pass default values via context dict

8. **Return actions** from wizard methods:
   - Close wizard: `{'type': 'ir.actions.act_window_close'}`
   - Open created record: Return ir.actions.act_window dict
   - Reload view: `{'type': 'ir.actions.act_window_close', 'res_model': 'base'}`
   - Show notification: Use ir.actions.client with display_notification

## Usage Examples

### Simple Data Entry Wizard

```bash
/wizard-new wizard.invoice.create "Create Invoice Wizard" "partner_id:Many2one/res.partner,invoice_date:Date,due_date:Date,journal_id:Many2one/account.journal,notes:Text"
```

**Output - models/wizard_invoice_create.py:**
```python
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
    notes = fields.Text(string='Notes')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Set default journal and payment term based on partner."""
        if self.partner_id:
            # Set default journal based on partner
            if self.partner_id.property_payment_term_id:
                # Calculate due date
                self.due_date = fields.Date.context_today(self)

    def action_confirm(self):
        """Create invoice from wizard data."""
        self.ensure_one()

        # Validate
        if not self.partner_id:
            raise UserError(_('Please select a customer.'))

        # Create invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': self.invoice_date,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [],
            'narration': self.notes,
        }

        invoice = self.env['account.move'].create(invoice_vals)

        # Open the created invoice
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_cancel(self):
        """Cancel wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

**Output - views/wizard_invoice_create_views.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_invoice_create_form" model="ir.ui.view">
        <field name="name">wizard.invoice.create.form</field>
        <field name="model">wizard.invoice.create</field>
        <field name="arch" type="xml">
            <form string="Create Invoice">
                <sheet>
                    <group>
                        <group string="Customer">
                            <field name="partner_id" required="1"/>
                            <field name="journal_id" required="1"/>
                        </group>
                        <group string="Dates">
                            <field name="invoice_date" required="1"/>
                            <field name="due_date" required="1"/>
                        </group>
                    </group>
                    <group string="Notes">
                        <field name="notes" nolabel="1" placeholder="Additional notes..."/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Create Invoice" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_invoice_create" model="ir.actions.act_window">
        <field name="name">Create Invoice</field>
        <field name="res_model">wizard.invoice.create</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

### Export Wizard

```bash
/wizard-new wizard.product.export "Product Export Wizard" "date_from:Date,date_to:Date,category_id:Many2one/product.category,include_variants:Boolean,file_format:Selection"
```

**Output - models/wizard_product_export.py:**
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError
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
        domain = [('sale_ok', '=', True)]
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
        file_content = base64.b64encode(output.getvalue())
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

**Output - views/wizard_product_export_views.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_product_export_form" model="ir.ui.view">
        <field name="name">wizard.product.export.form</field>
        <field name="model">wizard.product.export</field>
        <field name="arch" type="xml">
            <form string="Export Products">
                <sheet>
                    <group>
                        <group string="Filters">
                            <field name="date_from"/>
                            <field name="date_to"/>
                            <field name="category_id"/>
                        </group>
                        <group string="Options">
                            <field name="file_format" required="1"/>
                            <field name="include_variants"/>
                        </group>
                    </group>
                </sheet>
                <footer>
                    <button name="action_export" string="Export" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_product_export" model="ir.actions.act_window">
        <field name="name">Export Products</field>
        <field name="res_model">wizard.product.export</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

### Batch Process Wizard with Lines

```bash
/wizard-new wizard.picking.mass.update "Mass Update Pickings" "picking_type_id:Many2one/stock.picking.type,location_id:Many2one/stock.location,location_dest_id:Many2one/stock.location,note:Text" --has_lines=true
```

**Output - models/wizard_picking_mass_update.py:**
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardPickingMassUpdate(models.TransientModel):
    _name = 'wizard.picking.mass.update'
    _description = 'Mass Update Pickings Wizard'

    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', required=True)
    location_id = fields.Many2one('stock.location', string='Source Location')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
    note = fields.Text(string='Note')
    line_ids = fields.One2many('wizard.picking.mass.update.line', 'wizard_id', string='Pickings')

    @api.model
    def default_get(self, fields_list):
        """Get default values from active records."""
        res = super().default_get(fields_list)

        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_ids and active_model == 'stock.picking':
            pickings = self.env['stock.picking'].browse(active_ids)
            line_vals = []
            for picking in pickings:
                line_vals.append((0, 0, {
                    'picking_id': picking.id,
                    'update_location': True,
                    'update_dest': False,
                }))
            res['line_ids'] = line_vals

        return res

    def action_apply(self):
        """Apply changes to selected pickings."""
        self.ensure_one()

        if not self.line_ids:
            raise UserError(_('No pickings selected.'))

        updated_count = 0
        for line in self.line_ids:
            if line.picking_id.state != 'draft':
                continue

            vals = {}
            if line.update_location and self.location_id:
                vals['location_id'] = self.location_id.id
            if line.update_dest and self.location_dest_id:
                vals['location_dest_id'] = self.location_dest_id.id
            if self.note:
                vals['note'] = self.note

            if vals:
                line.picking_id.write(vals)
                updated_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('%d pickings updated.') % updated_count,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """Cancel wizard."""
        return {'type': 'ir.actions.act_window_close'}


class WizardPickingMassUpdateLine(models.TransientModel):
    _name = 'wizard.picking.mass.update.line'
    _description = 'Mass Update Pickings Wizard Lines'

    wizard_id = fields.Many2one('wizard.picking.mass.update', required=True, ondelete='cascade')
    picking_id = fields.Many2one('stock.picking', string='Picking', required=True, readonly=True)
    picking_state = fields.Selection(related='picking_id.state', string='State', readonly=True)
    update_location = fields.Boolean(string='Update Source', default=True)
    update_dest = fields.Boolean(string='Update Destination')
```

## Calling the Wizard

### From a button in a form view:

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
            'active_id': self.id,
            'active_model': self._name,
        }
    }
```

### From an action in XML:

```xml
<act_window id="action_wizard_name"
    name="Wizard Action"
    res_model="wizard.name"
    binding_model="model.name"
    binding_views="list"
    view_mode="form"
    target="new"/>
```

### From a server action:

```python
# In server action code
action = {
    'type': 'ir.actions.act_window',
    'name': 'Wizard Name',
    'res_model': 'wizard.name',
    'view_mode': 'form',
    'target': 'new',
    'context': {
        'active_id': object.id,
        'active_model': object._name,
    }
}
```

## Best Practices

1. **Transient Model Usage:**
   - Only use for temporary data collection
   - Keep wizard logic simple and focused
   - Don't create complex relations between wizards and regular models
   - Remember records are automatically cleaned up

2. **Context Handling:**
   - Always use context to pass active_id/active_ids
   - Set default values via context dict
   - Clean up context before passing to methods

3. **Return Values:**
   - Close wizard: `{'type': 'ir.actions.act_window_close'}`
   - Open created record: Return action dict with res_model, res_id
   - Show notification: Use ir.actions.client
   - Refresh parent: Return act_window_close with special flags

4. **Security:**
   - Check access rights in wizard methods
   - Validate user permissions
   - Use ensure_one() for single record operations
   - Handle errors gracefully with UserError

5. **Performance:**
   - Batch process large datasets
   - Use background processing for long tasks
   - Show progress to user
   - Consider using _cr.execute() for bulk updates

6. **User Experience:**
   - Provide helpful default values
   - Use onchange methods to auto-fill fields
   - Add validation with clear error messages
   - Use confirm attribute on destructive actions
   - Group related fields logically

## Next Steps

After creating the wizard:
- Add the wizard model to `__init__.py`
- Register views in `__manifest__.py` data files
- Add button or action to trigger wizard
- Test wizard functionality
- Add proper security access rights
- Consider adding translations for user-facing strings
