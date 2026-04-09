---
name: odoo-module-structure
description: |
  Module architecture patterns dan best practices untuk Odoo. Gunakan skill ini ketika:
  - Mendesain module structure baru
  - Memahami arsitektur modul yang ada
  - Need modular design patterns
  - Mau organize code dengan baik
  - Understanding CE vs EE architecture

  Fokus pada bagaimana mengorganisasi module agar maintainable dan extensible.
---

# Odoo Module Structure Skill

## Overview

Skill ini membantu memahami dan mendesain struktur modul Odoo yang baik.

## Module Structure Basics

### Standard Odoo Module Layout

```
module_name/
├── __init__.py              # Module initialization
├── __manifest__.py          # Module metadata (or __openerp__.py for older versions)
├── models/
│   ├── __init__.py
│   ├── model_1.py
│   └── model_2.py
├── views/
│   ├── __init__.py
│   ├── model_1_views.xml
│   └── model_2_views.xml
├── controllers/
│   ├── __init__.py
│   └── main.py
├── wizards/
│   ├── __init__.py
│   └── wizard_model.py
├── reports/
│   ├── __init__.py
│   └── report_model.py
├── security/
│   ├── __init__.py
│   ├── ir.model.access.csv
│   └── ir.rule.xml
├── data/
│   ├── __init__.py
│   └── demo_data.xml
├── i18n/
│   ├── __init__.py
│   └── module_name.pot
├── static/
│   ├── src/
│   │   ├── js/
│   │   ├── xml/
│   │   └── css/
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    └── test_model.py
```

## Module Design Patterns

### 1. Single Model Module

Untuk modul sederhana dengan satu model:

```
simple_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── simple_model.py
├── views/
│   └── simple_model_views.xml
└── security/
    └── simple_model_access.csv
```

### 2. Multi-Model Module

Untuk modul kompleks dengan banyak model:

```
complex_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── main_model.py      # Primary model
│   ├── line_model.py     # One2many lines
│   └── settings.py       # Configuration
├── views/
│   ├── main_model_views.xml
│   ├── line_model_views.xml
│   └── settings_views.xml
├── wizards/
│   └── wizard_model.py
├── reports/
│   └── report_model.py
└── security/
    └── complex_module_security.xml
```

### 3. Module with API

```
api_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── api_model.py      # Main API model
│   └── api_key.py       # API key management
├── controllers/
│   ├── __init__.py
│   └── api_controller.py
├── security/
│   └── api_key_access.xml
└── static/
    └── src/
        └── js/
            └── api_client.js
```

### 4. Module with Portal

```
portal_module/
├── __init__.py
├── __manifest__.py
├── models/
├── views/
├── controllers/
│   ├── __init__.py
│   ├── website.py       # Website controllers
│   └── portal.py        # Portal controllers
├── views/
│   ├── portal_templates.xml
│   └── website_views.xml
└── static/
    └── src/
        └── scss/
            └── portal.scss
```

## Model Organization

### 1. By Feature

```
models/
├── __init__.py
├── sale.py        # All sale-related models
├── purchase.py    # All purchase-related models
├── inventory.py   # All inventory-related models
└── reporting.py   # All reporting models
```

### 2. By Domain

```
models/
├── __init__.py
├── hr/
│   ├── __init__.py
│   ├── employee.py
│   └── department.py
└── project/
    ├── __init__.py
    ├── project.py
    └── task.py
```

## Inheritance Patterns

### 1. Extend Existing Model

```python
# In your_module/models.py
from odoo import models, fields

class SaleOrderExtended(models.Model):
    _inherit = 'sale.order'

    custom_field = fields.Char(string='Custom Field')
```

### 2. Create New Model with Inheritance

```python
# Create new model that inherits from multiple
class CustomSaleOrder(models.Model):
    _name = 'custom.sale.order'
    _description = 'Custom Sale Order'
    _inherit = ['sale.order', 'mail.thread']

    # Add new fields
    custom_field = fields.Char()
```

### 3. Delegate Inheritance

```python
class SaleOrderLineProxy(models.Model):
    _name = 'sale.order.line.proxy'
    _description = 'Sale Order Line Proxy'
    _inherits = {'sale.order.line': 'line_id'}

    line_id = fields.Many2one('sale.order.line', required=True, ondelete='cascade')
    custom_field = fields.Char()
```

## Module Dependencies

### 1. Required Dependencies

```python
# __manifest__.py
{
    'name': 'My Module',
    'depends': [
        'base',           # Always required
        'sale',          # Requires sale module
        'stock',         # Requires stock module
    ],
}
```

### 2. Optional Dependencies

```python
# Handle optional dependencies
def some_method(self):
    # Check if module is installed
    if self.env.registry.get('sale'):
        # Do something with sale
        pass
```

### 3. Soft Dependencies

```python
{
    'name': 'My Module',
    'depends': ['base'],
    'soft_dependency': ['sale'],  # Loaded after, not required
}
```

## Data Organization

### 1. Demo Data

