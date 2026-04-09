---
description: Generate Odoo 19 tree view XML with columns, decorations, and configuration. Use when user wants to create a tree/list view.
---


You are helping the user create an Odoo 19 tree view XML definition.

## Steps

1. **Parse input**:
   - Extract model name (e.g., "sale.order")
   - Parse field list (comma-separated)
   - Identify decoration rules
   - Check for editable option
   - Parse additional options

2. **Generate tree view XML** following Odoo 19 conventions:

   ```xml
   <record id="view_{model}_tree" model="ir.ui.view">
       <field name="name">{model}.tree</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <tree string="{Model Label}"
                 default_order="{primary_field} asc"
                 create="true"
                 edit="true"
                 delete="true"
                 multi_edit="true"
                 limit="80"
                 {optional_attributes}>
               <field name="name"/>
               <field name="partner_id"/>
               <field name="amount_total" sum="Total" avg="Average"/>
               <field name="date_order"/>
               <field name="state" widget="badge"
                      decoration-success="draft"
                      decoration-info="confirmed"
                      decoration-warning="sent"
                      decoration-danger="cancelled"/>
               <field name="active" widget="boolean_toggle"/>

               <!-- Optional button column -->
               <button name="action_method" string="Confirm" type="object"
                       icon="fa-check" states="draft"/>
           </tree>
       </field>
   </record>
   ```

3. **Apply decorations** (color coding based on field values):
   - `decoration-success="field_value"` - green background
   - `decoration-info="field_value"` - blue background
   - `decoration-warning="field_value"` - orange background
   - `decoration-danger="field_value"` - red background
   - `decoration-muted="field_value"` - gray background
   - `decoration-bf="field_value"` - bold font
   - `decoration-it="field_value"` - italic font
   - `decoration-primary="field_value"` - primary color
   - `decoration-secondary="field_value"` - secondary color

4. **Configure tree view attributes**:
   - `default_order="field asc/desc"` - default sorting
   - `editable="top"` or `"bottom"` - enable inline editing
   - `multi_edit="true"` - enable multi-row editing
   - `create="true/false"` - show create button
   - `edit="true/false"` - show edit button
   - `delete="true/false"` - show delete button
   - `limit="80"` - default page size
   - `import="true/false"` - enable import
   - `export="xlsx"` - enable export

5. **Add field-specific attributes**:
   - `sum="Total"` - show sum at bottom (numeric fields)
   - `avg="Average"` - show average at bottom
   - `widget="badge"` - badge display for selection
   - `widget="boolean_toggle"` - toggle switch
   - `widget="boolean_favorite"` - favorite star
   - `widget="handle"` - drag handle for reordering
   - `widget="progressbar"` - progress bar
   - `widget="monetary"` - monetary display
   - `widget="many2many_tags"` - tag-style display
   - `widget="priority"` - priority star

6. **Add optional features**:
   - Control buttons: `<button>` element with states, icon
   - Multi-selection: `<field name="name" optional="show/hide"/>`
   - Column widths: `<field name="name" column_invisible="True"/>`

7. **Update manifest**:
   - Add view file to `data` list in `__manifest__.py`
   - File path: `"views/{model}_views.xml"`

8. **Validate XML**:
   - Check proper field references
   - Verify decoration syntax
   - Ensure proper nesting
   - Validate widget usage

## Usage Examples

**Basic tree view:**
```
/view-tree "sale.order" --fields="name,partner_id,date_order,amount_total,state"
```

**With decorations:**
```
/view-tree "sale.order" --fields="name,partner_id,state,amount_total" \
  --decorations="state:badge" --default_order="date_order desc"
```

**Editable tree view:**
```
/view-tree "account.move.line" --fields="name,debit,credit,account_id" \
  --editable="bottom" --multi_edit=true
```

**With buttons:**
```
/view-tree "stock.picking" --fields="name,partner_id,state,move_count" \
  --button="action_confirm:fa-check:Confirm:draft"
```

## Odoo 19 Specific Features

- Use `decoration-` attributes for conditional styling
- Support for `multi_edit` attribute
- New widget options: `widget="favorite"` for favorites
- Enhanced `column_invisible` for dynamic columns
- Improved export options with `export` attribute
- Better performance with `limit` attribute
- Support for `import_xls` and `import_xlsx` attributes
