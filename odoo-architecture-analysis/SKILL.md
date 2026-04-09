---
name: odoo-architecture-analysis
description: |
  Analisis arsitektur modular Odoo - modular structure, API design, integration patterns, CE vs EE differences,
  inheritance chains, service layer patterns. Gunakan ketika:
  - User bertanya tentang arsitektur modul Odoo
  - Perlu memahami modular structure dari custom modules
  - Perlu analisis CE vs EE differences
  - Ingin understand inheritance dan extension patterns
  - Ingin understand service layer dan API design
---

# Odoo Architecture Analysis Skill

## Path Resolution
GUNAKAN odoo-path-resolver untuk mendapatkan paths. Contoh:
```python
paths = resolve()
ce_path = paths['addons']['ce']
ee_path = paths['addons']['ee']
custom_path = paths['addons']['custom'][0]
config = paths['project']['config']
```

## Overview

Skill ini membantu menganalisis arsitektur modular Odoo secara menyeluruh. Odoo adalah platform ERP yang sangat modular, memungkinkan pengembang untuk memperluas dan menyesuaikan fungsionalitas melalui sistem modul yang canggih. Pemahaman mendalam tentang arsitektur ini sangat penting untuk melakukan migrasi, debugging, dan pengembangan fitur baru.

Arsitektur Odoo dibangun di atas beberapa layer utama:
- **Presentation Layer**: XML views, web controllers, portal templates
- **Business Logic Layer**: Models, methods, constraints, computations
- **Data Layer**: PostgreSQL database, XML data files
- **Service Layer**: External APIs, RPC calls, background jobs

Modul-modul Odoo saling berinteraksi melalui mekanisme yang well-defined, memungkinkan customization yang extensif tanpa merusak core functionality.

## Step 1: Identify Module Structure

Langkah pertama dalam analisis arsitektur adalah mengidentifikasi struktur modul. Setiap modul Odoo memiliki struktur direktori dan file-file standar yang harus dipahami.

### 1.1 Module Directory Structure

Modul Odoo standar memiliki struktur berikut:

```
module_name/
├── __init__.py           # Python package initialization
├── __manifest__.py       # Module metadata (Odoo 10+) atau __openerp__.py (Odoo 9-)
├── models/
│   ├── __init__.py
│   ├── model_name.py     # Model definitions
│   └── ...
├── views/
│   ├── model_name_views.xml
│   ├── model_name_templates.xml
│   └── ...
├── controllers/
│   ├── __init__.py
│   ├── main.py
│   └── ...
├── wizards/
│   ├── __init__.py
│   ├── wizard_name.py
│   └── ...
├── reports/
│   ├── __init__.py
│   ├── report_name.py
│   └── ...
├── security/
│   ├── ir.model.access.csv
│   └── ...
├── data/
│   ├── demo.xml
│   └── data.xml
├── static/
│   ├── description/
│   │   └── icon.png
│   ├── src/
│   │   ├── js/
│   │   ├── css/
│   │   └── xml/
│   └── lib/
└── tests/
    ├── __init__.py
    ├── test_model.py
    └── ...
```

### 1.2 Manifest File Analysis

File `__manifest__.py` adalah jantung dari setiap modul Odoo. Berikut adalah contoh manifest lengkap:

```python
{
    'name': "Module Name",
    'version': '19.0.1.0.0',
    'category': 'Category/Subcategory',
    'summary': 'Short description',
    'description': """
Long description of the module
Can contain multiple lines
    """,
    'author': 'Author Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'purchase',
        'stock',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/model_views.xml',
        'views/model_templates.xml',
        'data/model_data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

### 1.3 Identifying Dependencies

Dependencies dalam Odoo sangat penting untuk dipahami. Ada beberapa jenis dependencies:

**Direct Dependencies**: Ditentukan dalam `depends` pada manifest
- `base`: Wajib untuk semua modul
- `sale`, `purchase`, `stock`, `account`: Modul bisnis utama
- `web`: Diperlukan untuk web interface customization

**Indirect Dependencies**: Dependencies dari dependencies
- Jika modul A bergantung pada B, dan B bergantung pada C, maka A secara implisit juga bergantung pada C

**Soft vs Hard Dependencies**:
- `depends`: Hard dependency - modul tidak dapat diinstall tanpa dependency
- `external_dependencies`: Python packages eksternal (misal: `python -m pip install library`)

### 1.4 Extended Models Identification

Untuk mengidentifikasi model yang diperluas oleh modul, lakukan grep untuk:

```python
# Single inheritance
class ModelName(models.Model):
    _inherit = 'original.model'

