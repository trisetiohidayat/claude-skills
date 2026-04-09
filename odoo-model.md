---
name: odoo-model
description: Generate Odoo model with fields, methods, and corresponding views. Odoo 17/18/19 compatible. Use when user asks to "create model", "add model", "define model", or "new model class"
---

# Odoo Model Creation Guide

You are helping the user create an Odoo model with fields, methods, and views.

## Steps

1. **Parse input**:
   - Model technical name (e.g., "custom.model" or "module.model")
   - Fields: comma-separated list with format "name:type:options"
   - Views: comma-separated (tree, form, search, kanban, calendar, pivot, graph)
   - Target module: which module to add this to
   - Odoo version (default: from project CLAUDE.md)

2. **Determine module location**:
   - Check project structure from CLAUDE.md
   - Find addons path for the target module
   - Parse model name: `{module}.{model_name}`

3. **Generate Python model**:
   ```python
   # {date}
   from odoo import api, fields, models, _

   class {ModelClassName}(models.Model):
       _name = '{model.name}'
       _description = '{human readable description}'
       _order = 'name'
       _rec_name = 'name'

       # Fields
       name = fields.Char(string='Name', required=True, index=True, copy=False)
       active = fields.Boolean(string='Active', default=True)
       company_id = fields.Many2one('res.company', string='Company',
                                   default=lambda self: self.env.company)
       description = fields.Text(string='Description')

       # Relational fields
       partner_id = fields.Many2one('res.partner', string='Partner')
       line_ids = fields.One2many('model.line', 'parent_id', string='Lines')

       # Computed fields
       amount_total = fields.Monetary(string='Total', compute='_compute_amount_total',
                                     store=True, currency_field='currency_id')
       currency_id = fields.Many2one('res.currency',
                                    default=lambda self: self.env.company.currency_id)

       # SQL constraints
       _sql_constraints = [
           ('name_unique', 'UNIQUE(name)', 'Name must be unique!'),
       ]

       # Compute methods
       @api.depends('line_ids.amount')
       def _compute_amount_total(self):
           for record in self:
               record.amount_total = sum(record.line_ids.mapped('amount'))

       # Action methods
       def action_confirm(self):
           for record in self:
               record.write({'state': 'confirmed'})
           return True

       # Display name
       def name_get(self):
           result = []
           for record in self:
               name = record.name
               if record.partner_id:
                   name = f'{name} ({record.partner_id.name})'
               result.append((record.id, name))
           return result
   ```

4. **Handle field types**:
   | Type | Syntax | Notes |
   |------|--------|-------|
   | Char | `fields.Char(string='Label')` | With size limit |
   | Text | `fields.Text(string='Label')` | Multi-line |
   | Html | `fields.Html(string='Label', sanitize=False)` | Rich text |
   | Integer | `fields.Integer(string='Label')` | Whole numbers |
   | Float | `fields.Float(string='Label', digits=(16,2))` | Decimal |
   | Monetary | `fields.Monetary(string='Label', currency_field='currency_id')` | Currency |
   | Boolean | `fields.Boolean(string='Label', default=False)` | Yes/No |
   | Date | `fields.Date(string='Label')` | Date only |
   | Datetime | `fields.Datetime(string='Label')` | Date + time |
   | Selection | `fields.Selection([('a','A'),('b','B')], string='Label')` | Dropdown |
   | Many2one | `fields.Many2one('model.name', string='Label')` | Link to one |
   | One2many | `fields.One2many('model.line', 'parent_id', string='Label')` | Children |
   | Many2many | `fields.Many2many('model.tag', string='Label')` | Multiple links |
   | Binary | `fields.Binary(string='Label', attachment=True)` | File storage |
   | Reference | `fields.Reference([('model','Label')], string='Label')` | Dynamic link |

