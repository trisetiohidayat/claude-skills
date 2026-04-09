---
name: odoo-migration-analysis
description: |
  Analisis migrasi Odoo antar versi - v15 ke v19, API changes, view migration, model migration,
  data migration, compatibility. Gunakan ketika:
  - User bertanya tentang migration
  - Need to migrate custom modules
  - Ingin understand version differences
  - Need to fix migration issues
---

# Odoo Migration Analysis Skill

## Overview

Skill ini membantu menganalisis dan melaksanakan migrasi modul Odoo antar versi. Migrasi dari Odoo 15 ke 19 melibatkan banyak perubahan API, deprecated methods, dan perubahan struktur yang harus dipahami dengan baik.

## When to Use This Skill

Gunakan skill ini ketika:
- User bertanya tentang migration Odoo antar versi
- Need to migrate custom modules dari Odoo 15 ke 19
- Ingin memahami perbedaan versi Odoo
- Need to fix migration issues
- Ingin upgrade production database
- Need to analyze compatibility

## Step 1: Identify Version Changes

### Major Changes Between Odoo 15 to 19

#### Python Version Changes

| Aspect | Odoo 15 | Odoo 19 |
|--------|---------|---------|
| Python Version | 3.8 | 3.10+ |
| Syntax | 3.8 features | 3.10+ features |
| Type Hints | Optional | Encouraged |

#### Module Manifest Changes

```python
# Odoo 15 - __manifest__.py
{
    'name': 'My Module',
    'version': '15.0.1.0.0',  # Format: MAJOR.MINOR.PATCH.REVISION
    'depends': ['base'],
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
}

# Odoo 19 - __manifest__.py
{
    'name': 'My Module',
    'version': '19.0.1.0.0',  # Format: MAJOR.MINOR.PATCH.REVISION
    'depends': ['base'],
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
    'category': 'Accounting/Finance',
    'summary': 'Module summary',
    'description': """
    Module description
    """,
}
```

#### Python API Changes

```python
# Odoo 15
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(string='Name')
    date = fields.Date(string='Date')

    @api.multi
    def my_method(self):
        for record in self:
            # Process each record
            pass

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.date = fields.Date.today()

# Odoo 19
from odoo import models, fields, api
from odoo.tools import date_utils

class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(string='Name')
    date = fields.Date(string='Date')

    def my_method(self):
        # @api.multi is now default for recordset methods
        for record in self:
            # Process each record
            pass

    @api.onchange('name')
    def _onchange_name(self):
        # Same pattern still works in Odoo 19
        if self.name:
            self.date = fields.Date.today()
```

#### Field Type Changes

```python
# Odoo 15 - Common field definitions
name = fields.Char(string='Name')
description = fields.Text(string='Description')
html_content = fields.Html(string='Content')
price = fields.Float(string='Price')
amount = fields.Monetary(string='Amount')
is_active = fields.Boolean(string='Active')
category = fields.Selection([
    ('cat1', 'Category 1'),
    ('cat2', 'Category 2'),
], string='Category')

# Odoo 19 - Additional options available
name = fields.Char(
    string='Name',
    required=True,
    index=True,
    translate=True,  # Enable translation
)
description = fields.Text(
    string='Description',
    translate=True,
)
html_content = fields.Html(
    string='Content',
    sanitize=True,
    sanitize_tags=False,
    strip_style=True,
)
price = fields.Float(
    string='Price',
    digits='Product Price',  # Use precision from decimal precision
)
amount = fields.Monetary(
    string='Amount',
    currency_field='currency_id',
)
is_active = fields.Boolean(
    string='Active',
    default=True,
)
category = fields.Selection(
    selection=[
        ('cat1', 'Category 1'),
        ('cat2', 'Category 2'),
    ],
    string='Category',
    required=True,
    copy=False,  # Don't copy during duplicate
)
```

## Step 2: Analyze Migration Requirements

### Manifest Migration

```python
# Migration checklist untuk __manifest__.py

# 1. Version update
OLD: 'version': '15.0.1.0.0',
NEW: 'version': '19.0.1.0.0',

# 2. Python dependencies
OLD: 'external_dependencies': {'python': ['requests']},
NEW: 'python_constraints': {  # Odoo 17+
    'python': '>=3.8',
    'odoo': '>=17.0',
    'odoo': '<18.0',
},

# 3. Application flag
OLD: 'application': True,
NEW: 'application': True,  # Still valid

# 4. Auto-install
OLD: 'auto_install': False,
NEW: 'auto_install': False,  # Still valid
```

### Model Migration

