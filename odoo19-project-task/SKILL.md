---
name: odoo19-project-task
description: Create Project Task management model dan view untuk Odoo 19. Gunakan skill ini ketika user ingin membuat task management, project tracking, atau extend project.task standard.
---

# Odoo 19 Project Task Generator

Skill ini digunakan untuk membuat Project Task-related models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Membuat custom project/task management
- Extending project.task model
- Task tracking dan milestone management
- Project timesheet integration

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Task model type**: Extend project.task atau create new
3. **Fields yang dibutuhkan**: Task-specific fields
4. **Dependencies**: project, timesheet, etc.

## Extending project.task

### Basic Extension
```python
from odoo import models, fields

class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    # Custom fields
    task_code = fields.Char(string='Task Code')
    estimated_hours = fields.Float(string='Estimated Hours')
```

## Complete Project Task Extension

```python
from odoo import models, fields, api, _

class ProjectTaskExtended(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'mail.thread', 'mail.activity.mixin']
    _description = 'Project Task (Extended)'

    # Task Identification
    task_code = fields.Char(
        string='Task Code',
        required=True,
        copy=False,
        default=lambda self: _('New'),
    )
    sequence = fields.Integer(default=10)

    # Task Details
    name = fields.Char(required=True, tracking=True)
    description = fields.Html(string='Description')

    # Project Relation
    project_id = fields.Many2one(required=True, tracking=True)

    # Task Status
    stage_id = fields.Many2one('project.task.type', string='Stage')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], default='1', tracking=True)

    # Dates
    date_assign = fields.Datetime(string='Assigned Date')
    date_deadline = fields.Date(string='Deadline', tracking=True)
    date_finished = fields.Datetime(string='Finished Date')

    # Planning
    planned_hours = fields.Float(string='Planned Hours')
    progress = fields.Float(string='Progress', default=0.0)

    # Resources
    user_id = fields.Many2one(tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer')

    # Tags
    tag_ids = fields.Many2many('project.tags', string='Tags')

    # Subtasks
    child_ids = fields.One2many(
        'project.task',
        'parent_id',
        string='Subtasks',
    )
    parent_id = fields.Many2one(
        'project.task',
        string='Parent Task',
        index=True,
    )
    subtask_count = fields.Integer(
        string='Subtask Count',
        compute='_compute_subtask_count',
    )

    # Milestone
    milestone_id = fields.Many2one(
        'project.milestone',
        string='Milestone',
        domain="[('project_id', '=', project_id)]",
    )

    # Custom Fields
    category = fields.Selection([
        ('development', 'Development'),
        ('design', 'Design'),
        ('testing', 'Testing'),
        ('deployment', 'Deployment'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ], string='Category')

    @api.depends('child_ids')
    def _compute_subtask_count(self):
        for task in self:
            task.subtask_count = len(task.child_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('task_code', _('New')) == _('New'):
                vals['task_code'] = self.env['ir.sequence'].next_by_code(
                    'project.task.code'
                ) or _('New')
        return super().create(vals_list)

    def action_finished(self):
        self.write({
            'date_finished': fields.Datetime.now(),
            'progress': 100,
            'stage_id': self.env.ref('project.project_task_stage_done').id,
        })
```

## Project Task Type (Stage)
```python
class ProjectTaskType(models.Model):
    _name = 'project.task.type'
    _description = 'Task Stage'
    _order = 'sequence,id'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(default=10)
    project_ids = fields.Many2many(
        'project.project',
        string='Projects',
    )
    legend_blocked = fields.Char(string='Red Legend')
    legend_in_progress = fields.Char(string='Blue Legend')
    legend_done = fields.Char(string='Green Legend')
    fold = fields.Boolean(string='Folded in Kanban')
    is_closed = fields.Boolean(string='Closed Stage')
```

## Project Tags
```python
class ProjectTags(models.Model):
    _name = 'project.tags'
    _description = 'Project Tags'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index', default=10)
    project_ids = fields.Many2many(
        'project.project',
        string='Projects',
    )
```

## View Integration

### Form View Extension
```xml
<record id="view_task_form_extended" model="ir.ui.view">
    <field name="name">project.task.form.extended</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_form2"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='project_id']" position="after">
            <field name="task_code"/>
            <field name="category"/>
        </xpath>
        <xpath expr="//field[@name='date_deadline']" position="after">
            <field name="planned_hours"/>
            <field name="progress"/>
        </xpath>
        <xpath expr="//field[@name='tag_ids']" position="before">
            <field name="milestone_id"/>
        </xpath>
    </field>
</record>
```

### Kanban View
```xml
<record id="view_task_kanban_extended" model="ir.ui.view">
    <field name="name">project.task.kanban.extended</field>
    <field name="model">project.task</field>
    <field name="inherit_id" ref="project.view_task_kanban"/>
    <field name="arch" type="xml">
        <xpath expr="//div[hasclass('o_kanban_record_body')]" position="inside">
            <div class="oe_kanban_bottom_left">
                <field name="progress"/>
            </div>
            <div class="oe_kanban_bottom_right">
                <field name="task_code"/>
            </div>
        </xpath>
    </field>
</record>
```

## Best Practices

1. **Inherit dari project.task** untuk maintain compatibility dengan Project app
2. **Use stage_id** untuk task lifecycle management
3. **Enable tracking** untuk important fields
4. **Consider subtask hierarchy** untuk large projects
5. **Integrate dengan timesheet** jika perlu tracking hours

## Dependencies

Module ini memerlukan:
- `project` (built-in)
- Optional: `project_timesheet`, `project_account`
