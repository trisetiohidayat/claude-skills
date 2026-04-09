---
description: Create or update Odoo views from natural language description. Updated for Odoo 19 compatibility.
---

You are helping the user create or modify Odoo XML views.

## ⚠️ CRITICAL ODOO 19 CHANGES

**Before creating views, determine the Odoo version!**

### Breaking Changes in Odoo 17+ (affects Odoo 19):

1. **`<tree>` → `<list>`** - Tree view renamed to list
2. **`attrs` → `invisible`** - Direct attribute instead of attrs dict
3. **Decorations** - Use comparison operators: `decoration-success="state == 'draft'"`
4. **Buttons** - Remove `states` attribute, use `invisible` instead
5. **Search groups** - Remove `expand` attribute from `<group>`
6. **Kanban** - Only use existing model fields (no `color`, `priority` unless they exist)

## Steps

1. **Parse input**:
   - Target model (e.g., "sale.order", "ark.dpv")
   - View type: list (was tree), form, search, kanban, calendar, pivot, graph
   - Fields: comma-separated list to include
   - Optional: decorations, groupings, filters, domain
   - **Check Odoo version** - Critical for syntax!

2. **Locate existing view file**:
   - Find in module_path/views/{model}_views.xml
   - Or find standard Odoo views for reference

3. **Generate view XML** based on type and version:

   **⚠️ LIST VIEW (was TREE in Odoo 16/17)**

   For Odoo 19, use `<list>`:
   ```xml
   <record id="view_{model}_list" model="ir.ui.view">
       <field name="name">{model}.list</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <list string="{Model Label}" default_order="name" create="true" edit="true" multi_edit="true">
               <field name="name"/>
               <field name="partner_id"/>
               <field name="amount_total" sum="Total"/>
               <!-- Odoo 19: Use comparison in decorations -->
               <field name="state" widget="badge"
                      decoration-success="state == 'draft'"
                      decoration-info="state == 'confirmed'"
                      decoration-warning="state == 'sent'"
                      decoration-danger="state == 'cancelled'"/>

               <!-- Odoo 19: No states attribute, use invisible -->
               <button name="action_confirm" string="Confirm" type="object"
                       icon="fa-check" invisible="state != 'draft'"/>
           </list>
       </field>
   </record>
   ```

   **FORM VIEW**
   ```xml
   <record id="view_{model}_form" model="ir.ui.view">
       <field name="name">{model}.form</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <form string="{Model Label}" create="true" edit="true">
               <header>
                   <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,sent"/>
                   <!-- Odoo 19: Use invisible instead of attrs -->
                   <button name="action_confirm" string="Confirm" type="object"
                           class="btn-primary" invisible="state != 'draft'"/>
                   <button name="action_cancel" string="Cancel" type="object"
                           invisible="state not in ('draft', 'confirmed')"/>
               </header>
               <sheet>
                   <div class="oe_title">
                       <field name="name" placeholder="Name"
                               attrs="{'readonly': [('state', '!=', 'draft')]}"/>
                   </div>

                   <group>
                       <group>
                           <field name="partner_id"/>
                           <field name="date_order"/>
                       </group>
                       <group>
                           <field name="amount_total"/>
                           <field name="currency_id"/>
                       </group>
                   </group>

                   <notebook>
                       <page string="Lines">
                           <field name="line_ids">
                               <!-- Odoo 19: Use list inside one2many -->
                               <list editable="bottom">
                                   <field name="product_id"/>
                                   <field name="quantity"/>
                                   <field name="price_unit"/>
                                   <field name="subtotal" sum="Total"/>
                               </list>
                           </field>
                       </page>
                       <page string="Other Info">
                           <group>
                               <field name="note"/>
                           </group>
                       </page>
                   </notebook>
               </sheet>
               <div class="oe_chatter">
                   <field name="message_follower_ids" widget="mail_followers"/>
                   <field name="activity_ids" widget="mail_activity"/>
                   <field name="message_ids" widget="mail_thread"/>
               </div>
           </form>
       </field>
   </record>
   ```

   **SEARCH VIEW (Odoo 19)**
   ```xml
   <record id="view_{model}_search" model="ir.ui.view">
       <field name="name">{model}.search</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <search string="{Model Label}">
               <field name="name" string="Name" filter_name="name"/>
               <field name="partner_id"/>
               <separator/>
               <filter string="My Items" name="my_items" domain="[('create_uid', '=', uid)]"/>
               <filter string="Draft" name="draft" domain="[('state', '=', 'draft')]"/>
               <filter string="Confirmed" name="confirmed" domain="[('state', '=', 'confirmed')]"/>
               <separator/>
               <!-- Odoo 19: NO expand attribute in group -->
               <group string="Group By">
                   <filter string="Partner" name="group_partner" domain="[]" context="{'group_by': 'partner_id'}"/>
                   <filter string="State" name="group_state" domain="[]" context="{'group_by': 'state'}"/>
               </group>
           </search>
       </field>
   </record>
   ```

   **KANBAN VIEW (Odoo 19)**
   ```xml
   <record id="view_{model}_kanban" model="ir.ui.view">
       <field name="name">{model}.kanban</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <kanban default_group_by="state" quick_create="false">
               <!-- ONLY include fields that exist in the model -->
               <field name="name"/>
               <field name="partner_id"/>
               <field name="amount"/>
               <field name="state"/>
               <!-- ❌ DON'T add color/priority unless they exist in model -->
               <templates>
                   <t t-name="kanban-box">
                       <div class="oe_kanban_card">
                           <div class="oe_kanban_content">
                               <field name="name"/>
                               <field name="partner_id"/>
                           </div>
                       </div>
                   </t>
               </templates>
           </kanban>
       </field>
   </record>
   ```

   **CALENDAR VIEW**
   ```xml
   <record id="view_{model}_calendar" model="ir.ui.view">
       <field name="name">{model}.calendar</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <calendar string="{Model Label}" date_start="start_date" date_stop="stop_date" color="state">
               <field name="name"/>
               <field name="partner_id"/>
           </calendar>
       </field>
   </record>
   ```

   **PIVOT VIEW**
   ```xml
   <record id="view_{model}_pivot" model="ir.ui.view">
       <field name="name">{model}.pivot</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <pivot string="{Model Label}" display_quantity="true">
               <field name="partner_id" type="row"/>
               <field name="date" type="col"/>
               <field name="amount_total" type="measure"/>
           </pivot>
       </field>
   </record>
   ```

   **GRAPH VIEW**
   ```xml
   <record id="view_{model}_graph" model="ir.ui.view">
       <field name="name">{model}.graph</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <graph string="{Model Label}" type="bar" stacked="true">
               <field name="date" type="row"/>
               <field name="amount_total" type="measure"/>
           </graph>
       </field>
   </record>
   ```

