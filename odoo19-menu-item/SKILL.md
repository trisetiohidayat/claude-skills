---
description: Generate Odoo 19 ir.ui.menu with parent, action, and configuration. Use when user wants to create a menu item.
---


You are helping the user create an Odoo 19 menu item XML definition.

## Steps

1. **Parse input**:
   - Extract menu name
   - Identify action reference
   - Check parent menu
   - Get sequence number
   - Parse group IDs
   - Check icon options

2. **Generate menu item XML** following Odoo 19 conventions:

   **Basic menu item:**
   ```xml
   <menuitem id="menu_{model}"
             name="{Menu Name}"
             action="action_{model}"
             sequence="10"
             parent="menu_parent_id"/>
   ```

   **Full menu definition:**
   ```xml
   <record id="menu_{model}" model="ir.ui.menu">
       <field name="name">{Menu Name}</field>
       <field name="action" ref="action_{model}"/>
       <field name="parent_id" ref="menu_parent_id"/>
       <field name="sequence">10</field>
       <field name="groups_id" eval="[(4, ref('group_sale_salesman'))]"/>
       <field name="web_icon">fa-shopping-cart</field>
       <field name="web_icon_data">
           PNG_BASE64_DATA
       </field>
       <field name="complete_name">Parent/{Menu Name}</field>
   </record>
   ```

3. **Configure menu attributes**:
   - `id` - unique menu identifier
   - `name` - menu display name
   - `action` - action reference
   - `parent` - parent menu ID
   - `sequence` - order number (lower = higher priority)
   - `groups_id` - security groups
   - `web_icon` - Font Awesome icon
   - `web_icon_data` - custom icon image
   - `active` - menu visibility

4. **Menu hierarchy**:
   ```xml
   <!-- Root menu -->
   <menuitem id="menu_my_root" name="My Module" sequence="10"/>

   <!-- Sub menu -->
   <menuitem id="menu_my_root_orders"
             name="Orders"
             parent="menu_my_root"
             sequence="10"/>

   <!-- Action menu -->
   <menuitem id="menu_sale_order"
             name="Sales Orders"
             action="action_sale_order"
             parent="menu_my_root_orders"
             sequence="10"/>
   ```

5. **Add parent menu**:
   ```xml
   <menuitem id="menu_sale_order"
             name="Sales Orders"
             action="action_sale_order"
             parent="menu_sale_root"
             sequence="10"/>
   ```

6. **Set sequence**:
   - Lower number = higher priority
   - Standard sequences:
     - `1` - very high priority
     - `10` - high priority
     - `50` - medium priority
     - `100` - low priority
   ```xml
   <menuitem id="menu_first" name="First" sequence="1"/>
   <menuitem id="menu_second" name="Second" sequence="2"/>
   <menuitem id="menu_third" name="Third" sequence="3"/>
   ```

7. **Add groups**:
   ```xml
   <!-- Single group -->
   <menuitem id="menu_admin_only"
             name="Admin Menu"
             action="action_admin"
             groups="base.group_system"/>

   <!-- Multiple groups -->
   <record id="menu_manager" model="ir.ui.menu">
       <field name="name">Manager Menu</field>
       <field name="action" ref="action_manager"/>
       <field name="groups_id" eval="[(4, ref('sales_team.group_sale_manager')), (4, ref('account.group_account_manager'))]"/>
   </record>
   ```

8. **Add web icon** (Font Awesome):
   ```xml
   <menuitem id="menu_sale"
             name="Sales"
             web_icon="fa-shopping-cart"/>

   <!-- Common icons -->
   <!-- fa-users, fa-building, fa-cog, fa-dashboard, fa-calendar,
        fa-file-text, fa-dollar, fa-truck, fa-bar-chart, fa-globe -->
   ```

9. **Add custom icon**:
   ```xml
   <menuitem id="menu_custom"
             name="Custom"
             web_icon="my_module,my_icon"/>
   ```

