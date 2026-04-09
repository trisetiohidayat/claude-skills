---
description: Create action methods for Odoo 19 models triggered by button clicks. Use when user wants to create an action method.
---


# Odoo 19 Action Method Creation

Create action methods triggered by button clicks in Odoo 19 models.

## Instructions

1. **Action Method Pattern:**

```python
def action_button_name(self):
    """Action description."""
    # Your logic here
    self.write({'state': 'done'})
    return True
```

2. **Common Return Types:**

```python
# Simple return (refresh view)
return True

# Return dictionary for action window
return {
    'type': 'ir.actions.act_window',
    'name': 'Title',
    'view_mode': 'form,tree',
    'res_model': 'model.name',
    'res_id': self.id,
    'target': 'new',  # or 'current', 'fullscreen'
    'context': self.env.context,
}

# Return dictionary for wizard
return {
    'type': 'ir.actions.act_window',
    'name': 'Wizard Name',
    'res_model': 'wizard.model',
    'view_mode': 'form',
    'target': 'new',
    'context': {
        'default_field': self.field,
    }
}
```

3. **Method Types:**

### State Change Actions
- Change record state (draft -> confirmed -> done)
- Update related fields
- Send notifications

### Wizard Actions
- Open a wizard dialog
- Pass context to wizard
- Process wizard results

### Server Actions
- Perform complex operations
- Create/update related records
- Generate reports

### Computation Actions
- Calculate totals
- Process data
- Sync with external systems

## Usage Examples

### Simple State Change

```bash
/method-action action_confirm state_change "Confirm Order" "Change state from draft to confirmed"
```

Output:
```python
def action_confirm(self):
    """Confirm the order."""
    for order in self:
        if order.state != 'draft':
            raise UserError(_('Only draft orders can be confirmed.'))
        order.write({
            'state': 'confirmed',
            'confirmation_date': fields.Datetime.now()
        })
    return True
```

### State Change with Validation

```bash
/method-action action_done state_change "Mark as Done" "Validate and change state to done" return_type="refresh"
```

Output:
```python
from odoo.exceptions import UserError

def action_done(self):
    """Mark record as done after validation."""
    for record in self:
        if record.state == 'done':
            raise UserError(_('Record is already done.'))

        if not record.line_ids:
            raise UserError(_('Cannot mark as done without lines.'))

        record.write({
            'state': 'done',
            'done_date': fields.Datetime.now(),
            'done_by': self.env.user.id
        })
    return True
```

### Open Wizard

```bash
/method-action action_open_wizard wizard "Create Invoice" "Open invoice creation wizard for selected records" return_type="action_window"
```

Output:
```python
def action_open_wizard(self):
    """Open wizard to create invoices."""
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': _('Create Invoice'),
        'res_model': 'account.invoice.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_order_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
    }
```

### Send Email Action

```bash
/method-action action_send_email email "Send Confirmation Email" "Send email confirmation to customer" return_type="none"
```

Output:
```python
def action_send_email(self):
    """Send confirmation email to customer."""
    template = self.env.ref('module.email_template_confirmation', raise_if_not_found=False)
    for record in self:
        if template and record.partner_id.email:
            template.send_mail(record.id, force_send=True)
            record.message_post(
                body=_('Confirmation email sent to %s') % record.partner_id.email
            )
        else:
            raise UserError(_('No email template or customer email found.'))
    return True
```

### Generate Report

```bash
/method-action action_print_report report "Print Order" "Generate PDF report for the order" return_type="action_window"
```

Output:
```python
def action_print_report(self):
    """Print order report."""
    self.ensure_one()
    return self.env.ref('module.report_order_id').report_action(self)
```

### Batch Action (Multiple Records)

```bash
/method-action action_batch_process server_action "Process Selected" "Process multiple selected records" return_type="none"
```

Output:
```python
def action_batch_process(self):
    """Process selected records in batch."""
    for record in self:
        if record.state != 'draft':
            continue

        # Your processing logic
        record.process_data()
        record.write({'state': 'processed'})

    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'message': _('Processed %d records') % len(self),
            'type': 'success',
        }
    }
```

