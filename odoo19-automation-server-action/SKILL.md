---
description: Generate Odoo 19 ir.actions.server with code execution, object_create, or multi actions. Use when user wants to create a server action for model workflows.
---


You are helping the user create an Odoo 19 ir.actions.server XML definition.

## Steps

1. **Parse input**:
   - Extract module name
   - Parse action name
   - Extract model name
   - Parse action state
   - Parse code or field definitions
   - Parse condition
   - Parse binding settings
   - Check trigger configuration

2. **Generate server action XML** following Odoo 19 conventions:

   **Basic code action:**
   ```xml
   <record id="server_action_{action_name}" model="ir.actions.server">
       <field name="name">{Action Name}</field>
       <field name="model_id" ref="model_{model_dot}"/>
       <field name="state">code</field>
       <field name="code">
           # Python code here
           records.write({'field': value})
       </field>
   </record>
   ```

3. **Configure server action attributes**:
   - `name` - action display name
   - `model_id` - target model (use ref to model_* with dots converted to underscores)
   - `state` - action type (code, object_create, object_write, multi, followers)
   - `code` - Python code to execute
   - `condition` - Python condition to evaluate before execution
   - `crud_model_id` - model to create records in
   - `link_field_id` - field to link to current record
   - `ref_object_id` - field reference for linking
   - `child_ids` - child actions for multi state
   - `binding_model_id` - bind to model (smart button)
   - `binding_type` - binding type (action, report)
   - `binding_view_types` - allowed view types (form, tree, kanban, list)
   - `trigger_obj_id` - for base_action_rule integration
   - `on_change` - trigger on field change
   - `use_relational_field` - use relational field context
   - `use_write` - use write instead of create
   - `active` - enable/disable action

4. **Action states**:

   **code** - Execute Python code:
   ```xml
   <field name="state">code</field>
   <field name="code">
       # Access current record with 'record' or 'records'
       for record in records:
           record.action_confirm()

       # Access environment with 'env'
       user = env.user

       # Return action
       action = {
           'type': 'ir.actions.act_window',
           'res_model': 'sale.order',
           'view_mode': 'form',
           'res_id': record.id,
       }
   </field>
   ```

   **object_create** - Create new record:
   ```xml
   <field name="state">object_create</field>
   <field name="crud_model_id" ref="model_mail_message"/>
   <field name="link_field_id" ref="mail_message_field_res_id"/>
   <field name="ref_object_id" ref="mail_message_field_res_model_id"/>
   <!-- Use fields to populate -->
   <field name="fields_line_ids" eval="[
       (0, 0, {'col1': 'subject', 'value1': 'Hello', 'type1': 'value'}),
       (0, 0, {'col1': 'body', 'value1': 'World', 'type1': 'value'}),
   ]"/>
   ```

   **object_write** - Update current record:
   ```xml
   <field name="state">object_write</field>
   <field name="fields_line_ids" eval="[
       (0, 0, {'col1': 'state', 'value1': 'done', 'type1': 'value'}),
       (0, 0, {'col1': 'date_done', 'value1': 'context_today()', 'type1': 'equation'}),
   ]"/>
   ```

   **multi** - Execute multiple actions:
   ```xml
   <field name="state">multi</field>
   <field name="child_ids" eval="[
       (4, ref('server_action_1')),
       (4, ref('server_action_2')),
   ]"/>
   ```

   **followers** - Add followers:
   ```xml
   <field name="state">followers</field>
   <field name="partner_ids" eval="[(4, ref('base.partner_admin'))]"/>
   ```

5. **Model reference format**:
   - For model `sale.order` use `model_sale_order`
   - For model `res.partner` use `model_res_partner`
   - Convert dots to underscores in ref

