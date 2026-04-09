---
name: odoo-batch
description: Batch operations, mass updates, data imports, and bulk processing in Odoo - wizard-based, script-based, or shell-based approaches. Use when user asks to "mass update", "batch process", "bulk import", "update all records", "import data", "export data", "batch operation", or "bulk write"
---

# Odoo Batch Operations & Mass Processing

You are helping users perform batch operations in Odoo - mass updates, data imports/exports, and bulk processing.

## When to Use

- Mass updating records (e.g., update all draft orders to confirmed)
- Bulk importing data from CSV/Excel
- Bulk exporting data
- Running operations on many records at once
- Scheduled batch jobs
- Data migration/cleanup

## Approaches

### Approach 1: Odoo Shell Script (Recommended for large datasets)

Best for: Large datasets, repeatable operations, complex logic

```python
#!/usr/bin/env python3
"""Batch update script - run with odoo shell"""
# -*- coding: utf-8 -*-

def mass_update(env):
    """Update all draft sale orders to sent"""
    domain = [('state', '=', 'draft')]
    records = env['sale.order'].search(domain)

    for record in records:
        record.write({'state': 'sent'})

    print(f"Updated {len(records)} records")

# Run
mass_update(env)
```

### Approach 2: Wizard/Transient Model

Best for: End users, one-time operations, with confirmation

```python
from odoo import models, fields, api, _

class MassUpdateWizard(models.TransientModel):
    _name = 'mass.update.wizard'
    _description = 'Mass Update Wizard'

    model_id = fields.Many2one('ir.model', string='Model', required=True)
    domain = fields.Text(string='Domain (Python domain expression)', required=True)
    field_to_update = fields.Many2one('ir.model.fields', string='Field to Update')
    value = fields.Char(string='New Value')

    def action_apply(self):
        self.ensure_one()
        model_name = self.model_id.model

        # Parse domain
        domain = safe_eval(self.domain)

        # Get records
        records = self.env[model_name].search(domain)

        # Update
        update_dict = {self.field_to_update.name: self.value}
        records.write(update_dict)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
```

### Approach 3: Scheduled Action (Cron)

Best for: Recurring operations, automated processes

```python
# In __manifest__.py
'data': [
    'data/cron_data.xml',
]

# data/cron_data.xml
<odoo>
    <record id="ir_cron_mass_update" model="ir.cron">
        <field name="name">Mass Update: Process Records</field>
        <field name="model_id" ref="model_mass_update_task"/>
        <field name="state">code</field>
        <field name="code">model.process_batch()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">hours</field>
        <field name="numbercall">-1</field>
    </record>
</odoo>
```

## CSV Import

### Standard Odoo Import

1. Enable Developer Mode
2. Go to: Settings > Import Data
3. Upload CSV file
4. Map columns to fields
5. Test Import
6. Execute Import

### Import Template Generation

```python
def generate_import_template(env, model_name, output_path):
    """Generate a CSV template for import"""
    model = env[model_name]
    fields = model.fields_get()

    with open(output_path, 'w') as f:
        # Header row
        headers = ['id', 'name'] + [k for k in fields.keys() if k not in ['id', 'name']]
        f.write(','.join(headers) + '\n')

        # Sample row
        sample = ['', ''] + ['' for _ in range(len(headers) - 2)]
        f.write(','.join(sample))

    print(f"Template saved to {output_path}")
```

### Import with Python

```python
import csv
import odoorpc

def import_csv(csv_path, model_name):
    """Import CSV data into Odoo"""
    odoo = odoorpc.ODOO('http://localhost:8069')
    odoo.login('db_name', 'user', 'password')
    Model = odoo.env[model_name]

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Prepare data
            data = {k: v for k, v in row.items() if v and k != 'id'}

            # Create or write
            if row.get('id'):
                record = Model.browse(int(row['id']))
                record.write(data)
            else:
                Model.create(data)

    print("Import completed")
```

## CSV Export

### Direct Export

1. Go to list view
2. Select records (or use Filters)
3. Click Actions > Export
4. Choose fields
5. Download CSV

### Programmatic Export

```python
import csv

def export_to_csv(env, model_name, domain, output_path, fields):
    """Export records to CSV"""
    records = env[model_name].search(domain)

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for record in records:
            row = {}
            for field in fields:
                value = record[field]
                if hasattr(value, 'ids'):
                    # Many2many/Many2one
                    value = ','.join([v.display_name for v in value])
                row[field] = value
            writer.writerow(row)

    print(f"Exported {len(records)} records to {output_path}")
```

