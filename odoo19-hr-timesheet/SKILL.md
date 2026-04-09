---
name: odoo19-hr-timesheet
description: Create HR Timesheet management model untuk Odoo 19. Gunakan skill ini ketika user ingin membuat timesheet tracking, employee time logging, atau extend account.analytic.line.
---

# Odoo 19 HR Timesheet Generator

Skill ini digunakan untuk membuat HR Timesheet models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Membuat timesheet tracking system
- Employee time logging
- Project time tracking
- Extending account.analytic.line

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Timesheet type**: Employee, Project, atau Task based
3. **Fields yang dibutuhkan**: Custom fields

## Extending account.analytic.line

```python
from odoo import models, fields, api

class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = 'account.analytic.line'

    # Custom fields
    employee_id = fields.Many2one('hr.employee', string='Employee')
    timesheet_code = fields.Char(string='Timesheet Code')
```

## Complete Timesheet Extension

```python
from odoo import models, fields, api, _

class AccountAnalyticLineExtended(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['account.analytic.line', 'mail.thread']
    _description = 'Analytic Line (Timesheet)'

    # Timesheet Identification
    timesheet_code = fields.Char(
        string='Timesheet Code',
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )

    # Employee Relation
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )

    # Project & Task
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        domain="[('project_id', '=', project_id)]",
    )

    # Time Details
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    unit_amount = fields.Float(
        string='Duration',
        default=0.0,
        tracking=True,
    )

    # Currency & Amount
    amount = fields.Monetary(
        string='Amount',
        compute='_compute_amount',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # Employee hourly rate
    hourly_rate = fields.Monetary(
        string='Hourly Rate',
        related='employee_id.timesheet_cost',
        store=True,
    )

    # Description
    name = fields.Text(string='Description')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approved', 'Approved'),
        ('invoiced', 'Invoiced'),
        ('refused', 'Refused'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('unit_amount', 'hourly_rate')
    def _compute_amount(self):
        for line in self:
            line.amount = line.unit_amount * line.hourly_rate

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('timesheet_code', _('New')) == _('New'):
                vals['timesheet_code'] = self.env['ir.sequence'].next_by_code(
                    'account.analytic.line.timesheet'
                ) or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_refuse(self):
        self.write({'state': 'refused'})
```

## Employee Timesheet Summary

```python
class HrEmployeeTimesheet(models.Model):
    _name = 'hr.employee.timesheet.summary'
    _description = 'Employee Timesheet Summary'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)

    total_hours = fields.Float(string='Total Hours', compute='_compute_total')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total')

    currency_id = fields.Many2one('res.currency', string='Currency')

    timesheet_line_ids = fields.Many2many(
        'account.analytic.line',
        string='Timesheet Lines',
    )

    @api.depends('timesheet_line_ids')
    def _compute_total(self):
        for record in self:
            record.total_hours = sum(record.timesheet_line_ids.mapped('unit_amount'))
            record.total_amount = sum(record.timesheet_line_ids.mapped('amount'))
```

## Best Practices

1. **Inherit dari account.analytic.line** untuk compatibility
2. **Link ke hr.employee** untuk employee tracking
3. **Use project/task relations** untuk project timesheets
4. **Enable tracking** untuk important fields

## Dependencies

- `hr` (built-in)
- `project` (for project/task)
- `sale_timesheet` (for invoicing)
