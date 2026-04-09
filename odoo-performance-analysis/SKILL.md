---
name: odoo-performance-analysis
description: |
  Analisis performa Odoo - N+1 queries, query optimization, caching, indexing, computed field optimization,
  batch processing. Gunakan ketika:
  - User bertanya tentang performance issues
  - Ingin detect N+1 queries
  - Need to optimize slow operations
  - Ingin analyze indexing strategies
---

# Odoo Performance Analysis Skill

## Overview

Skill ini membantu menganalisis dan mengoptimalkan performa aplikasi Odoo. Performance analysis merupakan aspek kritis dalam pengembangan Odoo, terutama untuk aplikasi dengan volume data besar atau kompleksitas tinggi.

## When to Use This Skill

Gunakan skill ini ketika:
- User mengeluhkan lambatnya operasi tertentu
- Ingin mendeteksi N+1 queries dalam kode
- Perlu optimize computed fields yang lambat
- Ingin analyze strategi indexing yang tepat
- Perlu optimize batch processing operations
- Ingin implement caching yang efektif

## Step 1: Detect N+1 Queries

### Understanding N+1 Problem

N+1 query problem adalah salah satu performance issue paling umum di Odoo. Masalah ini terjadi ketika kode melakukan query untuk setiap record dalam loop, daripada mengambil semua data sekaligus.

### Common N+1 Patterns to Detect

```python
# BAD: N+1 Query Pattern
for order in orders:
    print(order.partner_id.name)  # Each iteration triggers a query
    for line in order.order_line:
        print(line.product_id.name)  # Another query per line

# GOOD: Using mapped() or read()
orders = self.env['sale.order'].search([])
# Load related data upfront
orders.mapped('partner_id.name')  # Single query for all partner names
orders.mapped('order_line.product_id.name')  # Single query for all products
```

### Tools for Detecting N+1

1. **Query Logging**: Aktifkan SQL logging di Odoo config
2. **Odoo Debug Mode**: Gunakan debug mode untuk melihat queries
3. **py-chrome-devtools**: Analyze network requests
4. **PostgreSQL EXPLAIN ANALYZE**: Analyze query execution plans

### Code Patterns That Cause N+1

```python
# PATTERN 1: Loop dengan browse per record
# BAD
orders = self.env['sale.order'].search([])
for order in orders:
    partner = order.partner_id  # Query per order!
    for line in order.order_line:
        product = line.product_id  # Query per line!

# GOOD - Solution menggunakan mapped()
orders = self.env['sale.order'].search([])
# Pre-load semua related records
orders.read(['partner_id', 'order_line'])
for order in orders:
    # Data sudah di-cache, tidak ada query tambahan
    partner_name = order.partner_id.name

# PATTERN 2: Computed field tanpa @api.depends
# BAD
name = fields.Char(compute='_compute_name')
def _compute_name(self):
    for record in self:
        # Missing @api.depends means recomputed every time
        record.name = f"{self.partner_id.name} - {self.date}"

# GOOD
name = fields.Char(compute='_compute_name', store=True)
@api.depends('partner_id.name', 'date')
def _compute_name(self):
    for record in self:
        record.name = f"{record.partner_id.name} - {record.date}"

# PATTERN 3: Inline related field access
# BAD
for record in records:
    # Setiap akses ke related field adalah query
    print(record.partner_id.email)
    print(record.partner_id.phone)
    print(record.partner_id.street)

# GOOD - Menggunakan read() dengan fields
records.read(['partner_id', 'partner_id.email', 'partner_id.phone', 'partner_id.street'])
```

### Real-world N+1 Examples in Odoo

```python
# Contoh: Menghitung total order per partner
# BAD - N+1
partners = self.env['res.partner'].search([])
for partner in partners:
    orders = self.env['sale.order'].search([
        ('partner_id', '=', partner.id)
    ])
    total = sum(orders.mapped('amount_total'))

# GOOD - Single query dengan read_group
total_by_partner = self.env['sale.order'].read_group(
    domain=[('partner_id', 'in', partners.ids)],
    fields=['amount_total:sum'],
    groupby=['partner_id']
)
```

## Step 2: Analyze Query Patterns

### search() vs read() vs mapped()

Memilih method yang tepat sangat penting untuk performa:

| Method | Use Case | Query Count |
|--------|----------|-------------|
| search() | Mencari record IDs | 1 query |
| browse() | Mengakses record by ID | 1 query |
| read() | Membaca field tertentu | 1 query |
| mapped() | Transformasi data | 1+ queries |
| read_group() | Agregasi data | 1 query |