# Multiple inheritance
class ModelName(models.Model):
    _inherit = ['original.model1', 'original.model2']

# Extension without inheritance
class ModelName(models.Model):
    _name = 'extended.model'
    _inherits = {'original.model': 'field_name'}
```

## Step 2: Analyze CE vs EE

Odoo membedakan antara Community Edition (CE) dan Enterprise Edition (EE). Pemahaman tentang perbedaan ini sangat penting untuk analisis arsitektur.

### 2.1 Directory Structure CE vs EE

**Community Edition (CE)**:
```
odoo19.0-roedl/
└── odoo/
    └── addons/           # Standard addons
```

**Enterprise Edition (EE)**:
```
enterprise-roedl-19.0/
└── enterprise/           # Enterprise-specific modules
```

Dalam project Roedl:
- CE Path: `paths['addons']['ce']`
- EE Path: `paths['addons']['ee']`
- Custom Path: `paths['addons']['custom'][0]`

### 2.2 CE Module Structure

Modul CE terletak di `odoo/addons/` dan mencakup:
- `sale`: Sales management
- `purchase`: Purchase management
- `stock`: Warehouse management
- `account`: Accounting
- `project`: Project management
- `hr`: Human Resources
- `crm`: Customer Relationship Management
- `mrp`: Manufacturing
- `point_of_sale`: POS

### 2.3 EE Module Structure

Modul EE terletak di `enterprise/` dan mencakup:
- `sale_enterprise`: Advanced sale features
- `purchase_requisition`: Purchase requisitions
- `account_enterprise`: Advanced accounting
- `hr_payroll`: Payroll management
- `industry_fsm`: Field Service Management
- `documents`: Document management
- `approvals`: Approval workflows
- `studio`: Odoo Studio customization

### 2.4 Inheritance Analysis CE vs EE

Modul EE biasanya extends modul CE. Contohnya:

**CE base model** (sale.order):
```python
# odoo/addons/sale/models/sale_order.py
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Sales Order'

    name = fields.Char(string='Order Reference', required=True)
    state = fields.Selection(selection=[
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, tracking=True)
```

**EE extended model** (sale_enterprise):
```python
# enterprise/enterprise/sale_enterprise/models/sale_order.py
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Menambahkan field untukEnterprise features
    sale_order_template_id = fields.Many2one(
        'sale.order.template', string='Quotation Template',
        check_company=True)
    incoterm = fields.Many2one(
        'account.incoterms', 'Incoterm',
        help="International Commercial Terms are a series of predefined commercial terms")
```

### 2.5 Common EE Features

Fitur-fitur yang hanya tersedia di EE:
- `hr_payroll`: Payroll processing
- `industry_fsm`: Field Service Management
- `documents`: Advanced document management
- `approvals`: Approval workflow engine
- `studio`: No-code customization
- Advanced reporting
- Budget management
- Contract management

### 2.6 CE vs EE Testing Strategy

Ketika menganalisis modul custom:
1. Test selalu di EE terlebih dahulu karena EE include semua fitur CE
2. Jika modul depends pada `hr_payroll`, itu WAJIB EE-only
3. Untuk modul CE-only, test di CE environment

## Step 3: Analyze Inheritance Chain

Inheritance adalah fitur utama Odoo yang memungkinkan extensibility. Memahami berbagai pattern inheritance sangat penting.

### 3.1 Classical Inheritance (_inherit)

Pattern paling umum untuk extends model:

```python
from odoo import models, fields, api

class SaleOrderExtension(models.Model):
    _name = 'sale.order.extension'
    _inherit = 'sale.order'
    _description = 'Sale Order Extension'

    # Menambahkan field baru
    x_custom_field = fields.Char(string='Custom Field')

    # Override existing method
    def action_confirm(self):
        # Custom logic before parent call
        result = super().action_confirm()
        # Custom logic after parent call
        return result
```

**Karakteristik**:
- Model baru memiliki semua field dan method dari parent
- Bisa menambahkan field dan method baru
- Bisa override method parent dengan `super()`

### 3.2 Prototype Inheritance (_inherit dengan list)

Odoo 13+ mendukung multiple inheritance:

```python
class SaleOrderAdvanced(models.Model):
    _name = 'sale.order.advanced'
    _inherit = ['sale.order', 'mail.thread']
    _description = 'Sale Order Advanced'
```

Dengan ini, model mendapatkan:
- Semua field dari `sale.order`
- Semua field dari `mail.thread` (biasanya include `message_ids`, `message_follower_ids`)
- Semua method dari kedua parent

### 3.3 Delegation Inheritance (_inherits)

Untuk composed models dimana model baru memiliki relasi 1:1 ke parent:

```python
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherits = {'product.product': 'product_id'}

    product_id = fields.Many2one(
        'product.product', string='Product',
        required=True, delegate=True)
```

**Karakteristik**:
- child model menyimpan data di parent model
- Akses ke parent field melalui delegasi
- Lebih efisien untuk data yang jarang berbeda

### 3.4 Extension Points

Odoo menyediakan banyak extension points:

**1. Adding Fields**:
```python
class ExtendedModel(models.Model):
    _inherit = 'original.model'

    x_new_field = fields.Char(string='New Field')
```

**2. Adding Computed Fields**:
```python
class ExtendedModel(models.Model):
    _inherit = 'original.model'

    x_computed_field = fields.Char(
        string='Computed Field',
        compute='_compute_x_field',
        store=True)

    @api.depends('existing_field')
    def _compute_x_field(self):
        for record in self:
            record.x_computed_field = f"Computed: {record.existing_field}"
```

**3. Adding Related Fields**:
```python
class ExtendedModel(models.Model):
    _inherit = 'original.model'

    x_related_field = fields.Char(
        string='Related Field',
        related='partner_id.name',
        store=True)
```

**4. Adding Constraints**:
```python
class ExtendedModel(models.Model):
    _inherit = 'original.model'

    @api.constrains('field1', 'field2')
    def _check_constraint(self):
        for record in self:
            if record.field1 and record.field2:
                if record.field1 == record.field2:
                    raise ValidationError("Field1 cannot equal Field2")
```

**5. Adding Onchange Methods**:
```python
class ExtendedModel(models.Model):
    _inherit = 'original.model'

    @api.onchange('field1')
    def _onchange_field1(self):
        if self.field1:
            self.field2 = self.field1 * 2
```

### 3.5 Override Patterns

**Override Fields**:
```python
class OverrideField(models.Model):
    _inherit = 'original.model'

    # Override existing field
    name = fields.Char(
        string='Custom Name',  # Override string
        size=100,              # Override size
        required=False)        # Override required
```

**Override Defaults**:
```python
class OverrideDefault(models.Model):
    _inherit = 'original.model'

    def _get_default_field(self):
        return 'default_value'

    field_id = fields.Char(
        string='Field',
        default=_get_default_field)
```

**Override Methods**:
```python
class OverrideMethod(models.Model):
    _inherit = 'original.model'

    def existing_method(self, arg1):
        # Custom implementation
        result = super().existing_method(arg1)
        return result
```

## Step 4: Analyze Service Layer

Service layer dalam Odoo menangani interaksi dengan external systems dan API.

### 4.1 Controller Patterns

**HTTP Controllers**:
```python
from odoo import http
from odoo.http import request

class CustomController(http.Controller):

    @http.route('/my/route', type='http', auth='public', website=True)
    def my_route(self, **kwargs):
        values = {'variable': 'value'}
        return request.render('module.template_id', values)

    @http.route('/my/api', type='json', auth='user')
    def my_api(self, **kwargs):
        return {'status': 'success', 'data': []}

    @http.route('/my/upload', type='http', auth='user', csrf=False)
    def my_upload(self, **kwargs):
        file = kwargs.get('file')
        # Process file
        return request.make_response('OK')
```

**Controller Inheritance**:
```python
class ExtendedController(http.Controller):
    _inherit = 'original.controller'

    # Override existing route
    def _get_website_context(self, **kwargs):
        ctx = super()._get_website_context(**kwargs)
        ctx['custom_key'] = 'custom_value'
        return ctx
```

### 4.2 API Endpoints

Odoo menyediakan beberapa jenis API:

**XML-RPC**:
```python
import xmlrpc.client

url = 'http://localhost:8069'
db = 'roedl'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username,password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Execute method
result = models.execute_kw(
    db, uid, password,
    'sale.order', 'search_read',
    [[['state', '=', 'sale']]],
    {'fields': ['name', 'state', 'partner_id']}
)
```

**JSON-RPC**:
```javascript
// Web client using jsonrpc
var url = 'http://localhost:8069/jsonrpc';
var db = 'roedl';

odoo.jsonrpc(url, {
    service: 'object',
    method: 'execute',
    args: [db, uid, password, 'sale.order', 'search_read', [], {}]
}).then(function(result) {
    console.log(result);
});
```

### 4.3 Model Service Methods

**CRUD Operations**:
```python
# Create
new_record = env['model.name'].create({'field': 'value'})

# Read
records = env['model.name'].search([('field', '=', 'value')])
record = env['model.name'].browse(id)
name = record.name
values = record.read(['field1', 'field2'])

# Update
record.write({'field': 'new_value'})
records.write([{'field': 'value1'}, {'field': 'value2'}])

# Delete
record.unlink()
records.unlink()
```

**Search Operations**:
```python
# Basic search
records = env['model.name'].search([('field', '=', 'value')])

# Domain operators
domain = [
    ('field1', '=', 'value1'),
    ('field2', 'in', ['a', 'b', 'c']),
    ('field3', 'not in', ['x', 'y']),
    ('field4', 'ilike', 'pattern'),
    ('field5', '>=', 100),
    '|', ('field6', '=', 'a'), ('field6', '=', 'b'),
    '!', ('field7', '=', 'value'),
]

# Logical operators in domain
# '&' - AND (default)
# '|' - OR
# '!' - NOT

# Search with limits
records = env['model.name'].search(
    domain,
    offset=0,
    limit=10,
    order='name ASC'
)
```

**Computed and Related Fields**:
```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount_total',
        store=True)

    @api.depends('order_line.price_total')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(
                order.order_line.mapped('price_total'))
