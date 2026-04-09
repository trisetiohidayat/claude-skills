---
description: Generate Odoo 19 coach/dashboard view with columns and widgets. Use when user wants to create a dashboard/coach view.
---


You are helping the user create an Odoo 19 coach (dashboard) view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse column definitions with domains
   - Identify widget types for columns
   - Parse default values

2. **Generate coach view XML** following Odoo 19 conventions:

   **Basic coach view:**
   ```xml
   <record id="view_{model}_coach" model="ir.ui.view">
       <field name="name">{model}.coach</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <coach string="{Model Label}">
               <!-- Column 1: All items -->
               <column name="all_items" string="All Items">
                   <field name="name"/>
                   <field name="partner_id"/>
                   <field name="date"/>
                   <field name="user_id"/>
               </column>

               <!-- Column 2: My items -->
               <column name="my_items" string="My Items">
                   <field name="name"/>
                   <field name="partner_id"/>
                   <field name="date"/>
                   <field name="user_id"/>
                   <domain>[('user_id', '=', uid)]</domain>
               </column>

               <!-- Column 3: High priority -->
               <column name="high_priority" string="High Priority">
                   <field name="name"/>
                   <field name="partner_id"/>
                   <field name="priority"/>
                   <field name="date"/>
                   <domain>[('priority', '>=', '3')]</domain>
               </column>

               <!-- Column 4: Overdue -->
               <column name="overdue" string="Overdue">
                   <field name="name"/>
                   <field name="partner_id"/>
                   <field name="date_deadline"/>
                   <domain>[('date_deadline', '<', context_today().strftime('%Y-%m-%d')), ('state', 'not in', ['done', 'cancelled'])]</domain>
               </column>
           </coach>
       </field>
   </record>
   ```

3. **Configure coach attributes**:
   - `string="Label"` - view title
   - `default_column="column_id"` - default active column
   - `column_click="select|open"` - behavior on column click
   - `sample="1"` - show sample data

4. **Add columns**:
   ```xml
   <column name="column_id" string="Column Label">
       <field name="name"/>
       <field name="partner_id"/>
       <domain>[('field', '=', value)]</domain>
   </column>
   ```
   - `name` - unique column identifier
   - `string` - column display label
   - `domain` - filter domain for column

5. **Column domains**:
   - Simple: `[('user_id', '=', uid)]`
   - Date based: `[('date', '>=', context_today().strftime('%Y-%m-%d'))]`
   - State based: `[('state', 'in', ['draft', 'confirmed'])]`
   - Complex: `['|', ('field1', '=', value1), ('field2', '=', value2)]`

6. **Add fields to columns**:
   ```xml
   <column name="my_column">
       <field name="name"/>
       <field name="partner_id"/>
       <field name="date"/>
       <field name="state"/>
   </column>
   ```
   - Fields shown in each card/item
   - First field is typically the title

7. **Configure column widgets**:
   ```xml
   <column name="tasks" widget="kanban">
       <field name="name"/>
       <field name="project_id"/>
   </column>
   ```
   - `widget="kanban"` - kanban cards
   - `widget="tree"` - tree view
   - `widget="calendar"` - calendar view
   - `widget="activity"` - activity view

8. **Add column modifiers**:
   ```xml
   <column name="my_items" readonly="True">
   ```
   - `readonly="True"` - read-only column
   - `invisible="True"` - hidden column

9. **Set default column**:
   ```xml
   <coach default_column="my_items">
   ```

10. **Add color coding**:
    ```xml
    <column name="urgent" string="Urgent">
        <field name="name"/>
        <field name="priority"/>
        <domain>[('priority', '>=', '3')]</domain>
        <field name="color" widget="color_picker"/>
    </column>
    ```

11. **Add counts**:
    ```xml
    <column name="pending" string="Pending">
        <field name="name"/>
        <field name="state"/>
        <domain>[('state', '=', 'pending')]</domain>
        <count_field name="task_count"/>
    </column>
    ```

12. **Add aggregate data**:
    ```xml
    <column name="sales" string="Sales">
        <field name="name"/>
        <field name="amount_total"/>
        <aggregate name="total" field="amount_total" aggregation="sum"/>
    </column>
    ```

13. **Add date ranges**:
    ```xml
    <column name="this_week" string="This Week">
        <field name="name"/>
        <field name="date"/>
        <domain>[('date', '>=', (context_today() - datetime.timedelta(days=context_today().weekday())).strftime('%Y-%m-%d')),
                ('date', '<=', (context_today() + datetime.timedelta(days=6-context_today().weekday())).strftime('%Y-%m-%d'))]</domain>
    </column>
    ```

14. **Add user-specific columns**:
    ```xml
    <column name="my_tasks" string="My Tasks">
        <field name="name"/>
        <field name="user_id"/>
        <domain>[('user_id', '=', uid)]</domain>
    </column>
    ```

15. **Add team columns**:
    ```xml
    <column name="team_tasks" string="Team Tasks">
        <field name="name"/>
        <field name="team_id"/>
        <domain>[('team_id', 'in', user.team_ids.ids)]</domain>
    </column>
    ```

## Usage Examples

**Basic coach:**
```
/view-coach "project.task" --columns="all:All,my:My:user_id:uid,high:High:priority:3"
```

**Sales pipeline:**
```
/view-coach "crm.lead" --columns="leads:Leads:state:lead,prospects:Prospects:state:prospects,customers:Customers:state:customer" \
  --widgets="kanban,kanban,kanban"
```

**Project dashboard:**
```
/view-coach "project.task" --columns="my:My:user_id:uid,today:Today:date:today,overdue:Overdue:date_deadline:lt:today,week:ThisWeek:date:week" \
  --defaults="my"
```

**Support dashboard:**
```
/view-coach "helpdesk.ticket" --columns="new:New:state:new,assigned:Assigned:user_id:not_uid,high:High:priority:high,urgent:Urgent:priority:urgent"
```

## Odoo 19 Specific Features

- Enhanced coach view with better performance
- New `widget="activity"` for activity columns
- Improved column rendering
- Better mobile responsiveness
- Enhanced domain handling
- New aggregate data display
- Better color coding options
- Improved column customization
- Enhanced date range filters
- Better team-based filtering
- New count_field for record counts
- Improved sample data mode
