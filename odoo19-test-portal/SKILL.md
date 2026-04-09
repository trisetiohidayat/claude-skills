---
description: Create Odoo 19 portal tour tests with browser automation for customer/vendor portals. Use when user wants to create a portal tour test.
---


# Odoo 19 Portal Tour Test Creation

Create comprehensive portal tour tests for Odoo 19 using browser automation with proper user context, interactive UI testing, and portal-specific scenarios.

## Instructions

1. **Determine the file location:**
   - Portal tours should be in: `{module_name}/static/tests/tours/{tour_name}.js`
   - For backend tours: `{module_name}/static/tests/tours/{tour_name}.js`
   - Create the directory structure if it doesn't exist

2. **Generate the tour structure:**

```javascript
odoo.define('{module_name}.{tour_name}_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('{tour_name}', {
        test: true,
        url: '/my',
    }, [{
        trigger: 'selector',
        content: 'Description',
        position: 'bottom',
    }, {
        trigger: 'selector',
        content: 'Description',
        run: function (actions) {
            // Custom action
        },
    }]);
});
```

3. **Choose the right tour type:**
   - **Portal Tour**: Test customer/vendor portal functionality
   - **Backend Tour**: Test admin interface
   - **Hybrid Tour**: Test both portal and backend (separate tours)

4. **Common tour step patterns:**

```javascript
// Click on element
{
    trigger: 'a:contains("My Orders")',
    content: 'Click on My Orders menu',
    position: 'bottom',
}

// Fill in input
{
    trigger: 'input[name="search"]',
    content: 'Enter search term',
    run: 'text',
}

// Select dropdown option
{
    trigger: 'select[name="state"]',
    content: 'Select state',
    run: 'text',
}

// Wait for element
{
    trigger: '.o_portal_my_details',
    content: 'Wait for details to load',
    run: function () {},
}

// Custom JavaScript action
{
    trigger: '.o_button_submit',
    content: 'Submit form',
    run: function (actions) {
        actions.auto();
    },
}

// Check visible element
{
    trigger: '.o_portal_sidebar:visible',
    content: 'Verify sidebar is visible',
    run: function () {},
}
```

5. **User context setup:**

```javascript
// Portal user context
{
    trigger: '#login',
    content: 'Enter portal user email',
    run: 'portal_user@example.com',
}

// Admin user context
{
    trigger: '#login',
    content: 'Enter admin email',
    run: 'admin@example.com',
}

// Custom context with data setup
beforeLoad: function () {
    // Create test data
}
```

6. **Add to __manifest__.py:**
   - Add tour files to assets
   - Format: `'web.assets_tests': ['{module_name}/static/tests/tours/*.js']`

7. **Run tours:**
   ```bash
   # Run all tours
   ./odoo-bin -d test_db --test-enable --test-tags=python-only

   # Run specific tour
   ./odoo-bin -d test_db --test-enable --test-tags=post_install

   # Run with JavaScript console
   ./odoo-bin -d test_db --test-enable --test-tags=web_tour

   # Run tours in browser
   Visit: /web/tests?debug=1&module={module_name}
   ```

8. **Common selectors:**
   - Links: `a:contains("Text")`
   - Buttons: `button:contains("Text")` or `.btn-primary`
   - Inputs: `input[name="field_name"]`
   - Forms: `form.o_form_view`
   - Modals: `.modal-dialog`
   - Tables: `table.o_list_table`
   - Portal elements: `.o_portal_*`
   - Chatter: `.o_chatter`
   - Sidebar: `.o_portal_sidebar`

## Usage Examples

### Basic Portal Login Tour

```bash
/test-portal portal_sale portal_sale_my_orders tour_type="portal" test_steps="login,navigate_to_orders,view_order_details"
```

Output:
```javascript
// portal_sale/static/tests/tours/portal_sale_my_orders_tour.js

odoo.define('portal_sale.portal_sale_my_orders_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('portal_sale_my_orders', {
        test: true,
        url: '/my',
    }, [{
        trigger: '#login',
        content: 'Enter portal user email',
        position: 'top',
        run: 'portal@odoo.com',
    }, {
        trigger: '#password',
        content: 'Enter portal user password',
        position: 'top',
        run: 'portal',
    }, {
        trigger: 'button[type="submit"]',
        content: 'Click login button',
        position: 'bottom',
    }, {
        trigger: 'a:contains("Orders")',
        content: 'Navigate to Orders page',
        position: 'bottom',
    }, {
        trigger: '.o_portal_my_doc_table:visible',
        content: 'Verify orders table is visible',
        run: function () {},
    }, {
        trigger: '.o_portal_doc_table tbody tr:first-child a',
        content: 'Click on first order',
        position: 'bottom',
    }, {
        trigger: '.o_portal_sale_details:visible',
        content: 'Verify order details are displayed',
        run: function () {},
    }, {
        trigger: 'a[href="/my/orders"]',
        content: 'Navigate back to orders list',
        position: 'bottom',
    }]);
});
```

