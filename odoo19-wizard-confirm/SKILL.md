---
description: Create simple confirmation wizard with Yes/No action handling for critical operations in Odoo 19. Use when user wants to create a confirmation wizard.
---


# Odoo 19 Confirmation Wizard Creation

Create simple confirmation wizards with Yes/No action handling for critical operations like delete, cancel, or irreversible actions in Odoo 19.

## Instructions

1. **Parse the confirmation wizard requirements:**
   - Extract wizard technical name (e.g., 'wizard.cancel.confirm')
   - Parse wizard title for dialog header
   - Parse confirmation message
   - Check if reason field is required
   - Extract optional warning text

2. **Create the confirmation wizard model** (`models/wizard_name.py`):

   ```python
   from odoo import models, fields, api, _
   from odoo.exceptions import UserError

   class WizardConfirm(models.TransientModel):
       _name = 'wizard.confirm'
       _description = 'Confirmation Wizard'

       # Context fields
       active_id = fields.Integer(string='Active ID', readonly=True)
       active_model = fields.Char(string='Active Model', readonly=True)

       # Optional reason field
       reason = fields.Text(string='Reason', required=False)

       def action_confirm(self):
           """Execute the confirmed action."""
           self.ensure_one()

           # Get active record from context
           active_id = self.env.context.get('active_id')
           active_model = self.env.context.get('active_model')

           if not active_id or not active_model:
               raise UserError(_('No active record found.'))

           record = self.env[active_model].browse(active_id)

           # Your action logic here
           # Example: record.action_cancel()

           return {'type': 'ir.actions.act_window_close'}

       def action_cancel(self):
           """Cancel the wizard."""
           return {'type': 'ir.actions.act_window_close'}
   ```

