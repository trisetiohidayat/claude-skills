---
name: odoo19-hr-employee
description: Create HR Employee management model dan fields untuk Odoo 19. Gunakan skill ini ketika user ingin membuat modul HR employee, employee attributes, employee payroll, atau extend hr.employee standard.
---

# Odoo 19 HR Employee Generator

Skill ini digunakan untuk membuat HR Employee-related models di Odoo 19.

## When to Use

Gunakan skill ini ketika:
- Ingin membuat custom employee fields
- Membuat employee attributes/module
- Extending hr.employee model
- Employee-related features (payroll, attributes, etc.)

## Input yang Diperlukan

1. **Module name**: Nama module custom
2. **Employee model type**: Extend hr.employee atau create new
3. **Fields yang dibutuhkan**: Employee-specific fields
4. **Dependencies**: hr, hr_contract, etc.

## Extending hr.employee

### Basic Extension
```python
from odoo import models, fields

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    # Custom fields
    employee_code = fields.Char(string='Employee Code')
    joining_date = fields.Date(string='Joining Date')
    department_id = fields.Many2one(inherited=True)
```

### Extended Employee with Custom Fields
```python
from odoo import models, fields, api

class HrEmployeeExtended(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Employee (Extended)'

    # Identification
    employee_code = fields.Char(
        string='Employee Code',
        required=True,
        copy=False,
        default=lambda self: _('New'),
    )
    nik = fields.Char(string='NIK', size=16)
    bpjs_number = fields.Char(string='BPJS Number')

    # Employment Info
    employment_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('freelance', 'Freelance'),
    ], string='Employment Type', default='permanent')

    joining_date = fields.Date(string='Joining Date')
    probation_end_date = fields.Date(string='Probation End Date')
    contract_end_date = fields.Date(string='Contract End Date')

    # Organizational
    department_id = fields.Many2one(inherited=True)
    job_id = fields.Many2one(inherited=True)
    parent_id = fields.Many2one(inherited=True)

    # Custom Related Fields
    skill_ids = fields.Many2many(
        'hr.skill',
        string='Skills',
    )
    certificate_ids = fields.One2many(
        'hr.employee.certificate',
        'employee_id',
        string='Certificates',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_code', _('New')) == _('New'):
                vals['employee_code'] = self.env['ir.sequence'].next_by_code(
                    'hr.employee.code'
                ) or _('New')
        return super().create(vals_list)
```

## Employee Certificate Model
```python
class HrEmployeeCertificate(models.Model):
    _name = 'hr.employee.certificate'
    _description = 'Employee Certificate'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    name = fields.Char(string='Certificate Name', required=True)
    certificate_type = fields.Selection([
        ('education', 'Education'),
        ('training', 'Training'),
        ('skill', 'Skill Certification'),
        ('language', 'Language'),
        ('other', 'Other'),
    ], string='Type')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    issuing_authority = fields.Char(string='Issuing Authority')
    certificate_number = fields.Char(string='Certificate Number')
    active = fields.Boolean(default=True)
```

## Complete Module Structure

### Model (models/hr_employee_extended.py)
```python
from odoo import models, fields, api, _

class HrEmployeeExtended(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Employee (Extended)'

    # Personal Info - Extended
    place_of_birth = fields.Char(string='Place of Birth')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ], string='Marital Status')
    dependent_count = fields.Integer(string='Number of Dependents', default=0)

    # Employment Details
    employee_code = fields.Char(
        string='Employee Code',
        required=True,
        copy=False,
        default=lambda self: _('New'),
    )
    employment_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ], string='Employment Type', default='permanent')

    joining_date = fields.Date(string='Joining Date')
    probation_end_date = fields.Date(string='Probation End Date')

    # Bank Details
    bank_account_id = fields.Many2one(inherited=True)

    # Documents
    id_number = fields.Char(string='ID Number (KTP)')
    passport_number = fields.Char(string='Passport Number')
    tax_id = fields.Char(string='Tax ID (NPWP)')

    # Custom Relations
    certificate_ids = fields.One2many(
        'hr.employee.certificate',
        'employee_id',
        string='Certificates',
    )
    training_ids = fields.One2many(
        'hr.employee.training',
        'employee_id',
        string='Trainings',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_code', _('New')) == _('New'):
                vals['employee_code'] = self.env['ir.sequence'].next_by_code(
                    'hr.employee.code'
                ) or _('New')
        return super().create(vals_list)
```

### Security (security/hr_security.xml)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="hr_employee_category_user" model="res.groups">
        <field name="name">Employee/User</field>
        <field name="category_id" ref="base.module_category_human_resources"/>
    </record>
</odoo>
```

### View Extension (views/hr_employee_view.xml)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_employee_form_extended" model="ir.ui.view">
        <field name="name">hr.employee.form.extended</field>
        <field name="model">hr.employee</field>
        <field name="inherit_id" ref="hr.view_employee_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='department_id']" position="after">
                <field name="employee_code"/>
                <field name="employment_type"/>
                <field name="joining_date"/>
            </xpath>
            <xpath expr="//field[@name='birthday']" position="after">
                <field name="place_of_birth"/>
                <field name="marital_status"/>
            </xpath>
            <xpath expr="//field[@name='identification_id']" position="after">
                <field name="tax_id"/>
            </xpath>
        </field>
    </record>
</odoo>
```

## Common Patterns

### Employee with Contract Integration
```python
class HrEmployeeWithContract(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'hr.contract']

    # Contract info directly on employee
    contract_id = fields.Many2one(
        'hr.contract',
        string='Current Contract',
        compute='_compute_current_contract',
        store=True,
    )
    contract_start_date = fields.Date(
        string='Contract Start',
        related='contract_id.date_start',
        store=True,
    )
    contract_end_date = fields.Date(
        string='Contract End',
        related='contract_id.date_end',
        store=True,
    )

    @api.depends('contract_ids.state')
    def _compute_current_contract(self):
        for emp in self:
            active_contracts = emp.contract_ids.filtered(
                lambda c: c.state == 'open'
            )
            emp.contract_id = active_contracts[:1]
```

### Employee Skills & Competencies
```python
class HrEmployeeSkill(models.Model):
    _name = 'hr.employee.skill'
    _description = 'Employee Skill'

    employee_id = fields.Many2one('hr.employee', required=True)
    skill_id = fields.Many2one('hr.skill', required=True)
    level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ], string='Level')
    years_experience = fields.Integer(string='Years of Experience')
```

## Best Practices

1. **Always inherit dari hr.employee** untuk maintain compatibility
2. **Use sequences** untuk employee code numbering
3. **Leverage hr module's built-in fields** sebelum membuat duplicate
4. **Consider hr_contract integration** untuk employment info
5. **Add proper access rights** dengan security groups

## Dependencies

Module ini memerlukan:
- `hr` (built-in)
- Optional: `hr_contract`, `hr_skills`, `hr_attendance`
