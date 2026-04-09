---
name: odoo-testing
description: Create and run unit tests, integration tests, and automated tests for Odoo modules. Use when user asks to "write tests", "create test case", "run tests", "test coverage", "unit test", "pytest", "odoo test", or any testing-related task for Odoo modules
---

# Odoo Testing Framework Guide

You are helping users write and run tests for Odoo modules.

## Testing Philosophy

1. **Test behavior, not implementation** - Test what the code does, not how it does it
2. **Isolate tests** - Each test should be independent
3. **Test edge cases** - Empty data, maximum values, special characters
4. **Keep tests fast** - Avoid unnecessary database operations
5. **Use meaningful assertions** - Clear error messages when tests fail

## Odoo Test Types

| Type | Purpose | Speed | When to Use |
|------|---------|-------|-------------|
| Unit Tests | Test single method/logic | Fast | Most common |
| Transaction Tests | Test ORM operations | Medium | CRUD operations |
| HTTP Tests | Test controllers/API | Slow | API endpoints |
| Tours | Test UI workflows | Slowest | User scenarios |

## Test File Structure

### Location
```
module/
├── tests/
│   ├── __init__.py          # Import test classes
│   ├── test_model.py         # Model tests
│   ├── test_wizard.py        # Wizard tests
│   └── test_api.py           # API/controller tests
```

### Setup

```python
# tests/__init__.py
from . import test_model
```

```python
# tests/test_model.py
# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('custom_module', 'model_tests')
class TestCustomModel(TransactionCase):
    """Test cases for custom model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

        # Create test record
        self.record = self.env['custom.model'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
            'state': 'draft',
        })

    def test_record_creation(self):
        """Test that records can be created"""
        self.assertTrue(self.record.id)
        self.assertEqual(self.record.name, 'Test Record')
        self.assertEqual(self.record.state, 'draft')

    def test_name_get(self):
        """Test name_get display"""
        name = self.record.name_get()
        self.assertIsInstance(name, list)
        self.assertEqual(len(name), 1)
        self.assertEqual(name[0][0], self.record.id)

    def test_state_transition(self):
        """Test state machine transitions"""
        # Initial state
        self.assertEqual(self.record.state, 'draft')

        # Transition to confirm
        self.record.action_confirm()
        self.assertEqual(self.record.state, 'confirmed')

        # Transition to done
        self.record.action_done()
        self.assertEqual(self.record.state, 'done')

    def test_constrained_write(self):
        """Test that write respects constraints"""
        with self.assertRaises(ValidationError):
            self.record.write({'name': ''})  # Empty name should fail

    def test_company_dependency(self):
        """Test company-dependent fields"""
        company = self.env.company
        self.record.write({'company_id': company.id})
        self.assertEqual(self.record.company_id, company)
```

## Common Test Patterns

### Test CRUD Operations

```python
def test_crud_operations(self):
    """Test create, read, update, delete"""

    # Create
    record = self.env['custom.model'].create({
        'name': 'CRUD Test',
        'value': 100,
    })
    self.assertTrue(record.id)

    # Read
    read_record = self.env['custom.model'].browse(record.id)
    self.assertEqual(read_record.name, 'CRUD Test')

    # Update
    read_record.write({'value': 200})
    self.assertEqual(read_record.value, 200)

    # Delete
    record_id = record.id
    record.unlink()
    self.assertFalse(self.env['custom.model'].browse(record_id).exists())
```

### Test Computed Fields

```python
def test_computed_field(self):
    """Test computed field calculation"""

    # Create order with lines
    order = self.env['sale.order'].create({
        'partner_id': self.partner.id,
    })

    self.env['sale.order.line'].create([
        {'order_id': order.id, 'product_id': self.product_a.id, 'price_unit': 100, 'product_uom_qty': 2},
        {'order_id': order.id, 'product_id': self.product_b.id, 'price_unit': 50, 'product_uom_qty': 1},
    ])

    # Trigger computation
    order._compute_amount()

    # Verify
    self.assertEqual(order.amount_total, 250)
```

### Test Onchange Methods

```python
def test_onchange_partner(self):
    """Test onchange behavior"""

    # Set partner with specific properties
    partner = self.env['res.partner'].create({
        'name': 'Test Partner',
        'property_payment_term_id': self.env.ref('account.account_payment_term_30days').id,
    })

    # Create record
    record = self.env['custom.model'].create({
        'partner_id': partner.id,
    })

    # Trigger onchange
    record._onchange_partner_id()

    # Verify onchange result
    self.assertEqual(record.payment_term_id, partner.property_payment_term_id)
```

### Test Constraints