```

### 4.4 Background Jobs

**Using Queue Job**:
```python
from odoo.addons.queue_job.models.job import job

class MyModel(models.Model):
    _name = 'my.model'

    @job
    def process_async(self):
        # Long-running operation
        for record in self:
            # Process record
            pass

    def button_process(self):
        self.with_context(
            queue_job__uuid='unique-uuid'
        ).process_async.delay()
```

**Using Cron**:
```python
class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def _cron_daily_task(self):
        # Run daily
        records = self.search([('state', '=', 'draft')])
        for record in records:
            record.action_process()
        return True
```

### 4.5 Integration Patterns

**Webhooks**:
```python
class WebhookController(http.Controller):

    @http.route('/webhook/external', type='json', auth='none',
                cors='*', csrf=False)
    def handle_webhook(self, **payload):
        # Validate webhook signature
        # Process payload
        # Create/update records
        return {'status': 'received'}
```

**External API**:
```python
import requests

class ExternalAPI(models.Model):
    _name = 'external.api'

    def call_external_service(self, endpoint, data):
        url = f"https://api.example.com/{endpoint}"
        headers = {'Authorization': f'Bearer {self._get_token()}'}

        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(f"API Error: {response.text}")
```

## Step 5: Document Architecture

Dokumentasi arsitektur yang baik sangat penting untuk maintenance dan onboarding.

### 5.1 Module Dependencies Diagram

Buat diagram yang menunjukkan:
- Modul ini depends pada modul apa saja
- Modul lain apa yang depend pada modul ini
- External system integrations

```
┌─────────────────────────────────────────────────────────────┐
│                    Current Module                            │
│                    (asb_project)                            │
├─────────────────────────────────────────────────────────────┤
│  Dependencies:                                              │
│  ├── base (required)                                        │
│  ├── project (core)                                         │
│  ├── account (accounting)                                   │
│  └── mail (notifications)                                   │
├─────────────────────────────────────────────────────────────┤
│  Extended Models:                                            │
│  ├── project.project                                        │
│  └── project.task                                           │
├─────────────────────────────────────────────────────────────┤
│  External Integrations:                                      │
│  ├── None (internal module only)                           │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Extended Models Documentation

