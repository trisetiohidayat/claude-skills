---
description: Add fields to an existing Odoo 19 model. Supports Char, Text, Html, Selection, Many2one, One2many, Many2many, Date, Datetime, Boolean, Integer, Float, Monetary, Binary, Image, and Reference fields.
---


# Odoo 19 Field Addition

Add various types of fields to Odoo 19 models following proper conventions.

## Instructions

1. **Identify the target model file:**
   - Locate the model in `{module_name}/models/{model_filename}.py`

2. **Add the field definition:**
   - Place fields in logical groups (basic fields, relational fields, computed fields)
   - Use consistent indentation (4 spaces)
   - Add proper string labels

3. **Field Type Guidelines:**

### Basic Fields

```python
# Char - Short text (max 255 characters)
name = fields.Char(string='Name', required=True, tracking=True)

# Text - Long text without formatting
description = fields.Text(string='Description', help='Detailed description')

# Html - Rich text with formatting
content = fields.Html(string='Content', sanitize=True)

# Boolean - True/False
is_active = fields.Boolean(string='Active', default=True)

# Integer - Whole numbers
quantity = fields.Integer(string='Quantity', default=0)

# Float - Decimal numbers
price = fields.Float(string='Price', digits='Product Price')

# Selection - Dropdown options
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], string='State', default='draft')
```

### Date/Time Fields

```python
# Date - Date only
date = fields.Date(string='Date', default=fields.Date.context_today)

# Datetime - Date and time
create_date = fields.Datetime(string='Created on', readonly=True)

# Relative dates
deadline = fields.Date(string='Deadline',
    default=lambda self: self._default_deadline())
```

### Relational Fields

```python
# Many2one - Many records to one record
partner_id = fields.Many2one(
    'res.partner',
    string='Customer',
    required=True,
    ondelete='cascade',
    domain=[('is_company', '=', True)]
)

# One2many - One record to many records (inverse of Many2one)
order_line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    string='Order Lines'
)

# Many2many - Many records to many records
tag_ids = fields.Many2many(
    'product.tag',
    'product_tag_rel',
    'product_id',
    'tag_id',
    string='Tags'
)

# Reference - Dynamic model reference
ref = fields.Reference(
    selection='_get_ref_selection',
    string='Reference'
)
```

### Special Fields

```python
# Monetary - Currency-aware money field
amount = fields.Monetary(
    string='Amount',
    currency_field='currency_id'
)
currency_id = fields.Many2one('res.currency', string='Currency')

# Binary - File attachment
file = fields.Binary(string='File')

# Image - Image with automatic thumbnail
image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)

# Computed field (use /field-compute for full implementation)
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,
    help='Computed total amount'
)

# Related field
partner_name = fields.Char(
    related='partner_id.name',
    string='Partner Name',
    readonly=True
)
```

## Usage Examples

### Basic Char Field

```bash
/field-add Char isbn "ISBN Number" required=true tracking=true help_text="International Standard Book Number"
```

Output:
```python
isbn = fields.Char(
    string='ISBN Number',
    required=True,
    tracking=True,
    help='International Standard Book Number'
)
```

### Many2one Field with Domain

```bash
/field-add Many2one category_id "Product Category" related_model="product.category" required=true domain="[('is_published', '=', True)]"
```

Output:
```python
category_id = fields.Many2one(
    'product.category',
    string='Product Category',
    required=True,
    domain=[('is_published', '=', True)]
)
```

### One2many Field

```bash
/field-add One2many line_ids "Order Lines" related_model="sale.order.line" inverse_field="order_id"
```

Output:
```python
line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    string='Order Lines'
)
```

### Many2many Field

```bash
/field-add Many2many tag_ids "Tags" related_model="product.tag" help_text="Product tags for filtering"
```

Output:
```python
tag_ids = fields.Many2many(
    'product.tag',
    string='Tags',
    help='Product tags for filtering'
)
```

### Selection Field

```bash
/field-add Selection priority "Priority" selection_options="[('0', 'Low'), ('1', 'Normal'), ('2', 'High')]" default="1" tracking=true
```

Output:
```python
priority = fields.Selection([
    ('0', 'Low'),
    ('1', 'Normal'),
    ('2', 'High'),
], string='Priority', default='1', tracking=True)
```

### Date Field

```bash
/field-add Date deadline "Deadline" required=true default="fields.Date.context_today"
```

Output:
```python
deadline = fields.Date(
    string='Deadline',
    required=True,
    default=fields.Date.context_today
)
```

