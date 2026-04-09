---
description: Create approval workflow with state field and transition methods. Use when user wants to add approval workflow with approval chain, history, and notifications.
---


# Odoo 19 Approval Workflow

Create approval workflow with state field, transition methods, and approval chain support.

## Instructions

1. **Add state selection field:**

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
], string='State', default='draft', tracking=True)
```

2. **Add approval fields:**

```python
# Approver
approver_id = fields.Many2one('res.users', string='Approver', tracking=True)

# Approval dates
approval_date = fields.Datetime(string='Approval Date', readonly=True)
rejection_date = fields.Datetime(string='Rejection Date', readonly=True)

# Approval history
approval_line_ids = fields.One2many('approval.line', 'record_id', string='Approval History')
```

3. **Create transition methods:**

```python
def action_submit(self):
    """Submit for approval."""
    self.write({'state': 'pending'})

def action_approve(self):
    """Approve the request."""
    self.write({'state': 'approved', 'approval_date': fields.Datetime.now()})

def action_reject(self):
    """Reject the request."""
    self.write({'state': 'rejected', 'rejection_date': fields.Datetime.now()})

def action_reset(self):
    """Reset to draft."""
    self.write({'state': 'draft'})
```

4. **Add approval history model:**

```python
class ApprovalLine(models.Model):
    _name = 'approval.line'
    _description = 'Approval History'

    record_id = fields.Many2one('model.name', string='Record', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='pending')
    date = fields.Datetime(string='Date', default=fields.Datetime.now())
    notes = fields.Text(string='Notes')
```

## Usage Examples

### Simple Single-Level Approval

```bash
/flow-approval purchase.order single "draft,pending,approved,rejected" approval_field="approver_id"
```

Output:
```python
# purchase_order/models/purchase_order.py

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', tracking=True)

    approver_id = fields.Many2one('res.users', string='Approver', tracking=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True)
    rejection_date = fields.Datetime(string='Rejection Date', readonly=True)

    def action_submit(self):
        """Submit for approval."""
        for order in self:
            if not order.approver_id:
                raise UserError(_('Please select an approver before submitting.'))
            order.write({'state': 'pending'})
            order.message_post(
                body=_('Submitted for approval to %s') % order.approver_id.name
            )
        return True

    def action_approve(self):
        """Approve the purchase order."""
        for order in self:
            if order.state != 'pending':
                raise UserError(_('Only pending orders can be approved.'))
            order.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now(),
            })
            order.message_post(
                body=_('Approved by %s') % self.env.user.name
            )
        return True

    def action_reject(self):
        """Reject the purchase order."""
        for order in self:
            if order.state != 'pending':
                raise UserError(_('Only pending orders can be rejected.'))
            order.write({
                'state': 'rejected',
                'rejection_date': fields.Datetime.now(),
            })
            order.message_post(
                body=_('Rejected by %s') % self.env.user.name
            )
        return True

    def action_reset(self):
        """Reset to draft."""
        for order in self:
            if order.state == 'approved':
                raise UserError(_('Cannot reset approved orders.'))
            order.write({'state': 'draft'})
        return True
```

### Multi-Level Approval

```bash
/flow-approval hr.expense multi_level "draft,manager_pending,finance_pending,approved,rejected" approval_field="approver_id" history="true"
```

Output:
```python
# hr_expense/models/hr_expense.py