6. **Code execution examples**:

   **Simple field update:**
   ```xml
   <field name="code">
       for record in records:
           record.write({'state': 'approved'})
   </field>
   ```

   **Conditional logic:**
   ```xml
   <field name="code">
       for record in records:
           if record.amount > 1000:
               record.write({'need_approval': True})
           else:
               record.write({'need_approval': False})
   </field>
   ```

   **Create related records:**
   ```xml
   <field name="code">
       for record in records:
           env['mail.message'].create({
               'res_id': record.id,
               'model': record._name,
               'message_type': 'notification',
               'body': 'Order processed',
           })
   </field>
   ```

   **Send email:**
   ```xml
   <field name="code">
       template = env.ref('my_module.email_template_my_template')
       for record in records:
           template.send_mail(record.id, force_send=True)
   </field>
   ```

   **Return action:**
   ```xml
   <field name="code">
       action = {
           'type': 'ir.actions.act_window',
           'name': 'Related Records',
           'res_model': 'sale.order.line',
           'view_mode': 'tree,form',
           'domain': [('order_id', '=', record.id)],
           'context': {'default_order_id': record.id},
       }
   </field>
   ```

   **Wizard launch:**
   ```xml
   <field name="code">
       action = env.ref('my_module.action_my_wizard').read()[0]
       action['context'] = {'default_active_id': record.id}
       return action
   </field>
   ```

   **Complex processing:**
   ```xml
   <field name="code"><![CDATA[
       total = 0
       for record in records:
           line_total = sum(line.price_subtotal for line in record.order_line)
           record.write({'amount_total': line_total})
           total += line_total

       # Send summary
       env['mail.message'].create({
           'res_id': records[0].id,
           'model': records._name,
           'body': 'Processed %d orders totaling %s' % (len(records), total),
       })

       return {
           'type': 'ir.actions.client',
           'tag': 'display_notification',
           'params': {
               'message': 'Processed %d orders' % len(records),
               'type': 'success',
           }
       }
   ]]></field>
   ```

7. **Add condition**:
   ```xml
   <!-- Only execute if condition is true -->
   <field name="condition">
       record.amount > 0
   </field>

   <!-- Multiple conditions -->
   <field name="condition">
       record.state == 'draft' and record.user_id == env.user
   </field>

   <!-- Check related records -->
   <field name="condition">
       len(record.order_line) > 0
   </field>
   ```

8. **Bind to model** (smart button/action menu):
   ```xml
   <!-- Bind to form view -->
   <field name="binding_model_id" ref="model_res_partner"/>
   <field name="binding_type">action</field>

   <!-- Bind to specific view types -->
   <field name="binding_view_types">form</field>

   <!-- Bind to multiple view types -->
   <field name="binding_view_types">form,tree</field>
   ```

9. **Object create with fields**:
   ```xml
   <field name="state">object_create</field>
   <field name="crud_model_id" ref="model_project_task"/>
   <field name="link_field_id" ref="project_task_field_project_id"/>
   <field name="fields_line_ids" eval="[
       (0, 0, {
           'col1': 'name',
           'value1': 'Task from ' + record.name,
           'type1': 'value',
       }),
       (0, 0, {
           'col1': 'user_id',
           'value1': str(env.user.id),
           'type1': 'value',
       }),
       (0, 0, {
           'col1': 'date_deadline',
           'value1': '(context_today() + timedelta(days=7)).strftime("%Y-%m-%d")',
           'type1': 'equation',
       }),
   ]"/>
   ```

10. **Object write with fields**:
    ```xml
    <field name="state">object_write</field>
    <field name="fields_line_ids" eval="[
        (0, 0, {
            'col1': 'state',
            'value1': 'approved',
            'type1': 'value',
        }),
        (0, 0, {
            'col1': 'approved_date',
            'value1': 'context_today().strftime("%Y-%m-%d")',
            'type1': 'equation',
        }),
        (0, 0, {
            'col1': 'approved_user_id',
            'value1': 'str(env.user.id)',
            'type1': 'value',
        }),
    ]"/>
    ```

11. **Multi-action**:
    ```xml
    <record id="server_action_multi" model="ir.actions.server">
        <field name="name">Multi Action Example</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="state">multi</field>
        <field name="child_ids" eval="[
            (4, ref('server_action_send_email')),
            (4, ref('server_action_update_state')),
            (4, ref('server_action_create_invoice')),
        ]"/>
    </record>
    ```

12. **Followers action**:
    ```xml
    <record id="server_action_add_followers" model="ir.actions.server">
        <field name="name">Add Team as Followers</field>
        <field name="model_id" ref="model_project_task"/>
        <field name="state">followers</field>
        <field name="partner_ids" eval="[
            (4, ref('base.partner_admin')),
            (4, ref('base.partner_demo')),
        ]"/>
    </record>
    ```

13. **Action for button**:
    ```xml
    <!-- Server action for button -->
    <record id="server_action_button" model="ir.actions.server">
        <field name="name">Button Action</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="state">code</field>
        <field name="code">
            for record in records:
                record.action_button_clicked()
        </field>
    </record>

    <!-- Then add button to view -->
    <button name="%(server_action_button)d" string="Click Me" type="action"/>
    ```

14. **Context menu action**:
    ```xml
    <record id="server_action_context" model="ir.actions.server">
        <field name="name">Context Menu Action</field>
        <field name="model_id" ref="model_res_partner"/>
        <field name="state">code</field>
        <field name="code">
            action = env.ref('my_module.action_window').read()[0]
            action['domain'] = [('partner_id', '=', record.id)]
            return action
        </field>
        <field name="binding_model_id" ref="model_res_partner"/>
        <field name="binding_type">action</field>
    </record>
    ```

