---
description: Generate Odoo 19 ir.cron scheduled task with interval and method execution. Use when user wants to create a scheduled task that runs automatically.
---


You are helping the user create an Odoo 19 ir.cron scheduled task XML definition.

## Steps

1. **Parse input**:
   - Extract module name
   - Parse cron name
   - Extract model name
   - Parse method name
   - Parse interval settings
   - Check active status
   - Check doall flag
   - Check numbercall limit
   - Check priority
   - Check user_id
   - Parse execution state
   - Parse code or method call

2. **Generate cron XML** following Odoo 19 conventions:

   **Basic cron with method call:**
   ```xml
   <record id="ir_cron_{method_name}" model="ir.cron">
       <field name="name">{Cron Name}</field>
       <field name="model_id" ref="model_{model_dot}"/>
       <field name="state">code</field>
       <field name="code">model.{method_name}()</field>
       <field name="interval_number">{interval_number}</field>
       <field name="interval_type">{interval_type}</field>
       <field name="numbercall">{numbercall}</field>
       <field name="doall">{doall}</field>
       <field name="active">{active}</field>
       <field name="priority">{priority}</field>
       <field name="user_id" ref="base.user_admin"/>
   </record>
   ```

3. **Configure cron attributes**:
   - `name` - cron task name
   - `model_id` - model to execute on (use ref to model_* with dots converted to underscores)
   - `state` - execution type (code, multi)
   - `code` - Python code to execute
   - `interval_number` - interval count
   - `interval_type` - time unit (minutes, hours, days, weeks, months)
   - `numbercall` - repeat count (-1 = unlimited)
   - `doall` - execute missed runs if server offline
   - `active` - enable/disable cron
   - `priority` - execution order (lower = higher priority)
   - `user_id` - run as specific user
   - `nextcall` - next execution date/time
   - `lastrun` - last execution date/time

4. **Interval types**:
   - `minutes` - run every N minutes
   - `hours` - run every N hours
   - `days` - run every N days
   - `weeks` - run every N weeks
   - `months` - run every N months

5. **Common interval configurations**:
   ```xml
   <!-- Every 5 minutes -->
   <field name="interval_number">5</field>
   <field name="interval_type">minutes</field>

   <!-- Every hour -->
   <field name="interval_number">1</field>
   <field name="interval_type">hours</field>

   <!-- Daily at midnight -->
   <field name="interval_number">1</field>
   <field name="interval_type">days</field>

   <!-- Weekly -->
   <field name="interval_number">1</field>
   <field name="interval_type">weeks</field>

   <!-- Monthly -->
   <field name="interval_number">1</field>
   <field name="interval_type">months</field>
   ```

6. **Model reference format**:
   - For model `sale.order` use `model_sale_order`
   - For model `res.partner` use `model_res_partner`
   - For model `mail.mail` use `model_mail_mail`
   - Convert dots to underscores in ref

7. **Method call in code**:
   ```xml
   <!-- Simple method -->
   <field name="code">model.process_expired_records()</field>

   <!-- With arguments -->
   <field name="code">model.process_records(days=7)</field>

   <!-- Multiple methods -->
   <field name="code">model.cleanup_old_records() and model.send_notifications()</field>

   <!-- With result checking -->
   <field name="code">results = model.process_batch(); log(results)</field>
   ```

8. **Set active state**:
   ```xml
   <!-- Active cron -->
   <field name="active" eval="True"/>

   <!-- Inactive cron -->
   <field name="active" eval="False"/>
   ```

9. **Configure doall**:
   ```xml
   <!-- Don't run missed executions (default) -->
   <field name="doall" eval="False"/>

   <!-- Run all missed executions if server was down -->
   <field name="doall" eval="True"/>
   ```

10. **Set execution limit**:
    ```xml
    <!-- Unlimited executions -->
    <field name="numbercall">-1</field>

    <!-- Run 10 times then stop -->
    <field name="numbercall">10</field>

    <!-- Run once then disable -->
    <field name="numbercall">1</field>
    ```

11. **Set priority**:
    ```xml
    <!-- Higher priority (runs first) -->
    <field name="priority">1</field>

    <!-- Normal priority (default) -->
    <field name="priority">5</field>

    <!-- Lower priority (runs last) -->
    <field name="priority">10</field>
    ```

12. **Run as specific user**:
    ```xml
    <!-- Run as admin -->
    <field name="user_id" ref="base.user_admin"/>

    <!-- Run as specific user -->
    <field name="user_id" ref="base.user_demo"/>

    <!-- Run as system (no user) -->
    <field name="user_id" eval="False"/>
    ```

13. **Set next execution time**:
    ```xml
    <!-- Specific date/time -->
    <field name="nextcall" eval="DateTime.now().strftime('%Y-%m-%d 00:00:00')"/>

    <!-- Tomorrow at 2 AM -->
    <field name="nextcall" eval="(DateTime.now() + timedelta(days=1)).strftime('%Y-%m-%d 02:00:00')"/>

    <!-- Next Monday -->
    <field name="nextcall" eval="(DateTime.now() + timedelta(days=(7 - DateTime.now().weekday()))).strftime('%Y-%m-%d 09:00:00')"/>
    ```

