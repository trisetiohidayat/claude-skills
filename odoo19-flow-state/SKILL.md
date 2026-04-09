---
description: Create state machine workflow with state changes, mail.thread tracking, and automatic transitions. Use when user wants to create a workflow with state field and transitions.
---


# Odoo 19 State Machine Workflow

Create state machine workflow with state field, transition methods, mail.thread tracking, and automatic transitions.

## Instructions

1. **Add state selection field:**

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('cancel', 'Cancelled'),
], string='State', default='draft', required=True, tracking=True)
```

2. **Inherit mail.thread for tracking:**

```python
class YourModel(models.Model):
    _name = 'your.model'
    _description = 'Your Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

3. **Create transition methods:**

```python
@api.model
def _default_state(self):
    """Get default state."""
    return 'draft'

def action_start(self):
    """Transition from draft to in_progress."""
    self.write({'state': 'in_progress'})

def action_done(self):
    """Transition from in_progress to done."""
    self.write({'state': 'done'})

def action_cancel(self):
    """Cancel the record."""
    self.write({'state': 'cancel'})

def action_draft(self):
    """Reset to draft."""
    self.write({'state': 'draft'})
```

4. **Add tracking fields:**

```python
# State transition tracking
state_date = fields.Datetime(string='State Date', readonly=True)
previous_state = fields.Char(string='Previous State', readonly=True)

# User tracking
state_user_id = fields.Many2one('res.users', string='Changed By', readonly=True)

# Duration tracking
duration_days = fields.Float(string='Duration (Days)', compute='_compute_duration')
```

5. **Add computed methods:**

```python
@api.depends('state', 'state_date')
def _compute_duration(self):
    """Compute duration in current state."""
    for record in self:
        if record.state_date:
            delta = fields.Datetime.now() - record.state_date
            record.duration_days = delta.total_seconds() / 86400
        else:
            record.duration_days = 0.0
```

## Usage Examples

### Linear State Machine

```bash
/flow-state project.task linear "draft:in_progress:done:cancel" tracking="true"
```

Output:
```python
# project/models/project_task.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Project Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, sequence, id desc'

    # State field with tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)

    # State tracking fields
    state_date = fields.Datetime(string='State Date', readonly=True)
    previous_state = fields.Char(string='Previous State', readonly=True, tracking=True)
    state_user_id = fields.Many2one('res.users', string='Changed By', readonly=True)

    # Progress tracking
    progress = fields.Float(string='Progress', default=0.0, tracking=True)
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready for Next Stage'),
        ('blocked', 'Blocked'),
    ], string='Kanban State', default='normal', tracking=True)

    # Date tracking
    start_date = fields.Datetime(string='Start Date', readonly=True)
    done_date = fields.Datetime(string='Completion Date', readonly=True)
    cancel_date = fields.Datetime(string='Cancellation Date', readonly=True)

    @api.model
    def _read_group_state_ids(self, states, domain, order):
        """Read group for states."""
        return states

    def action_start(self):
        """Start the task."""
        for task in self:
            if task.state != 'draft':
                raise UserError(_('Only draft tasks can be started.'))

            task.write({
                'state': 'in_progress',
                'previous_state': task.state,
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'start_date': fields.Datetime.now(),
            })

            task.message_post(
                body=_('Task started by %s') % self.env.user.name
            )
        return True

    def action_done(self):
        """Mark task as done."""
        for task in self:
            if task.state != 'in_progress':
                raise UserError(_('Only in-progress tasks can be marked as done.'))

            if task.progress < 100:
                task.progress = 100.0

            task.write({
                'state': 'done',
                'previous_state': task.state,
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'done_date': fields.Datetime.now(),
            })

            task.message_post(
                body=_('Task completed by %s') % self.env.user.name
            )
        return True

    def action_cancel(self):
        """Cancel the task."""
        for task in self:
            if task.state == 'done':
                raise UserError(_('Cannot cancel completed tasks.'))

            task.write({
                'state': 'cancel',
                'previous_state': task.state,
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'cancel_date': fields.Datetime.now(),
            })

            task.message_post(
                body=_('Task cancelled by %s') % self.env.user.name
            )
        return True

    def action_draft(self):
        """Reset to draft."""
        for task in self:
            if task.state == 'done':
                if not self.env.user.has_group('base.group_system'):
                    raise UserError(_('Only administrators can reset completed tasks.'))

            task.write({
                'state': 'draft',
                'previous_state': task.state,
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'progress': 0.0,
            })

            task.message_post(
                body=_('Task reset to draft by %s') % self.env.user.name
            )
        return True

    def action_set_kanban_blocked(self):
        """Set kanban state to blocked."""
        self.write({'kanban_state': 'blocked'})
        self.message_post(body=_('Task marked as blocked'))

    def action_set_kanban_normal(self):
        """Set kanban state to normal."""
        self.write({'kanban_state': 'normal'})

    def action_set_kanban_done(self):
        """Set kanban state to done."""
        self.write({'kanban_state': 'done'})
```