```python
# Migration patterns untuk models

# 1. Import changes
# Odoo 15
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

# Odoo 19
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils, DEFAULT_SERVER_DATE_FORMAT

# 2. Field definition migration
# Odoo 15
date_start = fields.Date(string='Start Date')
date_end = fields.Datetime(string='End Date')

# Odoo 19
date_start = fields.Date(string='Start Date', required=True)
date_end = fields.Datetime(string='End Date', tracking=True)

# 3. Compute field migration
# Odoo 15
total_amount = fields.Float(
    compute='_compute_total',
    store=False,
)
@api.multi
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

# Odoo 19
total_amount = fields.Float(
    compute='_compute_total',
    store=True,  # Consider storing for performance
    compute_sudo=False,  # Respect ACL
)
def _compute_total(self):
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('amount'))

# 4. Related field migration
# Odoo 15
partner_name = fields.Char(related='partner_id.name', string='Partner Name')

# Odoo 19
partner_name = fields.Char(
    related='partner_id.name',
    string='Partner Name',
    store=True,  # Consider storing
)
```

### View Migration

```xml
<!-- Odoo 15 - View Migration -->

<!-- 1. Tree view -->
<tree string="My List" decoration-success="state=='done'">
    <field name="name"/>
    <field name="state"/>
</tree>

<!-- Odoo 19 -->
<list string="My List" decoration-success="state=='done'">
    <field name="name"/>
    <field name="state"/>
</list>

<!-- 2. Form view -->
<form string="My Form" version="15.0">
    <sheet>
        <group>
            <field name="name"/>
        </group>
    </sheet>
</form>

<!-- Odoo 19 -->
<form string="My Form">
    <sheet>
        <group>
            <field name="name"/>
        </group>
    </sheet>
</form>

<!-- 3. Field attributes -->
<!-- Odoo 15 -->
<field name="date" attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- Odoo 19 -->
<field name="date" invisible="state == 'draft'"/>

<!-- 4. Button migration -->
<!-- Odoo 15 -->
<button name="action_confirm" string="Confirm" type="object"/>

<!-- Odoo 19 - Same but with more options -->
<button name="action_confirm" string="Confirm" type="object"
        class="oe_highlight" icon="fa-check"/>

<!-- 5. Kanban view -->
<kanban>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_global_click">
                <field name="name"/>
            </div>
        </t>
    </templates>
</kanban>

<!-- Odoo 19 - Similar -->
<list>
    <templates>
        <t t-name="list-item">
            <div class="d-flex">
                <field name="name"/>
            </div>
        </t>
    </templates>
</list>
```

### Controller Migration

```python
# Odoo 15 - HTTP Controller
from odoo import http

class MyController(http.Controller):

    @http.route('/my/module/page', type='http', auth='public')
    def my_page(self, **kw):
        return http.request.render('my_module.my_template', {
            'data': 'value'
        })

    @http.route('/my/module/json', type='json', auth='user')
    def my_json(self):
        return {'result': 'ok'}

# Odoo 19 - Similar but with improvements
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/module/page', type='http', auth='user')
    def my_page(self, **kw):
        # More secure default
        return http.request.render('my_module.my_template', {
            'data': 'value'
        })

    @http.route('/my/module/json', type='json', auth='user',
                cors='*')
    def my_json(self):
        return {'result': 'ok'}
```

## Step 3: Check Dependencies

### Module Dependencies

```python
# Analyzing dependencies untuk migration

# 1. Direct dependencies
OLD: 'depends': ['base', 'sale']
NEW: 'depends': ['base', 'sale'],

# 2. External dependencies
# Odoo 15
OLD: 'external_dependencies': {
    'python': ['requests', 'numpy'],
    'bin': ['pdftotext'],
}

# Odoo 19 - Use pip requirements
# Create requirements.txt in module root
# Or use python_constraints

# 3. Testing dependencies
OLD: 'test': ['my_module/tests/test_basic.yml'],

# Odoo 19 - Test files automatically discovered
# No need to list in manifest

# 4. Demo data
OLD: 'demo': ['demo/demo.xml'],

# Odoo 19 - Same
NEW: 'demo': ['demo/demo.xml'],
```

### CE vs EE Dependencies

```python
# Check if module requires Enterprise Edition

# Patterns indicating EE requirement:
# 1. Uses hr_payroll module
# 2. Uses industry_fsm module
# 3. Uses documents module with advanced features
# 4. Uses premium apps

def check_ee_dependency(module_xml_id):
    """Check if module depends on EE"""
    ee_modules = [
        'hr_payroll', 'hr_payroll_account',
        'industry_fsm', 'documents',
        'spreadsheet', 'approvals',
    ]
    return any(ee in module_xml_id for ee in ee_modules)

# In migration, handle EE modules differently
if check_ee_dependency(module_name):
    print(f"Warning: {module_name} requires Enterprise Edition")
    # Consider creating CE version or flagging as EE-only
```