## Mass Update Examples

### Update by Domain

```python
def mass_update_by_domain(env):
    """Mass update records matching domain"""

    # Update all active partners to inactive if no orders
    partners = env['res.partner'].search([
        ('customer_rank', '>', 0),
        ('sale_order_ids', '=', False),
    ])

    partners.write({'active': False})
    print(f"Deactivated {len(partners)} partners")
```

### Update with Computation

```python
def recompute_all_totals(env):
    """Recompute totals for all orders"""

    orders = env['sale.order'].search([])
    for order in orders:
        order._compute_amount()

    print(f"Recomputed {len(orders)} orders")
```

### Update Related Records

```python
def update_child_records(env):
    """Update all line items based on parent"""

    orders = env['sale.order'].search([('state', '=', 'draft')])

    for order in orders:
        for line in order.order_line:
            # Update line price based on partner pricelist
            line.product_id_change()
            line._onchange_quantity()

    print(f"Updated {len(orders)} orders")
```

## Performance Best Practices

### For Large Datasets

```python
def batch_process_with_progress(env, model_name, domain, batch_size=1000):
    """Process records in batches to avoid memory issues"""

    records = env[model_name].search(domain)
    total = len(records)
    processed = 0

    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]

        for record in batch:
            # Process each record
            process_record(record)

        # Commit after each batch (in long-running jobs)
        env.cr.commit()
        processed += len(batch)

        print(f"Processed {processed}/{total}")

def process_record(record):
    """Process single record - implement your logic"""
    # Example: update field
    record.write({'processed': True})
```

### Using Recursive Search

```python
def process_with_cursor(env):
    """Process using raw SQL for maximum performance"""

    env.cr.execute("""
        SELECT id FROM sale_order
        WHERE state = 'draft'
    """)
    ids = [row[0] for row in env.cr.fetchall()]

    # Process in batches
    Model = env['sale.order']
    for i in range(0, len(ids), 1000):
        batch_ids = ids[i:i+1000]
        records = Model.browse(batch_ids)
        records.write({'state': 'sent'})
        env.cr.commit()
```

## Data Validation Before Batch Update

```python
def validate_before_update(env, model_name, domain):
    """Validate records before mass update"""

    records = env[model_name].search(domain)
    warnings = []

    for record in records:
        # Check business rules
        if hasattr(record, '_validate_batch'):
            result = record._validate_batch()
            if not result['valid']:
                warnings.append({
                    'id': record.id,
                    'name': record.display_name,
                    'warnings': result['warnings']
                })

    return warnings
```

## Undo/Backup Before Batch Operations

```python
def backup_before_batch(env, model_name, domain, backup_name):
    """Create backup records before mass update"""

    records = env[model_name].search(domain)

    # Create backup model
    backup_model = f'{model_name}.backup'
    if backup_model not in env:
        # Create backup model dynamically
        env['ir.model'].create({
            'name': f'{model_name} Backup',
            'model': backup_model,
        })

    # Copy records to backup
    for record in records:
        data = record.copy_data()[0]
        data['original_id'] = record.id
        env[backup_model].create(data)

    print(f"Backed up {len(records)} records to {backup_model}")
    return backup_model
```

## Wizard XML Template

```xml
<odoo>
    <record id="view_mass_update_wizard" model="ir.ui.view">
        <field name="name">mass.update.wizard.form</field>
        <field name="model">mass.update.wizard</field>
        <field name="arch" type="xml">
            <form string="Mass Update">
                <group>
                    <group>
                        <field name="model_id"/>
                        <field name="field_to_update"/>
                    </group>
                    <group>
                        <field name="domain" placeholder="[('state', '=', 'draft')]"/>
                        <field name="value" placeholder="New value"/>
                    </group>
                </group>
                <footer>
                    <button string="Cancel" special="cancel" class="btn-secondary"/>
                    <button string="Apply Update" name="action_apply" type="object" class="btn-primary"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_mass_update_wizard" model="ir.actions.act_window">
        <field name="name">Mass Update</field>
        <field name="res_model">mass.update.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

## Summary Output Format

When completing batch operations, always report:

```
## Batch Operation Summary

- Model: {model_name}
- Records affected: {count}
- Operation: {what was done}
- Duration: {time_taken}
- Errors: {count or 'None'}

## Records Processed
{list of record IDs or summary}

## Rollback Available?
{Yes/No + instructions}
```
