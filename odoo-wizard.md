---
name: odoo-wizard
description: Create Odoo transient model wizard with form view and action. Odoo 17/18/19 compatible. Use when user asks to "create wizard", "add wizard", "make popup", or "transient model"
---

# Odoo Wizard (Transient Model) Guide

You are helping the user create an Odoo wizard (transient model).

## Steps

1. **Parse input**:
   - Wizard technical name (e.g., "module.mass.update")
   - Source model (e.g., "sale.order", "account.move")
   - Action name (e.g., "Update Batch", "Mass Confirm")
   - Fields: list for wizard form
   - Operation: what the wizard should do
   - Odoo version (default: from project CLAUDE.md)

2. **Determine module location**:
   - Check project structure from CLAUDE.md
   - Create wizards/ directory if not exists

3. **Create wizard directory**:
   ```
   {module}/wizards/
   ```

4. **Generate transient model**:

   ```python
   # -*- coding: utf-8 -*-
   from odoo import api, fields, models, _

   class MassUpdateWizard(models.TransientModel):
       _name = 'mass.update.wizard'
       _description = 'Mass Update Wizard'

       # Source records field (auto-generated)
       res_model = fields.Char(string='Resource Model', required=True)

       # Active IDs passed from context
       res_ids = fields.Char(string='Resource IDs',
                          default=lambda self: self.env.context.get('active_ids', []))

       # Additional fields for user input
       new_state = fields.Selection([
           ('draft', 'Draft'),
           ('confirmed', 'Confirmed'),
           ('done', 'Done'),
       ], string='New State', required=True)

       description = fields.Text(string='Description/Notes')
      line_ids = fields.One2many('mass.update.wizard.line', 'wizard_id',
                                string='Items')

      date_field = fields.Date(string='Target Date')

      # Action method
      def action_apply(self):
          self.ensure_one()

          # Get records to update
          res_model = self.res_model
          res_ids = self._get_res_ids()

          records = self.env[res_model].browse(res_ids).exists()

          # Apply update
          for record in records:
              record.write({
                  'state': self.new_state,
                  'notes': self.description,
              })

          return {
              'type': 'ir.actions.client',
              'tag': 'reload',
          }

      def action_cancel(self):
          return {'type': 'ir.actions.act_window_close'}

      def _get_res_ids(self):
          """Parse res_ids from context"""
          if isinstance(self.res_ids, str):
              import ast
              return ast.literal_eval(self.res_ids)
          return self.res_ids or []

      # Line model for complex wizards
      class Line(models.TransientModel):
          _name = 'mass.update.wizard.line'
          _description = 'Wizard Line'

          wizard_id = fields.Many2one('mass.update.wizard', required=True)
          record_id = fields.Integer(string='Record ID')
          name = fields.Char(string='Name')
          state = fields.Char(string='Current State')
          action = fields.Selection([
               ('update', 'Update'),
               ('skip', 'Skip'),
           ], string='Action', default='update')
   ```

5. **Generate XML views**:

   ```xml
   <odoo>
       <!-- Form view -->
       <record id="view_mass_update_wizard_form" model="ir.ui.view">
           <field name="name">mass.update.wizard.form</field>
           <field name="model">mass.update.wizard</field>
           <field name="arch" type="xml">
               <form string="Mass Update Wizard">
                   <group>
                       <group>
                           <field name="new_state"/>
                           <field name="date_field"/>
                       </group>
                       <group>
                           <field name="description" placeholder="Notes..."/>
                       </group>
                   </group>

                   <!-- For complex wizards with line items -->
                   <field name="line_ids" invisible="not line_ids">
                       <list editable="bottom">
                           <field name="name" readonly="1"/>
                           <field name="state" readonly="1"/>
                           <field name="action"/>
                       </list>
                   </field>

                   <footer>
                       <button string="Cancel" special="cancel" class="btn-secondary"/>
                       <button string="Apply Update" name="action_apply"
                               type="object" class="btn-primary"/>
                   </footer>
               </form>
           </field>
       </record>

       <!-- Action to open wizard -->
       <record id="action_mass_update_wizard" model="ir.actions.act_window">
           <field name="name">Mass Update</field>
           <field name="res_model">mass.update.wizard</field>
           <field name="view_mode">form</field>
           <field name="target">new</field>
           <field name="context">{
               'default_res_model': 'sale.order',
           }</field>
       </record>
   </odoo>
   ```