## Step 4: Migration Patterns

### Common Migration Mappings

| Odoo 15 | Odoo 19 | Notes |
|---------|---------|-------|
| `<tree>` | `<list>` | View type |
| `attrs` | `invisible/readonly` | Field visibility |
| `_onchange_*` | `@api.onchange` | Same decorator |
| `@api.multi` | Default | Now default |
| `openerp` | `odoo` | Module reference |
| `base.module_name` | `base.module_name` | Still same |
| `web` | `web` | Still same |
| `cr` | `env.cr` | Cursor access |
| `pooler` | `env` | Pool access |

### Migration Script Pattern

```python
# scripts/migrate_module.py
#!/usr/bin/env python3
"""
Migration script untuk Odoo 15 ke 19
Usage: python migrate_module.py --module my_module
"""

import xml.etree.ElementTree as ET
import os
import sys
from pathlib import Path

class OdooMigration:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.changes = []

    def migrate_manifest(self):
        """Migrate __manifest__.py"""
        manifest_path = self.module_path / '__manifest__.py'

        # Read and update version
        content = manifest_path.read_text()
        content = content.replace("'version': '15.", "'version': '19.")
        manifest_path.write_text(content)
        self.changes.append("Updated manifest version")

    def migrate_views(self):
        """Migrate view XML files"""
        views_dir = self.module_path / 'views'

        if not views_dir.exists():
            return

        for xml_file in views_dir.glob('*.xml'):
            content = xml_file.read_text()

            # Tree to list
            content = content.replace('<tree ', '<list ')
            content = content.replace('</tree>', '</list>')

            # Update attrs to invisible/readonly
            # ... more patterns

            xml_file.write_text(content)
            self.changes.append(f"Migrated {xml_file.name}")

    def migrate_models(self):
        """Migrate model files"""
        models_dir = self.module_path / 'models'

        if not models_dir.exists():
            return

        for py_file in models_dir.glob('*.py'):
            content = py_file.read_text()

            # Remove @api.multi decorator (now default)
            content = content.replace('@api.multi\n', '')

            # Update imports
            content = content.replace('from openerp', 'from odoo')

            py_file.write_text(content)
            self.changes.append(f"Migrated {py_file.name}")

    def report(self):
        """Print migration report"""
        print("\n=== Migration Report ===")
        print(f"Module: {self.module_path.name}")
        print("\nChanges made:")
        for change in self.changes:
            print(f"  - {change}")
        print("=" * 25)

if __name__ == '__main__':
    module = sys.argv[1] if len(sys.argv) > 1 else '.'
    migrator = OdooMigration(module)
    migrator.migrate_manifest()
    migrator.migrate_views()
    migrator.migrate_models()
    migrator.report()
```

### Data Migration

```python
# Migration script untuk data updates

from odoo import api, SUPERUSER_ID
from odoo.tools import float_compare

def migrate(cr, version):
    """Data migration hook"""

    # 1. Update records dengan old values
    cr.execute("""
        UPDATE my_model
        SET state = 'new_state'
        WHERE state = 'old_state'
    """)

    # 2. Update field values
    cr.execute("""
        UPDATE my_model
        SET amount = amount * 1.1
        WHERE type = 'increase'
    """)

    # 3. Create missing records
    env = api.Environment(cr, SUPERUSER_ID, {})
    category = env['my.category'].create({
        'name': 'Default Category',
    })

    # 4. Migrate attachments
    cr.execute("""
        UPDATE ir_attachment
        SET res_model = 'new.model'
        WHERE res_model = 'old.model'
    """)

    # 5. Update sequences
    cr.execute("""
        SELECT setval('my_model_id_seq',
            (SELECT MAX(id) FROM my_model) + 1)
    """)
```

## Step 5: Testing Migration

### Test Strategy

