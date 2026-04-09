---
description: Create computed fields with @api.depends decorator for Odoo 19 models. Use when user wants to add a computed field to a model.
---


# Odoo 19 Computed Field Creation

Create computed fields with @api.depends decorator following Odoo 19 conventions.

## Instructions

1. **Field Definition:**

```python
# Basic computed field
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=False  # Default, computed on the fly
)

# Stored computed field (for search/sort)
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True  # Stored in database
)

# With inverse method
total = fields.Float(
    string='Total',
    compute='_compute_total',
    inverse='_inverse_total'
)

# With search method
priority_score = fields.Integer(
    string='Priority Score',
    compute='_compute_priority_score',
    search='_search_priority_score'
)
```

2. **Compute Method Pattern:**

```python
@api.depends('field1', 'field2', 'relation_id.field3')
def _compute_field_name(self):
    for record in self:
        record.field_name = record.field1 + record.field2
```

3. **Important Rules:**
   - Use `@api.depends()` decorator
   - List all field dependencies
   - Use `for record in self:` loop
   - Compute fields are readonly by default
   - Add `inverse` to allow writing
   - Add `store=True` to enable search/sort
   - Handle empty recordsets

4. **Dependency Paths:**
   - Direct fields: `'field_name'`
   - Relational fields: `'relation_id.field_name'`
   - One2many/Many2many: Use `_compute_total` with logic

## Usage Examples

### Simple Computed Field

```bash
/field-compute total _compute_total "subtotal,tax_id" store=true
```

Output:
```python
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,
    help='Total including tax'
)

@api.depends('subtotal', 'tax_id')
def _compute_total(self):
    for record in self:
        if record.tax_id:
            record.total = record.subtotal * (1 + record.tax_id.amount / 100)
        else:
            record.total = record.subtotal
```

### Multiple Fields Dependency

```bash
/field-compute full_name _compute_full_name "first_name,last_name" store=true
```

Output:
```python
full_name = fields.Char(
    string='Full Name',
    compute='_compute_full_name',
    store=True
)

@api.depends('first_name', 'last_name')
def _compute_full_name(self):
    for record in self:
        if record.first_name and record.last_name:
            record.full_name = f"{record.first_name} {record.last_name}"
        else:
            record.full_name = record.first_name or record.last_name or ''
```

### Computed Field with Relational Dependency

```bash
/field-compute partner_city _compute_partner_city "partner_id.city" store=true
```

Output:
```python
partner_city = fields.Char(
    string='Partner City',
    compute='_compute_partner_city',
    store=True
)

@api.depends('partner_id.city')
def _compute_partner_city(self):
    for record in self:
        record.partner_city = record.partner_id.city if record.partner_id else ''
```

### One2many Computed Field

```bash
/field-compute total_amount _compute_total_amount "line_ids.price_subtotal" store=true
```

Output:
```python
total_amount = fields.Float(
    string='Total Amount',
    compute='_compute_total_amount',
    store=True,
    help='Total of all order lines'
)

@api.depends('line_ids.price_subtotal')
def _compute_total_amount(self):
    for order in self:
        order.total_amount = sum(order.line_ids.mapped('price_subtotal'))
```

### Many2many Count

```bash
/field-compute tag_count _compute_tag_count "tag_ids" store=true
```

Output:
```python
tag_count = fields.Integer(
    string='Number of Tags',
    compute='_compute_tag_count',
    store=True
)

@api.depends('tag_ids')
def _compute_tag_count(self):
    for record in self:
        record.tag_count = len(record.tag_ids)
```

### Computed Field with Inverse

```bash
/field-compute full_address _compute_full_address "street,city,zip_code,country_id" inverse="_inverse_full_address"
```

Output:
```python
full_address = fields.Text(
    string='Full Address',
    compute='_compute_full_address',
    inverse='_inverse_full_address',
    help='Complete address in text format'
)

@api.depends('street', 'city', 'zip_code', 'country_id')
def _compute_full_address(self):
    for record in self:
        parts = []
        if record.street:
            parts.append(record.street)
        if record.zip_code:
            parts.append(record.zip_code)
        if record.city:
            parts.append(record.city)
        if record.country_id:
            parts.append(record.country_id.name)
        record.full_address = '\n'.join(parts) if parts else ''

def _inverse_full_address(self):
    for record in self:
        if record.full_address:
            lines = record.full_address.split('\n')
            record.street = lines[0] if len(lines) > 0 else False
            record.zip_code = lines[1] if len(lines) > 1 else False
            record.city = lines[2] if len(lines) > 2 else False
            # Note: country_id would require more complex parsing
```

### Computed Field with Search

```bash
/field-compute age_days _compute_age_days "birth_date" search="_search_age_days"
```