### Branching State Machine

```bash
/flow-state sale.order branching "draft:sent:confirmed:shipped:delivered,cancel:refunded" tracking="true" activities="true"
```

Output:
```python
# sale/models/sale_order.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled'),
        ('refunded', 'Refunded'),
    ], string='State', default='draft', required=True, tracking=True)

    # State tracking
    state_date = fields.Datetime(string='State Change Date', readonly=True)
    state_user_id = fields.Many2one('res.users', string='Changed By', readonly=True)
    state_history_ids = fields.One2many('sale.order.state.history', 'order_id', string='State History')

    # Branch-specific fields
    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=True)
    shipping_date = fields.Datetime(string='Shipping Date', readonly=True)
    delivery_date = fields.Datetime(string='Delivery Date', readonly=True)
    cancellation_date = fields.Datetime(string='Cancellation Date', readonly=True)
    refund_date = fields.Datetime(string='Refund Date', readonly=True)

    def action_quotation_send(self):
        """Send quotation to customer."""
        for order in self:
            if order.state != 'draft':
                raise UserError(_('Only draft quotations can be sent.'))

            # Send email logic here
            order.write({
                'state': 'sent',
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
            })

            order._add_state_history('sent')
            order.message_post(
                body=_('Quotation sent to customer')
            )
        return True

    def action_confirm(self):
        """Confirm the quotation."""
        for order in self:
            if order.state not in ['draft', 'sent']:
                raise UserError(_('Only draft or sent quotations can be confirmed.'))

            order.write({
                'state': 'sale',
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'confirmation_date': fields.Datetime.now(),
            })

            order._add_state_history('sale')
            order.message_post(
                body=_('Order confirmed')
            )
        return True

    def action_ship(self):
        """Ship the order."""
        for order in self:
            if order.state != 'sale':
                raise UserError(_('Only confirmed orders can be shipped.'))

            order.write({
                'state': 'shipped',
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'shipping_date': fields.Datetime.now(),
            })

            order._add_state_history('shipped')
            order.message_post(
                body=_('Order shipped')
            )
        return True

    def action_deliver(self):
        """Mark order as delivered."""
        for order in self:
            if order.state != 'shipped':
                raise UserError(_('Only shipped orders can be marked as delivered.'))

            order.write({
                'state': 'delivered',
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'delivery_date': fields.Datetime.now(),
            })

            order._add_state_history('delivered')
            order.message_post(
                body=_('Order delivered')
            )
        return True

    def action_cancel(self):
        """Cancel the order."""
        for order in self:
            if order.state in ['delivered', 'refunded']:
                raise UserError(_('Cannot cancel delivered or refunded orders.'))

            order.write({
                'state': 'cancel',
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'cancellation_date': fields.Datetime.now(),
            })

            order._add_state_history('cancel')
            order.message_post(
                body=_('Order cancelled')
            )
        return True

    def action_refund(self):
        """Refund the order."""
        for order in self:
            if order.state != 'delivered':
                raise UserError(_('Only delivered orders can be refunded.'))

            order.write({
                'state': 'refunded',
                'state_date': fields.Datetime.now(),
                'state_user_id': self.env.user.id,
                'refund_date': fields.Datetime.now(),
            })

            order._add_state_history('refunded')
            order.message_post(
                body=_('Order refunded')
            )
        return True

    def _add_state_history(self, new_state):
        """Add state to history."""
        self.env['sale.order.state.history'].create({
            'order_id': self.id,
            'state': new_state,
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
        })


class SaleOrderStateHistory(models.Model):
    _name = 'sale.order.state.history'
    _description = 'Sale Order State History'
    _order = 'date desc'

    order_id = fields.Many2one('sale.order', string='Order', required=True, ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancelled'),
        ('refunded', 'Refunded'),
    ], string='State', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now)
    notes = fields.Text(string='Notes')
```