15. **Action for onchange**:
    ```xml
    <record id="server_action_onchange" model="ir.actions.server">
        <field name="name">On Change Action</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="state">code</field>
        <field name="code">
            if record.partner_id:
                record.update({
                    'pricelist_id': record.partner_id.property_product_pricelist,
                })
        </field>
        <field name="on_change">True</field>
    </record>
    ```

16. **Base action rule integration**:
    ```xml
    <record id="server_action_automation" model="ir.actions.server">
        <field name="name">Automation Action</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="state">code</field>
        <field name="code">
            for record in records:
                record.action_send_reminder()
        </field>
    </record>

    <!-- Then use in base_action_rule -->
    <record id="rule_send_reminder" model="base_action_rule">
        <field name="name">Send Reminder</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="kind">on_write</field>
        <field name="server_action_ids" eval="[(4, ref('server_action_automation'))]"/>
    </record>
    ```

17. **Return wizard/action**:
    ```xml
    <field name="code"><![CDATA[
        wizard = env['my.wizard'].create({
            'order_id': record.id,
            'date': fields.Date.context_today(self),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'my.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'context': env.context,
        }
    ]]></field>
    ```

18. **Send notification**:
    ```xml
    <field name="code"><![CDATA[
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Action completed successfully!',
                'type': 'success',
                'sticky': False,
            }
        }
    ]]></field>
    ```

## Usage Examples

**Simple code action:**
```bash
/automation-server-action "sale_order" "Mark as Paid" "sale.order" \
  --state="code" --code="for record in records: record.write({'payment_state': 'paid'})"
```

**Conditional action:**
```bash
/automation-server-action "crm" "Convert High Value Lead" "crm.lead" \
  --state="code" --condition="record.probability >= 80" \
  --code="for record in records: record.action_convert()"
```

**Create related record:**
```bash
/automation-server-action "project" "Create Task from Project" "project.project" \
  --state="object_create" --create_model="project.task" \
  --create_fields='{"name": "New Task", "project_id": "record.id"}'
```

**Update fields:**
```bash
/automation-server-action "hr" "Confirm Employee" "hr.employee" \
  --state="object_write" --write_fields='{"state": "open", "confirmed_date": "context_today()"}'
```

**Multi-action:**
```bash
/automation-server-action "sale" "Complete Order Process" "sale.order" \
  --state="multi" --child_actions="server_action_confirm,server_action_invoice,server_action_email"
```

**Bind to model (smart button):**
```bash
/automation-server-action "account" "View Invoices" "res.partner" \
  --state="code" --binding_model="res.partner" \
  --code="action = env.ref('account.action_move_out_invoice_type').read()[0]; action['domain'] = [('partner_id', '=', record.id)]; return action"
```

**Send notification:**
```bash
/automation-server-action "stock" "Low Stock Alert" "stock.quant" \
  --state="code" --condition="record.quantity < record.reorder_level" \
  --code="env['mail.message'].create({'res_id': record.id, 'model': record._name, 'body': 'Low stock warning!'})"
```

## Field Types for object_create/object_write

**value** - Static value:
```xml
<field name="type1">value</field>
<field name="value1">My Value</field>
```

**equation** - Python expression:
```xml
<field name="type1">equation</field>
<field name="value1">record.partner_id.name</field>
```

**function** - Call function:
```xml
<field name="type1">function</field>
<field name="value1">context_today()</field>
```

## Best Practices

1. **Error Handling**:
   - Wrap code in try-except blocks
   - Log errors for debugging
   - Validate input data

2. **Performance**:
   - Process records in batches
   - Avoid complex loops
   - Use search() efficiently

3. **Security**:
   - Check user permissions
   - Validate record access
   - Use appropriate user context

4. **Testing**:
   - Test actions manually first
   - Test with various data scenarios
   - Verify return values

5. **Code Quality**:
   - Use descriptive variable names
   - Add comments for complex logic
   - Follow PEP 8 style guide

6. **User Experience**:
   - Return user-friendly notifications
   - Provide feedback on actions
   - Handle edge cases gracefully

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── data/
│   └── server_actions.xml  # Server action definitions
└── security/
    └── ir.model.access.csv  # Access rights
```

## Next Steps

After creating server actions:
- `/automation-cron` - Create scheduled tasks
- Add buttons to views that call server actions
- Create base_action_rule records for automation
- Test actions with various scenarios
- Monitor execution logs