### Portal Quote Creation Tour

```bash
/test-portal portal_quote portal_quote_create tour_type="portal" test_steps="login,navigate_to_quotes,create_quote,fill_quote,submit_quote"
```

Output:
```javascript
// portal_quote/static/tests/tours/portal_quote_create_tour.js

odoo.define('portal_quote.portal_quote_create_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('portal_quote_create', {
        test: true,
        url: '/my',
    }, [{
        trigger: '#login',
        content: 'Login as portal user',
        position: 'top',
        run: 'portal@odoo.com',
    }, {
        trigger: '#password',
        content: 'Enter password',
        position: 'top',
        run: 'portal',
    }, {
        trigger: 'button[type="submit"]',
        content: 'Submit login form',
        position: 'bottom',
    }, {
        trigger: 'a:contains("Quotes")',
        content: 'Navigate to Quotes section',
        position: 'bottom',
    }, {
        trigger: 'a:contains("New Quote Request")',
        content: 'Click on New Quote Request',
        position: 'bottom',
    }, {
        trigger: 'input[name="subject"]',
        content: 'Enter quote subject',
        position: 'top',
        run: 'Test Quote Request',
    }, {
        trigger: 'textarea[name="description"]',
        content: 'Enter quote description',
        position: 'top',
        run: 'This is a test quote request from tour',
    }, {
        trigger: 'input[name="expected_revenue"]',
        content: 'Enter expected revenue',
        position: 'top',
        run: '5000',
    }, {
        trigger: 'button:contains("Submit")',
        content: 'Submit quote request',
        position: 'bottom',
    }, {
        trigger: '.alert-success:visible',
        content: 'Verify success message',
        run: function () {},
    }]);
});
```

### Project Portal Task Tour

```bash
/test-portal project portal_project_tasks tour_type="portal" test_steps="login,navigate_to_tasks,view_task,add_comment"
```

Output:
```javascript
// project/static/tests/tours/portal_project_tasks_tour.js

odoo.define('project.portal_project_tasks_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('portal_project_tasks', {
        test: true,
        url: '/my',
    }, [{
        trigger: '#login',
        content: 'Login to portal',
        position: 'top',
        run: 'portal@odoo.com',
    }, {
        trigger: '#password',
        content: 'Enter password',
        position: 'top',
        run: 'portal',
    }, {
        trigger: 'button[type="submit"]',
        content: 'Submit login',
        position: 'bottom',
    }, {
        trigger: 'a:contains("Tasks")',
        content: 'Navigate to Tasks',
        position: 'bottom',
    }, {
        trigger: '.o_portal_my_task_table:visible',
        content: 'Verify tasks table is visible',
        run: function () {},
    }, {
        trigger: '.o_portal_task_table tbody tr:first-child a',
        content: 'Click on first task',
        position: 'bottom',
    }, {
        trigger: '.o_task_details:visible',
        content: 'Verify task details are displayed',
        run: function () {},
    }, {
        trigger: 'textarea[name="message"]',
        content: 'Add comment to task',
        position: 'top',
        run: 'Test comment from portal tour',
    }, {
        trigger: 'button:contains("Send")',
        content: 'Send comment',
        position: 'bottom',
    }, {
        trigger: '.o_chatter_message:contains("Test comment from portal tour")',
        content: 'Verify comment was added',
        run: function () {},
    }]);
});
```

### Portal Invoice Payment Tour

```bash
/test-portal portal_payment portal_invoice_payment tour_type="portal" test_steps="login,navigate_to_invoices,select_invoice,make_payment"
```

