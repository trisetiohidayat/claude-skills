---
description: Generate Odoo 19 map view with routing and partner locations. Use when user wants to create a map view.
---


You are helping the user create an Odoo 19 map view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Identify res_partner field
   - Parse fields to display
   - Check zoom level
   - Determine view mode

2. **Generate map view XML** following Odoo 19 conventions:

   **Basic map view:**
   ```xml
   <record id="view_{model}_map" model="ir.ui.view">
       <field name="name">{model}.map</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <map string="{Model Label}"
                res_partner="partner_id"
                default_zoom="10"
                routing="true"
                hide_name="false"
                hide_address="false"
                hide_phone="false"
                hide_email="false"
                hide_website="false">
               <field name="name"/>
               <field name="partner_id"/>
               <field name="street"/>
               <field name="city"/>
               <field name="zip"/>
               <field name="country_id"/>
               <field name="phone"/>
               <field name="email"/>
               <field name="website"/>
               <field name="color"/>
           </map>
       </field>
   </record>
   ```

3. **Configure map attributes**:
   - `res_partner="field_name"` - many2one field to res.partner (required)
   - `default_zoom="10"` - zoom level (1-19, default 10)
   - `routing="true"` - enable routing between locations
   - `hide_name="true"` - hide partner name in popup
   - `hide_address="true"` - hide address in popup
   - `hide_phone="true"` - hide phone in popup
   - `hide_email="true"` - hide email in popup
   - `hide_website="true"` - hide website in popup
   - `panel_background="color"` - marker color
   - `library="default"` - map library (default or custom)

4. **Zoom levels**:
   - `1` - world view
   - `5` - continent view
   - `10` - city view (default)
   - `15` - street view
   - `19` - building view

5. **Add routing**:
   ```xml
   <map res_partner="partner_id" routing="true">
   ```
   - Shows routes between locations
   - Calculates distances and travel time
   - Useful for delivery routes

6. **Hide/show popup fields**:
   ```xml
   <map res_partner="partner_id"
        hide_name="false"
        hide_address="false"
        hide_phone="true"
        hide_email="true">
   ```

7. **Add custom fields**:
   ```xml
   <map res_partner="partner_id">
       <field name="name"/>
       <field name="partner_id"/>
       <field name="street"/>
       <field name="city"/>
       <field name="state_id"/>
       <field name="zip"/>
       <field name="country_id"/>
       <field name="phone"/>
       <field name="mobile"/>
       <field name="email"/>
       <field name="website"/>
       <field name="function"/>
       <field name="category_id"/>
   </map>
   ```

8. **Color markers**:
   ```xml
   <map res_partner="partner_id" panel_background="#FF0000">
   ```
   - Custom marker color
   - Can be field reference: `panel_background="color"`

9. **Add location fields**:
   ```xml
   <map res_partner="partner_id">
       <field name="partner_id" description="Contact"/>
       <field name="street" description="Address"/>
       <field name="city" description="City"/>
       <field name="country_id" description="Country"/>
   </map>
   ```

10. **Multiple location sources**:
    ```xml
    <map res_partner="partner_id">
        <field name="partner_id"/>
        <field name="location_partner_id"/>
        <field name="warehouse_id" res_partner="location_partner_id"/>
    </map>
    ```

11. **Custom marker templates**:
    ```xml
    <map res_partner="partner_id">
        <field name="name"/>
        <field name="partner_id"/>
        <field name="image" widget="image"/>
        <field name="color"/>
    </map>
    ```

12. **Domain filtering**:
    - Set in action window
    - Filter displayed locations
    - Example: `domain="[('active', '=', True)]"`

13. **Add search view**:
    ```xml
    <search>
        <field name="partner_id"/>
        <filter string="My Partners" domain="[('user_id', '=', uid)]"/>
        <filter string="Country" name="country" context="{'group_by': 'country_id'}"/>
    </search>
    ```

14. **Map with routing details**:
    ```xml
    <map res_partner="partner_id"
         routing="true"
         default_zoom="12">
        <field name="partner_id"/>
        <field name="street"/>
        <field name="city"/>
        <field name="distance"/>
        <field name="travel_time"/>
    </map>
    ```

15. **Hide/Show panel**:
    ```xml
    <map res_partner="partner_id" hide_panel="true">
    ```

## Usage Examples

**Basic map:**
```
/view-map "res.partner" --res_partner="partner_id" --fields="name,street,city,phone"
```

**Delivery routes:**
```
/view-map "stock.picking" --res_partner="partner_id" --routing=true \
  --default_zoom="12" --fields="name,min_date,origin"
```

**Sales locations:**
```
/view-map "crm.lead" --res_partner="partner_id" --fields="name,partner_name,phone,email" \
  --hide_address=true --hide_website=true
```

**Warehouse locations:**
```
/view-map "stock.warehouse" --res_partner="partner_id" --default_zoom="8" \
  --fields="name,code,lot_stock_id"
```

**Custom zoom:**
```
/view-map "res.partner" --res_partner="partner_id" --default_zoom="15" \
  --fields="name,street,city,phone,email"
```

## Odoo 19 Specific Features

- Enhanced map rendering with better performance
- New routing engine with real-time traffic
- Improved marker clustering for large datasets
- Better mobile responsiveness
- Enhanced popup customization
- New `hide_panel` attribute
- Improved `panel_background` with field references
- Better zoom control with smooth transitions
- Enhanced geocoding accuracy
- New marker icons with custom images
- Improved routing with multiple stops
- Better integration with partner coordinates
- Enhanced search on map
- New street view integration
- Better export options (KML, GPX)