14. **Complex code execution**:
    ```xml
    <field name="code"><![CDATA[
        # Process expired orders
        orders = model.search([('state', '=', 'draft'), ('date_order', '<', (context_today() - timedelta(days=7)).strftime('%Y-%m-%d'))])
        for order in orders:
            order.action_cancel()
        log("Cancelled %d expired orders" % len(orders))
    ]]></field>
    ```

15. **Cron with condition**:
    ```xml
    <field name="code"><![CDATA[
        # Only run if business day
        from datetime import datetime
        if datetime.now().weekday() < 5:  # Monday-Friday
            model.process_daily_tasks()
    ]]></field>
    ```

16. **Batch processing cron**:
    ```xml
    <field name="code"><![CDATA[
        # Process in batches to avoid memory issues
        batch_size = 100
        records = model.search([('state', '=', 'todo'), ('processed', '=', False)], limit=batch_size)
        while records:
            records.process_batch()
            records = model.search([('state', '=', 'todo'), ('processed', '=', False)], limit=batch_size)
    ]]></field>
    ```

17. **Multi-model cron**:
    ```xml
    <field name="code"><![CDATA[
        # Clean up multiple models
        env['mail.message'].search([('date', '<', (context_today() - timedelta(days=90)).strftime('%Y-%m-%d'))]).unlink()
        env['ir.logging'].search([('create_date', '<', (context_today() - timedelta(days=30)).strftime('%Y-%m-%d'))]).unlink()
        log("Cleanup completed")
    ]]></field>
    ```

18. **Error handling in cron**:
    ```xml
    <field name="code"><![CDATA[
        try:
            model.sync_external_data()
        except Exception as e:
            _logger.error("Sync failed: %s", str(e))
            # Optionally send notification
            model.send_error_notification(str(e))
    ]]></field>
    ```

## Usage Examples

**Daily cleanup cron:**
```bash
/automation-cron "library_book" "Cleanup Old Books" "library.book" "cleanup_old_books" \
  --interval_number=1 --interval_type="days" --priority=10
```

**Hourly sync cron:**
```bash
/automation-cron "sale_order" "Sync External Orders" "sale.order" "sync_external_orders" \
  --interval_number=1 --interval_type="hours" --active=True --doall=False
```

**Weekly report cron:**
```bash
/automation-cron "project" "Generate Weekly Reports" "project.project" "generate_weekly_reports" \
  --interval_number=1 --interval_type="weeks" --priority=5 --doall=True
```

**Every 15 minutes:**
```bash
/automation-cron "stock" "Check Stock Levels" "stock.quant" "check_low_stock" \
  --interval_number=15 --interval_type="minutes" --priority=1
```

**Monthly maintenance:**
```bash
/automation-cron "maintenance" "Monthly Maintenance" "maintenance.request" "archive_closed" \
  --interval_number=1 --interval_type="months" --active=True
```

**Run once cron:**
```bash
/automation-cron "upgrade" "Data Migration" "upgrade.manager" "migrate_data" \
  --interval_number=1 --interval_type="days" --numbercall=1
```

**With specific nextcall:**
```bash
/automation-cron "backup" "Daily Backup" "backup.manager" "create_backup" \
  --interval_number=1 --interval_type="days" --nextcall="2025-01-01 02:00:00"
```

## Python Model Method Example

The cron expects a method on the model:

```python
# models/library_book.py

from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    # ... fields ...

    def cleanup_old_books(self):
        """Archive books not borrowed in last 2 years"""
        _logger.info("Starting book cleanup...")

        # Find old books
        old_books = self.search([
            ('last_borrow_date', '<', (context_today() - timedelta(days=730)).strftime('%Y-%m-%d')),
            ('active', '=', True),
        ])

        # Archive them
        old_books.write({'active': False})

        _logger.info("Archived %d old books", len(old_books))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Archived %d books') % len(old_books),
                'type': 'info',
            }
        }
```

## Best Practices

1. **Naming Conventions**:
   - Use descriptive cron names
   - Use lowercase with underscores for XML IDs
   - Prefix with module name

2. **Interval Selection**:
   - Choose appropriate interval for task frequency
   - Consider server load when setting intervals
   - Use minutes for frequent tasks sparingly

3. **Performance**:
   - Process records in batches for large datasets
   - Add search limits to avoid memory issues
   - Use proper indexing on search domains

4. **Error Handling**:
   - Always wrap code in try-except
   - Log errors for debugging
   - Send notifications for critical failures

5. **Testing**:
   - Test cron method manually first
   - Use `active=False` for development
   - Enable in production after testing

6. **Documentation**:
   - Document what the cron does
   - Comment complex logic
   - Note dependencies

7. **Security**:
   - Use appropriate user_id (admin for critical tasks)
   - Validate data in methods
   - Check permissions in code

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── {model_filename}.py  # Contains cron method
├── data/
│   └── cron_data.xml  # Cron definitions
```

## Next Steps

After creating the cron:
- `/automation-server-action` - Create server actions
- Test the cron method manually
- Schedule cron execution
- Monitor cron execution logs
