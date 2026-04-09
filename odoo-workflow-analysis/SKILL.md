---
name: odoo-workflow-analysis
description: |
  Analisis state machine dan approval flows dalam Odoo - state transitions, business rules,
  workflow mapping, button actions. Gunakan ketika:
  - User bertanya tentang workflow/approval process
  - Perlu understand state transitions
  - Ingin map business rules
  - Ingin analyze button actions dan flow
---

# Odoo Workflow Analysis Skill

## Overview

Skill ini membantu menganalisis workflow dan state machine dalam Odoo. Workflow dalam Odoo mencakup berbagai aspek mulai dari status dokumen, transisi state, validasi bisnis, hingga button actions yang memicu perubahan state. Pemahaman mendalam tentang workflow sangat penting untuk debugging, customization, dan migrasi modul.

Odoo workflow terdiri dari beberapa komponen utama:
- **State Fields**: Field `selection` yang merepresentasikan status dokumen
- **Transitions**: Aturan perpindahan dari satu state ke state lain
- **Button Actions**: Tombol yang memicu action tertentu
- **Business Rules**: Constraint dan validasi yang mengatur workflow
- **Approval Flows**: Proses persetujuan bertingkat

## Step 1: Identify State Fields

Langkah pertama dalam analisis workflow adalah mengidentifikasi field-field yangmerepresentasikan state atau status dari sebuah dokumen.

### 1.1 State Field Patterns

