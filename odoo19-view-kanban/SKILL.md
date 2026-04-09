---
description: Generate Odoo 19 kanban view with cards, progress bars, and drag-drop. Use when user wants to create a kanban view.
---


You are helping the user create an Odoo 19 kanban view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse field list for card display
   - Identify grouping field
   - Check quick_create and drag_drop options
   - Parse progress bar configuration

2. **Generate kanban view XML** following Odoo 19 conventions:

   **Basic kanban view:**
   ```xml
   <record id="view_{model}_kanban" model="ir.ui.view">
       <field name="name">{model}.kanban</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <kanban string="{Model Label}"
                  default_group_by="{grouping_field}"
                  quick_create="true"
                  drag_drop="true"
                  _fold="false">
               <field name="name"/>
               <field name="partner_id"/>
               <field name="stage_id"/>
               <field name="priority"/>
               <field name="date_deadline"/>
               <field name="user_id"/>
               <field name="kanban_dashboard"/>

               <templates>
                   <t t-name="kanban-box">
                       <div class="oe_kanban_card oe_kanban_global_click">
                           <div class="oe_kanban_header">
                               <div class="oe_kanban_header_title">
                                   <strong><field name="name"/></strong>
                               </div>
                               <div class="oe_kanban_header_right">
                                   <field name="priority" widget="priority"/>
                               </div>
                           </div>

                           <div class="oe_kanban_content">
                               <field name="partner_id"/>
                               <div class="text-muted">
                                   <field name="date_deadline"/>
                               </div>

                               <!-- Progress bar -->
                               <div class="progress" t-if="record.kanban_dashboard.raw_value.progress">
                                   <div class="progress-bar"
                                        t-att-style="'width: ' + record.kanban_dashboard.raw_value.progress + '%'"
                                        role="progressbar"/>
                               </div>
                           </div>

                           <div class="oe_kanban_footer">
                               <div class="oe_kanban_footer_left">
                                   <field name="user_id" widget="many2one_avatar"/>
                               </div>
                               <div class="oe_kanban_footer_right">
                                   <span class="oe_kanban_mail_new" title="Messages">
                                       <i class="fa fa-comment"/>
                                       <field name="message_count"/>
                                   </span>
                                   <span class="oe_kanban_attachments" title="Attachments">
                                       <i class="fa fa-paperclip"/>
                                       <field name="attachment_count"/>
                                   </span>
                               </div>
                           </div>

                           <!-- Kanban buttons -->
                           <div class="oe_kanban_bottom_right">
                               <a type="object" name="action_method" class="btn btn-primary">
                                   <i class="fa fa-check"/> Confirm
                               </a>
                           </div>

                           <!-- Color field -->
                           <div class="oe_kanban_color_border"
                                t-att-style="'border-left: 4px solid ' + record.color.raw_value"/>
                       </div>
                   </t>
               </templates>
           </kanban>
       </field>
   </record>
   ```

3. **Configure kanban view attributes**:
   - `default_group_by="field_name"` - field to group by
   - `quick_create="true"` - enable quick create box
   - `quick_create="_quick_create"` - auto-create
   - `drag_drop="true"` - enable drag-drop between groups
   - `_fold="false"` - enable column folding
   - `archivable="true"` - enable archive/unarchive
   - `editable="true"` - enable inline editing
   - `deletable="true"` - enable delete from kanban
   - `creatable="true"` - enable create from kanban
   - `group_by_tooltip="field_name"` - tooltip for group title

4. **Add card features**:
   - `oe_kanban_global_click` - entire card clickable
   - `oe_kanban_color_border` - colored left border
   - `oe_kanban_color_{color}` - color class (0-11)
   - `oe_kanban_button` - button styling
   - `oe_kanban_manage_toggle_position` - edit mode toggle

5. **Use color coding**:
   ```xml
   <div class="oe_kanban_card oe_kanban_color_3">
   <!-- Colors 0-11 available -->
   ```

6. **Add progress bars**:
   ```xml
   <field name="progress" widget="progressbar"/>
   <!-- Or custom progress -->
   <div class="progress">
       <div class="progress-bar progress-bar-success"
            t-att-style="'width: ' + record.progress.raw_value + '%'"/>
   </div>
   ```

7. **Add avatars**:
   ```xml
   <field name="user_id" widget="many2one_avatar"/>
   <field name="image" widget="image"/>
   ```

8. **Configure priority**:
   ```xml
   <field name="priority" widget="priority"/>
   <!-- 0-3 stars, affects card color -->
   ```

9. **Add badges and counters**:
   ```xml
   <span class="badge badge-primary">
       <field name="state_count"/>
   </span>
   ```

10. **Add buttons**:
    ```xml
    <a type="object" name="action_method" class="btn btn-primary btn-sm">
        <i class="fa fa-check"/> Confirm
    </a>
    <a type="action" name="%(action_id)d" class="btn btn-secondary btn-sm">
        Open
    </a>
    ```

11. **Add charts in kanban**:
    ```xml
    <div class="oe_kanban_chart">
        <field name="kanban_dashboard" widget="dashboard_graph"/>
    </div>
    ```

12. **Show counts**:
    ```xml
    <field name="message_count"/>
    <field name="attachment_count"/>
    <field name="activity_count"/>
    ```

13. **Add tooltips**:
    ```xml
    <div class="oe_kanban_tooltip" t-att-title="record.name.raw_value">
    ```

14. **Customize card layout**:
    - Header: title + priority/menu
    - Content: main fields + progress
    - Footer: avatars + counters
    - Bottom: action buttons

## Usage Examples

**Basic kanban:**
```
/view-kanban "crm.lead" --fields="name,partner_id,user_id,priority" \
  --group_by="stage_id"
```

**With quick create:**
```
/view-kanban "project.task" --fields="name,project_id,user_id,date_deadline" \
  --group_by="stage_id" --quick_create=true --drag_drop=true
```

**With progress:**
```
/view-kanban "project.project" --fields="name,partner_id,task_count,progress" \
  --group_by="stage_id" --progress="progress:100" --drag_drop=true
```

**Complex kanban:**
```
/view-kanban "sale.order" --fields="name,partner_id,amount_total,state,user_id" \
  --group_by="state" --quick_create=false --buttons="action_confirm:Confirm"
```

## Odoo 19 Specific Features

- Enhanced `widget="dashboard_graph"` for kanban charts
- New `widget="many2one_avatar_user"` for user avatars
- Improved `drag_drop` with better UX
- Better mobile responsiveness
- Enhanced `group_by` with color coding
- New `kanban_dashboard` field for rich content
- Support for `oe_kanban_card` with custom styling
- Improved `quick_create` with better validation
- Better integration with mail activities
- Enhanced progress bar styling