### Monetary Field

```bash
/field-add Monetary amount "Total Amount" required=true tracking=true
```

Output:
```python
amount = fields.Monetary(
    string='Total Amount',
    currency_field='currency_id',
    required=True,
    tracking=True
)
# Don't forget to add currency_id field if not exists
```

### Boolean Field

```bash/field-add Boolean is_active "Active" default=true tracking=true
```

Output:
```python
is_active = fields.Boolean(
    string='Active',
    default=True,
    tracking=True
)
```

### Float with Precision

```bash
/field-add Float weight "Weight (kg)" digits="Stock Weight" default="0.0"
```

Output:
```python
weight = fields.Float(
    string='Weight (kg)',
    digits='Stock Weight',
    default=0.0
)
```

### Html Field

```bash
/field-add Html description "Description" sanitize=true
```

Output:
```python
description = fields.Html(
    string='Description',
    sanitize=True
)
```

### Text Field

```bash/field-add Text notes "Notes" help_text="Additional notes and comments"
```

Output:
```python
notes = fields.Text(
    string='Notes',
    help='Additional notes and comments'
)
```

### Computed Field (Basic)

```bash
/field-add Float total "Total" compute_method="_compute_total" store=true
```

Output:
```python
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True
)
# Then use /field-compute to implement the compute method
```

### Related Field

```bash/field-add Char partner_email "Partner Email" related_field="partner_id.email" readonly=true
```

Output:
```python
partner_email = fields.Char(
    related='partner_id.email',
    string='Partner Email',
    readonly=True
)
```

## Field Attributes Reference

### Common Attributes

- `string` - Human-readable label
- `required` - Field must have a value
- `readonly` - Field cannot be edited
- `default` - Default value
- `help` - Tooltip help text
- `tracking` - Track changes in chatter
- `copy` - Copy field when duplicating record
- `index` - Create database index
- `store` - Store computed field in database
- `compute` - Compute method name
- `inverse` - Inverse method name
- `search` - Search method name

### Many2one Attributes

- `ondelete` - Behavior when related record is deleted ('cascade', 'set null', 'restrict')
- `domain` - Filter domain
- `context` - Context for the relation
- `delegate` - Delegate field access

### Relational Field Attributes

- `comodel_name` - Related model (can be used instead of positional arg)
- `inverse_name` - Inverse field for One2many
- `relation` - Table name for Many2many
- `column1` - First column in Many2many relation table
- `column2` - Second column in Many2many relation table

### Numeric Attributes

- `digits` - Precision (can be tuple or named precision)
- `digits_compute` - Dynamic precision

## Best Practices

1. **Naming:**
   - Use snake_case for field names
   - End Many2one fields with `_id`
   - End One2many/Many2many fields with `_ids` or `_lines`

2. **Organization:**
   - Group related fields together
   - Place computed fields after regular fields
   - Document complex fields

3. **Performance:**
   - Add index=True for frequently searched fields
   - Use store=True for computed fields used in domains/sorting
   - Consider readonly for related fields

4. **Translation:**
   - All string values are automatically translatable
   - Use help text for user guidance

5. **Security:**
   - Use proper ondelete behavior
   - Apply domain filters for Many2one fields
   - Consider field-level permissions

## Field Types Summary

| Type | Description | Example |
|------|-------------|---------|
| Char | Short text | name = fields.Char() |
| Text | Long text | description = fields.Text() |
| Html | Rich text | content = fields.Html() |
| Selection | Dropdown | state = fields.Selection() |
| Many2one | Foreign key | partner_id = fields.Many2one() |
| One2many | Reverse foreign key | line_ids = fields.One2many() |
| Many2many | Many-to-many | tag_ids = fields.Many2many() |
| Date | Date only | date = fields.Date() |
| Datetime | Date & time | create_date = fields.Datetime() |
| Boolean | True/False | active = fields.Boolean() |
| Integer | Whole number | quantity = fields.Integer() |
| Float | Decimal | price = fields.Float() |
| Monetary | Currency-aware | amount = fields.Monetary() |
| Binary | File | file = fields.Binary() |
| Image | Image | image_1920 = fields.Image() |
| Reference | Dynamic reference | ref = fields.Reference() |

## Next Steps

After adding fields:
- Use `/field-compute` to implement compute methods
- Use `/view-form` to add fields to form views
- Use `/view-tree` to add fields to tree views
- Run `odoo-bin -c odoo.conf -d db_name -u module_name --stop-after-init` to update
