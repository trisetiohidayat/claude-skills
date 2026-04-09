---
description: Migrate Odoo models from older versions to Odoo 19 syntax. Use when user wants to migrate model code to Odoo 19.
---


# Odoo 19 Model Migration

Migrate Odoo model code from older versions to Odoo 19 syntax, focusing on removing deprecated decorators and updating method signatures.

## Instructions

1. **Read the target model file:**
   - Identify all model classes in the file
   - Check for deprecated `@api.one`, `@api.multi`, `@api.model` decorators
   - Look for old-style computed fields and methods

2. **Remove @api.one decorators:**
   - `@api.one` methods should be converted to regular methods
   - Remove `self` iteration as Odoo 19 methods work on recordsets
   - Return values should be changed from single values to recordsets or dictionaries

3. **Remove @api.multi decorators:**
   - `@api.multi` is now the default behavior
   - Simply remove the decorator
   - Method signatures remain the same

4. **Update @api.model usage:**
   - Keep `@api.model` for methods that don't use self
   - Ensure methods don't rely on recordset data

5. **Update computed fields:**
   - Computed fields should use `@api.depends` instead of old-style decorators
   - Ensure compute methods work on recordsets, not single records

6. **Update onchange methods:**
   - Keep `@api.onchange` decorators
   - Return warnings in proper format: `{'warning': {'title': 'Title', 'message': 'Message'}}`

7. **Update constraint methods:**
   - Keep `@api.constrains` decorators
   - Raise `ValidationError` for validation failures

## Common Migration Patterns

### Pattern 1: Remove @api.one

**Before (Odoo 12-13):**
```python
@api.one
def compute_total(self):
    self.total = self.price * self.quantity
    return self.total
```

**After (Odoo 19):**
```python
def compute_total(self):
    for record in self:
        record.total = record.price * record.quantity
```

### Pattern 2: Remove @api.multi

**Before (Odoo 12-17):**
```python
@api.multi
def action_confirm(self):
    for order in self:
        order.state = 'confirmed'
    return True
```

**After (Odoo 19):**
```python
def action_confirm(self):
    for order in self:
        order.state = 'confirmed'
    return True
```

### Pattern 3: Update @api.depends

**Before (Odoo 12-15):**
```python
@api.one
@api.depends('price', 'quantity')
def compute_total(self):
    self.total = self.price * self.quantity
```

**After (Odoo 19):**
```python
@api.depends('price', 'quantity')
def compute_total(self):
    for record in self:
        record.total = record.price * record.quantity
```

### Pattern 4: Method Returns

**Before (Odoo 12-13 with @api.one):**
```python
@api.one
def get_name(self):
    return self.name
```

**After (Odoo 19):**
```python
def get_name(self):
    return self.mapped('name')  # Returns list
    # OR
    return dict([(rec.id, rec.name) for rec in self])  # Returns dict
```

## Usage Examples

### Example 1: Simple Model Migration

```bash
/migrate-model models/sale_order.py
```

**Input File (models/sale_order.py):**
```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'

    name = fields.Char(string='Order Reference', required=True)
    amount_total = fields.Float(string='Total')
    line_ids = fields.One2many('sale.order.line', 'order_id', string='Order Lines')

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'confirmed'
        return True

    @api.one
    def compute_amount(self):
        self.amount_total = sum(line.price for line in self.line_ids)

    @api.model
    def get_pending_orders(self):
        return self.search([('state', '=', 'draft')])
```

**Output File (models/sale_order.py):**
```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'

    name = fields.Char(string='Order Reference', required=True)
    amount_total = fields.Float(string='Total')
    line_ids = fields.One2many('sale.order.line', 'order_id', string='Order Lines')

    def action_confirm(self):
        for order in self:
            order.state = 'confirmed'
        return True

    def compute_amount(self):
        for order in self:
            order.amount_total = sum(line.price for line in order.line_ids)

    @api.model
    def get_pending_orders(self):
        return self.search([('state', '=', 'draft')])
```

### Example 2: Model with Computed Fields

```bash
/migrate-model models/product_product.py
```

**Input File:**
```python
from odoo import models, fields, api

class ProductProduct(models.Model):
    _name = 'product.product'
    _description = 'Product'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price')
    quantity = fields.Float(string='Quantity')
    total = fields.Float(string='Total', compute='_compute_total', store=False)

    @api.one
    @api.depends('price', 'quantity')
    def _compute_total(self):
        self.total = self.price * self.quantity

    @api.multi
    def update_prices(self, new_price):
        for product in self:
            product.price = new_price
```

**Output File:**
```python
from odoo import models, fields, api

class ProductProduct(models.Model):
    _name = 'product.product'
    _description = 'Product'

    name = fields.Char(string='Name', required=True)
    price = fields.Float(string='Price')
    quantity = fields.Float(string='Quantity')
    total = fields.Float(string='Total', compute='_compute_total', store=False)

    @api.depends('price', 'quantity')
    def _compute_total(self):
        for product in self:
            product.total = product.price * product.quantity

    def update_prices(self, new_price):
        for product in self:
            product.price = new_price
```

### Example 3: Complex Migration with Return Values

```bash
/migrate-model models/library_book.py
```

**Input File:**
```python
from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author')
    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
    ], string='State', default='available')

    @api.one
    def get_book_info(self):
        return {
            'title': self.name,
            'author': self.author,
            'state': self.state,
        }

    @api.multi
    def return_book(self):
        for book in self:
            book.state = 'available'
        return True

    @api.model
    def create_book(self, title, author):
        book = self.create({
            'name': title,
            'author': author,
        })
        return book
```

**Output File:**
```python
from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author')
    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
    ], string='State', default='available')

    def get_book_info(self):
        result = []
        for book in self:
            result.append({
                'title': book.name,
                'author': book.author,
                'state': book.state,
            })
        return result

    def return_book(self):
        for book in self:
            book.state = 'available'
        return True

    @api.model
    def create_book(self, title, author):
        book = self.create({
            'name': title,
            'author': author,
        })
        return book
```

## Migration Checklist

- [ ] Remove all `@api.one` decorators
- [ ] Remove all `@api.multi` decorators
- [ ] Update methods that used `@api.one` to iterate over recordsets
- [ ] Update return values from single records to appropriate data structures
- [ ] Keep `@api.model` for static methods
- [ ] Keep `@api.depends` for computed fields
- [ ] Keep `@api.onchange` for onchange methods
- [ ] Keep `@api.constrains` for constraint methods
- [ ] Test all migrated methods thoroughly
- [ ] Check for any `self.ensure_one()` calls that might be needed

## Important Notes

1. **Recordset Behavior:** In Odoo 19, all methods work on recordsets by default. Never assume a method receives a single record unless you call `self.ensure_one()`.

2. **Performance:** Use `self.mapped()` and `self.filtered()` for efficient recordset operations instead of iterating when possible.

3. **Return Values:** Methods that previously used `@api.one` and returned single values should now return lists, dictionaries, or recordsets depending on use case.

4. **Testing:** After migration, always test:
   - Single record operations
   - Multi-record operations
   - Empty recordsets
   - Methods called from different contexts (UI, API, cron)

5. **Backward Compatibility:** These changes are NOT backward compatible. Always backup before migrating.

## Related Skills

- `/model-new` - Create new Odoo 19 models
- `/field-compute` - Add computed fields
- `/method-constraint` - Add constraint methods
- `/method-onchange` - Add onchange methods
- `/method-action` - Add action methods