```python
# Test migration dengan realistic data

class TestMigration(base.TransactionCase):

    def setUp(self):
        super().setUp()
        self.Model = self.env['my.model']

    def test_migration_install(self):
        """Test module can be installed"""
        module = self.env['ir.module.module'].search([
            ('name', '=', 'my_module')
        ])
        self.assertEqual(module.state, 'installed')

    def test_data_integrity(self):
        """Test data integrity after migration"""
        # Check all records are accessible
        records = self.Model.search([])
        self.assertGreater(len(records), 0)

        # Check required fields
        for record in records:
            self.assertTrue(record.name)
            self.assertTrue(record.state)

    def test_field_computed(self):
        """Test computed fields work correctly"""
        # Create test record
        record = self.Model.create({
            'name': 'Test',
            'line_ids': [
                (0, 0, {'amount': 100}),
                (0, 0, {'amount': 200}),
            ],
        })

        # Check computed value
        self.assertEqual(record.total_amount, 300)

    def test_access_rights(self):
        """Test access rights after migration"""
        # Test dengan regular user
        user = self.env['res.users'].create({
            'login': 'test_user',
            'name': 'Test User',
        })

        model = self.Model.with_user(user)
        # Should be able to read
        records = model.search([])
        self.assertTrue(records)

    def test_views(self):
        """Test views load correctly"""
        # Get view
        view = self.env.ref('my_module.view_my_model_form')
        self.assertTrue(view)

        # Test form rendering
        record = self.Model.create({'name': 'Test'})
        form = Form(record)
        self.assertIn('name', form._view['fields'])
```

## Common Migration Issues

### Issue 1: View Type Not Updated

```
Symptoms: Views tidak muncul, error "View type tree not found"
Cause: <tree> belum diubah ke <list>
Solution:
- Replace all <tree> dengan <list> di XML files
- Replace all </tree> dengan </list>
```

### Issue 2: Field Attributes Changed

```
Symptoms: Fields tidak visible/hide sesuai kondisi
Cause: attrs belum diubah ke invisible/readonly
Solution:
- attrs="{'invisible': ...}" → invisible="..."
- attrs="{'readonly': ...}" → readonly="..."
```

### Issue 3: Deprecated Python APIs

```
Symptoms: Errors tentang deprecated methods
Cause: Using Odoo 15 API yang sudah dihapus
Solution:
- Remove @api.multi (now default)
- Update cr to env.cr
- Update pool to env
```

### Issue 4: Module Dependencies

```
Symptoms: Module tidak terinstall
Cause: Missing dependencies
Solution:
- Check all required modules
- Update depends di manifest
- Install missing modules first
```

### Issue 5: Database Schema

```
Symptoms: Fields tidak tersedia setelah upgrade
Cause: Column tidak dibuat
Solution:
- Odoo会自动add new fields
- Check untuk manual migration scripts
- Upgrade module dengan -u flag
```

### Issue 6: Security/ACL

```
Symptoms: Access errors setelah migration
Cause: ACL tidak di-migrate dengan benar
Solution:
- Check ir.model.access.csv
- Verify record rules
- Test dengan different users
```

## Migration Checklist

### Pre-Migration

- [ ] Backup production database
- [ ] Test di staging environment
- [ ] Document semua customizations
- [ ] Identify external dependencies
- [ ] Check CE vs EE requirements
- [ ] Review Odoo release notes

### During Migration

- [ ] Update __manifest__.py version
- [ ] Migrate model definitions
- [ ] Migrate view XMLs
- [ ] Migrate controllers
- [ ] Migrate security files
- [ ] Update data files
- [ ] Add migration scripts if needed

### Post-Migration

- [ ] Install module successfully
- [ ] Verify all fields exist
- [ ] Test CRUD operations
- [ ] Test views render correctly
- [ ] Test access rights
- [ ] Run existing tests
- [ ] Check for performance issues
- [ ] Test integration dengan related modules

## Version-specific Changes Reference

### Odoo 16 Changes
- Python 3.9+ required
- New ornament framework for JS
- Improved studio features
- Updated web client

### Odoo 17 Changes
- Python 3.10+ required
- New spreadsheet module
- Improved approval workflow
- Enhanced POS features

### Odoo 18 Changes
- Python 3.10+ required
- Further UI improvements
- New template variables
- Enhanced API

### Odoo 19 Changes
- Python 3.10+ required
- New architecture patterns
- Enhanced performance
- Updated security features

## Output Format

 Ketika menggunakan skill ini, berikan output dengan format berikut:

## Migration Analysis

### Version Changes Identified
1. **[Critical]**: [Change Type] - [Location]
2. **[High]**: [Change Type] - [Location]
3. **[Medium]**: [Change Type] - [Location]

### Required Modifications
1. [Modification 1]
2. [Modification 2]
3. [Modification 3]

### Compatibility Issues
- [Issue 1] - [Impact]
- [Issue 2] - [Impact]

### Migration Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Test Recommendations
- [Test 1]
- [Test 2]
- [Test 3]

### Estimated Effort
- Total changes: X files
- Manual changes: X
- Automated changes: X

## Notes

- Always backup sebelum migration
- Test thoroughly di staging
- Consider using migration tools
- Document semua changes
- Monitor untuk issues setelah migration