4. **Add decorations** (color coding) for Odoo 19:
   ```xml
   <!-- Odoo 19: Use comparison operators -->
   <field name="state"
          decoration-success="state == 'draft'"
          decoration-info="state == 'confirmed'"
          decoration-warning="state == 'sent'"
          decoration-danger="state in ('cancelled', 'rejected')"
          decoration-muted="state == 'done'"/>
   ```

5. **Handle invisible attribute** (Odoo 19 replacement for attrs):
   ```xml
   <!-- ❌ OLD (Odoo 16/17) -->
   <button attrs="{'invisible': [('state', '!=', 'draft')]}"/>
   <field name="amount" attrs="{'readonly': [('state', '!=', 'draft')]}"/>

   <!-- ✅ NEW (Odoo 19) -->
   <button invisible="state != 'draft'"/>
   <field name="amount" readonly="state != 'draft'"/>
   ```

6. **Handle special widgets:**
   - badge: status fields
   - statusbar: form header status
   - many2many_tags: tag-style display
   - monetary: with currency
   - boolean_toggle: switch for boolean
   - selection: dropdown
   - handle: drag-drop reorder
   - image: image preview
   - url: clickable link
   - email: mailto link
   - phone: tel link

7. **Update __manifest__.py** if new view file:
   - Add to data list: "views/{model}_views.xml"

8. **Validate XML**:
   - Check syntax
   - Verify proper nesting
   - Ensure field references exist
   - **Odoo 19**: Check no deprecated attributes

9. **Show summary**:
   - View type created/modified
   - Fields included
   - Special widgets/decorations used
   - Odoo 19 compatibility notes

## ⚠️ ODOO 19 COMPATIBILITY CHECKLIST

Before finalizing views, check:

### For List Views:
- [ ] Used `<list>` instead of `<tree>`
- [ ] Decorations use comparison: `decoration-success="state == 'draft'"`
- [ ] Buttons use `invisible` instead of `states`

### For Form Views:
- [ ] Buttons use `invisible` instead of `attrs`
- [ ] One2many uses `<list>` inside, not `<tree>`

### For Search Views:
- [ ] No `expand` attribute in `<group>` tags

### For Kanban Views:
- [ ] Only include fields that exist in the model
- [ ] Don't add `color` or `priority` unless they exist in the model

### For All Views:
- [ ] No `attrs` attributes
- [ ] No `states` attributes on buttons

## Example Usage

```
/odoo-view create "sale.order" list \
  --fields="name,date_order,partner_id,amount_total,state" \
  --decorations="state:badge" --odoo-version=19
```

```
/odoo-view create "res.partner" kanban \
  --fields="name,email,phone,is_company" --odoo-version=19
```

## Important Notes

### For Odoo 19:
- **Always use `<list>`** instead of `<tree>`
- **Decorations require comparison**: `decoration-success="state == 'draft'"`
- **Use `invisible` attribute**: `invisible="state != 'draft'"`
- **Remove `expand` from search groups**
- **Kanban**: Only use existing model fields
- **One2many tree views**: Use `<list editable="bottom">`

### General:
- Always include proper field names from the model
- Use sum="Total" on numeric fields in list views
- Add journal/min/max attributes for numeric fields
- Use widget="phone"/"email" for proper formatting
- Set create/edit/multi_edit attributes on list view
- Use domain and context on action and view records
