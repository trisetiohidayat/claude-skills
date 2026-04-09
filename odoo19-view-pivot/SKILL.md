---
description: Generate Odoo 19 pivot view for data analysis with measures and dimensions. Use when user wants to create a pivot view.
---


You are helping the user create an Odoo 19 pivot view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Parse row dimension fields
   - Parse column dimension fields
   - Parse measure fields
   - Identify active measures
   - Determine default order

2. **Generate pivot view XML** following Odoo 19 conventions:

   **Basic pivot view:**
   ```xml
   <record id="view_{model}_pivot" model="ir.ui.view">
       <field name="name">{model}.pivot</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <pivot string="{Model Label}"
                  display_quantity="true"
                  default_order="field_name asc"
                  disable_linking="true">
               <!-- Row dimensions -->
               <field name="partner_id" type="row"/>
               <field name="date" type="row" interval="month"/>
               <field name="user_id" type="row"/>

               <!-- Column dimensions -->
               <field name="product_id" type="col"/>
               <field name="state" type="col"/>
               <field name="date" type="col" interval="year"/>

               <!-- Measures -->
               <field name="price_total" type="measure" widget="monetary"/>
               <field name="quantity" type="measure"/>
               <field name="delay" type="measure" widget="duration"/>
           </pivot>
       </field>
   </record>
   ```

3. **Configure pivot attributes**:
   - `string="Label"` - view title
   - `display_quantity="true"` - show quantity column
   - `default_order="field asc/desc"` - default sorting
   - `disable_linking="true"` - disable drill-down
   - `default_active_measures="measure1,measure2"` - default active measures
   - `default_active_group_by="field1,field2"` - default grouping
   - `default_row_groupby="field_name"` - default row grouping
   - `default_col_groupby="field_name"` - default column grouping
   - `empty_text="Empty"` - text for empty values

4. **Add row dimensions**:
   ```xml
   <field name="partner_id" type="row"/>
   <field name="date" type="row" interval="month"/>
   ```
   - `type="row"` - row dimension
   - `interval="day|week|month|quarter|year"` - date interval

5. **Add column dimensions**:
   ```xml
   <field name="state" type="col"/>
   <field name="product_id" type="col"/>
   ```
   - `type="col"` - column dimension
   - Can use interval for date fields

6. **Add measures**:
   ```xml
   <field name="amount_total" type="measure"/>
   <field name="quantity" type="measure"/>
   <field name="price_unit" type="measure" widget="monetary"/>
   ```
   - `type="measure"` - aggregate field
   - Numeric fields: sum by default
   - Can use count, sum, avg, min, max

7. **Use measure widgets**:
   - `widget="monetary"` - currency formatting
   - `widget="duration"` - duration display
   - `widget="percentage"` - percentage display
   - `widget="bar"` - bar chart visualization

8. **Configure date intervals**:
   ```xml
   <field name="date_order" type="row" interval="month"/>
   <!-- Intervals: day, week, month, quarter, year -->
   ```

9. **Add active measures**:
   ```xml
   <pivot default_active_measures="price_total,quantity">
   ```

10. **Configure default grouping**:
    ```xml
    <pivot default_row_groupby="partner_id"
           default_col_groupby="date:month">
    ```

11. **Enable/disable linking**:
    ```xml
    <pivot disable_linking="true">
    ```
    - Prevents clicking to drill down
    - Improves performance

12. **Display quantity**:
    ```xml
    <pivot display_quantity="true">
    ```
    - Shows count of records

13. **Customize empty values**:
    ```xml
    <pivot empty_text="-">
    ```

14. **Order by measure**:
    ```xml
    <pivot default_order="price_total desc">
    ```

## Usage Examples

**Basic pivot:**
```
/view-pivot "sale.report" --rows="partner_id,date:month" \
  --measures="price_total,quantity" --active_measures="price_total"
```

**With columns:**
```
/view-pivot "account.move.line" --rows="partner_id" --columns="account_id,date:year" \
  --measures="debit,credit,balance" --default_order="debit desc"
```

**Sales analysis:**
```
/view-pivot "sale.report" --rows="date:quarter,user_id" --columns="state" \
  --measures="price_total,quantity,margin" --active_measures="price_total,margin"
```

**Project analysis:**
```
/view-pivot "project.task" --rows="project_id,stage_id" --columns="user_id" \
  --measures="planned_hours,effective_hours,progress" --default_order="planned_hours desc"
```

## Odoo 19 Specific Features

- Enhanced `default_active_measures` with multiple measures
- New `widget="bar"` for bar visualization in cells
- Improved `interval` handling with better performance
- Better mobile responsiveness
- Enhanced date interval options
- Improved measure calculation performance
- Better export options (Excel, CSV)
- New `widget="percentage"` for percentage display
- Enhanced drill-down capabilities
- Better handling of large datasets
- Improved empty value handling
