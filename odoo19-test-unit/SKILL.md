---
description: Create comprehensive Odoo 19 unit test case classes using TransactionCase. Use when user wants to create unit tests for a model.
---


# Odoo 19 Unit Test Creation

Create comprehensive unit test case classes for Odoo 19 models using proper testing conventions with TransactionCase, test methods, and assertions.

## Instructions

1. **Determine the file location:**
   - Tests should be in: `{module_name}/tests/{test_filename}.py`
   - Use descriptive names (e.g., `test_book.py`, `test_sale_order.py`)
   - Create the `tests/` directory if it doesn't exist

2. **Generate the test case class structure:**

```python
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class {TestClassName}(TransactionCase):
    """Test cases for {ModelName} model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()
        # Create common test data
        {test_data_setup}

    def test_{test_method_name}(self):
        """Test description"""
        # Arrange
        {setup_data}
        # Act
        {action}
        # Assert
        {assertions}
```

3. **Choose the right test case type:**
   - **TransactionCase**: Each test method runs in its own transaction (isolated)
   - **SingleTransactionCase**: All tests share one transaction (faster but less isolated)
   - **HttpCase**: For web/tour testing (use `/test-portal` instead)
   - **SavepointCase**: Advanced use with nested transactions

4. **Common test patterns:**

```python
# Test record creation
def test_create_record(self):
    record = self.env[{model_name}].create({
        'name': 'Test Record',
    })
    self.assertTrue(record.id)
    self.assertEqual(record.name, 'Test Record')

# Test constraints
def test_constraint_validation(self):
    with self.assertRaises(ValidationError):
        self.env[{model_name}].create({
            'field': invalid_value,
        })

# Test computed fields
def test_computed_field(self):
    record = self.env[{model_name}].create({
        'field1': value1,
        'field2': value2,
    })
    self.assertEqual(record.computed_field, expected_value)

# Test onchange methods
def test_onchange_method(self):
    record = self.env[{model_name}].new({
        'field1': value1,
    })
    record._onchange_method()
    self.assertEqual(record.field2, expected_value)
```

5. **Useful assertion methods:**
   - `assertEqual(a, b)` - Check equality
   - `assertNotEqual(a, b)` - Check inequality
   - `assertTrue(x)` - Check truthy
   - `assertFalse(x)` - Check falsy
   - `assertRaises(Exception)` - Check exception raised
   - `assertIn(a, b)` - Check membership
   - `assertIsNone(x)` - Check None
   - `assertIsInstance(x, type)` - Check type

6. **Test data setup patterns:**

```python
def setUp(self):
    super().setUp()
    # Create test partner
    self.partner = self.env['res.partner'].create({
        'name': 'Test Partner',
        'email': 'test@example.com',
    })
    # Create test product
    self.product = self.env['product.product'].create({
        'name': 'Test Product',
        'list_price': 100.0,
    })
```

7. **Add to __init__.py:**
   - Create or update `tests/__init__.py`
   - Import the test file: `from . import test_{test_filename}`

8. **Run tests:**
   ```bash
   # Run all tests for a module
   ./odoo-bin -d test_db --test-enable --stop-after-init -i {module_name}

   # Run specific test file
   ./odoo-bin -d test_db --test-enable --test-tags {module_name} --stop-after-init

   # Run specific test class
   ./odoo-bin -d test_db --test-enable --test-tags {module_name}.{test_class_name}
   ```

## Usage Examples

### Basic Unit Test

```bash
/test-unit library_book TestBook book.library test_methods="test_create_book,test_delete_book"
```

Output:
```python
# library_book/tests/test_book.py

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestBook(TransactionCase):
    """Test cases for Book model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.Book = self.env['book.library']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Author',
            'email': 'author@example.com',
        })

    def test_create_book(self):
        """Test creating a new book"""
        # Arrange
        book_data = {
            'name': 'Test Book',
            'isbn': '978-0-123456-78-9',
            'author_ids': [(4, self.partner.id)],
        }
        # Act
        book = self.Book.create(book_data)
        # Assert
        self.assertTrue(book.id)
        self.assertEqual(book.name, 'Test Book')
        self.assertEqual(book.isbn, '978-0-123456-78-9')
        self.assertEqual(len(book.author_ids), 1)

    def test_delete_book(self):
        """Test deleting a book"""
        # Arrange
        book = self.Book.create({
            'name': 'Book to Delete',
        })
        book_id = book.id
        # Act
        book.unlink()
        # Assert
        book_found = self.Book.search([('id', '=', book_id)])
        self.assertFalse(book_found)
```