### Best Practices untuk Query

```python
# SEARCH - Gunakan untuk mencari record IDs
# Ketika hanya butuh IDs atau domain complex
ids = self.search([('state', '=', 'done')], limit=100)

# READ - Gunakan ketika butuh field tertentu
# Lebih efisien dari browse() untuk banyak record
records = self.search([('id', 'in', ids)])
data = records.read(['name', 'partner_id', 'amount_total'])

# MAPPED - Gunakan untuk transformasi sederhana
names = records.mapped('name')
partner_ids = records.mapped('partner_id.id')

# READ_GROUP - Gunakan untuk aggregasi
result = self.read_group(
    domain=[('state', '=', 'done')],
    fields=['amount_total:sum', 'date:max'],
    groupby=['partner_id']
)
```

### Batch Processing Patterns

```python
# Pattern 1: Chunk processing untuk data besar
BATCH_SIZE = 1000

def process_large_dataset(self):
    ids = self.search([]).ids
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i:i + BATCH_SIZE]
        records = self.browse(batch_ids)
        self._process_batch(records)

# Pattern 2: Menggunakan with_context(tracking_disable=True)
def bulk_write(self, vals_list):
    # Disable tracking untuk bulk operations
    self.with_context(tracking_disable=True).write(vals_list)

# Pattern 3: Menggunakan su() untuk elevated privileges
def process_as_admin(self):
    self = self.sudo()  # Bypass record rules
    # Process operations
```

### Query Optimization Techniques

```python
# Technique 1: Select specific fields saja
# BAD - Mengambil semua fields
record = self.browse(id)
name = record.name

# GOOD - Hanya mengambil yang dibutuhkan
record = self.browse(id)
name = record.name  # Akan menggunakan minimal fields

# Technique 2: Gunakan limit когда perlu
first_10 = self.search([], limit=10)

# Technique 3: Gunakan offset untuk pagination
page2 = self.search([], limit=10, offset=10)

# Technique 4: Order by indexed column
ordered = self.search([], order='create_date desc')

# Technique 5: Gunakan active_test=False jika perlu
all_records = self.with_context(active_test=False).search([])
```

## Step 3: Analyze Indexes

### Index Types di PostgreSQL

1. **B-tree Index**: Default, untuk =, <, >, <=, >=
2. **GIN Index**: Untuk full-text search, array
3. **GiST Index**: Untuk geometric data
4. **Partial Index**: Hanya untuk subset data
5. **Composite Index**: Multiple columns

### Index Strategies di Odoo

```python
# Automatic Indexes
# Odoo automatically creates indexes untuk:
# - Fields dengan index=True
# - Foreign key fields
# - Many2one relations

# Manual Index Definition di model
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(index=True)  # B-tree index
    reference = fields.Char(index='btree')  # Explicit B-tree
    category_id = fields.Many2one('my.category', index=True)

# Composite Index di _indexes
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    date = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ])

    # Composite index
    _table = 'my_model'
    _indexes = [
        'CREATE INDEX idx_date_state ON my_model (date, state)',
        'CREATE INDEX idx_date_partial ON my_model (date) WHERE state = \'done\''
    ]

# Partial Index untuk frequently queried subset
_indexes = [
    'CREATE INDEX idx_active_orders ON sale_order (date_order) '
    'WHERE state IN (\'sale\', \'done\')'
]
```

### Index Usage Analysis

```python
# Analyze query performance dengan EXPLAIN
# Di Odoo shell:
record = self.env.cr.execute("EXPLAIN ANALYZE SELECT * FROM sale_order WHERE date_order > '2024-01-01'")
print(self.env.cr.fetchall())

# Atau menggunakan Odoo tool
from odoo.tools import sql
sql.explain(self.env.cr, "SELECT * FROM sale_order WHERE date_order > '2024-01-01'")
```

### Auto Index Configuration

```python
# Di config file:
# [options]
# auto_index = True

# Enable di model
class MyModel(models.Model):
    _name = 'my.model'
    _auto_index = True  # Enable auto indexing
```

## Step 4: Optimize Computed Fields

### Computed Field Best Practices

