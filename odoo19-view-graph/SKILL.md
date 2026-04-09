---
description: Generate Odoo 19 graph view (bar, line, pie) for data visualization. Use when user wants to create a graph view.
---


You are helping the user create an Odoo 19 graph view XML definition.

## Steps

1. **Parse input**:
   - Extract model name
   - Determine graph type (bar, line, pie)
   - Parse field list for dimensions and measures
   - Check for stacked option
   - Determine orientation
   - Check sort order

2. **Generate graph view XML** following Odoo 19 conventions:

   **Basic graph view:**
   ```xml
   <record id="view_{model}_graph" model="ir.ui.view">
       <field name="name">{model}.graph</field>
       <field name="model">{model}</field>
       <field name="arch" type="xml">
           <graph string="{Model Label}"
                  type="bar"
                  stacked="true"
                  orientation="vertical"
                  order="desc"
                  disable_linking="true">
               <!-- X-axis / Dimensions -->
               <field name="date" type="row" interval="month"/>
               <field name="partner_id" type="row"/>
               <field name="state" type="row"/>

               <!-- Measures (Y-axis) -->
               <field name="price_total" type="measure"/>
               <field name="quantity" type="measure"/>
               <field name="profit" type="measure" widget="monetary"/>
           </graph>
       </field>
   </record>
   ```

3. **Configure graph attributes**:
   - `string="Label"` - view title
   - `type="bar|line|pie"` - graph type
   - `stacked="true"` - stack multiple measures
   - `orientation="vertical|horizontal"` - bar orientation
   - `order="asc|desc|none"` - sort order
   - `disable_linking="true"` - disable drill-down
   - `limit="10"` - limit records shown
   - `display_quantity="true"` - show quantity
   - `mode="bar|line|pie"` - default mode

4. **Choose graph type**:
   - `type="bar"` - bar chart (default)
   - `type="line"` - line chart
   - `type="pie"` - pie chart

5. **Add dimensions** (X-axis):
   ```xml
   <field name="date" type="row" interval="month"/>
   <field name="partner_id" type="row"/>
   <field name="state" type="row"/>
   ```
   - `type="row"` - X-axis dimension
   - `interval="day|week|month|quarter|year"` - date intervals

6. **Add measures** (Y-axis):
   ```xml
   <field name="price_total" type="measure"/>
   <field name="quantity" type="measure"/>
   <field name="amount" type="measure" widget="monetary"/>
   ```
   - `type="measure"` - Y-axis measure
   - Multiple measures create grouped bars

7. **Configure stacking**:
   ```xml
   <graph type="bar" stacked="true">
   ```
   - Stacks multiple measures on same bar
   - Useful for comparing totals

8. **Set orientation**:
   ```xml
   <graph type="bar" orientation="vertical">
   <!-- or -->
   <graph type="bar" orientation="horizontal">
   ```
   - `vertical` - vertical bars (default)
   - `horizontal` - horizontal bars

9. **Configure line graphs**:
   ```xml
   <graph type="line" stacked="false">
       <field name="date" type="row" interval="day"/>
       <field name="amount" type="measure"/>
   </graph>
   ```
   - Multiple measures create multiple lines
   - Stacked lines create area chart

10. **Configure pie charts**:
    ```xml
    <graph type="pie">
        <field name="category" type="row"/>
        <field name="amount" type="measure"/>
    </graph>
    ```
    - First field defines slices
    - Measure defines slice size
    - Shows percentages

11. **Use date intervals**:
    ```xml
    <field name="date_order" type="row" interval="month"/>
    <!-- Intervals: day, week, month, quarter, year -->
    ```

12. **Add measure widgets**:
    - `widget="monetary"` - currency formatting
    - `widget="duration"` - duration display
    - `widget="percentage"` - percentage display

13. **Limit records**:
    ```xml
    <graph limit="10">
    ```
    - Shows top N records
    - Based on current ordering

14. **Disable linking**:
    ```xml
    <graph disable_linking="true">
    ```
    - Prevents clicking to drill down
    - Improves performance

## Usage Examples

**Basic bar graph:**
```
/view-graph "sale.report" --type="bar" --fields="date:month,price_total"
```

**Stacked bar:**
```
/view-graph "account.invoice.report" --type="bar" --fields="partner_id,price_total,residual" \
  --stacked=true --orientation="horizontal"
```

**Line graph:**
```
/view-graph "sale.report" --type="line" --fields="date:week,quantity,price_total" \
  --order="desc"
```

**Pie chart:**
```
/view-graph "crm.lead" --type="pie" --fields="stage_id,probability"
```

**Multi-measure graph:**
```
/view-graph "project.task" --type="bar" --fields="user_id,planned_hours,effective_hours" \
  --stacked=true --limit="15"
```

## Odoo 19 Specific Features

- Enhanced graph rendering with better performance
- New `widget="percentage"` for percentage display
- Improved `stacked` attribute with better visualization
- Better mobile responsiveness
- Enhanced line chart with smoother curves
- Improved pie chart with better labels
- Better drill-down capabilities
- Enhanced export options (PNG, data)
- New graph animations
- Better handling of multiple measures
- Improved date interval options
- Enhanced tooltip display