10. **Root menu without action**:
    ```xml
    <menuitem id="menu_my_root"
              name="My Module"
              sequence="10"
              web_icon="fa-cog"/>
    ```

11. **Separator menu**:
    ```xml
    <menuitem id="menu_separator"
              name="."
              parent="menu_parent"
              sequence="99"/>
    ```

12. **Multi-level menu**:
    ```xml
    <!-- Level 1: Root -->
    <menuitem id="menu_project_root"
              name="Project"
              sequence="10"
              web_icon="fa-project-diagram"/>

    <!-- Level 2: Configuration -->
    <menuitem id="menu_project_config"
              name="Configuration"
              parent="menu_project_root"
              sequence="100"/>

    <!-- Level 3: Settings -->
    <menuitem id="menu_project_settings"
              name="Settings"
              action="action_project_settings"
              parent="menu_project_config"
              sequence="10"
              groups="base.group_system"/>
    ```

13. **Action menu only**:
    ```xml
    <!-- Without parent, creates top-level menu -->
    <menuitem id="menu_partners"
              name="Contacts"
              action="action_partner"/>
    ```

14. **Conditional menu**:
    ```xml
    <menuitem id="menu_advanced"
              name="Advanced Features"
              action="action_advanced"
              groups="base.group_system,base.group_multi_company"/>
    ```

15. **Menu with tooltip**:
    ```xml
    <record id="menu_with_tooltip" model="ir.ui.menu">
        <field name="name">Menu with Tooltip</field>
        <field name="action" ref="action_my"/>
        <field name="description">This is a helpful tooltip</field>
    </record>
    ```

16. **Mobile app menu**:
    ```xml
    <menuitem id="menu_mobile"
              name="Mobile"
              action="action_mobile"
              mobile="true"/>
    ```

17. **Favorite menu**:
    ```xml
    <menuitem id="menu_favorite"
              name="Favorites"
              action="action_favorite"
              favorite="true"/>
    ```

## Common Menu Sequences

**Standard application menu** (app drawer):
```xml
<menuitem id="menu_app_root" name="My App" sequence="10" web_icon="fa-app"/>
```

**Top-level menus** (within app):
```xml
<menuitem id="menu_orders" name="Orders" sequence="10"/>
<menuitem id="menu_customers" name="Customers" sequence="20"/>
<menuitem id="menu_products" name="Products" sequence="30"/>
<menuitem id="menu_reporting" name="Reporting" sequence="40"/>
<menuitem id="menu_config" name="Configuration" sequence="100"/>
```

**Sub-menus**:
```xml
<menuitem id="menu_sales_orders" name="Sales Orders" sequence="10"/>
<menuitem id="menu_quotations" name="Quotations" sequence="20"/>
<menuitem id="menu_returns" name="Returns" sequence="30"/>
```

## Usage Examples

**Basic menu:**
```
/menu-item "Sales Orders" --action="action_sale_order" --sequence="10"
```

**With parent:**
```
/menu-item "Sales Orders" --action="action_sale_order" \
  --parent="menu_sale_root" --sequence="10"
```

**Admin menu:**
```
/menu-item "Settings" --action="action_settings" \
  --parent="menu_config" --groups="base.group_system" --sequence="100"
```

**With icon:**
```
/menu-item "CRM" --action="action_crm" --icon="fa-users" \
  --parent="menu_root" --sequence="5"
```

**Multi-level:**
```
/menu-item "Sales > Orders > Sales Orders" \
  --action="action_sale_order" --sequence="10"
```

## Odoo 19 Specific Features

- Enhanced `web_icon` with new Font Awesome icons
- New `mobile` attribute for mobile-specific menus
- Improved `groups_id` handling
- Better menu caching performance
- New `favorite` attribute for favorite menus
- Enhanced `description` for tooltips
- Improved `complete_name` auto-generation
- Better menu accessibility
- New menu animations
- Enhanced menu search
- Improved mobile menu display
- New menu icons (Font Awesome 6)
- Better menu folding/collapsing
- Enhanced menu permissions
- New menu theme support