```python
# GOOD: Stored computed field dengan lengkap @api.depends
total_amount = fields.Monetary(
    compute='_compute_total_amount',
    store=True,  # Simpan ke database
    compute_sudo=False  # Respect access rights
)

@api.depends('line_ids.price_subtotal', 'currency_id')
def _compute_total_amount(self):
    for record in self:
        total = sum(record.line_ids.mapped('price_subtotal'))
        record.total_amount = record.currency_id.round(total)

# GOOD: Multi-field dependency
@api.depends('line_ids.price_subtotal', 'line_ids.tax_ids.amount', 'discount')
def _compute_total_amount(self):
    for record in self:
        subtotal = sum(record.line_ids.mapped('price_subtotal'))
        taxes = sum(line.price_subtotal * line.tax_ids.amount / 100
                    for line in record.line_ids)
        record.total_amount = subtotal + taxes - record.discount
```

### Non-stored vs Stored Computed Fields

```python
# NON-STORED: Hitung setiap saat
# Use when: value changes frequently, rarely accessed
name = fields.Char(compute='_compute_name')
@api.depends('first_name', 'last_name')
def _compute_name(self):
    for record in self:
        record.name = f"{record.first_name} {record.last_name}"

# STORED: Simpan di database
# Use when: expensive computation, frequently accessed
total = fields.Float(compute='_compute_total', store=True)
@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))

# STORED dengan recursive dependency
parent_path = fields.Char(compute='_compute_parent_path', store=True)
@api.depends('parent_id.parent_path')
def _compute_parent_path(self):
    for record in self:
        if record.parent_id:
            record.parent_path = f"{record.parent_id.parent_path}/{record.id}"
        else:
            record.parent_path = str(record.id)
```

### Related Field Optimization

```python
# Related fields adalah computed fields yang tersimpan
# Secara otomatis di-cache

# GOOD: Simple related field
partner_name = fields.Char(related='partner_id.name', store=True)

# GOOD: Related field dengan store=True
country_id = fields.Many2one('res.country')
country_name = fields.Char(related='country_id.name', store=True)
zip = fields.Char(related='country_id.zip_required', store=True)

# RELATED field dengan store=True sangat efisien
# karena langsung disimpan di table dan tidak perlu join saat read
```

### Caching Strategies

```python
# Using @api.model untuk cached computations
@api.model
def get_default_values(self):
    # This is cached per transaction
    return {
        'currency_id': self.env.company.currency_id.id,
        'country_id': self.env.company.country_id.id,
    }

# Using self.env.cache untuk manual caching
def _compute_expensive_value(self):
    for record in self:
        if record.id in self.env.cache:
            record.value = self.env.cache[record.id]
        else:
            record.value = self._calculate_expensive(record.id)
            self.env.cache[record.id] = record.value

# Using context untuk cache invalidation
def read(self, fields):
    # Disable tracking dalam context
    return super().with_context(
        tracking_disable=True
    ).read(fields)
```

## Step 5: Optimization Strategies

### Batch Processing

```python
# Pattern 1: Process dalam batches
def process_orders(self, order_ids):
    BATCH_SIZE = 100
    for i in range(0, len(order_ids), BATCH_SIZE):
        batch = self.browse(order_ids[i:i + BATCH_SIZE])
        batch._process_batch()
        self.env.cr.commit()  # Commit per batch

# Pattern 2: Delayed computation
@api.depends('line_ids.price_subtotal')
def _compute_total(self):
    # Delay computation jika banyak records
    if len(self) > 1000:
        self._compute_total_delayed()
    else:
        self._compute_total_now()

# Pattern 3: Background execution
def schedule_recomputation(self):
    # Schedule recompute di background
    self.env.ref('base.ir_cron_compute_myfield').method_id.unlink()
    self._recompute_fields()
```

### Lazy Evaluation

```python
# Lazy field evaluation
class MyModel(models.Model):
    _name = 'my.model'

    lazy_data = fields.Binary(
        compute='_compute_lazy_data',
        compute_sudo=True,
        store=False
    )

    def _compute_lazy_data(self):
        # Only compute when accessed
        for record in self:
            if not record.lazy_data:
                record.lazy_data = self._load_heavy_data(record.id)

# Using defer=True untuk postpone computation
def process_later(self):
    # Fields dengan compute_sudo=True akan di-compute saat needed
    records = self.with_context(defer_compute=True).search([])
```

### Database-level Optimizations