Output:
```javascript
// portal_payment/static/tests/tours/portal_invoice_payment_tour.js

odoo.define('portal_payment.portal_invoice_payment_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('portal_invoice_payment', {
        test: true,
        url: '/my',
    }, [{
        trigger: '#login',
        content: 'Login as portal user',
        position: 'top',
        run: 'portal@odoo.com',
    }, {
        trigger: '#password',
        content: 'Enter password',
        position: 'top',
        run: 'portal',
    }, {
        trigger: 'button[type="submit"]',
        content: 'Submit login',
        position: 'bottom',
    }, {
        trigger: 'a:contains("Invoices")',
        content: 'Navigate to Invoices',
        position: 'bottom',
    }, {
        trigger: '.o_portal_my_invoices:visible',
        content: 'Verify invoices list',
        run: function () {},
    }, {
        trigger: '.o_invoice_pay:first',
        content: 'Click Pay button on first invoice',
        position: 'bottom',
    }, {
        trigger: '.o_payment_form:visible',
        content: 'Verify payment form is displayed',
        run: function () {},
    }, {
        trigger: 'input[name="amount"]',
        content: 'Enter payment amount',
        position: 'top',
        run: '100',
    }, {
        trigger: 'button:contains("Pay Now")',
        content: 'Submit payment',
        position: 'bottom',
    }, {
        trigger: '.alert-success:contains("Payment successfully processed")',
        content: 'Verify payment success',
        run: function () {},
    }]);
});
```

### Backend Admin Tour with Portal User Setup

```bash
/test-portal portal_setup portal_user_setup tour_type="backend" test_steps="login_as_admin,create_portal_user,configure_portal_access"
```

Output:
```javascript
// portal_setup/static/tests/tours/portal_user_setup_tour.js

odoo.define('portal_setup.portal_user_setup_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('portal_user_setup', {
        test: true,
        url: '/web',
    }, [{
        trigger: '#login',
        content: 'Login as admin',
        position: 'top',
        run: 'admin',
    }, {
        trigger: '#password',
        content: 'Enter admin password',
        position: 'top',
        run: 'admin',
    }, {
        trigger: 'button[type="submit"]',
        content: 'Submit login',
        position: 'bottom',
    }, {
        trigger: '.o_app[data-menu-xmlid="base.menu_users"]',
        content: 'Open Users menu',
        position: 'bottom',
    }, {
        trigger: '.o_list_button_add',
        content: 'Create new user',
        position: 'bottom',
    }, {
        trigger: 'input[name="name"]',
        content: 'Enter user name',
        position: 'top',
        run: 'Portal Test User',
    }, {
        trigger: 'input[name="email"]',
        content: 'Enter user email',
        position: 'top',
        run: 'portal_test@example.com',
    }, {
        trigger: 'input[name="login"]',
        content: 'Enter login',
        position: 'top',
        run: 'portal_test',
    }, {
        trigger: '.o_field_many2one[name="groups_id"] input',
        content: 'Add Portal group',
        position: 'top',
        run: 'text',
    }, {
        trigger: '.ui-menu-item:contains("Portal")',
        content: 'Select Portal group',
        position: 'bottom',
    }, {
        trigger: 'button:contains("Save")',
        content: 'Save user',
        position: 'bottom',
    }, {
        trigger: '.o_form_status_indicator:contains("Saved")',
        content: 'Verify user was saved',
        run: function () {},
    }]);
});
```

### Multi-Step Portal Workflow Tour

```bash
/test-portal helpdesk helpdesk_ticket_workflow tour_type="portal" test_steps="login,create_ticket,upload_attachment,track_status"
```

Output:
```javascript
// helpdesk/static/tests/tours/helpdesk_ticket_workflow_tour.js

odoo.define('helpdesk.helpdesk_ticket_workflow_tour', function (require) {
    "use strict";

    var tour = require('web_tour.tour');

    tour.register('helpdesk_ticket_workflow', {
        test: true,
        url: '/my',
    }, [{
        trigger: '#login',
        content: 'Login to customer portal',
        position: 'top',
        run: 'portal@odoo.com',
    }, {
        trigger: '#password',
        content: 'Enter password',
        position: 'top',
        run: 'portal',
    }, {
        trigger: 'button[type="submit"]',
        content: 'Submit login form',
        position: 'bottom',
    }, {
        trigger: 'a:contains("Helpdesk")',
        content: 'Navigate to Helpdesk section',
        position: 'bottom',
    }, {
        trigger: 'a:contains("New Ticket")',
        content: 'Create new ticket',
        position: 'bottom',
    }, {
        trigger: 'input[name="subject"]',
        content: 'Enter ticket subject',
        position: 'top',
        run: 'Issue with product delivery',
    }, {
        trigger: 'select[name="category_id"]',
        content: 'Select ticket category',
        position: 'top',
        run: 'text',
    }, {
        trigger: 'textarea[name="description"]',
        content: 'Enter ticket description',
        position: 'top',
        run: 'My product has not been delivered yet. Order #12345.',
    }, {
        trigger: 'input[type="file"]',
        content: 'Upload attachment',
        position: 'top',
        run: function (actions) {
            // Simulate file upload
        },
    }, {
        trigger: 'button:contains("Submit")',
        content: 'Submit ticket',
        position: 'bottom',
    }, {
        trigger: '.o_portal_helpdesk_ticket:visible',
        content: 'Verify ticket was created',
        run: function () {},
    }, {
        trigger: '.o_ticket_status:contains("Submitted")',
        content: 'Verify ticket status',
        run: function () {},
    }]);
});
```