Output:
```python
age_days = fields.Integer(
    string='Age (Days)',
    compute='_compute_age_days',
    search='_search_age_days',
    help='Age in days since birth date'
)

@api.depends('birth_date')
def _compute_age_days(self):
    for record in self:
        if record.birth_date:
            delta = fields.Date.today() - record.birth_date
            record.age_days = delta.days
        else:
            record.age_days = 0

def _search_age_days(self, operator, value):
    if operator not in ('>', '<', '>=', '<=', '=', '!='):
        return []
    birth_date = fields.Date.today() - timedelta(days=value)
    return [('birth_date', operator, birth_date)]
```

### Dynamic Selection Field

```bash
/field-compute available_products _compute_available_products "category_id" store=false
```

Output:
```python
# Field definition
available_products = fields.Many2many(
    'product.product',
    string='Available Products',
    compute='_compute_available_products',
    store=False  # Computed on the fly
)

@api.depends('category_id')
def _compute_available_products(self):
    for record in self:
        if record.category_id:
            # Get products from the same category
            record.available_products = self.env['product.product'].search([
                ('categ_id', '=', record.category_id.id),
                ('available_in_pos', '=', True)
            ])
        else:
            record.available_products = self.env['product.product']
```

### Computed Boolean

```bash
/field-compute is_overdue _compute_is_overdue "date_due,state" store=true
```

Output:
```python
is_overdue = fields.Boolean(
    string='Is Overdue',
    compute='_compute_is_overdue',
    store=True,
    help='True if payment is overdue'
)

@api.depends('date_due', 'state')
def _compute_is_overdue(self):
    today = fields.Date.today()
    for record in self:
        if record.state != 'paid' and record.date_due:
            record.is_overdue = record.date_due < today
        else:
            record.is_overdue = False
```

### Currency-Aware Computed Field

```bash
/field-compute amount_currency _compute_amount_currency "amount,company_id.currency_id" store=true
```

Output:
```python
amount_currency = fields.Float(
    string='Amount in Company Currency',
    compute='_compute_amount_currency',
    store=True,
    help='Amount converted to company currency'
)

@api.depends('amount', 'company_id.currency_id')
def _compute_amount_currency(self):
    for record in self:
        if record.company_id.currency_id:
            record.amount_currency = record.currency_id._convert(
                record.amount,
                record.company_id.currency_id,
                record.company_id,
                fields.Date.today()
            )
        else:
            record.amount_currency = record.amount
```

## Best Practices

1. **Dependency Management:**
   - Always specify all dependencies in @api.depends
   - Use dot notation for relational fields: `'partner_id.name'`
   - Avoid circular dependencies

2. **Performance:**
   - Use `store=True` for fields used in domains, sorting, or search
   - Keep compute logic simple
   - Avoid heavy database queries in compute methods
   - Use `mapped()` for efficient field access on recordsets

3. **Loop Pattern:**
   - Always use `for record in self:` to handle recordsets
   - Never assume single record (self may have multiple records)
   - Handle empty values gracefully

4. **Inverse Methods:**
   - Implement when field should be writable
   - Parse and split values appropriately
   - Handle validation errors

5. **Search Methods:**
   - Return domain that searches the underlying fields
   - Handle all common operators: =, !=, >, <, >=, <=
   - Consider performance implications

## Common Patterns

### Count Relations
```python
@api.depends('line_ids')
def _compute_line_count(self):
    for record in self:
        record.line_count = len(record.line_ids)
```

### Sum Relations
```python
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Format Strings
```python
@api.depends('code', 'name')
def _compute_display_name(self):
    for record in self:
        record.display_name = f"[{record.code}] {record.name}"
```

### Conditional Values
```python
@api.depends('state', 'date_done')
def _compute_is_completed(self):
    for record in self:
        record.is_completed = record.state == 'done' and bool(record.date_done)
```

### Date Calculations
```python
@api.depends('start_date', 'end_date')
def _compute_duration(self):
    for record in self:
        if record.start_date and record.end_date:
            record.duration = (record.end_date - record.start_date).days + 1
        else:
            record.duration = 0
```

## Performance Tips

1. **Use `store=True` when:**
   - Field is used in domains/filters
   - Field is used for sorting
   - Field is used in search method
   - Computation is expensive

2. **Avoid `store=True` when:**
   - Field changes frequently
   - Computation is simple/fast
   - Field only used for display

3. **Optimize dependencies:**
   - Only depend on fields that affect the result
   - Use specific field paths, not broad relations
   - Consider using `@api.depends_context` for context changes

## Error Handling

```python
@api.depends('partner_id')
def _compute_partner_email(self):
    for record in self:
        try:
            record.partner_email = record.partner_id.email or ''
        except AccessError:
            record.partner_email = ''
```

## Next Steps

After creating computed fields:
- Use `/field-add` to add the computed field to the model
- Use `/view-form` to display computed fields (readonly by default)
- Use `/view-tree` to show stored computed fields
- Test with records that have different dependency values