```python
def test_sql_constraint(self):
    """Test SQL constraint violation"""

    # Create first record
    self.env['custom.model'].create({
        'code': 'UNIQUE123',
    })

    # Try duplicate - should fail
    with self.assertRaises(Exception):  # psycopg2.UniqueViolation
        self.env['custom.model'].create({
            'code': 'UNIQUE123',
        })

def test_python_constraint(self):
    """Test Python constraint"""

    with self.assertRaises(ValidationError):
        self.env['custom.model'].create({
            'name': '',  # Should fail - name required
            'value': -10,  # Should fail - value must be positive
        })
```

### Test Access Rights

```python
def test_access_rights(self):
    """Test record rule enforcement"""

    # Create record as admin
    record = self.env['custom.model'].create({
        'name': 'Access Test',
    })

    # Switch to different user
    User = self.env['res.users']
    user = User.create({
        'name': 'Test User',
        'login': 'test_user',
        'groups_id': [(4, self.env.ref('base.group_user').id)],
    })

    # Record should be visible to user
    record_as_user = record.with_user(user)
    self.assertTrue(record_as_user.check_access_rights('read', raise_exception=False))
```

### Test Workflow/State Machine

```python
def test_workflow_approval(self):
    """Test approval workflow"""

    record = self.env['custom.model'].create({
        'name': 'Workflow Test',
    })

    # Initial state
    self.assertEqual(record.state, 'draft')

    # Submit for approval
    record.action_submit()
    self.assertEqual(record.state, 'pending')

    # Approve
    record.action_approve()
    self.assertEqual(record.state, 'approved')

    # Reject
    record.action_reject()
    self.assertEqual(record.state, 'rejected')
```

## Running Tests

### Run Single Test

```bash
# Run specific test class
odoo-bin -d db_name -u module_name --test-tags '/test_model'

# Run specific test method
oddoo-bin -d db_name -u module_name --test-tags '/test_model::TestCustomModel::test_record_creation'
```

### Run All Module Tests

```bash
# From module directory
odoo-bin -d db_name -u module_name --test-tags '.'
```

### Run with Coverage

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run --source=module_name $(which odoo-bin) \
  -d db_name -u module_name --test-tags '.' \
  --stop-after-init

# Generate report
coverage report -m
```

### Pytest Integration

```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --tb=short"
```

```python
# conftest.py
import pytest
from odoo.api import Environment

@pytest.fixture
def odoo_env():
    """Odoo environment fixture"""
    # Setup Odoo environment
    pass
```

## Test Utilities

### Helper Methods

```python
class TestCustomModel(TransactionCase):

    def _create_test_partner(self, **kwargs):
        """Create test partner with defaults"""
        defaults = {
            'name': 'Test Partner',
            'email': 'test@example.com',
        }
        defaults.update(kwargs)
        return self.env['res.partner'].create(defaults)

    def _create_test_record(self, **kwargs):
        """Create test record with defaults"""
        defaults = {
            'name': 'Test Record',
            'state': 'draft',
        }
        defaults.update(kwargs)
        return self.env['custom.model'].create(defaults)
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_with_mock(self):
    """Test with mocked external service"""

    with patch('module.external_api.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.get_data.return_value = {'result': 'success'}

        # Call method that uses external API
        result = self.record.fetch_external_data()

        # Verify
        self.assertEqual(result, 'success')
        mock_instance.get_data.assert_called_once()
```

## Test Coverage Guidelines

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| Core business logic | 90%+ | Critical |
| Computed fields | 90%+ | Critical |
| Constraints | 100% | Critical |
| Workflow transitions | 90%+ | High |
| Access rights | 80%+ | Medium |
| UI/Views | 50%+ | Low |

## Common Mistakes to Avoid

```python
# BAD: Hardcoded IDs
record = self.env.ref('base.user_root')  # Fragile!

# GOOD: Search for the record
record = self.env['res.users'].search([('login', '=', 'root')], limit=1)

# BAD: No teardown
def test_something(self):
    self.env['custom.model'].create({'name': 'Test'})
    # No assertion! Test passes vacuously

# GOOD: Clear assertions
def test_something(self):
    record = self.env['custom.model'].create({'name': 'Test'})
    self.assertTrue(record.exists())

# BAD: Test depends on order
def test_second(self):
    self.assertTrue(self.record.id)  # Depends on test_first

# GOOD: Independent tests
def test_second(self):
    new_record = self.env['custom.model'].create({'name': 'Another'})
    self.assertTrue(new_record.id)
```

## Summary Output

After running tests, always present:

```
## Test Results

- Total Tests: {count}
- Passed: {count}
- Failed: {count}
- Skipped: {count}
- Duration: {time}

## Failures
{list of failed tests with error details}

## Coverage
- Overall: {percentage}%
- Critical paths: {percentage}%
```
