---
name: odoo-performance-guide
description: |
  Performance optimization guide untuk Odoo development. Gunakan skill ini ketika:
  - Optimize slow queries
  - Improve page load time
  - Reduce database load
  - Optimize computed fields
  - Handle large datasets
  - Reduce memory usage

  Fokus pada Odoo-specific performance patterns dan optimizations.
---

# Odoo Performance Guide

## Overview

Skill ini membantu mengidentifikasi dan menyelesaikan performance issues di Odoo.

## Common Performance Issues

### 1. N+1 Query Problem

#### ❌ BAD - N+1 Queries

```python
# SALAH - N+1 queries
def get_order_details(self):
    result = []
    for order in self:
        result.append({
            'name': order.name,
            'customer': order.partner_id.name,  # Each access = 1 query!
            'lines': [line.product_id.name for line in order.order_line]  # Each access = 1 query!
        })
    return result
```

#### ✅ GOOD - Optimized

```python
# BENAR - Use mapped/read to avoid N+1
def get_order_details(self):
    # Prefetch all needed fields
    orders = self.with_context(prefetch_fields=True)
    return [{
        'name': order.name,
        'customer': order.partner_id.name,
        'lines': order.order_line.mapped('product_id.name')
    } for order in orders]

# Atau gunakan read() untuk batch
def get_order_details(self):
    data = self.read(['name', 'partner_id'])
    # Access partner_id in batch, not per record
```

### 2. Computed Fields

#### ❌ BAD - Expensive Computation

```python
# SALAH - No store, recomputes every time
total_amount = fields.Float(compute='_compute_total')

def _compute_total(self):
    for rec in self:
        rec.total_amount = sum(rec.line_ids.mapped('price'))
```

#### ✅ GOOD - Store When Possible

```python
# BENAR - Store if data doesn't change often
total_amount = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.price', 'line_ids.quantity')
def _compute_total(self):
    for rec in self:
        rec.total_amount = sum(rec.line_ids.mapped('price_subtotal'))
```

### 3. Search and Browse

#### ❌ BAD - Multiple Searches

```python
# SALAH - Multiple searches
def process_orders(self):
    for order in self:
        partner = self.env['res.partner'].search([('id', '=', order.partner_id.id)])
        # ...
```

#### ✅ GOOD - Use Existing Recordset

```python
# BENAR - Use already-loaded record
def process_orders(self):
    for order in self:
        partner = order.partner_id  # Already in cache!
        # ...
```

### 4. Batch Operations

#### ❌ BAD - Individual Writes

```python
# SALAH - Write one by one
for order in orders:
    order.write({'state': 'done'})
```

#### ✅ GOOD - Batch Write

```python
# BENAR - Single write for all
orders.write({'state': 'done'})
```

### 5. SQL Queries

#### ❌ BAD - Raw SQL in Loop

```python
# SALAH - Raw SQL in loop
for order in self:
    self.env.cr.execute(f"SELECT * FROM sale_order_line WHERE order_id = {order.id}")
```

#### ✅ GOOD - ORM or Batch Query

```python
# BENAR - Use ORM
order_lines = self.env['sale.order.line'].search([('order_id', 'in', self.ids)])

# Or single query
query = "SELECT * FROM sale_order_line WHERE order_id = ANY(%s)"
self.env.cr.execute(query, (self.ids,))
```

## Field Optimization

### 1. Use Proper Field Types

| Field Type | When to Use |
|------------|-------------|
| `many2one` | For relationships (indexed by default) |
| `integer` | For numbers, faster than float |
| `selection` | For limited options |
| `boolean` | For flags |

### 2. Indexes

#### ✅ Add Index for Frequently Searched Fields

```python
# BENAR - Add index for search-heavy fields
name = fields.Char(string='Name', index=True)
reference = fields.Char(string='Reference', index=True)

# Compound index
class SaleOrder(models.Model):
    _indexes = [
        ('state_date_index', 'state, date_order'),
    ]
```

### 3. Lazy Loading

#### ✅ Use store=False for Heavy Computations

