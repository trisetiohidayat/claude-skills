---
description: Add logging with _logger for Odoo 19 models. Use when user wants to add logging to a module.
---


# Odoo 19 Logging Utility (/utils-logging)

This skill helps you implement proper logging in your Odoo 19 modules using Python's logging framework integrated with Odoo's configuration system.

## Logging Overview

Odoo 19 uses Python's standard `logging` module with a custom configuration system. Logging is essential for debugging, monitoring, and auditing your Odoo applications.

## Basic Logger Setup

### Import and Initialize Logger

```python
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class YourModel(models.Model):
    _name = 'your.model'
    _description = 'Your Model'

    def your_method(self):
        _logger.info('Processing record %s', self.id)
        # Your code here
```

### Logger Naming Convention

Always use `__name__` as the logger name, which automatically includes the full Python module path:

```python
# For module: library_management/models/book.py
_logger = logging.getLogger(__name__)
# Logger name becomes: library_management.models.book
```

## Log Levels

Odoo supports all standard Python logging levels:

### 1. DEBUG - Detailed diagnostic information

```python
def action_compute_price(self):
    _logger.debug('Starting price computation for product %s', self.id)
    _logger.debug('Cost: %s, Margin: %s', self.cost, self.margin)
    # Calculation logic
    _logger.debug('Computed price: %s', self.price)
```

**Use for:**
- Variable values
- Method entry/exit points
- Complex algorithm steps
- Data structure contents

### 2. INFO - General information about program execution

```python
def action_create_order(self):
    _logger.info('Creating new order for customer %s', self.partner_id.name)
    order = self.env['sale.order'].create({
        'partner_id': self.partner_id.id,
        # ... other fields
    })
    _logger.info('Order created successfully: %s', order.name)
```

**Use for:**
- Business process milestones
- Record creation/update/deletion
- External API calls
- Scheduled task execution

### 3. WARNING - Something unexpected happened

```python
@api.constrains('email')
def _check_email(self):
    for record in self:
        if record.email and '@' not in record.email:
            _logger.warning('Invalid email format for record %s: %s', record.id, record.email)
            # Continue processing but warn
```

**Use for:**
- Recoverable issues
- Deprecated feature usage
- Configuration problems
- Data quality issues

### 4. ERROR - Serious problem occurred

```python
def action_sync_external(self):
    try:
        external_api.sync(self)
    except ConnectionError as e:
        _logger.error('Failed to sync record %s with external API: %s', self.id, str(e))
        raise
```

**Use for:**
- Exceptions that prevent operation completion
- API failures
- Database errors
- Permission issues

### 5. CRITICAL - Very serious error

```python
def action_process_payment(self):
    if not self.company_id.currency_id:
        _logger.critical('Company %s has no currency configured. Payment processing aborted.', self.company_id.id)
        raise UserError(_('Critical system configuration error.'))
```

**Use for:**
- System-level failures
- Data corruption risks
- Security breaches
- Complete service unavailability

## Logging Best Practices

### 1. Use Lazy Formatting

Pass format arguments as separate parameters (not f-strings or % formatting):

```python
# Good - Lazy formatting
_logger.info('Processing order %s for customer %s', order.name, customer.name)

# Avoid - Immediate formatting
_logger.info(f'Processing order {order.name} for customer {customer.name}')

# Avoid
_logger.info('Processing order %s for customer %s' % (order.name, customer.name))
```

**Why?** Lazy formatting only performs string interpolation if the log level is enabled.

### 2. Include Context and Identifiers

Always include record IDs, names, or other identifying information:

```python
def action_confirm(self):
    _logger.info('Confirming order %s (ID: %s) for partner %s (ID: %s)',
                 self.name, self.id, self.partner_id.name, self.partner_id.id)
```

### 3. Log at Appropriate Entry Points