### Cyclic State Machine

```bash
/flow-state recurring.contract cyclic "draft:active:suspended:expired:cancelled:reactive:active" tracking="true" activities="true" auto_transitions="true"
```

Output:
```python
# contract/models/contract.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class Contract(models.Model):
    _name = 'contract.contract'
    _description = 'Recurring Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)

    # Contract dates
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    expiration_date = fields.Date(string='Expiration Date', readonly=True)

    # State tracking
    state_history_ids = fields.One2many('contract.state.history', 'contract_id', string='State History')

    # Suspension fields
    suspension_count = fields.Integer(string='Suspension Count', default=0)
    max_suspensions = fields.Integer(string='Max Suspensions', default=3)

    # Auto-transition fields
    auto_expire = fields.Boolean(string='Auto Expire', default=True)
    expire_days = fields.Integer(string='Days Before Expiration', default=30)

    def action_start(self):
        """Activate the contract."""
        for contract in self:
            if contract.state != 'draft':
                raise UserError(_('Only draft contracts can be activated.'))

            if not contract.start_date or contract.start_date > fields.Date.context_today(contract):
                raise UserError(_('Contract start date must be today or in the past.'))

            expiration_date = contract.end_date if contract.end_date else (
                contract.start_date + timedelta(days=365)
            )

            contract.write({
                'state': 'active',
                'expiration_date': expiration_date,
            })

            contract._add_state_history('active')
            contract.message_post(
                body=_('Contract activated from %s to %s') % (
                    contract.start_date, contract.expiration_date
                )
            )
        return True

    def action_suspend(self):
        """Suspend the contract."""
        for contract in self:
            if contract.state != 'active':
                raise UserError(_('Only active contracts can be suspended.'))

            if contract.suspension_count >= contract.max_suspensions:
                raise UserError(_('Maximum suspension limit reached.'))

            contract.write({
                'state': 'suspended',
                'suspension_count': contract.suspension_count + 1,
            })

            contract._add_state_history('suspended')
            contract.message_post(
                body=_('Contract suspended (%d/%d)') % (
                    contract.suspension_count, contract.max_suspensions
                )
            )
        return True

    def action_reactivate(self):
        """Reactivate a suspended contract."""
        for contract in self:
            if contract.state not in ['suspended', 'expired']:
                raise UserError(_('Only suspended or expired contracts can be reactivated.'))

            contract.write({'state': 'active'})
            contract._add_state_history('active')
            contract.message_post(
                body=_('Contract reactivated')
            )
        return True

    def action_expire(self):
        """Mark contract as expired."""
        for contract in self:
            if contract.state != 'active':
                raise UserError(_('Only active contracts can be expired.'))

            contract.write({'state': 'expired'})
            contract._add_state_history('expired')
            contract.message_post(
                body=_('Contract expired')
            )
        return True

    def action_cancel(self):
        """Cancel the contract."""
        for contract in self:
            if contract.state == 'cancelled':
                raise UserError(_('Contract is already cancelled.'))

            contract.write({'state': 'cancelled'})
            contract._add_state_history('cancelled')
            contract.message_post(
                body=_('Contract cancelled by %s') % self.env.user.name
            )
        return True

    def _cron_auto_expire_contracts(self):
        """Cron job to auto-expire contracts."""
        today = fields.Date.context_today(self)
        expiring_contracts = self.search([
            ('state', '=', 'active'),
            ('auto_expire', '=', True),
            ('expiration_date', '<=', today),
        ])

        for contract in expiring_contracts:
            contract.action_expire()

        return True

    def _add_state_history(self, new_state):
        """Add state to history."""
        self.env['contract.state.history'].create({
            'contract_id': self.id,
            'state': new_state,
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
        })


class ContractStateHistory(models.Model):
    _name = 'contract.state.history'
    _description = 'Contract State History'
    _order = 'date desc'

    contract_id = fields.Many2one('contract.contract', string='Contract', required=True, ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='State', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now)
    notes = fields.Text(string='Notes')
```

