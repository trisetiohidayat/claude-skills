---
description: Generate Odoo 19 ir.actions.act_window with views, domain, and context. Use when user wants to create a window action for opening a model with specific views.
---


You are helping the user create an Odoo 19 action window XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse action name
   - Parse view modes
   - Check view type
   - Parse domain
   - Parse context
   - Check limit
   - Determine target

2. **Generate action window XML** following Odoo 19 conventions:

   **Basic action window:**
   ```xml
   <record id="action_{model}" model="ir.actions.act_window">
       <field name="name">{Action Name}</field>
       <field name="type">ir.actions.act_window</field>
       <field name="res_model">{model}</field>
       <field name="view_mode">tree,form</field>
       <field name="view_type">form</field>
       <field name="domain">[]</field>
       <field name="context">{}</field>
       <field name="limit">80</field>
       <field name="target">current</field>
       <field name="help" type="html">
           <p class="o_view_nocontent_smiling_face">
               Create your first {model} record!
           </p>
       </field>
   </record>
   ```

3. **Configure action attributes**:
   - `name` - action display name
   - `type` - always "ir.actions.act_window"
   - `res_model` - target model
   - `view_mode` - comma-separated view modes
   - `view_type` - primary view type (form, tree, kanban)
   - `domain` - filter domain
   - `context` - context dictionary
   - `limit` - default record limit
   - `target` - window target
   - `search_view_id` - specific search view
   - `flags` - UI flags
   - `binding_model_id` - bind to model
   - `binding_type` - binding type (action, report)
   - `binding_view_types` - allowed view types

4. **View modes** (comma-separated):
   - `tree` - list view
   - `form` - detail view
   - `kanban` - kanban board
   - `calendar` - calendar view
   - `pivot` - pivot analysis
   - `graph` - chart view
   - `activity` - activity view
   - `map` - map view
   - `co_tree` - calendar tree view
   - `co_kanban` - calendar kanban view

5. **View types**:
   - `form` - start in form view (default)
   - `tree` - start in tree view
   - `kanban` - start in kanban view

6. **Add domain filter**:
   ```xml
   <field name="domain">[('state', '=', 'draft')]</field>
   <!-- or -->
   <field name="domain">[('user_id', '=', uid)]</field>
   <!-- or -->
   <field name="domain">[('date', '>=', (context_today()).strftime('%Y-%m-%d'))]</field>
   ```

7. **Add context**:
   ```xml
   <field name="context">{'default_state': 'draft'}</field>
   <!-- or -->
   <field name="context">{'search_default_my_items': 1}</field>
   <!-- or -->
   <field name="context">{'default_user_id': uid}</field>
   <!-- or multiple -->
   <field name="context">{'default_state': 'draft', 'search_default_my_items': 1}</field>
   ```

8. **Set target**:
   ```xml
   <field name="target">current</field>
   <!-- opens in current window -->
   <field name="target">new</field>
   <!-- opens in new window/dialog -->
   <field name="target">inline</field>
   <!-- opens inline -->
   <field name="target">fullscreen</field>
   <!-- opens in fullscreen -->
   ```

9. **Add help message**:
   ```xml
   <field name="help" type="html">
       <p class="o_view_nocontent_smiling_face">
           Create your first record!
       </p>
       <p>
           You can also configure settings or import data.
       </p>
   </field>
   ```

10. **Bind specific views**:
    ```xml
    <field name="view_ids" eval="[(5, 0, 0),
        (0, 0, {'view_mode': 'tree', 'view_id': ref('view_my_tree')}),
        (0, 0, {'view_mode': 'form', 'view_id': ref('view_my_form')})]"/>
    ```

11. **Add search view**:
    ```xml
    <field name="search_view_id" ref="view_{model}_search"/>
    ```

12. **Set flags**:
    ```xml
    <field name="flags">{'sidebar': False}</field>
    <!-- or -->
    <field name="flags">{'header': False}</field>
    <!-- or -->
    <field name="flags">{'pager': False}</field>
    <!-- or -->
    <field name="flags">{'action_buttons': True}</field>
    ```

13. **Add limit**:
    ```xml
    <field name="limit">80</field>
    <!-- default page size -->
    ```

14. **Create dashboard action**:
    ```xml
    <record id="action_{model}_dashboard" model="ir.actions.act_window">
        <field name="name">{Model} Dashboard</field>
        <field name="res_model">{model}</field>
        <field name="view_mode">pivot,graph</field>
        <field name="context">{'group_by': ['date:month']}</field>
    </record>
    ```

15. **Create calendar action**:
    ```xml
    <record id="action_{model}_calendar" model="ir.actions.act_window">
        <field name="name">{Model} Calendar</field>
        <field name="res_model">{model}</field>
        <field name="view_mode">calendar</field>
        <field name="view_type">form</field>
        <field name="context">{}</field>
    </record>
    ```

16. **Create kanban action**:
    ```xml
    <record id="action_{model}_kanban" model="ir.actions.act_window">
        <field name="name">{Model} Kanban</field>
        <field name="res_model">{model}</field>
        <field name="view_mode">kanban,tree,form</field>
        <field name="view_type">kanban</field>
        <field name="context">{'default_group_by': 'stage_id'}</field>
    </record>
    ```

17. **Bind to model** (smart button):
    ```xml
    <field name="binding_model_id" ref="model_res_partner"/>
    <field name="binding_type">action</field>
    ```

18. **Auto-open in form**:
    ```xml
    <record id="action_{model}_form" model="ir.actions.act_window">
        <field name="name">{Model}</field>
        <field name="res_model">{model}</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="context">{}</field>
    </record>
    ```

## Usage Examples

**Basic action:**
```
/action-window "sale.order" "Sales Orders" --view_mode="tree,form"
```

**With domain:**
```
/action-window "account.move" "Customer Invoices" --view_mode="tree,form" \
  --domain="[('move_type', '=', 'out_invoice')]"
```

**Kanban action:**
```
/action-window "project.task" "Tasks" --view_mode="kanban,tree,form" \
  --view_type="kanban" --context="{'default_group_by': 'stage_id'}"
```

**Dashboard action:**
```
/action-window "sale.report" "Sales Dashboard" --view_mode="pivot,graph" \
  --context="{'group_by': ['date:month', 'user_id']}"
```

**With search filter:**
```
/action-window "res.partner" "Customers" --view_mode="tree,form" \
  --context="{'search_default_my_items': 1}"
```

**New window action:**
```
/action-window "wizard.model" "Run Wizard" --view_mode="form" \
  --target="new" --context="{'default_active_id': active_id}"
```

## Odoo 19 Specific Features

- Enhanced `view_mode` with new view types
- New `binding_view_types` for smart buttons
- Improved `target` attribute with better UX
- Enhanced `context` handling with defaults
- New `flags` options for better UI control
- Improved `help` message with rich content
- Better `limit` handling
- Enhanced `domain` with advanced filters
- New `search_view_id` integration
- Improved dashboard actions
- Better calendar actions
- Enhanced kanban actions
- New `binding_model_id` for smart buttons
- Improved view binding with `view_ids`