```python
@api.model
def cron_send_invoices(self):
    """Scheduled task to send pending invoices"""
    _logger.info('Starting invoice sending cron job')

    invoices = self.search([
        ('state', '=', 'posted'),
        ('sent', '=', False)
    ])

    _logger.info('Found %s invoices to send', len(invoices))

    for invoice in invoices:
        try:
            invoice.action_send_email()
            _logger.info('Invoice %s sent successfully', invoice.name)
        except Exception as e:
            _logger.error('Failed to send invoice %s: %s', invoice.name, str(e))

    _logger.info('Invoice sending cron job completed')
```

### 4. Use Exception Logging

Include exception information when logging errors:

```python
def action_import_data(self):
    try:
        self._process_import()
    except Exception as e:
        _logger.exception('Exception occurred during data import for record %s', self.id)
        # exception() automatically includes traceback
```

### 5. Log External Interactions

Always log calls to external systems:

```python
def _call_payment_gateway(self, amount, currency):
    _logger.info('Calling payment gateway: amount=%s %s, transaction_id=%s',
                 amount, currency.name, self.transaction_id)

    try:
        response = self.payment_gateway_api.charge(amount, currency.code)
        _logger.info('Payment gateway response: status=%s, transaction_id=%s',
                     response.get('status'), response.get('transaction_id'))
        return response
    except Exception as e:
        _logger.error('Payment gateway error: %s', str(e), exc_info=True)
        raise
```

## Logging in Different Contexts

### Model Methods

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sales Order'

    def action_confirm(self):
        _logger.info('Confirming sales order: %s', self.name)

        if not self.partner_id:
            _logger.warning('Order %s has no partner set', self.id)
            return False

        try:
            self._validate_order()
            self.write({'state': 'sale'})
            _logger.info('Order %s confirmed successfully', self.name)
        except ValidationError as e:
            _logger.error('Validation failed for order %s: %s', self.name, str(e))
            raise
```

### API Controllers

```python
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ApiConnector(http.Controller):

    @http.route('/api/v1/orders', type='json', auth='user', methods=['POST'])
    def create_order(self, **kwargs):
        _logger.info('API: Creating order from external request')
        _logger.debug('Request data: %s', kwargs)

        try:
            order = request.env['sale.order'].create(kwargs)
            _logger.info('API: Order created successfully: %s', order.name)
            return {'status': 'success', 'order_id': order.id}
        except Exception as e:
            _logger.error('API: Failed to create order: %s', str(e), exc_info=True)
            return {'status': 'error', 'message': str(e)}
```

### Scheduled Tasks (Cron)

```python
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    @api.model
    def cron_send_due_notifications(self):
        """Send notifications for overdue books"""
        _logger.info('Starting cron: Send due notifications')

        overdue_books = self.search([
            ('borrowing_ids.return_date', '<', fields.Date.today()),
            ('borrowing_ids.state', '=', 'borrowed')
        ])

        _logger.info('Found %s overdue books', len(overdue_books))

        for book in overdue_books:
            for borrowing in book.borrowing_ids.filtered(lambda b: b.state == 'borrowed'):
                if borrowing.return_date < fields.Date.today():
                    _logger.info('Sending notification for book %s borrowed by %s',
                                 book.name, borrowing.borrower_id.name)
                    try:
                        borrowing.action_send_reminder()
                    except Exception as e:
                        _logger.error('Failed to send reminder for borrowing %s: %s',
                                      borrowing.id, str(e))

        _logger.info('Cron completed: Sent notifications for %s overdue books',
                     len(overdue_books))
```

### Data Import/Export

```python
def action_import_csv(self):
    """Import books from CSV file"""
    _logger.info('Starting CSV import for library books')

    if not self.data_file:
        _logger.warning('No data file provided for import')
        return

    try:
        import_data = self._decode_csv_data()
        _logger.info('Parsed %s rows from CSV', len(import_data))

        created_count = 0
        error_count = 0

        for row in import_data:
            try:
                self.env['library.book'].create(row)
                created_count += 1
            except Exception as e:
                error_count += 1
                _logger.error('Failed to import row %s: %s', row.get('name', 'Unknown'), str(e))

        _logger.info('CSV import completed: %s created, %s errors', created_count, error_count)

    except Exception as e:
        _logger.exception('Critical error during CSV import')
        raise