## Best Practices

1. **Tour Design:**
   - Keep tours focused and short
   - Test one user journey per tour
   - Use descriptive content messages
   - Include visual verification steps

2. **Selector Strategy:**
   - Use specific, stable selectors
   - Prefer data attributes over class names
   - Avoid complex CSS selectors
   - Use visible pseudo-selector for verification

3. **Timing and Waits:**
   - Tours auto-wait for elements
   - Use `run: function () {}` for verification only
   - Avoid explicit waits when possible
   - Handle asynchronous operations properly

4. **User Context:**
   - Set up test data before tour runs
   - Use consistent test users
   - Clean up after tours
   - Document user permissions

5. **Error Handling:**
   - Include validation steps
   - Provide clear failure messages
   - Test error conditions
   - Verify success states

6. **Performance:**
   - Minimize DOM queries
   - Use efficient selectors
   - Avoid unnecessary steps
   - Run tours in parallel when possible

7. **Maintainability:**
   - Comment complex steps
   - Use meaningful tour names
   - Keep selectors up to date
   - Document prerequisites

## Advanced Patterns

### Conditional Steps Based on State

```javascript
{
    trigger: '.o_state_draft',
    content: 'Handle draft state',
    run: function (actions) {
        if (this.$('.o_state_draft').length) {
            actions.auto('.btn_confirm');
        }
    },
}
```

### Custom Verification Functions

```javascript
{
    trigger: '.o_portal_orders',
    content: 'Verify orders are displayed',
    run: function () {
        var $orders = this.$('.o_portal_order_row');
        if ($orders.length === 0) {
            console.error('No orders found');
        }
    },
}
```

### Dynamic Data Entry

```javascript
{
    trigger: 'input[name="reference"]',
    content: 'Enter dynamic reference',
    run: function () {
        var timestamp = new Date().getTime();
        this.$('input[name="reference"]').val('TEST-' + timestamp)
            .trigger('input');
    },
}
```

### Wait for AJAX Completion

```javascript
{
    trigger: '.o_loading:visible',
    content: 'Wait for data to load',
    run: function () {
        return this.$('.o_loading:hidden').length > 0;
    },
}
```

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── controllers/
│   └── portal.py
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   └── portal.js
│   │   └── css/
│   │       └── portal.css
│   └── tests/
│       └── tours/
│           ├── {tour_name}_tour.js
│           └── {another_tour}_tour.js
└── views/
    └── portal_templates.xml
```

## Manifest Configuration

Update `__manifest__.py` to include tour assets:

```python
'assets': {
    'web.assets_tests': [
        '{module_name}/static/tests/tours/*.js',
    ],
},
```

## Running Tours

### Command Line

```bash
# Run all tours
./odoo-bin -d test_db --test-enable --test-tags=web_tour

# Run specific module tours
./odoo-bin -d test_db --test-enable --test-tags={module_name}

# Run with debug mode
./odoo-bin -d test_db --test-enable --test-tags=web_tour --debug

# Run tours in development
./odoo-bin -d test_db --test-enable --test-tags=post_install
```

### Browser

```
Navigate to: /web/tests?debug=1&module={module_name}
```

## Common Issues and Solutions

### Element Not Found
- Increase wait time with verification step
- Check element visibility with `:visible`
- Verify selector specificity

### Timing Issues
- Use `run: function () {}` for wait-only steps
- Add verification steps before actions
- Check for loading indicators

### Portal User Authentication
- Set up test portal user in data
- Use consistent login credentials
- Verify user has proper permissions

### Dynamic Content
- Use more general selectors
- Wait for content to load
- Verify element existence before interaction

## Next Steps

After creating portal tours:
- Run tours locally to verify
- Set up continuous integration
- Test in different browsers
- Monitor tour execution times
- Maintain tours with UI changes

## Tour Testing Checklist

- [ ] Tour completes without errors
- [ ] All steps execute in order
- [ ] Proper user context is set
- [ ] Test data is created/cleaned up
- [ ] Success/failure conditions are verified
- [ ] Tour runs consistently across environments
- [ ] Documentation is up to date
- [ ] Performance is acceptable