5. **Generate XML views**:

   **Tree/List view**:
   ```xml
   <record id="view_{model}_tree" model="ir.ui.view">
       <field name="name">{model}.tree</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <list>
               <field name="name"/>
               <field name="partner_id"/>
               <field name="amount_total" sum="Total"/>
               <field name="state" widget="badge"
                      decoration-success="state == 'done'"
                      decoration-warning="state == 'draft'"/>
           </list>
       </field>
   </record>
   ```

   **Form view**:
   ```xml
   <record id="view_{model}_form" model="ir.ui.view">
       <field name="name">{model}.form</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <form>
               <header>
                   <field name="state" widget="statusbar"/>
                   <button name="action_confirm" string="Confirm" type="object"
                           class="btn-primary" invisible="state != 'draft'"/>
               </header>
               <sheet>
                   <group>
                       <group>
                           <field name="name"/>
                           <field name="partner_id"/>
                       </group>
                       <group>
                           <field name="amount_total"/>
                           <field name="currency_id"/>
                       </group>
                   </group>
                   <notebook>
                       <page string="Lines" name="lines">
                           <field name="line_ids">
                               <list editable="bottom">
                                   <field name="name"/>
                                   <field name="amount"/>
                               </list>
                           </field>
                       </page>
                       <page string="Notes" name="notes">
                           <field name="description"/>
                       </page>
                   </notebook>
               </sheet>
               <div class="oe_chatter">
                   <field name="message_follower_ids"/>
                   <field name="activity_ids"/>
                   <field name="message_ids"/>
               </div>
           </form>
       </field>
   </record>
   ```

   **Search view**:
   ```xml
   <record id="view_{model}_search" model="ir.ui.view">
       <field name="name">{model}.search</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <search>
               <field name="name"/>
               <field name="partner_id"/>
               <filter string="Active" name="active" domain="[('active','=',True)]"/>
               <filter string="Draft" name="draft" domain="[('state','=','draft')]"/>
               <group>
                   <filter string="Partner" name="group_partner"
                           context="{'group_by': 'partner_id'}"/>
                   <filter string="State" name="group_state"
                           context="{'group_by': 'state'}"/>
               </group>
           </search>
       </field>
   </record>
   ```

   **Action window**:
   ```xml
   <record id="action_{model}" model="ir.actions.act_window">
       <field name="name">{Model Label}</field>
       <field name="res_model">{model}</field>
       <field name="view_mode">tree,form</field>
       <field name="domain">[]</field>
       <field name="context">{}</field>
       <field name="help">Help text for the view</field>
   </record>
   ```

   **Menu item** (if application=True):
   ```xml
   <menuitem id="menu_{model}" name="{Model Label}"
             action="action_{model}" sequence="10" parent="menu_parent"/>
   ```

6. **Generate security rules** (ir.model.access.csv):
   ```csv
   id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
   access_{model}_user,{model} user,model_{model},base.group_user,1,0,0,0
   access_{model}_manager,{model} manager,model_{model},base.group_system,1,1,1,1
   ```

7. **Update __manifest__.py**:
   - Add to data list: `"views/{model}_views.xml"`
   - Add to data list: `"security/ir.model.access.csv"`
   - Update models/__init__.py to import new model

8. **Run validation**:
   - Check Python syntax
   - Validate XML structure
   - Run pre-commit if available

9. **Show summary**:
   - Files created/modified
   - Next steps: install module, test in UI

## Example Usage

```
/odoo-model create "custom.vehicle"
  --fields="name:char,partner_id:many2one:res.partner,license_plate:char,vin_number:char"
  --views="tree,form,search"
```

```
Create model for equipment tracking:
- Model: equipment.tracking
- Fields: name, serial_number, location, partner_id, status
- Views: tree, form, kanban
- Module: custom_equipment
```

## Important Notes

- Use `tracking=True` on important fields for chatter tracking
- Always add `_order = "name"` for default sorting
- Use `store=True` on computed fields that need to be searchable
- Add proper `currency_field` for Monetary fields
- Use `ondelete='cascade'` for One2many inverse
- Always add SQL constraints for unique fields
- Add mail.thread inheritance for messaging features