### Create Related Records

```bash
/method-action action_create_invoice server_action "Create Invoice" "Create invoice from order" return_type="action_window"
```

Output:
```python
def action_create_invoice(self):
    """Create invoice from order."""
    self.ensure_one()

    if self.invoice_ids:
        raise UserError(_('Invoice already exists.'))

    invoice_vals = {
        'partner_id': self.partner_id.id,
        'move_type': 'out_invoice',
        'invoice_line_ids': [],
    }

    # Create invoice lines from order lines
    for line in self.order_line_ids:
        invoice_vals['invoice_line_ids'].append((0, 0, {
            'name': line.name,
            'quantity': line.quantity,
            'price_unit': line.price_unit,
            'product_id': line.product_id.id,
        }))

    invoice = self.env['account.move'].create(invoice_vals)

    self.write({
        'invoice_ids': [(4, invoice.id)]
    })

    return {
        'type': 'ir.actions.act_window',
        'name': _('Invoice'),
        'view_mode': 'form',
        'res_model': 'account.move',
        'res_id': invoice.id,
        'target': 'current',
    }
```

### Cancel Action with Reason

```bash
/method-action action_cancel state_change "Cancel" "Cancel the order and require reason" return_type="refresh"
```

Output:
```python
def action_cancel(self):
    """Cancel the record."""
    for record in self:
        if record.state == 'cancel':
            raise UserError(_('Record is already cancelled.'))

        if record.state in ['done', 'processed']:
            if not self.env.user.has_group('base.group_system'):
                raise UserError(_('Only administrators can cancel processed records.'))

        record.write({'state': 'cancel'})

    return True
```

### Compute and Update

```bash
/method-action action_recompute computation "Recompute Totals" "Recompute all totals for the record" return_type="none"
```

Output:
```python
def action_recompute(self):
    """Recompute totals and other computed fields."""
    for record in self:
        # Trigger recomputation
        record._compute_amount()
        record._compute_tax()
        record._compute_total()

        record.message_post(
            body=_('Totals recomputed.')
        )

    return True
```

### Sync with External System

```bash
/method-action action_sync_external server_action "Sync to External" "Sync record data to external system" return_type="none"
```

Output:
```python
def action_sync_external(self):
    """Sync record to external system."""
    for record in self:
        try:
            # Your sync logic
            record._sync_to_external()

            record.write({
                'sync_date': fields.Datetime.now(),
                'sync_status': 'success'
            })

            record.message_post(
                body=_('Successfully synced to external system.')
            )

        except Exception as e:
            record.write({
                'sync_status': 'failed'
            })
            record.message_post(
                body=_('Sync failed: %s') % str(e)
            )
            raise

    return True
```

### Duplicate Record

```bash
/method-action action_duplicate server_action "Duplicate" "Create a copy of the record" return_type="action_window"
```

Output:
```python
def action_duplicate(self):
    """Duplicate the record."""
    self.ensure_one()

    # Default copy uses ormcopy method
    new_record = self.copy({
        'name': _('%s (copy)') % self.name,
        'state': 'draft',
        'date': False,
    })

    return {
        'type': 'ir.actions.act_window',
        'name': _('Duplicated Record'),
        'view_mode': 'form',
        'res_model': self._name,
        'res_id': new_record.id,
        'target': 'current',
    }
```

### Archive/Unarchive

```bash
/method-action action_archive server_action "Archive" "Archive the record" return_type="none"
```

Output:
```python
def action_archive(self):
    """Archive the record."""
    for record in self:
        if record.state not in ['draft', 'cancel']:
            raise UserError(_('Only draft or cancelled records can be archived.'))

        record.active = False

    return True

def action_unarchive(self):
    """Unarchive the record."""
    for record in self:
        record.active = True

    return True
```

### Reset to Draft

```bash
/method-action action_draft state_change "Reset to Draft" "Reset record to draft state" return_type="none"
```