3. **Create the confirmation wizard view** (`views/wizard_view.xml`):

   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <odoo>
       <record id="view_wizard_confirm_form" model="ir.ui.view">
           <field name="name">wizard.confirm.form</field>
           <field name="model">wizard.confirm</field>
           <field name="arch" type="xml">
               <form string="Confirmation">
                   <sheet>
                       <div class="alert alert-warning" role="alert">
                           <strong>Warning!</strong> This action cannot be undone.
                       </div>

                       <p class="text-muted">
                           Are you sure you want to proceed?
                       </p>

                       <group>
                           <field name="reason" nolabel="1" placeholder="Please provide a reason..."
                                  options="{'rows': 3}"/>
                       </group>
                   </sheet>
                   <footer>
                       <button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
                       <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                   </footer>
               </form>
           </field>
       </record>

       <record id="action_wizard_confirm" model="ir.actions.act_window">
           <field name="name">Confirm Action</field>
           <field name="res_model">wizard.confirm</field>
           <field name="view_mode">form</field>
           <field name="target">new</field>
       </record>
   </odoo>
   ```

4. **Key characteristics of confirmation wizards:**
   - Minimal fields (usually just reason)
   - Clear, prominent warning message
   - Simple Yes/No buttons
   - Cannot be undone warning
   - Quick to complete

5. **Standard confirmation patterns:**

   ```python
   # Pattern 1: Cancel confirmation
   def action_cancel(self):
       """Cancel with confirmation."""
       return {
           'type': 'ir.actions.act_window',
           'name': _('Cancel Confirmation'),
           'res_model': 'wizard.cancel.confirm',
           'view_mode': 'form',
           'target': 'new',
           'context': {
               'active_id': self.id,
               'active_model': self._name,
           }
       }

   # Pattern 2: Delete confirmation
   def action_delete(self):
       """Delete with confirmation."""
       return {
           'type': 'ir.actions.act_window',
           'name': _('Delete Confirmation'),
           'res_model': 'wizard.delete.confirm',
           'view_mode': 'form',
           'target': 'new',
           'context': {
               'active_id': self.id,
               'active_model': self._name,
           }
       }

   # Pattern 3: Batch action confirmation
   def action_batch_process(self):
       """Batch process with confirmation."""
       return {
           'type': 'ir.actions.act_window',
           'name': _('Batch Process Confirmation'),
           'res_model': 'wizard.batch.confirm',
           'view_mode': 'form',
           'target': 'new',
           'context': {
               'active_ids': self.ids,
               'active_model': self._name,
           }
       }
   ```

6. **Message templates for common actions:**

   - **Cancel:** "Are you sure you want to cancel this record? This action cannot be undone."
   - **Delete:** "Are you sure you want to delete this record? This action is irreversible."
   - **Reset:** "Are you sure you want to reset this record? All changes will be lost."
   - **Approve:** "Are you sure you want to approve this record? It will be sent to the next stage."
   - **Reject:** "Are you sure you want to reject this record? Please provide a reason."
   - **Archive:** "Are you sure you want to archive this record? It will be hidden from views."

7. **Styling the wizard:**
   - Use `alert-warning` for destructive actions
   - Use `alert-info` for informational confirmations
   - Use `alert-danger` for critical deletions
   - Make messages clear and concise
   - Use icons when appropriate

8. **Handling multiple records:**
   - Use `active_ids` instead of `active_id`
   - Show count of affected records
   - Process all records in batch
   - Show success/failure count

9. **Return actions from wizard:**
   - Close and refresh: `{'type': 'ir.actions.act_window_close'}`
   - Show notification: Use ir.actions.client with display_notification
   - Reload view: Return special dict
   - Open next wizard: Return action dict

## Usage Examples

### Simple Cancel Confirmation (No Reason Required)

```bash
/wizard-confirm wizard.order.cancel "Cancel Order" "Are you sure you want to cancel this order? This action cannot be undone."
```

**Output - models/wizard_order_cancel.py:**
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardOrderCancel(models.TransientModel):
    _name = 'wizard.order.cancel'
    _description = 'Order Cancel Confirmation'

    def action_confirm(self):
        """Cancel the order."""
        self.ensure_one()

        # Get active record from context
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if not active_id or not active_model:
            raise UserError(_('No active record found.'))

        order = self.env[active_model].browse(active_id)

        # Check if order can be cancelled
        if order.state == 'done':
            raise UserError(_('Cannot cancel a completed order.'))

        # Cancel the order
        order.action_cancel()

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Cancel the wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

**Output - views/wizard_order_cancel_views.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_order_cancel_form" model="ir.ui.view">
        <field name="name">wizard.order.cancel.form</field>
        <field name="model">wizard.order.cancel</field>
        <field name="arch" type="xml">
            <form string="Cancel Order">
                <sheet>
                    <div class="alert alert-warning" role="alert">
                        <strong>Warning!</strong> This action cannot be undone.
                    </div>

                    <p class="text-muted">
                        Are you sure you want to cancel this order? This action cannot be undone.
                    </p>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Yes, Cancel" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="No" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_order_cancel" model="ir.actions.act_window">
        <field name="name">Cancel Order</field>
        <field name="res_model">wizard.order.cancel</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

### Delete Confirmation with Reason

```bash
/wizard-confirm wizard.partner.delete "Delete Partner" "Are you sure you want to delete this partner? This action is irreversible." --require_reason=true --warning_text="All related documents will also be deleted."
```

**Output - models/wizard_partner_delete.py:**
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardPartnerDelete(models.TransientModel):
    _name = 'wizard.partner.delete'
    _description = 'Partner Delete Confirmation'

    reason = fields.Text(string='Reason', required=True)

    def action_confirm(self):
        """Delete the partner."""
        self.ensure_one()

        # Validate reason
        if not self.reason:
            raise UserError(_('Please provide a reason for deletion.'))

        # Get active record from context
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if not active_id or not active_model:
            raise UserError(_('No active record found.'))

        partner = self.env[active_model].browse(active_id)

        # Check if partner can be deleted
        if partner.child_ids:
            raise UserError(_('Cannot delete a partner with contacts.'))

        # Add deletion reason to chatter
        partner.message_post(
            body=_('Partner deleted. Reason: %s') % self.reason
        )

        # Delete the partner
        partner.unlink()

        return {
            'type': 'ir.actions.act_window_close',
            'infos': {'deleted': True}
        }

    def action_cancel(self):
        """Cancel the wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

**Output - views/wizard_partner_delete_views.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_partner_delete_form" model="ir.ui.view">
        <field name="name">wizard.partner.delete.form</field>
        <field name="model">wizard.partner.delete</field>
        <field name="arch" type="xml">
            <form string="Delete Partner">
                <sheet>
                    <div class="alert alert-danger" role="alert">
                        <strong>Danger!</strong> All related documents will also be deleted.
                    </div>

                    <p class="text-muted">
                        Are you sure you want to delete this partner? This action is irreversible.
                    </p>

                    <group>
                        <label for="reason" string="Reason"/>
                        <field name="reason" nolabel="1" required="1"
                               placeholder="Please provide a reason for deletion..."
                               options="{'rows': 4}"/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Yes, Delete" type="object" class="btn-danger"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_partner_delete" model="ir.actions.act_window">
        <field name="name">Delete Partner</field>
        <field name="res_model">wizard.partner.delete</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

### Batch Cancel Confirmation

```bash
/wizard-confirm wizard.invoice.cancel "Cancel Invoices" "Are you sure you want to cancel these invoices?" --require_reason=false
```

**Output - models/wizard_invoice_cancel.py:**
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardInvoiceCancel(models.TransientModel):
    _name = 'wizard.invoice.cancel'
    _description = 'Invoice Cancel Confirmation'

    reason = fields.Text(string='Reason')

    @api.model
    def default_get(self, fields_list):
        """Get default values from active records."""
        res = super().default_get(fields_list)

        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_ids and active_model == 'account.move':
            invoices = self.env['account.move'].browse(active_ids)
            res['invoice_count'] = len(invoices)
            res['invoice_names'] = ', '.join(invoices.mapped('name'))

        return res

    invoice_count = fields.Integer(string='Invoice Count', readonly=True)
    invoice_names = fields.Char(string='Invoices', readonly=True)

    def action_confirm(self):
        """Cancel the invoices."""
        self.ensure_one()

        # Get active records from context
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if not active_ids or not active_model:
            raise UserError(_('No active records found.'))

        invoices = self.env[active_model].browse(active_ids)

        # Cancel invoices
        cancelled_count = 0
        for invoice in invoices:
            if invoice.state == 'draft':
                invoice.button_cancel()
                cancelled_count += 1

                # Add reason to chatter
                if self.reason:
                    invoice.message_post(
                        body=_('Cancellation reason: %s') % self.reason
                    )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('%d invoices cancelled.') % cancelled_count,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """Cancel the wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

**Output - views/wizard_invoice_cancel_views.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_invoice_cancel_form" model="ir.ui.view">
        <field name="name">wizard.invoice.cancel.form</field>
        <field name="model">wizard.invoice.cancel</field>
        <field name="arch" type="xml">
            <form string="Cancel Invoices">
                <sheet>
                    <div class="alert alert-warning" role="alert">
                        <strong>Warning!</strong> You are about to cancel <field name="invoice_count" readonly="1"/> invoice(s).
                    </div>

                    <group>
                        <group>
                            <field name="invoice_count" readonly="1"/>
                        </group>
                    </group>

                    <group>
                        <label for="reason" string="Reason (Optional)"/>
                        <field name="reason" nolabel="1" placeholder="Please provide a reason..."
                               options="{'rows': 3}"/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Yes, Cancel All" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_invoice_cancel" model="ir.actions.act_window">
        <field name="name">Cancel Invoices</field>
        <field name="res_model">wizard.invoice.cancel</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

### State Change Confirmation

```bash
/wizard-confirm wizard.order.reset "Reset Order" "Are you sure you want to reset this order to draft? All current approvals will be lost." --require_reason=true --warning_text="This will require re-approval."
```

**Output - models/wizard_order_reset.py:**
```python
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardOrderReset(models.TransientModel):
    _name = 'wizard.order.reset'
    _description = 'Order Reset Confirmation'

    reason = fields.Text(string='Reason', required=True)
    lose_approvals = fields.Boolean(string='I understand I will lose all approvals', default=False)

    @api.constrains('lose_approvals')
    def _check_lose_approvals(self):
        """Ensure user understands the consequence."""
        for wizard in self:
            if not wizard.lose_approvals:
                raise UserError(_('Please confirm that you understand the consequences.'))

    def action_confirm(self):
        """Reset the order to draft."""
        self.ensure_one()

        # Validate
        if not self.reason:
            raise UserError(_('Please provide a reason.'))

        # Get active record from context
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if not active_id or not active_model:
            raise UserError(_('No active record found.'))

        order = self.env[active_model].browse(active_id)

        # Reset to draft
        order.write({
            'state': 'draft',
            'reset_reason': self.reason,
        })

        # Post message
        order.message_post(
            body=_('Order reset to draft. Reason: %s') % self.reason
        )

        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Cancel the wizard."""
        return {'type': 'ir.actions.act_window_close'}
```

**Output - views/wizard_order_reset_views.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_wizard_order_reset_form" model="ir.ui.view">
        <field name="name">wizard.order.reset.form</field>
        <field name="model">wizard.order.reset</field>
        <field name="arch" type="xml">
            <form string="Reset Order">
                <sheet>
                    <div class="alert alert-warning" role="alert">
                        <strong>Warning!</strong> This will require re-approval.
                    </div>

                    <p class="text-muted">
                        Are you sure you want to reset this order to draft? All current approvals will be lost.
                    </p>

                    <group>
                        <field name="lose_approvals"/>
                    </group>

                    <group>
                        <label for="reason" string="Reason"/>
                        <field name="reason" nolabel="1" required="1"
                               placeholder="Please explain why you need to reset this order..."
                               options="{'rows': 4}"/>
                    </group>
                </sheet>
                <footer>
                    <button name="action_confirm" string="Yes, Reset" type="object" class="btn-primary"/>
                    <button name="action_cancel" string="Cancel" type="object" class="btn-secondary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_wizard_order_reset" model="ir.actions.act_window">
        <field name="name">Reset Order</field>
        <field name="res_model">wizard.order.reset</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

## Calling Confirmation Wizards

### From a button in form view:

```python
def action_cancel_with_confirm(self):
    """Show confirmation dialog before cancelling."""
    return {
        'type': 'ir.actions.act_window',
        'name': _('Cancel Confirmation'),
        'res_model': 'wizard.order.cancel',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'active_id': self.id,
            'active_model': self._name,
        }
    }
```

### From a list view action:

```xml
<act_window id="action_wizard_cancel"
    name="Cancel"
    res_model="wizard.order.cancel"
    binding_model="sale.order"
    binding_views="list"
    view_mode="form"
    target="new"/>
```

### Replace standard delete action:

```python
def unlink(self):
    """Override delete to show confirmation."""
    # Show confirmation wizard instead
    return {
        'type': 'ir.actions.act_window',
        'name': _('Delete Confirmation'),
        'res_model': 'wizard.delete.confirm',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'active_ids': self.ids,
            'active_model': self._name,
        }
    }
```

## Best Practices

1. **Clarity:**
   - Use clear, concise messages
   - Explain what will happen
   - Warn about consequences
   - Be specific about what's affected

2. **User Experience:**
   - Keep wizards simple and quick
   - Don't ask for unnecessary information
   - Use appropriate colors and icons
   - Make buttons clear (Yes/No or Confirm/Cancel)

3. **Safety:**
   - Always validate permissions
   - Check record state before action
   - Log confirmation reasons
   - Provide undo when possible

4. **Styling:**
   - Use `alert-warning` for cancellations
   - Use `alert-danger` for deletions
   - Use `alert-info` for informational
   - Keep messages short and readable

5. **Required Reasons:**
   - Require reasons for destructive actions
   - Store reasons in chatter
   - Use reasons for audit trail
   - Make reason field prominent

6. **Multiple Records:**
   - Show count of affected records
   - List record names if feasible
   - Process in batch
   - Show success/failure count

7. **Confirmation Checkbox:**
   - Use for critical actions
   - Make user acknowledge consequences
   - Use clear checkbox labels
   - Validate checkbox is checked

8. **Return Behavior:**
   - Close wizard after action
   - Show success notification
   - Refresh parent view
   - Handle errors gracefully

## Next Steps

After creating the confirmation wizard:
- Add wizard model to `__init__.py`
- Register views in `__manifest__.py` data files
- Add button or action to trigger wizard
- Test wizard functionality
- Add proper translations
- Consider adding audit logging
- Ensure proper access rights