```python
# BENAR - Heavy computation, don't store
expensive_field = fields.Char(
    compute='_compute_expensive',
    store=False  # Only compute when needed
)
```

## View Optimization

### 1. Limit Fields in Tree View

```xml
<!-- BENAR - Only show essential fields -->
<tree>
    <field name="name"/>
    <field name="partner_id"/>
    <field name="date_order"/>
    <field name="state"/>
</tree>
```

### 2. Use decoration

```xml
<!-- BENAR - Color-code based on state -->
<tree decoration-success="state=='done'" decoration-warning="state=='pending'">
    <field name="name"/>
    <field name="state"/>
</tree>
```

### 3. Limit List Size

```python
# In action
'limit': 80,  # Default Odoo limit
```

## Caching

### 1. Use @api.model with Cache

```python
# BENAR - Cacheable method
@api.model
def get_config(self):
    # This result is cached
    return self.env['ir.config_parameter'].get_param('my_param')
```

### 2. Context-based Caching

```python
# BENAR - Use context for caching
def get_data(self):
    return self.with_context(lang=self.env.user.lang).mapped('field')
```

## Large Dataset Handling

### 1. Chunk Processing

```python
# BENAR - Process in chunks
def process_large_dataset(self):
    batch_size = 100
    ids = self.ids
    for i in range(0, len(ids), batch_size):
        batch = self.browse(ids[i:i+batch_size])
        batch._process_batch()
```

### 2. Use read_group for Aggregation

```python
# BENAR - Use read_group instead of multiple searches
def get_sales_summary(self):
    return self.env['sale.order'].read_group(
        domain=[('state', '=', 'sale')],
        fields=['amount_total:sum', 'partner_id'],
        groupby=['partner_id']
    )
```

### 3. Pagination

```python
# In controller or model
def get_page(self, offset=0, limit=20):
    return self.search([], offset=offset, limit=limit)
```

## Database Optimization

### 1. Use exists() for Related Records

```python
# BENAR - Check existence efficiently
orders_with_lines = self.search([('order_line', '!=', False)])

# Instead of
orders_with_lines = self.search([])
filtered = [o for o in orders_with_lines if o.order_line]
```

### 2. Use filtered()

```python
# BENAR - Filter in memory
draft_orders = orders.filtered(lambda o: o.state == 'draft')
```

### 3. Use mapped()

```python
# BENAR - Get all values at once
names = orders.mapped('name')
# Instead of loop
names = [o.name for o in orders]
```

## Performance Testing

### 1. Measure Query Count

```python
import logging
_logger = logging.getLogger(__name__)

def some_method(self):
    _logger.info('Starting method')
    # Your code
    _logger.info('Method completed')
```

### 2. Use Odoo Debug Mode

```
# Enable debug mode in Odoo
# View > Debug > View Logs
```

### 3. SQL EXPLAIN

```python
# Analyze query performance
self.env.cr.execute("EXPLAIN ANALYZE SELECT * FROM sale_order WHERE ...")
```

## Quick Performance Checklist

### Before Production

- [ ] No N+1 queries (use prefetch, read_group)
- [ ] Computed fields stored if appropriate
- [ ] Indexes on frequently searched fields
- [ ] Batch operations instead of loops
- [ ] Lazy loading for heavy computations
- [ ] Limited fields in list views
- [ ] Proper pagination
- [ ] No raw SQL in loops

### Monitoring

- [ ] Query count reasonable (< 100 per request)
- [ ] Response time < 2 seconds
- [ ] No memory leaks

## Common Patterns to Avoid

| Pattern | Problem | Solution |
|---------|---------|----------|
| Loop with `.search()` | N+1 queries | Use `.filtered()` |
| `for rec in self` + field access | N+1 | Use `.mapped()` |
| Unstored computed on large dataset | Slow | Add `store=True` or `store=False` |
| Raw SQL in loop | N+1 | ORM or single query |
| No limits on search | Memory | Add `limit` |

## Related Skills

- `odoo-debug-tdd`: Debug performance issues
- `odoo-code-quality`: Clean code patterns
- `odoo-module-test`: Test performance