```

## Configuring Log Levels

### Via Odoo Configuration File

```ini
# odoo.conf
[options]
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log
logrotate = True
log_db = True
```

### Module-Specific Logging

```ini
# odoo.conf
log_handler = :WARNING,library_management:DEBUG,library_management.models.book:INFO
```

### Runtime Log Level Change

```python
# In Python console or debug context
import logging
logging.getLogger('library_management').setLevel(logging.DEBUG)
```

## Structured Logging

For better log analysis, use structured logging with consistent format:

```python
def action_process_payment(self, amount, payment_method):
    _logger.info(
        'Payment processed: order_id=%s, amount=%s, currency=%s, method=%s, status=%s',
        self.id,
        amount,
        self.currency_id.name,
        payment_method,
        'success'
    )
```

This makes logs easier to parse and analyze.

## Conditional Logging

Avoid expensive operations when log level is disabled:

```python
def action_complex_operation(self):
    # Check if debug logging is enabled before expensive operation
    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug('Complex operation details: %s', self._get_detailed_debug_info())

    # Your operation here
```

## Logging Performance Considerations

```python
# Good - Lazy evaluation
_logger.debug('Data: %s', self._get_expensive_data())

# Bad - Forces evaluation even if debug is disabled
_logger.debug(f'Data: {self._get_expensive_data()}')
```

## Audit Logging

For audit trails, consider creating a separate audit log model:

```python
class AuditLog(models.Model):
    _name = 'audit.log'
    _description = 'Audit Log'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', 'User', required=True)
    model_name = fields.Char('Model', required=True, index=True)
    record_id = fields.Integer('Record ID', index=True)
    action = fields.Selection([
        ('create', 'Create'),
        ('write', 'Update'),
        ('unlink', 'Delete'),
    ], required=True)
    details = fields.Text('Details')
    create_date = fields.DateTime('Date', readonly=True)
```

Usage:

```python
def write(self, vals):
    result = super().write(vals)
    for record in self:
        self.env['audit.log'].sudo().create({
            'user_id': self.env.user.id,
            'model_name': self._name,
            'record_id': record.id,
            'action': 'write',
            'details': f'Updated fields: {list(vals.keys())}',
        })
    return result
```

## Common Logging Patterns

### Entry/Exit Logging

```python
def action_sync_external_data(self):
    _logger.info('Starting external data sync for company %s', self.company_id.name)

    try:
        result = self._do_sync()
        _logger.info('External data sync completed successfully')
        return result
    except Exception as e:
        _logger.error('External data sync failed: %s', str(e), exc_info=True)
        raise
```

### Loop Logging

```python
def action_mass_update(self):
    records = self.search([('state', '=', 'draft')])

    _logger.info('Starting mass update for %s records', len(records))

    success_count = 0
    for i, record in enumerate(records, 1):
        try:
            record.action_process()
            success_count += 1

            # Log progress every 100 records
            if i % 100 == 0:
                _logger.info('Progress: %s/%s records processed', i, len(records))

        except Exception as e:
            _logger.error('Failed to process record %s: %s', record.id, str(e))

    _logger.info('Mass update completed: %s successful, %s failed',
                 success_count, len(records) - success_count)
```

## Viewing Logs

### Server Log File

```bash
# View real-time logs
tail -f /var/log/odoo/odoo.log

# Filter by level
grep "ERROR" /var/log/odoo/odoo.log

# Filter by module
grep "library_management" /var/log/odoo/odoo.log
```

### Odoo UI Log Viewer

Install `log_viewer` module or use Odoo DB logs:

```python
# View logs in database
logs = request.env['ir.logging'].search([
    ('name', '=', 'library_management.models.book'),
    ('level', '>=', logging.WARNING)
], order='create_date desc', limit=100)
```

## Summary

- Import `logging` and create logger with `logging.getLogger(__name__)`
- Use appropriate log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Use lazy formatting for performance
- Include context (IDs, names) in log messages
- Log external API calls and exceptions
- Use `exc_info=True` or `.exception()` for error logging
- Configure log levels in odoo.conf
- Consider audit logging for business-critical operations