6. **Create wizard entry point** (action on source model):

   ```xml
   <!-- In source model views -->
   <button name="%(module.action_mass_update_wizard)d"
           string="Mass Update"
           type="action"
           invisible="context.get('hide_mass_update', False)"/>
   ```

7. **Update __manifest__.py**:
   ```python
   "data": [
       "wizards/wizard_views.xml",
   ],
   ```

8. **Update wizard __init__.py**:
   ```python
   from . import wizard_file_name
   ```

9. **Update module __init__.py**:
   ```python
   from . import wizards
   ```

10. **Validate**:
    - Check TransientModel is used (not Model)
    - Ensure action_apply method exists
    - Validate XML structure

## Wizard Types

### Type 1: Simple Confirmation
```python
class ConfirmWizard(models.TransientModel):
    _name = 'confirm.wizard'
    _description = 'Simple Confirmation'

    def _get_default_record(self):
        return self.env.context.get('active_id')

    record_id = fields.Many2one('model.name', default=_get_default_record)
    message = fields.Text(string='Message',
                         default='Are you sure?')

    def action_confirm(self):
        record = self.record_id
        # Do something
        return {'type': 'ir.actions.act_window_close'}
```

### Type 2: Mass Action
```python
class MassActionWizard(models.TransientModel):
    _name = 'mass.action.wizard'
    _description = 'Mass Action Wizard'

    action_type = fields.Selection([
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('archive', 'Archive'),
    ], required=True, default='update')

    def action_execute(self):
        active_ids = self.env.context.get('active_ids', [])
        model = self.env.context.get('active_model')

        for record in self.env[model].browse(active_ids):
            if self.action_type == 'update':
                record.write({'state': 'done'})
            elif self.action_type == 'archive':
                record.write({'active': False})

        return {'type': 'ir.actions.act_window_close'}
```

### Type 3: Multi-Step Wizard
```python
class MultiStepWizard(models.TransientModel):
    _name = 'multi.step.wizard'
    _description = 'Multi-Step Wizard'

    step = fields.Integer(default=1)

    # Step 1
    partner_id = fields.Many2one('res.partner', string='Partner')

    # Step 2
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity', default=1.0)

    def next_step(self):
        self.write({'step': self.step + 1})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def previous_step(self):
        self.write({'step': self.step - 1})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_finish(self):
        # Create the final record
        self.env['target.model'].create({
            'partner_id': self.partner_id.id,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
        })
        return {'type': 'ir.actions.act_window_close'}
```

## Wizard Best Practices

```python
# Always use TransientModel
class Wizard(models.TransientModel):  # NOT models.Model

# Always use ensure_one() before bulk operations
def action_apply(self):
    self.ensure_one()

# Use context to pass active_ids
# context = {'active_ids': [1,2,3], 'active_model': 'sale.order'}

# Return close action
return {'type': 'ir.actions.act_window_close'}

# Or return reload
return {'type': 'ir.actions.client', 'tag': 'reload'}
```

## Important Notes

- Always use `models.TransientModel` for wizards (NOT `models.Model`)
- Use `widget="many2many_tags"` for record selection
- Set `target="new"` to open in popup dialog
- Return `'type': 'ir.actions.act_window_close'` to close wizard
- Context `active_ids` and `active_model` are auto-passed by Odoo
- Transient models auto-cleanup, no manual cleanup needed
- Add button in footer: Cancel (`special="cancel"`) + Confirm