Output:
```python
def action_draft(self):
    """Reset record to draft."""
    for record in self:
        if record.state == 'draft':
            continue

        if record.state == 'done':
            if not self.env.user.has_group('base.group_system'):
                raise UserError(_('Only administrators can reset done records.'))

        # Reset fields
        record.write({
            'state': 'draft',
            'approved_date': False,
            'approved_by': False,
        })

        record.message_post(
            body=_('Reset to draft.')
        )

    return True
```

### Approve Workflow

```bash
/method-action action_approve state_change "Approve" "Approve the record" return_type="none"
```

Output:
```python
def action_approve(self):
    """Approve the record."""
    for record in self:
        if record.state != 'submitted':
            raise UserError(_('Only submitted records can be approved.'))

        record.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now()
        })

        # Send notification
        record.message_post(
            body=_('Approved by %s') % self.env.user.name
        )

    return True
```

### Reject with Reason

```bash
/method-action action_reject state_change "Reject" "Reject the record" return_type="none"
```

Output:
```python
def action_reject(self):
    """Reject the record."""
    for record in self:
        if record.state not in ['submitted', 'approved']:
            raise UserError(_('Cannot reject records in this state.'))

        record.write({
            'state': 'rejected',
            'rejected_by': self.env.user.id,
            'rejected_date': fields.Datetime.now()
        })

        record.message_post(
            body=_('Rejected by %s') % self.env.user.name
        )

    return True
```

### Open Related Records

```bash
/method-action action_view_lines server_action "View Lines" "Open order lines" return_type="action_window"
```

Output:
```python
def action_view_lines(self):
    """View order lines."""
    self.ensure_one()

    return {
        'type': 'ir.actions.act_window',
        'name': _('Order Lines'),
        'view_mode': 'tree,form',
        'res_model': 'order.line',
        'domain': [('order_id', '=', self.id)],
        'context': {
            'default_order_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
    }
```

## Best Practices

1. **Method Naming:**
   - Use prefix `action_` for button methods
   - Be descriptive: `action_confirm`, `action_send_email`
   - Group related actions: `action_*_invoice`

2. **Validation:**
   - Always validate state before changes
   - Check permissions when needed
   - Provide clear error messages

3. **User Feedback:**
   - Use message_post for trail
   - Send notifications for important actions
   - Show success messages

4. **Return Values:**
   - Return True for simple actions
   - Return action dict for navigation
   - Return client action for notifications

5. **Error Handling:**
   - Use UserError for user-facing errors
   - Use ValidationError for validation errors
   - Handle exceptions appropriately

6. **Performance:**
   - Batch operations when possible
   - Avoid unnecessary database calls
   - Use ensure_one() for single record operations

## Button Definition in Views

Add buttons to form views:

```xml
<header>
    <button name="action_draft" string="Reset to Draft"
            type="object" states="cancel,done"
            class="btn-secondary"/>
    <button name="action_confirm" string="Confirm"
            type="object" states="draft"
            class="btn-primary"/>
    <button name="action_done" string="Mark as Done"
            type="object" states="confirmed"
            class="btn-primary"/>
    <button name="action_cancel" string="Cancel"
            type="object" states="draft,confirmed"
            class="btn-danger"/>
</header>
```

## Common Return Patterns

### Refresh Current View
```python
return True
```

### Open Record
```python
return {
    'type': 'ir.actions.act_window',
    'res_model': 'model.name',
    'res_id': record.id,
    'view_mode': 'form',
    'target': 'current',
}
```

### Open Wizard
```python
return {
    'type': 'ir.actions.act_window',
    'res_model': 'wizard.model',
    'view_mode': 'form',
    'target': 'new',
    'context': {...}
}
```

### Show Notification
```python
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'message': _('Success!'),
        'type': 'success',
    }
}
```

### Reload View
```python
return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}
```

## Next Steps

After creating action methods:
- Add buttons to form views
- Set button states attribute
- Configure button classes
- Add security rules
- Test all user scenarios
- Add unit tests