State field dalam Odoo umumnya menggunakan tipe `selection`:

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    state = fields.Selection(
        selection=[
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sales Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        readonly=True,
        copy=False,
        tracking=True,
        default='draft'
    )
```

**Common State Field Characteristics**:
- Tipe: `fields.Selection`
- Readonly: Umumnya readonly karena hanya boleh diubah melalui method
- Default: Biasa设置为 'draft' sebagai state awal
- Tracking: Sering menggunakan tracking=True untuk mencatat perubahan

### 1.2 Common State Patterns by Module

**Sale Order States**:
| State | Description | Next States |
|-------|-------------|-------------|
| draft | Quotation created | sent, sale, cancel |
| sent | Quotation sent to customer | sale, cancel |
| sale | Sales order confirmed | done, cancel |
| done | Order locked (completed) | cancel |
| cancel | Order cancelled | draft |

**Purchase Order States**:
| State | Description | Next States |
|-------|-------------|-------------|
| draft | RFQ created | sent, purchase, cancel |
| sent | RFQ sent to vendor | purchase, cancel |
| purchase | PO confirmed | done, cancel |
| done | Purchase order done | cancel |
| cancel | PO cancelled | draft |

**Account Move States**:
| State | Description | Next States |
|-------|-------------|-------------|
| draft | Journal entry draft | posted, cancel |
| posted | Journal entry posted | cancel |
| cancel | Entry cancelled (reversed) | draft |

**Project Task States**:
| State | Description | Next States |
|-------|-------------|-------------|
| draft | New task | todo, cancel |
| todo | Task ready to start | in_progress, cancel |
| in_progress | Task in progress | done, cancel |
| done | Task completed | - |
| cancel | Task cancelled | draft |

### 1.3 Identifying State Fields in Code

Gunakan grep untuk mencari state fields:

```bash
# Find state fields
grep -rn "state.*fields.Selection" --include="*.py" /path/to/addons/

# Find specific state values
grep -rn "'draft'" --include="*.py" /path/to/addons/
grep -rn "'done'" --include="*.py" /path/to/addons/
grep -rn "'cancel'" --include="*.py" /path/to/addons/
```

**Pattern yang harus diperhatikan**:
```python
# State field definition
state = fields.Selection(selection=[...], string='Status')

# State in view
<field name="state"/>

# State in domain
[('state', '=', 'draft')]

# State in button attrs
attrs="{'invisible': [('state', '=', 'draft')]}"
```

### 1.4 Multiple State Fields

Beberapa modul memiliki lebih dari satu state field:

```python
class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    # Primary state
    state = fields.Selection(selection=[...], string='Status')

    # Picking state (for PO with dropship)
    picking_state = fields.Selection([
        ('waiting', 'Waiting'),
        ('assigned', 'Ready to Transfer'),
        ('done', 'Transferred'),
    ], string='Picking Status')

    # Invoice state
    invoice_state = fields.Selection([
        ('no', 'No Invoice'),
        ('to invoice', 'To Invoice'),
        ('invoiced', 'Invoiced'),
    ], string='Invoice Status')
```

### 1.5 Kanban State (Statusbar)

Odoo juga menggunakan statusbar dalam view:

```xml
<field name="state" widget="statusbar"
       statusbar_colors="{'cancel': 'danger', 'done': 'success'}"/>
```

Widget ini menampilkan progress bar dengan warna yang berbeda untuk setiap state.

## Step 2: Map State Transitions

Setelah mengidentifikasi state fields, langkah berikutnya adalah memetakan transisi dari satu state ke state lainnya.

### 2.1 Button-based Transitions

Transisi state biasanya dipicu oleh button dalam XML view:

```xml
<button name="action_draft" type="object" string="Set to Draft" states="cancel"/>
<button name="action_confirm" type="object" string="Confirm" states="draft,sent"/>
<button name="action_done" type="object" string="Mark Done" states="sale"/>
<button name="action_cancel" type="object" string="Cancel" states="draft,sent,sale"/>
```

**Button Types**:
- `type="object"`: Memanggil method Python
- `type="action"`: Membuka ir.actions record
- `type="workflow"`: Memicu workflow transition (Odoo lama)

### 2.2 Method Implementation

Setiap button type="object" memanggil method tertentu:

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    def action_draft(self):
        """Set order back to draft state"""
        for order in self:
            order.state = 'draft'
        return True

    def action_confirm(self):
        """Confirm the sale order"""
        for order in self:
            # Validation
            if not order.order_line:
                raise UserError(_('No order lines'))

            # Update state
            order.state = 'sale'

            # Trigger related actions
            order._action_notify()
        return True

    def action_done(self):
        """Lock the order (done state)"""
        for order in self:
            order.state = 'done'
        return True

    def action_cancel(self):
        """Cancel the order"""
        for order in self:
            if order.state == 'done':
                raise UserError(_('Cannot cancel a locked order'))
            order.state = 'cancel'
        return True
```

### 2.3 Complete Flow Mapping

Contoh complete workflow mapping untuk sale order:

```
┌──────────┐    action_confirm     ┌──────────┐
│  draft  │ ──────────────────→  │   sent   │
└──────────┘                      └──────────┘
     ↑                                  │
     │                                  │ action_confirm
     │                                  ↓
     │                           ┌──────────┐
     │                           │   sale   │
     │                           └──────────┘
     │                                │
     │                                │ action_done
     │                                ↓
     │                           ┌──────────┐
     │                           │   done   │
     │                           └──────────┘
     │                                │
     │                                │ action_cancel
     │                                ↓
     │                           ┌────────────┐
     └───────────────────────────│  cancel   │
              action_draft        └────────────┘
```

### 2.4 Workflow with Conditions

有些transisi有条件限制:

```python
class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    def action_confirm(self):
        """Confirm purchase order with validation"""
        for order in self:
            # Check minimum orders
            if order.amount_total < order.partner_id.minimum_order_amount:
                raise UserError(
                    _('Minimum order amount is %s') %
                    order.partner_id.minimum_order_amount
                )

            # Check required fields
            if not order.date_planned:
                raise UserError(_('Planned Date is required'))

            order.state = 'purchase'

            # Create picking
            order._create_picking()
        return True
```

### 2.5 Cascading State Changes

一个state变化可能会触发其他相关records的state变化:

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    def action_cancel(self):
        """Cancel order and related records"""
        for order in self:
            # Cancel related picking
            for picking in order.picking_ids:
                if picking.state not in ('done', 'cancel'):
                    picking.action_cancel()

            # Cancel related invoices
            for invoice in order.invoice_ids:
                if invoice.state == 'posted':
                    invoice.button_draft()

            order.state = 'cancel'
        return True
```

### 2.6 Tracing Complete Flow

Untuk melacak complete flow, ikuti langkah-langkah berikut:

1. **Cari state field**: Temukan definition dari selection field
2. **Cari buttons**: Temukan semua button yang mengubah state
3. **Cari methods**: Analisa implementasi dari setiap action method
4. **Cari constraints**: Temukan validasi yang membatasi transisi
5. **Trace related**: Ikuti perubahan ke related models

```bash
# Find state transitions in Python
grep -rn "def action_" --include="*.py" | grep -v "test"

# Find state buttons in XML
grep -rn "name.*action_.*type.*object" --include="*.xml"
```

## Step 3: Analyze Business Rules

Business rules adalah validasi dan constraint yang mengatur apa yang bisa dan tidak bisa dilakukan dalam setiap state.

### 3.1 @api.constrains

`@api.constrains` decorator digunakan untuk validasi yang harus dipenuhi:

```python
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.constrains('order_line', 'state')
    def _check_order_line(self):
        for order in self:
            if order.state in ('sale', 'done'):
                if not order.order_line:
                    raise ValidationError(
                        _('Sales order must have at least one order line.')
                    )

    @api.constrains('date_order', 'state')
    def _check_date(self):
        for order in self:
            if order.state == 'sale':
                if order.date_order > fields.Datetime.now():
                    raise ValidationError(
                        _('Order date cannot be in the future.')
                    )
```

**Characteristics of @api.constrains**:
- Dipanggil saat record di-create atau di-update
- Jika validasi gagal, transaction di-rollback
- Semua fields dalam decorator akan di-load

### 3.2 @api.onchange

`@api.onchange` digunakan untuk validasi dan updating field secara real-time:

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            # Update addresses
            self.partner_invoice_id = self.partner_id.address_get(['invoice'])[
                'invoice'
            ]
            self.partner_shipping_id = self.partner_id.address_get(['delivery'])[
                'delivery'
            ]

            # Update payment terms
            self.payment_term_id = self.partner_id.property_payment_term_id

            # Warning for high risk partner
            if self.partner_id.risk_insurance_limit:
                if self.amount_total > self.partner_id.risk_insurance_limit:
                    return {
                        'warning': {
                            'title': _('High Risk Order'),
                            'message': _(
                                'Order amount exceeds partner insurance limit!'
                            )
                        }
                    }
```

### 3.3 Required Fields by State

有些field只特定state下required:

```python
class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    @api.constrains('date_planned', 'state')
    def _check_date_planned(self):
        for po in self:
            if po.state in ('purchase', 'done'):
                if not po.date_planned:
                    raise ValidationError(
                        _('Planned Date is required for confirmed orders.')
                    )
```

### 3.4 State-based Field Visibility

在XML中使用domain控制字段可见性:

```xml
<field name="date_done" invisible="state != 'done'"/>
<field name="picking_ids" invisible="state == 'draft'"/>
<field name="invoice_ids" readonly="state in ('done', 'cancel')"/>
```

### 3.5 Business Rules Validation Order

Validasi dilakukan dalam urutan berikut:

1. **@api.constrains** - Model-level validation
2. **Required fields** - Database-level constraint
3. **SQL constraints** - Low-level database validation
4. **State transitions** - Method-level validation

```python
class Model(models.Model):
    _name = 'model.name'

    # SQL constraint
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique!')
    ]

    # Python constraint
    @api.constrains('field1', 'field2')
    def _check_fields(self):
        # Validasi logic
        pass
```

### 3.6 Approval Rules

对于需要审批的工作流:

```python
class PurchaseRequest(models.Model):
    _name = 'purchase.request'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    @api.constrains('state', 'request_line')
    def _check_approver(self):
        for request in self:
            if request.state == 'approved':
                if not request.approver_id:
                    raise ValidationError(
                        _('Please assign an approver before approving.')
                    )

    def button_to_approve(self):
        """Submit for approval"""
        for request in self:
            if not request.request_line:
                raise ValidationError(_('Please add at least one line.'))
            request.state = 'to_approve'
        return True

    def button_approve(self):
        """Approve the request"""
        for request in self:
            # Check approval limit
            if request.amount > request.approver_id.approval_limit:
                raise UserError(
                    _('Amount exceeds your approval limit. '
                      'Please contact your manager.')
                )
            request.write({
                'state': 'approved',
                'approver_id': self.env.user.id,
                'approval_date': fields.Datetime.now(),
            })
        return True
```

## Step 4: Document Workflow

Dokumentasi workflow yang baik sangat penting untuk maintenance dan understanding.

### 4.1 State Diagram

Buat state diagram menggunakan format text:

```
┌────────────────────────────────────────────────────────────────────┐
│                         PURCHASE ORDER WORKFLOW                     │
└────────────────────────────────────────────────────────────────────┘

                              ┌─────────┐
                              │  draft  │
                              └────┬────┘
                                   │
                    action_confirm │ action_reject
                                   │ (from to_approve)
                                   ↓
                              ┌───────────┐
               ┌──────────────│ to_approve │
               │              └─────┬───────┘
               │                    │
               │ action_approve     │
               │                    │ action_reject
               │                    ↓
               │              ┌───────────┐
               │              │  approved │
               │              └─────┬─────┘
               │                    │
               │ action_done        │ action_cancel
               │                    ↓
               │              ┌───────────┐
               └─────────────→│   done    │
                              └───────────┘

Legend:
- action_* : Button/Method yang memicu transisi
- States dengan border : Final states
```

### 4.2 Transition Table

Buat tabel transisi yang detail:

| From State | To State | Trigger | Condition | Side Effect |
|------------|----------|---------|-----------|-------------|
| draft | to_approve | button_to_approve | Has lines | Send notification |
| to_approve | approved | button_approve | Approved by user | Set approval_date |
| to_approve | rejected | button_reject | Rejected by user | Clear approver |
| approved | done | button_done | - | Create PO |
| any | cancel | button_cancel | Not done | Cancel related |
| any | draft | button_draft | Was cancelled | Reset all |

### 4.3 Business Rules Summary

| Rule | Description | Error Message |
|------|-------------|----------------|
| Must have lines | PO must have at least one line | 'Please add at least one product line' |
| Required date | Date planned required for confirm | 'Planned date is required' |
| Amount limit | Amount must not exceed limit | 'Amount exceeds approval limit' |
| Partner check | Partner must be active | 'Partner is not active' |

### 4.4 Button Actions Reference

```python
# Dalam model: purchase_request.py
def button_to_approve(self):
    """Submit request for approval"""
    self.write({'state': 'to_approve'})
    # Kirim notifikasi ke approver
    self._send_approval_notification()
    return True

def button_approve(self):
    """Approve the request"""
    for record in self:
        record.write({
            'state': 'approved',
            'approved_by': self.env.uid,
            'approval_date': fields.Datetime.now(),
        })
    return True

def button_reject(self):
    """Reject the request"""
    return {
        'name': 'Reject Request',
        'view_mode': 'form',
        'res_model': 'reject.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
    }
```

## Common State Patterns

### Standard Module States

**Sale Order**:
```
draft → sent → sale → done → cancel
         ↑______│   ↓
                └───────
```

**Purchase Order**:
```
draft → sent → purchase → done → cancel
         ↑______│        ↓
                └──────────
```

**Account Invoice**:
```
draft → posted → cancel → draft (reversed)
              ↓
          paid
```

**Project Task**:
```
draft → todo → in_progress → done → cancel
   ↑              ↓
   └──────────────┘
```

**Stock Picking**:
```
draft → waiting → assigned → done → cancel
           ↓
        confirmed
```

### Approval Workflow Patterns

**Simple Approval**:
```
draft → pending_approval → approved → done
                              ↓
                           rejected (back to draft)
```

**Multi-level Approval**:
```
draft → level1_approval → level2_approval → approved
         ↓                      ↓
      rejected              rejected
```

**State with Amount Threshold**:
```
draft → pending_approval → approved (amount < 1000)
                              ↓
                         manager_approval (amount >= 1000)
```

## Button Analysis

### Button XML Patterns

```xml
<!-- Basic button -->
<button name="action_confirm" type="object" string="Confirm"/>

<!-- Button with icon -->
<button name="action_confirm" type="object" string="Confirm"
        icon="fa-check" class="oe_highlight"/>

<!-- Button with states visibility -->
<button name="action_confirm" type="object" string="Confirm"
        states="draft,sent" class="oe_highlight"/>

<!-- Button with context -->
<button name="action_assign" type="object" string="Assign"
        context="{'assign_to': True}"/>

<!-- Button with confirm dialog -->
<button name="action_cancel" type="object" string="Cancel"
        confirm="Are you sure you want to cancel?"/>

<!-- Split button (dropdown) -->
<div name="actions" class="oe_button_box">
    <button name="action_confirm" type="object" string="Confirm"
            class="oe_highlight"/>
    <button name="action_done" type="object" string="Done"/>
</div>
```

### Button Attributes Reference

| Attribute | Description | Example |
|-----------|-------------|---------|
| name | Method name to call | `action_confirm` |
| type | Button type | `object`, `action`, `workflow` |
| string | Button label | `Confirm` |
| icon | Icon class | `fa-check`, `fa-times` |
| class | CSS classes | `oe_highlight`, `oe_read_only` |
| states | Visible states | `draft,sent,sale` |
| invisible | Condition to hide | `state == 'done'` |
| help | Tooltip text | `Confirm this order` |
| confirm | Confirmation message | `Are you sure?` |

### Method-Button Mapping

**Standard Button Methods**:

```python
# Base document workflow
def action_draft(self):           # Set to draft
def action_confirm(self):         # Confirm document
def action_done(self):            # Mark as done
def action_cancel(self):          # Cancel document
def action_archive(self):         # Archive record
def action_unarchive(self):       # Unarchive record

# Approval workflow
def action_submit(self):          # Submit for approval
def action_approve(self):         # Approve
def action_reject(self):          # Reject
def action_request_approval(self): # Request approval

# Print/Export
def action_print(self):           # Print report
def action_export(self):          # Export data
def action_send_by_email(self):   # Send email

# Related documents
def action_view_invoice(self):    # View related invoice
def action_view_picking(self):    # View related picking
def action_view_delivery(self):   # View delivery
```

## Workflow with Wizard

有些workflow需要通过wizard进行确认:

```python
class CancelReasonWizard(models.TransientModel):
    _name = 'cancel.reason.wizard'
    _description = 'Cancel Reason Wizard'

    reason = fields.Text(string='Cancellation Reason', required=True)

    def action_confirm_cancel(self):
        """Confirm cancellation with reason"""
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')

        if active_model == 'sale.order':
            order = self.env[active_model].browse(active_id)
            order.write({
                'state': 'cancel',
                'cancel_reason': self.reason,
            })

        return {'type': 'ir.actions.act_window_close'}
```

```xml
<!-- Wizard button in form -->
<button name="%(cancel_reason_wizard_action)d" type="action"
        string="Cancel Order"
        states="draft,sent,sale"/>
```

## Advanced Workflow Patterns

### State Machine with Sub-states

```python
class ProjectTask(models.Model):
    _name = 'project.task'

    # Main state
    state = fields.Selection([
        ('draft', 'New'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft')

    # Sub-state for progress
    progress_state = fields.Selection([
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('review', 'In Review'),
    ], string='Progress Status')

    # Block/unblock task
    def button_block(self):
        self.write({'state': 'progress', 'progress_state': 'blocked'})

    def button_unblock(self):
        self.write({'progress_state': 'pending'})
```

### Workflow with Timeout

```python
class ApprovalRequest(models.Model):
    _name = 'approval.request'

    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], default='pending')

    request_date = fields.Datetime(default=fields.Datetime.now)
    approval_deadline = fields.Datetime()

    @api.model
    def _cron_check_expired(self):
        """Check for expired approval requests"""
        expired = self.search([
            ('state', '=', 'pending'),
            ('approval_deadline', '<', fields.Datetime.now())
        ])
        expired.write({'state': 'expired'})
        return True
```

### Workflow with State History

```python
class DocumentWorkflow(models.Model):
    _name = 'document.workflow'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
    ])

    # State history tracking
    state_history = fields.One2many(
        'document.state.history',
        'document_id',
        string='State History'
    )

    def write(self, vals):
        if 'state' in vals:
            old_state = self.state
            new_state = vals['state']
            if old_state != new_state:
                self._create_state_history(old_state, new_state)
        return super().write(vals)

    def _create_state_history(self, old_state, new_state):
        for record in self:
            record.state_history.create({
                'document_id': record.id,
                'from_state': old_state,
                'to_state': new_state,
                'changed_by': self.env.uid,
                'change_date': fields.Datetime.now(),
            })
```

## Output Format

Berikan analisis dalam format berikut:

```markdown
## Workflow Analysis: [Module Name]

### State Machine

| Field | Type | Initial State | States |
|-------|------|---------------|--------|
| state | selection | draft | draft, confirm, done, cancel |

### State Diagram

[ASCII diagram atau penjelasan flow]

### Transitions

| From | To | Trigger | Conditions |
|------|----|---------|------------|
| draft | confirm | button_confirm | Validation passed |
| confirm | done | button_done | - |
| any | cancel | button_cancel | Not in done |

### Business Rules

| Rule | Type | Validation |
|------|------|------------|
| Must have lines | @constrains | order_line exists |
| Date required | @constrains | date_order when confirmed |

### Button Actions

| Button | Method | States Visible |
|--------|--------|----------------|
| Confirm | action_confirm | draft, sent |
| Done | action_done | sale |
| Cancel | action_cancel | draft, sent, sale |
```

## Tips for Effective Workflow Analysis

1. **Start with state field**: Temukan definition selection field pertama
2. **Map all buttons**: Identifikasi semua button yang mengubah state
3. **Trace method implementation**: Ikuti logic dalam setiap action method
4. **Check constraints**: Temukan validasi yang membatasi transisi
5. **Test edge cases**: Coba semua kombinasi state dan validasi
6. **Document thoroughly**: Buat dokumentasi lengkap untuk referensi
7. **Check related models**: Cari cascading effects ke related models

## Examples

### Example 1: Sale Order Workflow

```
## Workflow: Sale Order

### State Machine
- Field: state (selection)
- Initial: draft
- States: draft → sent → sale → done → cancel

### Transitions
- draft → sent: action_quotation_send()
- sent → sale: action_confirm()
- sale → done: action_done()
- any → cancel: action_cancel()
- cancel → draft: action_draft()

### Business Rules
- Must have order lines (constrains)
- Payment term required for confirm
- Cannot cancel if invoice is paid

### Buttons
- Send by Email: action_quotation_send
- Confirm: action_confirm (states: draft,sent)
- Lock: action_done (states: sale)
- Cancel: action_cancel
```

### Example 2: Approval Flow

```
## Workflow: Purchase Request Approval

### State Machine
- Field: state
- Initial: draft
- States: draft → to_approve → approved → done, rejected

### Transitions
- draft → to_approve: button_to_approve
- to_approve → approved: button_approve (limit check)
- to_approve → rejected: button_reject
- approved → done: button_done

### Approval Rules
- < 1000: Self-approval allowed
- 1000-10000: Manager approval required
- > 10000: Director approval required

### Business Rules
- Lines required before submit
- Budget must be available
- Approver cannot be requester
```

### Example 3: Complex State with Multiple Fields

```
## Workflow: Purchase Order (Multi-field)

### State Fields
1. state: Main workflow state
   - States: draft, sent, purchase, done, cancel

2. picking_state: Receiving status
   - States: waiting, assigned, done

3. invoice_state: Invoice status
   - States: no, to_invoice, invoiced, paid

### Complex Transitions
- Main state affects picking and invoice state
- Cancel PO → cancel picking
- Confirm PO → create picking
- Receive goods → update picking_state
- Create invoice → update invoice_state
```
