---
name: odoo-field
description: Add fields to existing Odoo models and update views. Odoo 17/18/19 compatible. Use when user asks to "add field", "add column", "new field", or "extend model"
---

# Odoo Field Operations Guide

You are helping the user add fields to an existing Odoo model and update views.

## Steps

1. **Parse input**:
   - Target model (e.g., "sale.order", "res.partner")
   - Field definition: "field_name:field_type:options"
   - Optional: view location (tree, form, search, kanban)
   - Optional: compute method, depends, related, groups
   - Odoo version (default: from project CLAUDE.md)

2. **Locate model file**:
   - Check project structure from CLAUDE.md
   - Use Glob to find: `**/{module}/models/{model}.py`
   - For standard Odoo models: find in Odoo source path

3. **Determine if inheritance or direct modification**:
   - If standard Odoo model (sale.order, res.partner, etc.):
     - Create/modify inherited model in custom module
     - Use `class SaleOrder(models.Model): _inherit = 'sale.order'`
   - If custom model:
     - Add field directly to original model class

4. **Generate field code** based on type:

   ```python
   # Basic fields
   name = fields.Char(string='Name')
   description = fields.Text(string='Description')
   amount = fields.Integer(string='Amount')
   price = fields.Float(string='Price', digits=(16,2))
   is_active = fields.Boolean(string='Active', default=True)

   # Required field
   code = fields.Char(string='Code', required=True)

   # With default value
   priority = fields.Selection([
       ('0', 'Low'), ('1', 'Normal'), ('2', 'High')
   ], string='Priority', default='1')

   # Copyable
   reference = fields.Char(string='Reference', copy=False)

   # Tracking changes
   notes = fields.Text(string='Notes', tracking=True)

   # Company dependent
   rate = fields.Float(string='Rate', company_dependent=True)

   # Many2one (link to another model)
   partner_id = fields.Many2one('res.partner', string='Partner')
   user_id = fields.Many2one('res.users', string='Responsible',
                            default=lambda self: self.env.user)
   currency_id = fields.Many2one('res.currency', string='Currency',
                                default=lambda self: self.env.company.currency_id)

   # With domain filter
   category_id = fields.Many2one('product.category', string='Category',
                                 domain="[('parent_id', '=', False)]")

   # With context
   tag_ids = fields.Many2many('res.partner.category', string='Tags',
                             context={},)

   # One2many (children)
   line_ids = fields.One2many('model.line', 'parent_id', string='Lines')

   # Many2many (multiple links)
   tag_ids = fields.Many2many('model.tag', string='Tags')

   # Selection/Dropdown
   state = fields.Selection([
       ('draft', 'Draft'),
       ('confirmed', 'Confirmed'),
       ('done', 'Done'),
       ('cancelled', 'Cancelled'),
   ], string='State', default='draft')

   # Computed field
   amount_total = fields.Monetary(string='Total',
                                 compute='_compute_amount_total',
                                 store=True,
                                 currency_field='currency_id')

   @api.depends('line_ids.amount')
   def _compute_amount_total(self):
       for record in self:
           record.amount_total = sum(record.line_ids.mapped('amount'))

   # Related field (mirror from related model)
   partner_name = fields.Char(related='partner_id.name',
                              string='Partner Name',
                              store=False, readonly=True)

   # Binary field for files
   document = fields.Binary(string='Document', attachment=True)
   document_file_name = fields.Char(string='File Name')

   # HTML field
   notes = fields.Html(string='Notes', sanitize=False)

   # Reference field (dynamic reference)
   reference = fields.Reference([
       ('sale.order', 'Sale Order'),
       ('account.move', 'Invoice'),
   ], string='Reference')

   # Date/Datetime
   date_start = fields.Date(string='Start Date')
   datetime_start = fields.Datetime(string='Start Date/Time',
                                   default=fields.Datetime.now)
   ```

5. **Add field to model file**:
   - Find the class definition
   - Add field in logical position (grouped by type or alphabetical)
   - For computed fields, add the compute method below

6. **Update views**:

   **Add to tree/list view:**
   ```xml
   <list>
       <field name="name"/>
       <field name="new_field"/>
       <field name="amount_total" sum="Total"/>
   </list>
   ```

   **Add to form view:**
   ```xml
   <form>
       <sheet>
           <group>
               <group>
                   <field name="name"/>
                   <field name="new_field"/>
               </group>
               <group>
                   <field name="amount"/>
               </group>
           </group>
       </sheet>
   </form>
   ```

   **Add to search view:**
   ```xml
   <search>
       <field name="new_field"/>
       <filter string="Filter Label" name="filter_name"
               domain="[('new_field', '=', 'value')]"/>
   </search>
   ```

7. **Handle special cases:**
   - **Monetary fields**: Ensure currency_id field exists
   - **Many2one with domain**: Add domain filter
   - **Selection fields**: Add selection values
   - **Computed fields**: Add @api.depends decorator
   - **Related fields**: Use related= parameter
   - **Company-dependent**: Use company_dependent=True

8. **Update __manifest__.py** if new inheritance class:
   - Add proper dependency if inheriting from different addon
   - Add new view file to data list

9. **Update security** (ir.model.access.csv):
   ```csv
   access_model_user,model user,model_model,base.group_user,1,0,0,0
   ```

10. **Validate and test**:
    - Check Python syntax
    - Validate XML structure
    - Update module in Odoo
    - Test in UI

## Field Options Reference

| Option | Purpose | Example |
|--------|---------|---------|
| `string` | Field label | `string='Name'` |
| `required` | Mandatory field | `required=True` |
| `default` | Default value | `default=True` |
| `index` | Database index | `index=True` |
| `copy` | Copy on duplicate | `copy=False` |
| `tracking` | Track changes | `tracking=True` |
| `readonly` | Read-only | `readonly=True` |
| `store` | Persist computed | `store=True` |
| `company_dependent` | Per-company value | `company_dependent=True` |
| `groups` | Restrict to groups | `groups='base.group_user'` |
| `ondelete` | On delete behavior | `ondelete='cascade'` |
| `delegate` | Delegate inheritance | `delegate=True` |

## Widget Reference

| Widget | Use For | Example |
|--------|---------|---------|
| `many2one` | Partner selection | Default for Many2one |
| `many2one_button` | Action button | For external refs |
| `many2many_tags` | Tags display | For Many2many |
| `selection` | Dropdown | Default for Selection |
| `radio` | Radio buttons | For Selection |
| `boolean_toggle` | Switch | For Boolean |
| `mail_followers` | Followers | For m2m to res.users |
| `mail_activity` | Activities | For activity_ids |
| `mail_thread` | Messages | For message_ids |
| `monetary` | Currency display | For Monetary |
| `handle` | Drag handle | For sequence |
| `image` | Image preview | For binary images |
| `pdf_viewer` | PDF display | For attachments |
| `progressbar` | Progress | For percentage fields |

## Example Usage

```
/odoo-field add "sale.order" --field="reference_code:char(string='Reference Code')" --views="tree,form"
```

```
Add field to res.partner:
- Field name: customer_rating
- Type: Selection
- Options: Low, Medium, High
- Add to: form view
```

## Important Notes

- Always specify string parameter for field labels
- For Many2one fields, check if comodel_name exists
- For computed fields, include proper @api.depends
- Use copy=False for reference fields that shouldn't be duplicated
- Use tracking=True for important fields to track in chatter
- For monetary fields, always add currency_field parameter
- Test in Odoo UI after updating module
- Remember to update module manifest if needed