```python
# 1. Use SQL WHERE clause instead of Python filtering
# BAD
records = self.search([])
filtered = records.filtered(lambda r: r.state == 'done')

# GOOD
records = self.search([('state', '=', 'done')])

# 2. Use database functions
# BAD
for record in records:
    record.name = record.name.upper()

# GOOD
self.env.cr.execute("""
    UPDATE my_model
    SET name = UPPER(name)
    WHERE id IN %s
""", [tuple(records.ids)])

# 3. Use ON CONFLICT untuk bulk insert
def bulk_create(self, values_list):
    # Odoo 12+ supports this natively
    return self.create(values_list)
```

### Caching with Redis (Odoo Enterprise)

```python
# Konfigurasi Redis caching
# Di odoo.conf:
# cache_backend = redis
# redis_host = localhost
# redis_port = 6379
# redis_db = 0

# Using cache
from odoo.addons.base.models.ir_caching import memorize

@memorize('my_cache_key')
def get_expensive_data(self, param):
    # Data akan di-cache di Redis
    return self._compute_expensive(param)

# Invalidating cache
def write(self, vals):
    result = super().write(vals)
    if 'state' in vals:
        # Invalidate cache jika state berubah
        self.env.cache.clear()
    return result
```

## Common Performance Issues and Solutions

### Issue 1: Slow List View

```
Symptoms: List view dengan banyak records sangat lambat
Root Cause: Missing indexes, N+1 queries di list columns
Solution:
- Add index pada fields yang di-search
- Remove computed fields dari list view
- Use read_group untuk aggregation
- Limit fields di list view
```

```xml
<!-- BAD: List view dengan computed fields -->
<tree>
    <field name="name"/>
    <field name="total_amount"/> <!-- Computed field -->
    <field name="partner_name"/> <!-- Related field without store -->
</tree>

<!-- GOOD: List view optimized -->
<tree>
    <field name="name"/>
    <field name="total_amount" sum="Total"/> <!-- Stored computed -->
    <field name="partner_id"/> <!-- Many2one -->
</tree>
```

### Issue 2: Slow Form Load

```
Symptoms: Opening a form takes too long
Root Cause: Many2one fields dengan domain, computed fields
Solution:
- Use inline views untuk related fields
- Optimize computed field dependencies
- Use store=True untuk computed fields
- Lazy load images/attachments
```

### Issue 3: Slow Search

```
Symptoms: Search operations timeout
Root Cause: Missing indexes, wrong field types
Solution:
- Add index=True untuk searchable fields
- Use index=True pada Char fields yang di-search
- Consider full-text search (GIN index)
```

### Issue 4: Memory Issues

```
Symptoms: Odoo process memory keeps growing
Root Cause: Loading too much data, caching
Solution:
- Use batch processing
- Clear environment after use
- Avoid loading all records at once
```

## Performance Checklist

- [ ] Enable query logging untuk debugging
- [ ] Use mapped() bukan loop untuk related data
- [ ] Add index=True pada searchable fields
- [ ] Use store=True untuk computed fields yang sering diakses
- [ ] Specify @api.depends dengan lengkap
- [ ] Use read_group untuk aggregation
- [ ] Limit fields di list view
- [ ] Use batch processing untuk bulk operations
- [ ] Avoid circular dependencies di computed fields
- [ ] Monitor query count dalam development

## Profiling Tools

### Odoo Built-in Profiler

```python
# Enable profiler
self.env.cr.execute("SELECT pg_stat_statements_reset()")
# Run operations
# View results
self.env.cr.execute("SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10")
```

### External Profiling

```python
# Using cProfile
import cProfile
import pstats

def profile_my_function(self):
    profiler = cProfile.Profile()
    profiler.enable()
    # Your code here
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

## Output Format

 Ketika menggunakan skill ini, berikan output dengan format berikut:

## Performance Analysis

### Issues Found
1. **N+1 Queries**: [location] - [impact]
2. **Missing Indexes**: [field] - [impact]
3. **Unstored Computed**: [field] - [impact]
4. **Inefficient Queries**: [location] - [impact]

### Optimization Recommendations
1. [Recommendation] - [Expected Impact]
2. [Recommendation] - [Expected Impact]
3. [Recommendation] - [Expected Impact]

### Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Impact
- Query count reduction: X%
- Response time improvement: X%
- Memory usage reduction: X%

## Notes

- Always test performance changes dengan realistic data volumes
- Use EXPLAIN ANALYZE untuk verify query optimization
- Consider trade-offs antara storage dan compute time
- Monitor production metrics setelah deployment