### Complex State Machine with Dependencies

```bash
/flow-state manufacturing.order complex "draft:planned:in_progress:quality_check:done,failed:cancelled,redo:in_progress" tracking="true" activities="true"
```

Output:
```python
# manufacturing/models/manufacturing_order.py

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ManufacturingOrder(models.Model):
    _name = 'manufacturing.order'
    _description = 'Manufacturing Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('quality_check', 'Quality Check'),
        ('done', 'Done'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)

    # Quality control fields
    quality_check_passed = fields.Boolean(string='Quality Passed', readonly=True)
    quality_check_notes = fields.Text(string='Quality Notes')
    quality_check_user_id = fields.Many2one('res.users', string='Quality Inspector', readonly=True)

    # Production tracking
    quantity_produced = fields.Float(string='Quantity Produced', default=0.0)
    quantity_target = fields.Float(string='Quantity Target', required=True)

    # Progress calculation
    progress_percentage = fields.Float(
        string='Progress',
        compute='_compute_progress_percentage',
        store=True
    )

    @api.depends('quantity_produced', 'quantity_target')
    def _compute_progress_percentage(self):
        """Compute progress percentage."""
        for order in self:
            if order.quantity_target > 0:
                order.progress_percentage = (order.quantity_produced / order.quantity_target) * 100
            else:
                order.progress_percentage = 0.0

    def action_plan(self):
        """Plan the manufacturing order."""
        for order in self:
            if order.state != 'draft':
                raise UserError(_('Only draft orders can be planned.'))

            if not order.quantity_target or order.quantity_target <= 0:
                raise UserError(_('Target quantity must be positive.'))

            order.write({'state': 'planned'})
            order.message_post(
                body=_('Manufacturing order planned')
            )
        return True

    def action_start_production(self):
        """Start production."""
        for order in self:
            if order.state != 'planned':
                raise UserError(_('Only planned orders can start production.'))

            order.write({
                'state': 'in_progress',
                'quantity_produced': 0.0,
            })
            order.message_post(
                body=_('Production started')
            )
        return True

    def action_update_quantity(self, quantity):
        """Update produced quantity."""
        for order in self:
            if order.state != 'in_progress':
                raise UserError(_('Can only update quantity during production.'))

            order.quantity_produced = quantity

            if order.quantity_produced >= order.quantity_target:
                order.write({'state': 'quality_check'})
                order.message_post(
                    body=_('Target quantity reached. Ready for quality check.')
                )
        return True

    def action_pass_quality(self):
        """Pass quality check."""
        for order in self:
            if order.state != 'quality_check':
                raise UserError(_('Only orders in quality check can pass.'))

            order.write({
                'state': 'done',
                'quality_check_passed': True,
                'quality_check_user_id': self.env.user.id,
            })
            order.message_post(
                body=_('Quality check passed by %s') % self.env.user.name
            )
        return True

    def action_fail_quality(self):
        """Fail quality check."""
        for order in self:
            if order.state != 'quality_check':
                raise UserError(_('Only orders in quality check can fail.'))

            order.write({
                'state': 'failed',
                'quality_check_passed': False,
                'quality_check_user_id': self.env.user.id,
            })
            order.message_post(
                body=_('Quality check failed by %s. Notes: %s') % (
                    self.env.user.name, order.quality_check_notes or 'No notes'
                )
            )
        return True

    def action_redo(self):
        """Redo failed order."""
        for order in self:
            if order.state != 'failed':
                raise UserError(_('Only failed orders can be redone.'))

            order.write({
                'state': 'in_progress',
                'quantity_produced': 0.0,
                'quality_check_passed': False,
            })
            order.message_post(
                body=_('Order set for redo')
            )
        return True

    def action_cancel(self):
        """Cancel the order."""
        for order in self:
            if order.state == 'done':
                raise UserError(_('Cannot cancel completed orders.'))

            order.write({'state': 'cancelled'})
            order.message_post(
                body=_('Order cancelled by %s') % self.env.user.name
            )
        return True

    @api.constrains('quantity_produced', 'quantity_target')
    def _check_quantity(self):
        """Validate quantity."""
        for order in self:
            if order.quantity_produced < 0:
                raise UserError(_('Quantity produced cannot be negative.'))

            if order.state in ['in_progress', 'quality_check', 'done']:
                if order.quantity_produced > order.quantity_target:
                    raise UserError(_('Cannot produce more than target quantity.'))
```

