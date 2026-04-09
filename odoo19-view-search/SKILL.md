---
description: Generate Odoo 19 search view with filters, groupers, and domains. Use when user wants to create a search view.
---


You are helping the user create an Odoo 19 search view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse searchable fields
   - Parse custom filters with domains
   - Parse group_by fields
   - Identify default filter

2. **Generate search view XML** following Odoo 19 conventions:

   **Basic search view:**
   ```xml
   <record id="view_{model}_search" model="ir.ui.view">
       <field name="name">{model}.search</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <search string="{Model Label}">
               <!-- Searchable fields -->
               <field name="name" string="Name" filter_name="name"/>
               <field name="partner_id" string="Customer"/>
               <field name="date_order" string="Order Date"/>
               <field name="user_id" string="Salesperson"/>

               <separator/>

               <!-- Filters -->
               <filter string="My Orders" name="my_orders"
                       domain="[('user_id', '=', uid)]"/>
               <filter string="My Draft Orders" name="my_draft"
                       domain="[('state', '=', 'draft'), ('user_id', '=', uid)]"/>
               <filter string="Draft" name="draft"
                       domain="[('state', '=', 'draft')]"/>
               <filter string="Confirmed" name="confirmed"
                       domain="[('state', 'in', ['sale', 'done'])]"/>

               <separator/>

               <!-- Date filters -->
               <filter string="Today" name="today"
                       domain="[('date_order', '>=', (context_today()).strftime('%Y-%m-%d'))]"/>
               <filter string="This Week" name="this_week"
                       domain="[('date_order', '>=', (context_today() - datetime.timedelta(days=context_today().weekday())).strftime('%Y-%m-%d')),
                               ('date_order', '<=', (context_today() + datetime.timedelta(days=6-context_today().weekday())).strftime('%Y-%m-%d'))]"/>
               <filter string="This Month" name="this_month"
                       domain="[('date_order', '>=', (context_today()).replace(day=1).strftime('%Y-%m-%d')),
                               ('date_order', '<=', (context_today() + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')]"/>
               <filter string="This Year" name="this_year"
                       domain="[('date_order', '>=', (context_today()).replace(month=1, day=1).strftime('%Y-%m-%d')),
                               ('date_order', '<=', (context_today()).replace(month=12, day=31).strftime('%Y-%m-%d'))]"/>

               <separator/>

               <!-- Group by -->
               <group expand="0" string="Group By">
                   <filter string="Customer" name="group_partner" domain="[]" context="{'group_by': 'partner_id'}"/>
                   <filter string="Salesperson" name="group_user" domain="[]" context="{'group_by': 'user_id'}"/>
                   <filter string="State" name="group_state" domain="[]" context="{'group_by': 'state'}"/>
                   <filter string="Order Date" name="group_date" domain="[]" context="{'group_by': 'date_order:month'}"/>
                   <filter string="Team" name="group_team" domain="[]" context="{'group_by': 'team_id'}"/>
               </group>

               <!-- Advanced search -->
               <searchpanel>
                   <field name="category_id" icon="fa-folder"/>
                   <field name="state" icon="fa-check-circle" select="multi">
                       <value name="draft" string="Draft"/>
                       <value name="sale" string="Sales Order"/>
                       <value name="done" string="Done"/>
                   </field>
                   <field name="date_order" icon="fa-calendar" select="date"/>
               </searchpanel>
           </search>
       </field>
   </record>
   ```

3. **Add searchable fields**:
   ```xml
   <field name="name" string="Name" filter_name="name"/>
   <field name="partner_id" string="Customer"/>
   <field name="date_order" string="Order Date"/>
   ```
   - `filter_name` - custom filter identifier
   - `string` - display label

4. **Create filters**:
   ```xml
   <filter string="Label" name="filter_id"
           domain="[('field', '=', value)]"/>
   ```
   - `string` - display label
   - `name` - unique identifier
   - `domain` - filter domain

5. **Filter domains**:
   - Simple: `[('field', '=', value)]`
   - Multiple: `[('field1', '=', value1), ('field2', '!=', value2)]`
   - Or: `['|', ('field1', '=', value1), ('field2', '=', value2)]`
   - In: `[('field', 'in', [value1, value2])]`
   - Like: `[('field', 'ilike', '%text%')]`