```xml
<!-- data/demo_data.xml -->
<odoo>
    <data noupdate="1">
        <record id="demo_partner_1" model="res.partner">
            <field name="name">Demo Customer</field>
        </record>
    </data>
</odoo>
```

### 2. Configuration Data

```xml
<!-- data/data.xml -->
<odoo>
    <data>
        <!-- Sequence -->
        <record id="seq_sale_order" model="ir.sequence">
            <field name="name">Sale Order</field>
            <field name="prefix">SO%(year)s%(month)s%(day)s-</field>
        </record>

        <!-- Journal -->
        <record id="default_sale_journal" model="account.journal">
            <field name="name">Sales Journal</field>
            <field name="code">SAL</field>
        </record>
    </data>
</odoo>
```

## Security Organization

### 1. Access Control List (ACL)

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_user,sale.order.user,model_sale_order,group_sale_user,1,1,1,0
access_sale_order_manager,sale.order.manager,model_sale_order,group_sale_manager,1,1,1,1
```

### 2. Record Rules

```xml
<!-- security/ir.rule.xml -->
<odoo>
    <record id="rule_sale_order_user" model="ir.rule">
        <field name="name">User: Own Orders Only</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="groups" eval="[(4, ref('sales_team.group_sale_salesman'))]"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
    </record>
</odoo>
```

### 3. Groups

```xml
<!-- security/res_groups.xml -->
<odoo>
    <record id="group_custom_user" model="res.groups">
        <field name="name">Custom / User</field>
        <field name="category_id" ref="base.module_category_custom"/>
    </record>
</odoo>
```

## View Organization

### 1. By Model

```
views/
├── sale_order_views.xml      # All sale.order views
├── sale_order_line_views.xml # All sale.order.line views
└── partner_views.xml         # Res.partner extension
```

### 2. By Type

```
views/
├── form/
│   ├── sale_order_form.xml
│   └── partner_form.xml
├── tree/
│   ├── sale_order_tree.xml
│   └── partner_tree.xml
└── search/
    ├── sale_order_search.xml
    └── partner_search.xml
```

## Controller Organization

### 1. REST API Pattern

```python
# controllers/api.py
class CustomAPI(http.Controller):
    @http.route('/api/customers', type='json', auth='user')
    def list_customers(self, **kwargs):
        return self.env['res.partner'].search_read(
            kwargs.get('domain', []),
            ['name', 'email', 'phone']
        )
```

### 2. Website Controller

```python
# controllers/website.py
class WebsiteController(http.Controller):
    @http.route('/my/customers', website=True, auth='user')
    def portal_customers(self):
        return http.request.render('module.portal_customers', {
            'customers': http.request.env.user.partner_id.customer_ids
        })
```

## Testing Organization

### 1. Test File Structure

```
tests/
├── __init__.py
├── test_model.py           # Model tests
├── test_wizard.py          # Wizard tests
├── test_api.py             # Controller tests
└── test_portal.py         # Portal tests
```

### 2. Test Class Organization

```python
# tests/test_model.py
class TestCustomModel(models.TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup test data

    def test_create(self):
        """Test model creation"""
        pass

    def test_write(self):
        """Test model write"""
        pass
```

## Best Practices

### 1. Module Naming

| Type | Example | Notes |
|------|---------|-------|
| Technical | `module_name` | lowercase, underscore |
| Display | "Module Name" | In __manifest__.py |
| Category | "Localizations" | In category_id |

### 2. File Size

| File Type | Recommended Max Lines |
|-----------|---------------------|
| Model | 500 lines |
| Controller | 300 lines |
| Wizard | 200 lines |
| View XML | 1000 lines |

### 3. Code Organization

- One model per file
- Logical grouping in __init__.py
- Clear method ordering
- Docstrings for complex methods

### 4. Module Dependencies

- Keep dependencies minimal
- Use soft_dependency when possible
- Document required modules

## CE vs EE Architecture

### Community Edition (CE)

```
odoo/addons/
├── sale/
│   ├── models/
│   ├── views/
│   └── controllers/
```

### Enterprise Edition (EE)

```
enterprise/
├── sale/
│   ├── models/
│   │   ├── sale_order.py      # CE
│   │   └── sale_order.py      # EE extension
│   ├── views/
│   └── ...
```

### Pattern: CE Base + EE Extension

```python
# In EE module
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # EE-only functionality
    def _invoice_hook(self):
        # EE-specific hook
        pass
```

## Quick Reference

### Module Checklist

- [ ] __init__.py present
- [ ] __manifest__.py valid
- [ ] All dependencies declared
- [ ] Security defined
- [ ] Views organized
- [ ] Tests present
- [ ] Icon present

### File Organization

```
├── models/     # Business logic
├── views/      # UI definitions
├── controllers # HTTP endpoints
├── wizards     # Interactive dialogs
├── reports    # Print reports
├── security    # Access control
├── data       # Initial data
└── tests      # Test cases
```

## Related Skills

- `odoo-base-understanding`: Understanding existing modules
- `odoo19-module-new`: Creating new modules
- `odoo19-model-inherit`: Inheritance patterns
- `odoo-business-process`: Business logic design