## Best Practices

1. **State Management:**
   - Always use required=True on state field
   - Set sensible default state
   - Use tracking=True for state field

2. **Transitions:**
   - Validate current state before transition
   - Use descriptive method names (action_*)
   - Provide clear error messages

3. **History Tracking:**
   - Record all state changes
   - Track user and timestamp
   - Store notes for important transitions

4. **Mail Thread:**
   - Always inherit mail.thread for tracking
   - Post meaningful messages
   - Use message_post for state changes

5. **Activities:**
   - Create activities for state transitions
   - Assign to appropriate users
   - Set due dates

6. **Auto Transitions:**
   - Use cron jobs for scheduled transitions
   - Validate conditions before auto-transition
   - Log automatic changes

## View Configuration

### Form View with Status Bar

```xml
<form>
    <header>
        <button name="action_draft" string="Draft" type="object" states="cancel" class="btn-secondary"/>
        <button name="action_start" string="Start" type="object" states="draft" class="btn-primary"/>
        <button name="action_done" string="Done" type="object" states="in_progress" class="btn-primary"/>
        <button name="action_cancel" string="Cancel" type="object" states="draft,in_progress" class="btn-danger"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,in_progress,done"/>
    </header>
    <sheet>
        <!-- Your fields here -->
    </sheet>
</form>
```

### Tree View with State Colors

```xml
<tree>
    <field name="name"/>
    <field name="state"/>
    <field name="date" widget="date"/>
    <button name="action_start" string="Start" type="object" states="draft" icon="fa-play"/>
    <button name="action_done" string="Done" type="object" states="in_progress" icon="fa-check"/>
</tree>
```

### Kanban View with State Grouping

```xml
<kanban default_group_by="state">
    <field name="state"/>
    <field name="priority"/>
    <templates>
        <t t-name="kanban-box">
            <div>
                <field name="name"/>
                <field name="state"/>
            </div>
        </t>
    </templates>
</kanban>
```

### Search View with State Filters

```xml
<search>
    <filter string="Draft" name="draft" domain="[('state', '=', 'draft')]"/>
    <filter string="In Progress" name="in_progress" domain="[('state', '=', 'in_progress')]"/>
    <filter string="Done" name="done" domain="[('state', '=', 'done')]"/>
    <separator/>
    <filter string="My Records" name="my_records" domain="[('create_uid', '=', uid)]"/>
    <group expand="0" string="Group By">
        <filter string="State" name="group_state" context="{'group_by': 'state'}"/>
    </group>
</search>
```

## State Chatter Messages

```python
# State change with details
self.message_post(
    body=_('State changed from <b>%s</b> to <b>%s</b>') % (
        previous_state, new_state
    )
)

# State change with user
self.message_post(
    body=_('State changed to %s by %s') % (
        new_state_label, self.env.user.name
    )
)

# State change with details
self.message_post(
    body=_(
        'Order <b>%(order)s</b> moved to <b>%(state)s</b><br/>'
        'Amount: <b>%(amount)s</b><br/>'
        'Date: %(date)s'
    ) % {
        'order': self.name,
        'state': new_state_label,
        'amount': self.amount,
        'date': fields.Datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
)
```

## Next Steps

After creating state machine:
- `/view-form` - Create form view with status bar
- `/view-tree` - Create tree view with state colors
- `/view-kanban` - Create kanban view grouped by state
- `/automation-cron` - Set up auto-transitions
- `/security-rule` - Create state-based access rules
- `/method-constraint` - Add state validation constraints
