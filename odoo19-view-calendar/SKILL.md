---
description: Generate Odoo 19 calendar view with date fields, colors, and filters. Use when user wants to create a calendar view.
---


You are helping the user create an Odoo 19 calendar view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Identify date_start field (required)
   - Check for date_stop or date_delay field
   - Identify color field
   - Parse additional fields
   - Determine default mode

2. **Generate calendar view XML** following Odoo 19 conventions:

   **Basic calendar view:**
   ```xml
   <record id="view_{model}_calendar" model="ir.ui.view">
       <field name="name">{model}.calendar</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <calendar string="{Model Label}"
                     date_start="{start_date_field}"
                     date_stop="{end_date_field}"
                     date_delay="{delay_field}"
                     color="{color_field}"
                     mode="month"
                     quick_create="true"
                     event_open_popup="true"
                     all_day="all_day"
                     timezone="true">
               <field name="name"/>
               <field name="partner_id"/>
               <field name="user_id"/>
               <field name="state"/>
               <field name="location"/>
           </calendar>
       </field>
   </record>
   ```

3. **Configure calendar attributes**:
   - `date_start="field_name"` - start date/time field (required)
   - `date_stop="field_name"` - end date/time field
   - `date_delay="field_name"` - duration field (alternative to date_stop)
   - `color="field_name"` - field for event coloring
   - `mode="month|week|day|3day"` - default view mode
   - `quick_create="true"` - enable quick create on click
   - `event_open_popup="true"` - open event in popup
   - `all_day="field_name"` - all-day event boolean field
   - `timezone="true"` - show timezone info
   - `scale="month|week|day"` - alias for mode
   - `form_view_id="view_id"` - custom form view
   - `create="true|false"` - enable create
   - `edit="true|false"` - enable edit
   - `delete="true|false"` - enable delete

4. **Use color field**:
   - Color field should be integer (0-11) or many2one with color field
   - Many2one field: user_id, partner_id, stage_id
   - Selection field: converts to colors
   - Can use `color_field` attribute on many2one to specify color field

5. **Add event fields**:
   - Main display field: first field or `name` field
   - Additional fields shown in event details
   - Fields with special widgets:
     - `widget="many2one_avatar"` - show avatar
     - `widget="badge"` - show as badge

6. **Configure all-day events**:
   ```xml
   <calendar date_start="start_date" all_day="is_all_day">
   ```
   - When all_day field is true, shows without time

7. **Use duration** instead of end date:
   ```xml
   <calendar date_start="start_date" date_delay="duration">
   ```
   - Duration field in hours
   - Alternative to date_stop

8. **Add filters** in search view:
   ```xml
   <search>
       <field name="user_id"/>
       <filter string="My Events" name="my_events" domain="[('user_id', '=', uid)]"/>
       <filter string="This Week" name="this_week"
               domain="[('date_start', '>=', (context_today() - datetime.timedelta(days=context_today().weekday())).strftime('%Y-%m-%d')),
                       ('date_start', '<=', (context_today() + datetime.timedelta(days=6-context_today().weekday())).strftime('%Y-%m-%d'))]"/>
   </search>
   ```

9. **Customize event display**:
   - First field shown as title
   - Additional fields shown in popover
   - Avatar fields shown with images
   - Color field determines event color

10. **Handle timezone**:
    - Set `timezone="true"` to show timezone
    - Uses user's timezone preference
    - Shows timezone in event details

11. **Add custom scales/modes**:
    - `mode="month"` - full month view
    - `mode="week"` - week view
    - `mode="day"` - day view
    - `mode="3day"` - 3-day view

## Usage Examples

**Basic calendar:**
```
/view-calendar "calendar.event" --date_start="start" --date_stop="stop" \
  --color="user_id" --fields="name,partner_id,location"
```

**With duration:**
```
/view-calendar "project.task" --date_start="date_deadline" --date_delay="planned_hours" \
  --color="stage_id" --mode="week"
```

**Monthly view:**
```
/view-calendar "hr.leave" --date_start="date_from" --date_stop="date_to" \
  --color="state" --mode="month" --fields="name,employee_id,holiday_status_id"
```

**Day view with filters:**
```
/view-calendar "sale.order" --date_start="date_order" --color="state" \
  --mode="day" --quick_create=true --fields="name,partner_id,amount_total"
```

## Odoo 19 Specific Features

- Enhanced `mode` attribute with better UX
- Improved `event_open_popup` for better mobile experience
- New `timezone` attribute for timezone support
- Better color field handling with more colors
- Improved `quick_create` with validation
- Better integration with mobile view
- Enhanced event popover with more fields
- Support for `all_day` with custom styling
- Better performance with large datasets
- Improved navigation between dates
