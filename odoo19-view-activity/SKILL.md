---
description: Generate Odoo 19 activity view for scheduling and tracking activities. Use when user wants to create an activity view.
---


You are helping the user create an Odoo 19 activity view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse fields to display
   - Identify activity filters
   - Parse quick actions

2. **Generate activity view XML** following Odoo 19 conventions:

   **Basic activity view:**
   ```xml
   <record id="view_{model}_activity" model="ir.ui.view">
       <field name="name">{model}.activity</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <activity string="{Model Label}">
               <field name="name"/>
               <field name="partner_id"/>
               <field name="date_deadline"/>
               <field name="state"/>
               <field name="user_id"/>
               <field name="activity_ids"/>
               <field name="activity_user_id"/>
               <field name="activity_summary"/>
               <field name="activity_type_id"/>
           </activity>
       </field>
   </record>
   ```

3. **Ensure model inherits mail.activity.mixin**:
   ```python
   class MyModel(models.Model):
       _name = 'my.model'
       _inherit = ['mail.thread', 'mail.activity.mixin']
   ```

4. **Configure activity attributes**:
   - `string="Label"` - view title
   - `default_filter="overdue|today|upcoming|all"` - default filter
   - `limit="80"` - default page size
   - `domain="[]"` - additional filter domain

5. **Add activity fields**:
   ```xml
   <activity>
       <field name="name"/>
       <field name="partner_id"/>
       <field name="activity_ids" widget="list_activity"/>
       <field name="activity_user_id"/>
       <field name="activity_date_deadline"/>
       <field name="activity_summary"/>
       <field name="activity_note"/>
   </activity>
   ```

6. **Activity filters**:
   - `overdue` - activities past due date
   - `today` - activities due today
   - `upcoming` - future activities
   - `all` - all activities

7. **Add activity state colors**:
   ```xml
   <field name="activity_state" decoration-danger="overdue"
          decoration-warning="today"
          decoration-success="upcoming"/>
   ```

8. **Display activity details**:
   ```xml
   <activity>
       <field name="name"/>
       <field name="partner_id"/>
       <field name="activity_ids">
           <kanban>
               <field name="activity_type_id"/>
               <field name="summary"/>
               <field name="date_deadline"/>
               <field name="user_id"/>
           </kanban>
       </field>
   </activity>
   ```

9. **Add activity type filtering**:
   ```xml
   <search>
       <filter string="Email" name="activity_email"
               domain="[('activity_ids.activity_type_id.category', '=', 'email')]"/>
       <filter string="Call" name="activity_call"
               domain="[('activity_ids.activity_type_id.category', '=', 'phonecall')]"/>
       <filter string="Meeting" name="activity_meeting"
               domain="[('activity_ids.activity_type_id.category', '=', 'meeting')]"/>
       <filter string="Task" name="activity_task"
               domain="[('activity_ids.activity_type_id.category', '=', 'task')]"/>
   </search>
   ```

10. **My activities filter**:
    ```xml
    <filter string="My Activities" name="my_activities"
            domain="[('activity_ids.user_id', '=', uid)]"/>
    ```

11. **Scheduled activities**:
    ```xml
    <filter string="Scheduled" name="scheduled"
            domain="[('activity_ids.date_deadline', '>=', context_today().strftime('%Y-%m-%d'))]"/>
    ```

12. **Overdue activities**:
    ```xml
    <filter string="Overdue" name="overdue"
            domain="[('activity_ids.date_deadline', '<', context_today().strftime('%Y-%m-%d')),
                    ('activity_ids.state', 'not in', ['done'])]"/>
    ```

13. **Add activity buttons**:
    ```xml
    <activity>
       <field name="name"/>
       <button name="schedule_activity" string="Schedule Activity"
               type="object" class="oe_highlight"/>
    </activity>
    ```

14. **Mark as done**:
    ```xml
    <activity>
       <field name="activity_ids" widget="list_activity">
           <button name="action_done" string="Mark Done"
                   type="object" icon="fa-check"/>
       </field>
    </activity>
    ```

15. **Add summary field**:
    ```xml
    <field name="activity_summary" widget="text"/>
    <field name="activity_note" widget="text"/>
    ```

16. **Add date fields**:
    ```xml
    <field name="activity_date_deadline"/>
    <field name="activity_date_create"/>
    <field name="activity_date_done"/>
    ```

17. **Add user assignment**:
    ```xml
    <field name="activity_user_id" widget="many2one_avatar"/>
    ```

18. **Activity type display**:
    ```xml
    <field name="activity_type_id" widget="badge"/>
    ```

## Usage Examples

**Basic activity:**
```
/view-activity "res.partner" --fields="name,email,phone,activity_ids"
```

**With filters:**
```
/view-activity "crm.lead" --fields="name,partner_id,activity_ids,activity_summary" \
  --filters="overdue,today,upcoming"
```

**Sales activities:**
```
/view-activity "sale.order" --fields="name,partner_id,amount_total,activity_ids" \
  --filters="my_activities,overdue" --actions="schedule_call,mark_done"
```

**Project activities:**
```
/view-activity "project.task" --fields="name,project_id,user_id,activity_ids" \
  --filters="my_activities,today"
```

## Odoo 19 Specific Features

- Enhanced activity view with better performance
- New `widget="list_activity"` for better activity display
- Improved activity filtering with date ranges
- Better mobile responsiveness
- Enhanced activity state colors
- New activity type icons
- Improved quick actions
- Better activity delegation
- Enhanced activity templates
- New activity summary display
- Improved activity note editor
- Better activity recurrence support
- Enhanced activity statistics
- New activity dashboard
- Improved activity reporting