**project.project**:
```python
# Base fields inherited:
- id, create_uid, create_date, write_uid, write_date
- name, description, active, partner_id
- sequence, color, privacy_visibility

# Fields added by project:
- tasks (one2many)
- planned_hours
- resource_calendar_id

# Fields added by asb_project:
- x_custom_field (char)
- x_approval_required (boolean)
```

### 5.3 Custom Modifications Summary

Buat tabel yang merangkum semua kustomisasi:

| Aspect | Original | Modification | Reason |
|--------|----------|--------------|--------|
| Model | project.task | Added fields | Custom workflow |
| View | task_form | Added tab | Additional info |
| Method | action_confirm | Added validation | Business rule |
| Constraint | - | Added _check_budget | Budget control |

## Common Patterns

### Pattern Reference Table

| Pattern | Use Case | Example |
|---------|----------|---------|
| _inherit | Extend single model | `class Extended(models.Model): _inherit = 'base.model'` |
| _inherit[] | Extend multiple models | `class Extended(models.Model): _inherit = ['model1', 'model2']` |
| _inherits | Delegate to other model | `class Child(models.Model): _inherits = {'parent': 'parent_id'}` |
| _name | Create new model | `class NewModel(models.Model): _name = 'new.model'` |
| _table | Custom table name | `class Model(models.Model): _table = 'custom_table'` |
| _order | Default ordering | `class Model(models.Model): _order = 'name, id'` |
| _rec_name | Display name | `class Model(models.Model): _rec_name = 'reference'` |