### Test with Constraints and Computations

```bash
/test-unit sale_order TestSaleOrder sale.order test_methods="test_create_order,test_price_calculation,test_validate_order"
```

Output:
```python
# sale_order/tests/test_sale_order.py

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestSaleOrder(TransactionCase):
    """Test cases for Sale Order model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.SaleOrder = self.env['sale.order']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'customer_rank': 1,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })

    def test_create_order(self):
        """Test creating a sale order"""
        # Arrange & Act
        order = self.SaleOrder.create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                }),
            ],
        })
        # Assert
        self.assertTrue(order.id)
        self.assertEqual(order.state, 'draft')
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line[0].product_uom_qty, 2.0)

    def test_price_calculation(self):
        """Test price calculation"""
        # Arrange
        order = self.SaleOrder.create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 50.0,
                }),
            ],
        })
        # Act
        order._amount_all()
        # Assert
        self.assertEqual(order.amount_untaxed, 150.0)
        self.assertEqual(order.amount_total, 150.0)

    def test_validate_order(self):
        """Test order validation"""
        # Arrange
        order = self.SaleOrder.create({
            'partner_id': self.partner.id,
        })
        # Act
        order.action_confirm()
        # Assert
        self.assertEqual(order.state, 'sale')
        self.assertTrue(order.date_order)
```

### Test with Onchange Methods

```bash
/test-unit purchase_order TestPurchaseOrder purchase.order test_methods="test_onchange_partner_id,test_amount_calculation"
```

Output:
```python
# purchase_order/tests/test_purchase_order.py

from odoo.tests import TransactionCase


class TestPurchaseOrder(TransactionCase):
    """Test cases for Purchase Order model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.PurchaseOrder = self.env['purchase.order']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Vendor',
            'supplier_rank': 1,
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'standard_price': 80.0,
        })

    def test_onchange_partner_id(self):
        """Test onchange partner_id updates currency"""
        # Arrange
        order = self.PurchaseOrder.new({
            'partner_id': self.partner.id,
        })
        # Act
        order._onchange_partner_id()
        # Assert
        self.assertEqual(order.partner_id, self.partner)
        self.assertTrue(order.currency_id)

    def test_amount_calculation(self):
        """Test purchase order amount calculation"""
        # Arrange
        order = self.PurchaseOrder.create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_qty': 5.0,
                    'price_unit': 80.0,
                }),
            ],
        })
        # Act
        order._amount_all()
        # Assert
        self.assertEqual(order.amount_untaxed, 400.0)
        self.assertEqual(order.amount_total, 400.0)
```

### Test with Multiple Dependencies

```bash
/test-unit project_task TestProjectTask project.task dependencies="res.users,res.partner,project.project" test_methods="test_create_task,test_assign_user"
```

Output:
```python
# project_task/tests/test_project_task.py

from odoo.tests import TransactionCase


class TestProjectTask(TransactionCase):
    """Test cases for Project Task model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.Task = self.env['project.task']
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'test@example.com',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        self.project = self.env['project.project'].create({
            'name': 'Test Project',
        })

    def test_create_task(self):
        """Test creating a task"""
        # Arrange & Act
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'user_id': self.user.id,
            'partner_id': self.partner.id,
        })
        # Assert
        self.assertTrue(task.id)
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.project_id, self.project)
        self.assertEqual(task.user_id, self.user)
        self.assertEqual(task.stage_id.sequence, 1)

    def test_assign_user(self):
        """Test assigning a user to task"""
        # Arrange
        task = self.Task.create({
            'name': 'Unassigned Task',
            'project_id': self.project.id,
        })
        # Act
        task.write({
            'user_id': self.user.id,
        })
        # Assert
        self.assertEqual(task.user_id, self.user)
        self.assertTrue(task.message_follower_ids)
```

### Test with ValidationError

```bash
/test-unit library_book TestBookConstraints book.library test_methods="test_isbn_uniqueness,test_required_fields"
```