from odoo import models, fields, _
from odoo.exceptions import UserError

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('manager_pending', 'Manager Approval'),
        ('finance_pending', 'Finance Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', tracking=True)

    manager_id = fields.Many2one('res.users', string='Manager', tracking=True)
    finance_approver_id = fields.Many2one('res.users', string='Finance Approver', tracking=True)
    approval_line_ids = fields.One2many('expense.approval.line', 'expense_id', string='Approval History')

    def action_submit_manager(self):
        """Submit to manager for approval."""
        for expense in self:
            if not expense.manager_id:
                raise UserError(_('Please assign a manager before submitting.'))
            expense.write({'state': 'manager_pending'})
            expense._add_approval_line('manager_pending', expense.manager_id)
            expense.message_post(
                body=_('Submitted to manager %s for approval') % expense.manager_id.name
            )
        return True

    def action_manager_approve(self):
        """Manager approves the expense."""
        for expense in self:
            if expense.state != 'manager_pending':
                raise UserError(_('Only expenses pending manager approval can be approved.'))
            expense.write({'state': 'finance_pending'})
            expense._update_approval_line('approved')
            expense.message_post(
                body=_('Manager %s approved the expense') % self.env.user.name
            )
        return True

    def action_finance_approve(self):
        """Finance approves the expense."""
        for expense in self:
            if expense.state != 'finance_pending':
                raise UserError(_('Only expenses pending finance approval can be approved.'))
            expense.write({'state': 'approved'})
            expense._update_approval_line('approved')
            expense.message_post(
                body=_('Finance %s approved the expense') % self.env.user.name
            )
        return True

    def action_reject(self):
        """Reject the expense."""
        for expense in self:
            if expense.state not in ['manager_pending', 'finance_pending']:
                raise UserError(_('Cannot reject expenses in current state.'))
            expense.write({'state': 'rejected'})
            expense._update_approval_line('rejected')
            expense.message_post(
                body=_('Rejected by %s') % self.env.user.name
            )
        return True

    def action_reset(self):
        """Reset to draft."""
        for expense in self:
            if expense.state == 'approved':
                raise UserError(_('Cannot reset approved expenses.'))
            expense.write({'state': 'draft'})
        return True

    def _add_approval_line(self, status, user):
        """Add approval history line."""
        self.env['expense.approval.line'].create({
            'expense_id': self.id,
            'user_id': user.id,
            'status': status,
        })

    def _update_approval_line(self, status):
        """Update existing approval line."""
        line = self.env['expense.approval.line'].search([
            ('expense_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('status', '=', 'pending'),
        ], limit=1)
        if line:
            line.write({'status': status})
```

### Parallel Approval

```bash
/flow-approval project.task parallel "draft,pending,approved,rejected" approval_field="approval_group_id" notification="true"
```

Output:
```python
# project/models/project_task.py

from odoo import models, fields, _
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', tracking=True)

    approval_group_id = fields.Many2one('res.groups', string='Approval Group')
    required_approvals = fields.Integer(string='Required Approvals', default=1)
    approval_count = fields.Integer(string='Approval Count', default=0, compute='_compute_approval_count')
    approval_line_ids = fields.One2many('task.approval', 'task_id', string='Approvals')

    @api.depends('approval_line_ids.status')
    def _compute_approval_count(self):
        """Compute number of approvals received."""
        for task in self:
            task.approval_count = len(task.approval_line_ids.filtered(lambda l: l.status == 'approved'))

    def action_submit(self):
        """Submit for parallel approval."""
        for task in self:
            if not task.approval_group_id:
                raise UserError(_('Please select an approval group.'))

            users = task.approval_group_id.users
            if not users:
                raise UserError(_('Approval group has no users.'))

            task.write({'state': 'pending'})

            # Create approval requests for all users
            for user in users:
                self.env['task.approval'].create({
                    'task_id': task.id,
                    'user_id': user.id,
                    'status': 'pending',
                })

            task.message_post(
                body=_('Submitted for approval to %s') % task.approval_group_id.name
            )
        return True

    def action_approve(self):
        """Approve the task."""
        approval = self.env['task.approval'].search([
            ('task_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('status', '=', 'pending'),
        ], limit=1)

        if not approval:
            raise UserError(_('No pending approval found for you.'))

        approval.write({'status': 'approved', 'date': fields.Datetime.now()})

        if self.approval_count >= self.required_approvals:
            self.write({'state': 'approved'})
            self.message_post(
                body=_('Task approved by %s. Required approvals reached.') % self.env.user.name
            )
        else:
            remaining = self.required_approvals - self.approval_count
            self.message_post(
                body=_('Approved by %s. %d more approval(s) needed.') % (self.env.user.name, remaining)
            )
        return True

    def action_reject(self):
        """Reject the task."""
        approval = self.env['task.approval'].search([
            ('task_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('status', '=', 'pending'),
        ], limit=1)

        if not approval:
            raise UserError(_('No pending approval found for you.'))

        approval.write({'status': 'rejected', 'date': fields.Datetime.now()})
        self.write({'state': 'rejected'})
        self.message_post(
            body=_('Task rejected by %s') % self.env.user.name
        )
        return True

    def action_reset(self):
        """Reset to draft."""
        for task in self:
            if task.state == 'approved':
                raise UserError(_('Cannot reset approved tasks.'))
            task.write({'state': 'draft'})
            task.approval_line_ids.unlink()
        return True
```

### Chain Approval

```bash
/flow-approval sale.order chain "draft,level1,level2,level3,approved,rejected" approval_field="approver_id" history="true"
```

Output:
```python
# sale/models/sale_order.py

from odoo import models, fields, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('level1', 'Level 1 Approval'),
        ('level2', 'Level 2 Approval'),
        ('level3', 'Level 3 Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', tracking=True)

    level1_approver_id = fields.Many2one('res.users', string='Level 1 Approver')
    level2_approver_id = fields.Many2one('res.users', string='Level 2 Approver')
    level3_approver_id = fields.Many2one('res.users', string='Level 3 Approver')
    approval_line_ids = fields.One2many('sale.approval.line', 'order_id', string='Approval History')

    def action_submit(self):
        """Submit for first level approval."""
        for order in self:
            if not order.level1_approver_id:
                raise UserError(_('Please assign Level 1 approver.'))
            order.write({'state': 'level1'})
            order._add_approval_line('level1', order.level1_approver_id)
            order.message_post(
                body=_('Submitted to %s for Level 1 approval') % order.level1_approver_id.name
            )
        return True

    def action_level1_approve(self):
        """Level 1 approval."""
        for order in self:
            if order.state != 'level1':
                raise UserError(_('Only orders in Level 1 approval can be approved here.'))

            if order.level2_approver_id:
                order.write({'state': 'level2'})
                order._update_approval_line('approved')
                order._add_approval_line('level2', order.level2_approver_id)
                order.message_post(
                    body=_('Level 1 approved. Forwarded to %s for Level 2') % order.level2_approver_id.name
                )
            else:
                order.write({'state': 'approved'})
                order._update_approval_line('approved')
                order.message_post(
                    body=_('Order approved by Level 1')
                )
        return True

    def action_level2_approve(self):
        """Level 2 approval."""
        for order in self:
            if order.state != 'level2':
                raise UserError(_('Only orders in Level 2 approval can be approved here.'))

            if order.level3_approver_id:
                order.write({'state': 'level3'})
                order._update_approval_line('approved')
                order._add_approval_line('level3', order.level3_approver_id)
                order.message_post(
                    body=_('Level 2 approved. Forwarded to %s for Level 3') % order.level3_approver_id.name
                )
            else:
                order.write({'state': 'approved'})
                order._update_approval_line('approved')
                order.message_post(
                    body=_('Order approved by Level 2')
                )
        return True

    def action_level3_approve(self):
        """Level 3 approval."""
        for order in self:
            if order.state != 'level3':
                raise UserError(_('Only orders in Level 3 approval can be approved here.'))

            order.write({'state': 'approved'})
            order._update_approval_line('approved')
            order.message_post(
                body=_('Order approved by Level 3')
            )
        return True

    def action_reject(self):
        """Reject at any level."""
        for order in self:
            if order.state == 'draft':
                raise UserError(_('Cannot reject draft orders.'))
            if order.state == 'approved':
                raise UserError(_('Cannot reject approved orders.'))

            order.write({'state': 'rejected'})
            order._update_approval_line('rejected')
            order.message_post(
                body=_('Rejected at %s by %s') % (order._get_state_label(), self.env.user.name)
            )
        return True

    def action_reset(self):
        """Reset to draft."""
        for order in self:
            if order.state == 'approved':
                raise UserError(_('Cannot reset approved orders.'))
            order.write({'state': 'draft'})
            order.approval_line_ids.unlink()
        return True

    def _add_approval_line(self, level, user):
        """Add approval history line."""
        self.env['sale.approval.line'].create({
            'order_id': self.id,
            'user_id': user.id,
            'level': level,
            'status': 'pending',
        })

    def _update_approval_line(self, status):
        """Update existing approval line."""
        line = self.env['sale.approval.line'].search([
            ('order_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('status', '=', 'pending'),
        ], limit=1)
        if line:
            line.write({'status': status})

    def _get_state_label(self):
        """Get human-readable state label."""
        return dict(self._fields['state'].get_description(self.env)['selection']).get(self.state, self.state)
```

## Best Practices

1. **State Management:**
   - Always validate state before transitions
   - Use tracking=True on state field
   - Provide meaningful state labels

2. **User Experience:**
   - Show approver information clearly
   - Display approval history
   - Send notifications for pending approvals

3. **Security:**
   - Check user permissions in approval methods
   - Validate approver assignment
   - Prevent state circumvention

4. **Notifications:**
   - Send email on submission
   - Notify approvers of pending items
   - Alert submitter of approval/rejection

5. **History Tracking:**
   - Record all approval actions
   - Track timestamps and users
   - Store rejection reasons

## View Configuration

Add buttons to form view:

```xml
<header>
    <button name="action_submit" string="Submit" type="object" states="draft" class="btn-primary"/>
    <button name="action_approve" string="Approve" type="object" states="pending" class="btn-primary"/>
    <button name="action_reject" string="Reject" type="object" states="pending" class="btn-danger"/>
    <button name="action_reset" string="Reset to Draft" type="object" states="rejected" class="btn-secondary"/>
</header>
```

Add state badge:

```xml
<field name="state" widget="statusbar" statusbar_visible="draft,pending,approved"/>
```

## Security Rules

Create record rules for approvers:

```xml
<record id="approval_rule_manager" model="ir.rule">
    <field name="name">Manager can see pending approvals</field>
    <field name="model_id" ref="model_purchase_order"/>
    <field name="domain_force">[('state', '=', 'pending'), ('approver_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

## Next Steps

After creating approval workflow:
- `/view-form` - Create form view with approval buttons
- `/security-rule` - Create approver access rules
- `/automation-cron` - Set up approval reminders
- `/data-xml` - Create approval templates
