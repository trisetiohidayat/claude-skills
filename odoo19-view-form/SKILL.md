---
description: Generate Odoo 19 form view with sheet layout, groups, notebooks, and widgets. Use when user wants to create a form view.
---


You are helping the user create an Odoo 19 form view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse field list and identify groups
   - Determine layout type
   - Check for chatter requirement
   - Identify widget specifications

2. **Generate form view XML** following Odoo 19 conventions:

   **Basic form with sheet layout:**
   ```xml
   <record id="view_{model}_form" model="ir.ui.view">
       <field name="name">{model}.form</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <form string="{Model Label}" create="true" edit="true" delete="true">
               <header>
                   <button name="action_confirm" string="Confirm" type="object"
                           class="btn-primary" states="draft"/>
                   <button name="action_cancel" string="Cancel" type="object"
                           class="btn-secondary" states="draft,confirmed"/>
                   <field name="state" widget="statusbar"
                          statusbar_visible="draft,confirmed,done,cancelled"
                          statusbar_colors='{"draft":"blue","confirmed":"green","done":"gray","cancelled":"red"}'/>
               </header>

               <sheet>
                   <div class="oe_title">
                       <label for="name" string="Name"/>
                       <h1><field name="name" placeholder="Enter name..."/></h1>
                       <h2><field name="code" placeholder="Code"/></h2>
                   </div>

                   <!-- First group of fields -->
                   <group>
                       <group string="Information">
                           <field name="partner_id" required="1"/>
                           <field name="date_order" required="1"/>
                           <field name="user_id"/>
                           <field name="company_id" options="{'no_create': True}"/>
                       </group>
                       <group string="Details">
                           <field name="amount_total" widget="monetary"/>
                           <field name="currency_id" invisible="1"/>
                           <field name="payment_term_id"/>
                           <field name="fiscal_position_id"/>
                       </group>
                   </group>

                   <!-- Notebook with tabs -->
                   <notebook>
                       <page string="Lines" name="lines">
                           <field name="line_ids">
                               <tree editable="bottom">
                                   <field name="product_id"/>
                                   <field name="name"/>
                                   <field name="quantity"/>
                                   <field name="price_unit"/>
                                   <field name="subtotal" sum="Total"/>
                               </tree>
                           </field>
                       </page>

                       <page string="Other Information" name="other_info">
                           <group>
                               <group string="Internal Notes">
                                   <field name="note" placeholder="Internal notes..."/>
                               </group>
                               <group string="Configuration">
                                   <field name="company_id"/>
                                   <field name="team_id"/>
                               </group>
                           </group>
                       </page>
                   </notebook>
               </sheet>

               <!-- Mail chatter -->
               <div class="oe_chatter">
                   <field name="message_follower_ids" widget="mail_followers"/>
                   <field name="activity_ids" widget="mail_activity"/>
                   <field name="message_ids" widget="mail_thread"/>
               </div>
           </form>
       </field>
   </record>
   ```

3. **Configure form attributes**:
   - `create="true/false"` - allow creating new records
   - `edit="true/false"` - allow editing
   - `delete="true/false"` - allow deleting
   - `duplicate="true/false"` - allow duplicating

4. **Use field widgets**:
   - `widget="statusbar"` - status bar in header
   - `widget="many2many_tags"` - tag-style display
   - `widget="monetary"` - with currency field
   - `widget="selection"` - dropdown selector
   - `widget="radio"` - radio buttons
   - `widget="many2one"` - relational field with search
   - `widget="text"` - text area
   - `widget="html"` - HTML editor
   - `widget="image"` - image upload
   - `widget="binary"` - file upload
   - `widget="boolean_toggle"` - toggle switch
   - `widget="checkbox"` - checkbox
   - `widget="date"` - date picker
   - `widget="datetime"` - datetime picker
   - `widget="phone"` - phone number
   - `widget="email"` - email address
   - `widget="url"` - URL link
   - `widget="domain"` - domain editor
   - `widget="state_selection"` - state dropdown
   - `widget="priority"` - priority stars
   - `widget="progressbar"` - progress bar
   - `widget="percentage"` - percentage display
   - `widget="selection_badge"` - badge selection
   - `widget="many2many_checkboxes"` - checkbox list
   - `widget="many2one_avatar"` - with avatar
   - `widget="handle"` - drag handle

5. **Apply field modifiers** (attrs or domain):
   ```xml
   <field name="field_name" attrs="{
       'readonly': [('state', '!=', 'draft')],
       'required': [('type', '=', 'special')],
       'invisible': [('is_company', '=', False)]
   }"/>
   ```

   Or use Odoo 19's new modifiers:
   ```xml
   <field name="field_name" readonly="1"/>
   <field name="field_name" required="1"/>
   <field name="field_name" invisible="1"/>
   ```

6. **Add field options**:
   - `options="{'no_create': True}"` - disable create
   - `options="{'no_open': True}"` - disable open
   - `options="{'no_quick_create': True}"` - disable quick create
   - `options="{'limit': 10}"` - limit results
   - `options="{'color_field': 'color'}"` - color field
   - `placeholder="Enter value..."` - placeholder text

7. **Configure statusbar**:
   ```xml
   <field name="state" widget="statusbar"
          statusbar_visible="draft,confirmed,done"
          statusbar_colors='{"draft":"blue","confirmed":"green","done":"gray"}'
          clickable="true"/>
   ```

8. **Add buttons** in header:
   ```xml
   <button name="action_method" string="Label" type="object"
           class="btn-primary" states="draft" confirm="Are you sure?"/>
   ```

9. **Create groups**:
   - First `<group>` creates two-column layout
   - Nested `<group>` within creates sections
   - Use `string` attribute for section labels
   - Use `name` attribute for identification

10. **Configure one2many/many2many fields**:
    ```xml
    <field name="line_ids">
        <tree editable="bottom">
            <field name="product_id"/>
            <field name="quantity"/>
        </tree>
        <form>
            <!-- Form definition -->
        </form>
        <kanban>
            <!-- Kanban definition -->
        </kanban>
    </field>
    ```

11. **Add chatter** (mail.thread integration):
    ```xml
    <div class="oe_chatter">
        <field name="message_follower_ids" widget="mail_followers"/>
        <field name="activity_ids" widget="mail_activity"/>
        <field name="message_ids" widget="mail_thread"/>
    </div>
    ```

## Usage Examples

**Basic form view:**
```
/view-form "res.partner" --fields="name,email,phone,is_company" --layout="sheet"
```

**With notebook:**
```
/view-form "sale.order" --fields="name,partner_id,date_order|line_ids|note" \
  --layout="notebook" --chatter=true
```

**With statusbar:**
```
/view-form "stock.picking" --fields="name,partner_id,state,move_ids" \
  --widgets="state:statusbar" --chatter=true
```

**Complex form:**
```
/view-form "account.move" --fields="name,partner_id,invoice_date|invoice_line_ids|journal_id" \
  --layout="notebook" --chatter=true --editable-states="draft"
```

## Odoo 19 Specific Features

- Improved `statusbar_visible` and `statusbar_colors`
- New `widget="selection_badge"` for badge-style selections
- Enhanced `many2many_avatar` widget with user avatars
- Better mobile responsiveness with `oe_button_box`
- New `widget="many2one_barcode"` for barcode scanning
- Improved `widget="monetary"` with currency formatting
- Support for `widget="text"` with autocomplete
- Enhanced `domain` widget with better UI