Output:
```python
# library_book/tests/test_book_constraints.py

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestBookConstraints(TransactionCase):
    """Test constraints for Book model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.Book = self.env['book.library']

    def test_isbn_uniqueness(self):
        """Test ISBN must be unique"""
        # Arrange
        isbn = '978-0-123456-78-9'
        self.Book.create({
            'name': 'Book 1',
            'isbn': isbn,
        })
        # Act & Assert
        with self.assertRaises(ValidationError):
            self.Book.create({
                'name': 'Book 2',
                'isbn': isbn,
            })

    def test_required_fields(self):
        """Test required field validation"""
        # Act & Assert
        with self.assertRaises(ValidationError):
            self.Book.create({
                'isbn': '978-0-123456-78-9',
                # name is required but not provided
            })
```

## Best Practices

1. **Test Structure (AAA Pattern):**
   - Arrange: Set up test data
   - Act: Execute the method being tested
   - Assert: Verify expected behavior

2. **Test Independence:**
   - Each test should be independent
   - Use setUp() for common data
   - Don't rely on test execution order

3. **Descriptive Test Names:**
   - Use `test_` prefix for all test methods
   - Name should describe what is being tested
   - Example: `test_create_book_with_invalid_isbn_raises_error`

4. **Minimal Test Data:**
   - Create only necessary data
   - Use factories for complex objects
   - Clean up is automatic with TransactionCase

5. **Coverage:**
   - Test happy path (success scenarios)
   - Test edge cases and boundaries
   - Test error conditions and exceptions
   - Test computed fields and onchange methods

6. **Performance:**
   - Use SingleTransactionCase for read-only tests
   - Avoid unnecessary database writes
   - Use `self.env[{model}]` caching

7. **Assertions:**
   - One assertion per logical check
   - Use specific assertion methods
   - Include meaningful failure messages

## File Structure

```
{module_name}/
├── __init__.py
├── __manifest__.py
├── models/
│   └── {model_filename}.py
└── tests/
    ├── __init__.py  # Import test files: from . import test_book
    └── test_{model_filename}.py
```

## Advanced Patterns

### Testing Workflow State Changes

```python
def test_workflow_state_transitions(self):
    """Test state machine transitions"""
    order = self.SaleOrder.create({'partner_id': self.partner.id})
    self.assertEqual(order.state, 'draft')

    order.action_confirm()
    self.assertEqual(order.state, 'sale')

    order.action_done()
    self.assertEqual(order.state, 'done')
```

### Testing Many2many Relationships

```python
def test_many2many_relationship(self):
    """Test many2many field operations"""
    book = self.Book.create({'name': 'Test Book'})
    author1 = self.env['res.partner'].create({'name': 'Author 1'})
    author2 = self.env['res.partner'].create({'name': 'Author 2'})

    # Add authors
    book.write({'author_ids': [(6, 0, [author1.id, author2.id])]})
    self.assertEqual(len(book.author_ids), 2)

    # Remove author
    book.write({'author_ids': [(3, author1.id)]})
    self.assertEqual(len(book.author_ids), 1)
```

### Testing Search Methods

```python
def test_search_method(self):
    """Test custom search methods"""
    book1 = self.Book.create({'name': 'Python Programming'})
    book2 = self.Book.create({'name': 'Java Programming'})

    # Test name_search
    results = self.Book.name_search('Python')
    self.assertTrue(any(book1.id == r[0] for r in results))

    # Test custom search domain
    books = self.Book.search([('name', 'ilike', 'Programming')])
    self.assertEqual(len(books), 2)
```

## Next Steps

After creating unit tests, use:
- `/test-portal` - Create portal/tour tests for UI testing
- Run tests with different database configurations
- Add integration tests for multi-model scenarios
- Set up continuous integration for automated testing

## Testing Commands Reference

```bash
# Run all tests
./odoo-bin -d test_db --test-enable --stop-after-init

# Run specific module tests
./odoo-bin -d test_db --test-enable --test-tags {module_name} --stop-after-init

# Run with debug output
./odoo-bin -d test_db --test-enable --test-tags {module_name} --log-level=debug

# Run tests without stopping
./odoo-bin -d test_db --test-enable -i {module_name} --test-tags {module_name}

# Run specific test class
./odoo-bin -d test_db --test-enable --test-tags {module_name}.{test_class_name}
```