### Service Layer Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| @model | HTTP controller | `@http.route('/route', type='http', auth='user')` |
| @job | Background job | `@job` decorator + `.delay()` |
| @api.model | Model method | `@api.model def method(self):` |
| @api.one | Record processing | `@api.one def method(self):` (deprecated Odoo 11+) |

## Quick Reference

### Path Reference

Gunakan `paths = resolve()` untuk mendapatkan dynamic paths:

| Component | Dynamic Path |
|-----------|---------------|
| CE Modules | `paths['addons']['ce']` |
| EE Modules | `paths['addons']['ee']` |
| Custom Modules | `paths['addons']['custom'][0]` |
| Odoo Config | `paths['project']['config']` |
| Database | `paths['database']['name']` |

### Version Reference

| Odoo Version | Manifest Version Format |
|--------------|-------------------------|
| Odoo 15 | `15.0.1.0.0` |
| Odoo 19 | `19.0.1.0.0` |

### Common Migration Changes

| Odoo 15 | Odoo 19 |
|---------|---------|
| `<tree>` view | `<list>` view |
| `<form>` view | Same (no change) |
| `attrs` | `invisible`, `readonly` |
| `_onchange_*` | `_onchange_*` (still supported) |
| `states` attribute | `readonly` / `invisible` |
| `pbkdf2` password | Same (no change) |

## Output Format

Berikan analisis dalam format berikut:

```markdown
## Module Architecture

### Module Information
- **Name**: nama_modul
- **Version**: 19.0.1.0.0
- **Category**: Category/Subcategory
- **Dependencies**: base, sale, account

### Dependencies
<!-- Diagram atau tabel dependency -->

### Inheritance Chain
<!-- Penjelasan inheritance chain -->

### Extension Points
<!-- Daftar semua extensibility points -->

### CE vs EE Analysis
<!-- Perbedaan CE vs EE jika ada -->

### Service Layer
<!-- Controllers, APIs, Jobs -->
```

## Examples

### Example 1: Analyzing hr_course Module

```
## Module: hr_course (asb_project)

### Dependencies
- base (required)
- hr (required)
- mail (notifications)

### Inheritance Chain
- hr.employee.course -> Extended with custom fields
- hr.course -> Added approval workflow

### Extension Points
1. Fields: x_approval_required, x_approver_ids
2. Methods: action_submit, action_approve
3. Views: Added custom tab

### CE vs EE
- Uses: hr.course (CE module)
- No EE-specific dependencies
```

### Example 2: Analyzing invoice_merging Module

```
## Module: invoice_merging

### Dependencies
- account (required)
- sale (optional for sale orders)

### Inheritance Chain
- account.move -> Extended with merge capability

### Extension Points
1. Fields: x_merge_enabled, x_merged_from
2. Methods: action_merge_invoices, _get_mergeable_invoices
3. Business Rules: Validation for merge conditions

### CE vs EE
- Full CE compatibility
- Uses standard account.move model
```

## Tips for Effective Analysis

1. **Always check manifest first**: Understand dependencies before diving deep
2. **Use Grep for inheritance**: Find all `_inherit`, `_inherits`, `_name` occurrences
3. **Compare CE vs EE**: Start with CE, then check EE for extensions
4. **Map all extension points**: Document every field, method, view override
5. **Trace business logic**: Follow method calls to understand flow
6. **Test incrementally**: After understanding, test each component
7. **Document findings**: Keep architecture documentation updated