6. **Date filters**:
   ```xml
   <filter string="Today"
           domain="[('date', '>=', (context_today()).strftime('%Y-%m-%d'))]"/>
   <filter string="This Week"
           domain="[('date', '>=', (context_today() - datetime.timedelta(days=context_today().weekday())).strftime('%Y-%m-%d')),
                   ('date', '<=', (context_today() + datetime.timedelta(days=6-context_today().weekday())).strftime('%Y-%m-%d'))]"/>
   <filter string="This Month"
           domain="[('date', '>=', (context_today()).replace(day=1).strftime('%Y-%m-%d'))]"/>
   <filter string="This Year"
           domain="[('date', '>=', (context_today()).replace(month=1, day=1).strftime('%Y-%m-%d'))]"/>
   ```

7. **User-specific filters**:
   ```xml
   <filter string="My Items"
           domain="[('user_id', '=', uid)]"/>
   <filter string="My Draft Items"
           domain="[('user_id', '=', uid), ('state', '=', 'draft')]"/>
   ```

8. **Group by filters**:
   ```xml
   <group expand="0" string="Group By">
       <filter string="Partner" name="group_partner"
               domain="[]" context="{'group_by': 'partner_id'}"/>
       <filter string="Date" name="group_date"
               domain="[]" context="{'group_by': 'date:month'}"/>
   </group>
   ```
   - `expand="0"` - collapsed by default
   - `expand="1"` - expanded by default
   - `context="{'group_by': 'field'}"` - grouping field
   - `context="{'group_by': 'date:month'}"` - date with interval

9. **Add separators**:
   ```xml
   <separator/>
   ```
   - Visual separation between filters

10. **Combine filters**:
    ```xml
    <filter string="Draft Orders" name="draft_orders"
            domain="[('state', '=', 'draft')]">
        <filter string="My Draft" name="my_draft"
                domain="[('user_id', '=', uid)]"/>
    </filter>
    ```

11. **Add search panels** (Odoo 19):
    ```xml
    <searchpanel>
        <field name="category_id" icon="fa-folder"/>
        <field name="state" icon="fa-check-circle" select="multi">
            <value name="draft" string="Draft"/>
            <value name="sale" string="Sales Order"/>
        </field>
        <field name="date" icon="fa-calendar" select="date"/>
    </searchpanel>
    ```
    - `icon` - Font Awesome icon
    - `select="multi"` - multi-select
    - `select="date"` - date range
    - `<value>` - custom values for selection fields

12. **Custom filter groups**:
    ```xml
    <filter string="Important" name="important" domain="[]" context="{'group_by': 'priority'}">
        <filter string="High" name="high" domain="[('priority', '=', '3')]"/>
        <filter string="Medium" name="medium" domain="[('priority', '=', '2')]"/>
    </filter>
    ```

13. **Context in filters**:
    ```xml
    <filter string="Last 7 Days"
            domain="[('date', '>=', (context_today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'))]"
            context="{'default_date': (context_today()).strftime('%Y-%m-%d')}"/>
    ```

14. **Default filters**:
    - Set in action window: `context="{'search_default_my_orders': 1}"`
    - Multiple defaults: `context="{'search_default_draft': 1, 'search_default_my_items': 1}"`

## Usage Examples

**Basic search:**
```
/view-search "sale.order" --fields="name,partner_id,user_id,state" \
  --filters="my_items:user_id:uid,draft:state:draft"
```

**With groupers:**
```
/view-search "res.partner" --fields="name,email,phone,is_company" \
  --group_by="is_company,country_id" --default_filter="my_items"
```

**Advanced search:**
```
/view-search "account.move" --fields="name,partner_id,invoice_date,state" \
  --filters="this_month:invoice_date:month,outstanding:state:posted" \
  --group_by="partner_id,journal_id"
```

**With search panels:**
```
/view-search "product.template" --fields="name,default_code,categ_id" \
  --filters="to_order:virtual_available:lt:0" --group_by="categ_id"
```

## Odoo 19 Specific Features

- Enhanced `searchpanel` with better performance
- New `select="date"` for date range panels
- Improved `select="multi"` for multi-select panels
- Better panel icons with custom icons
- Enhanced date filters with better syntax
- Improved context handling in filters
- Better mobile responsiveness
- New panel categories with hierarchy
- Enhanced filter combining logic
- Improved default filter handling
- Better separator display
- Enhanced domain builder
