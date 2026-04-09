---
name: odoo-testing-strategy
description: |
  Strategi testing Odoo - unit tests, integration tests, E2E tests, test coverage, test automation,
  CI/CD integration. Gunakan ketika:
  - User bertanya tentang testing strategy
  - Ingin build test suite
  - Need to improve coverage
  - Ingin setup CI/CD
---

# Odoo Testing Strategy Skill

## Overview

Skill ini membantu merancang dan mengimplementasikan strategi testing yang komprehensif untuk proyek Odoo. Testing yang baik adalah fondasi dari kualitas software yang handal, dan dalam konteks enterprise Odoo, strategi testing yang solid menjadi semakin penting seiring dengan kompleksitas kustomisasi yang dilakukan.

Odoo menyediakan framework testing yang powerful berbasis Python unittest. Dengan memahami berbagai tipe testing yang tersedia, developer dapat membangun test suite yang mencakup unit tests untuk logic individual, integration tests untuk interaksi antar komponen, dan end-to-end tests untuk validasi alur bisnis secara menyeluruh.

Dalam konteks pengembangan Odoo, khususnya untuk proyek migration dari Odoo 15 ke 19, testing menjadi aspek kritis untuk memastikan semua functionality tetap berjalan dengan benar setelah migrasi. Skill ini akan memandu Anda melalui berbagai aspek testing, mulai dari struktur dasar hingga implementasi CI/CD yang robust.

## Step 1: Analyze Test Types

### 1.1 TransactionCase (Unit Tests)

TransactionCase adalah dasar dari unit testing di Odoo. Setiap test method berjalan dalam transaksi database yang terpisah, yang di-rollback setelah test selesai. Ini memastikan test tidak saling mempengaruhi dan database tetap bersih.

Struktur dasar unit test:

```python
# tests/test_vendor_model.py
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TestVendorModel(TransactionCase):
    """Unit tests untuk vendor model"""

    def setUp(self):
        """Set up test data"""
        super(TestVendorModel, self).setUp()

        # Create test partner (vendor)
        self.vendor = self.env['res.partner'].create({
            'name': 'Test Vendor',
            'email': 'test@vendor.com',
            'supplier_rank': 1,
        })

        # Create test product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'list_price': 100.00,
        })

    def test_vendor_creation(self):
        """Test vendor creation"""
        self.assertTrue(self.vendor.id)
        self.assertEqual(self.vendor.name, 'Test Vendor')
        self.assertTrue(self.vendor.supplier_rank > 0)
        _logger.info('Vendor creation test passed')

    def test_vendor_email_validation(self):
        """Test vendor email validation"""
        # Test valid email
        self.vendor.write({'email': 'valid@email.com'})
        self.assertEqual(self.vendor.email, 'valid@email.com')

        # Test invalid email should raise validation error
        with self.assertRaises(ValidationError):
            self.vendor.write({'email': 'invalid-email'})

    def test_vendor_search(self):
        """Test vendor search functionality"""
        # Search by name
        vendors = self.env['res.partner'].search([
            ('name', 'ilike', 'Test'),
            ('supplier_rank', '>', 0)
        ])
        self.assertIn(self.vendor.id, vendors.ids)

        # Search by email
        vendors = self.env['res.partner'].search([
            ('email', '=', 'test@vendor.com')
        ])
        self.assertEqual(len(vendors), 1)
        self.assertEqual(vendendor.id, self.vendor.id)

    def test_vendor_computed_fields(self):
        """Test computed fields on vendor"""
        # Create vendor with invoices
        invoice = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 10,
                'price_unit': 100.00,
            })],
        })
        invoice.action_post()

        # Refresh vendor to get computed values
        self.vendor.invalidate_recordset()

        # Check computed field
        self.assertEqual(self.vendor.total_invoiced, 1000.00)

    def test_vendor_name_search(self):
        """Test name search functionality"""
        partners = self.env['res.partner'].name_search('Test')
        partner_ids = [p[0] for p in partners]
        self.assertIn(self.vendor.id, partner_ids)

    def test_vendor_archive(self):
        """Test vendor archive functionality"""
        # Archive vendor
        self.vendor.write({'active': False})

        # Verify vendor is not in active search
        active_vendors = self.env['res.partner'].search([
            ('supplier_rank', '>', 0),
            ('active', '=', True)
        ])
        self.assertNotIn(self.vendor.id, active_vendors.ids)

        # Verify vendor still exists in inactive search
        all_vendors = self.env['res.partner'].search([
            ('supplier_rank', '>', 0),
        ])
        self.assertIn(self.vendor.id, all_vendors.ids)

    def test_vendor_unlink(self):
        """Test vendor deletion"""
        vendor_id = self.vendor.id
        self.vendor.unlink()

        # Verify vendor is deleted
        deleted_vendor = self.env['res.partner'].browse(vendor_id)
        self.assertFalse(deleted_vendor.exists())


class TestVendorConstraints(TransactionCase):
    """Test constraints pada vendor"""

    def test_supplier_rank_constraint(self):
        """Test supplier rank must be non-negative"""
        with self.assertRaises(ValidationError):
            self.env['res.partner'].create({
                'name': 'Test Vendor',
                'supplier_rank': -1,
            })

    def test_unique_email(self):
        """Test email uniqueness constraint"""
        # Create first vendor
        self.env['res.partner'].create({
            'name': 'Vendor 1',
            'email': 'same@email.com',
            'supplier_rank': 1,
        })

        # Create second vendor with same email should fail
        with self.assertRaises(ValidationError):
            self.env['res.partner'].create({
                'name': 'Vendor 2',
                'email': 'same@email.com',
                'supplier_rank': 1,
            })
```

### 1.2 HttpCase (Functional Tests)

HttpCase digunakan untuk menguji controller HTTP dan interaksi yang melibatkan request/response. Ini berguna untuk testing REST API endpoints dan web controllers.

```python
# tests/test_api_controller.py
from odoo.tests import HttpCase, tagged
from odoo.tests.common import new_test_user
import json


@tagged('api', '-standard')
class TestVendorAPI(HttpCase):
    """HTTP tests untuk vendor API"""

    def setUp(self):
        """Set up test environment"""
        super(TestVendorAPI, self).setUp()

        # Create test user
        self.user = new_test_user(
            self.env,
            login='test_user',
            groups='base.group_user',
        )

        # Create test vendor
        self.vendor = self.env['res.partner'].create({
            'name': 'API Test Vendor',
            'email': 'api@test.com',
            'supplier_rank': 1,
        })

    def test_api_vendor_list(self):
        """Test GET vendors list"""
        response = self.url_open('/api/vendors')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('vendors', data)

    def test_api_vendor_get(self):
        """Test GET single vendor"""
        response = self.url_open(f'/api/vendors/{self.vendor.id}')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['name'], 'API Test Vendor')

    def test_api_vendor_create(self):
        """Test POST create vendor"""
        payload = {
            'name': 'New Vendor',
            'email': 'new@vendor.com',
            'phone': '+1234567890',
        }

        response = self.url_open(
            '/api/vendors',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], 'New Vendor')

        # Verify vendor was created in database
        created_vendor = self.env['res.partner'].search([
            ('email', '=', 'new@vendor.com')
        ])
        self.assertTrue(created_vendor)

    def test_api_vendor_update(self):
        """Test PUT update vendor"""
        payload = {
            'name': 'Updated Vendor',
        }

        response = self.url_open(
            f'/api/vendors/{self.vendor.id}',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)

        # Verify update
        self.vendor.invalidate_recordset()
        self.assertEqual(self.vendor.name, 'Updated Vendor')

    def test_api_vendor_delete(self):
        """Test DELETE vendor"""
        vendor_id = self.vendor.id

        response = self.url_open(
            f'/api/vendors/{vendor_id}',
            method='DELETE'
        )

        self.assertEqual(response.status_code, 200)

        # Verify deletion
        deleted_vendor = self.env['res.partner'].browse(vendor_id)
        self.assertFalse(deleted_vendor.exists())

    def test_api_authentication_required(self):
        """Test API requires authentication"""
        # Remove public access
        response = self.url_open('/api/vendors')
        # Should redirect or return 401 depending on auth config
        self.assertIn(response.status_code, [401, 302, 403])

    def test_api_rate_limiting(self):
        """Test API rate limiting"""
        # Make multiple requests
        for i in range(5):
            response = self.url_open('/api/vendors')
            self.assertEqual(response.status_code, 200)

        # Additional requests might be rate limited
        # This depends on rate limiting configuration
```

### 1.3 HttpCase with Browser (E2E Tests)

Untuk testing UI yang lebih kompleks, Odoo menyediakan kemampuan untuk melakukan browser automation menggunakan selenium atau chromium.

```python
# tests/test_portal.py
from odoo.tests import HttpCase, tagged


@tagged('e2e', '-standard')
class TestPortalE2E(HttpCase):
    """End-to-end tests untuk portal"""

    def setUp(self):
        """Set up test environment"""
        super(TestPortalE2E, self).setUp()

        # Create portal user
        self.portal_user = self.env['res.users'].create({
            'login': 'portal_user',
            'name': 'Portal User',
            'email': 'portal@test.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        })

        # Create vendor for portal user
        self.vendor = self.env['res.partner'].create({
            'name': 'Portal Vendor',
            'email': 'portal@test.com',
            'user_ids': [(6, 0, [self.portal_user.id])],
            'supplier_rank': 1,
        })

    def test_portal_vendor_login(self):
        """Test portal vendor can login"""
        # Login as portal user
        self.authenticate('portal_user', 'portal_user')

        # Access portal dashboard
        response = self.url_open('/my')
        self.assertEqual(response.status_code, 200)

    def test_portal_view_invoices(self):
        """Test vendor can view their invoices"""
        # Create invoice for vendor
        invoice = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor.id,
            'invoice_date': fields.Date.today(),
        })

        # Login as portal user
        self.authenticate('portal_user', 'portal_user')

        # Access invoices page
        response = self.url_open('/my/invoices')
        self.assertEqual(response.status_code, 200)

    def test_portal_download_invoice_pdf(self):
        """Test vendor can download invoice PDF"""
        # Create and post invoice
        invoice = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor.id,
            'invoice_date': fields.Date.today(),
        })
        invoice.action_post()

        # Login as portal user
        self.authenticate('portal_user', 'portal_user')

        # Download PDF
        response = self.url_open(f'/my/invoices/{invoice.id}/pdf')
        self.assertEqual(response.status_code, 200)
        self.assertIn('pdf', response.headers.get('Content-Type', ''))


class TestVendorWorkflow(HttpCase):
    """Test complete vendor workflow"""

    def test_vendor_onboarding(self):
        """Test complete vendor onboarding flow"""
        # Start at vendor creation page (requires authentication)
        self.authenticate('admin', 'admin')

        # Create vendor
        response = self.url_open('/web#action=base.action_partner_supplier_form')
        self.assertEqual(response.status_code, 200)

        # This would require actual form submission in a real test
        # Using browser automation for more complex flows
        self.start_tour('/web', 'vendor_onboarding_tour')
```

### 1.4 Portal Tests

Portal tests khusus untuk menguji functionality yang tersedia untuk portal users:

```python
# tests/test_portal_access.py
from odoo.tests import TransactionCase, tagged


@tagged('portal', '-standard')
class TestPortalAccess(TransactionCase):
    """Test portal user access rights"""

    def setUp(self):
        """Set up test data"""
        super(TestPortalAccess, self).setUp()

        # Create portal user
        self.portal_user = self.env['res.users'].create({
            'login': 'portal_vendor',
            'name': 'Portal Vendor',
            'email': 'portal@vendor.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        })

        # Create partner for portal user
        self.partner = self.env['res.partner'].create({
            'name': 'Portal Vendor Partner',
            'email': 'portal@vendor.com',
            'user_ids': [(6, 0, [self.portal_user.id])],
            'supplier_rank': 1,
        })

    def test_portal_can_read_own_records(self):
        """Test portal user can read their own records"""
        # Switch to portal user
        partner = self.partner.with_user(self.portal_user)

        # Should be able to read own partner record
        self.assertTrue(partner.read(['name']))

    def test_portal_cannot_read_others_records(self):
        """Test portal user cannot read other vendor records"""
        # Create another vendor
        other_vendor = self.env['res.partner'].create({
            'name': 'Other Vendor',
            'email': 'other@vendor.com',
            'supplier_rank': 1,
        })

        # Switch to portal user
        vendor = other_vendor.with_user(self.portal_user)

        # Should raise access error
        with self.assertRaises(Exception):
            vendor.read(['name'])

    def test_portal_can_create_invoice(self):
        """Test portal vendor can create purchase invoice"""
        # Switch to portal user
        invoice = self.env['account.move'].with_user(self.portal_user)

        # Should be able to create purchase invoice
        # (depending on portal configuration)
        new_invoice = invoice.create({
            'move_type': 'in_invoice',
            'partner_id': self.partner.id,
            'invoice_date': fields.Date.today(),
        })

        self.assertTrue(new_invoice.id)
```

## Step 2: Analyze Test Structure

### 2.1 Test Files Location

Struktur direktori untuk tests di Odoo:

```
custom_addons/
└── roedl/
    └── vendor_module/
        ├── __init__.py
        ├── __manifest__.py
        ├── models/
        │   ├── __init__.py
        │   └── vendor.py
        ├── views/
        │   └── vendor_views.xml
        └── tests/
            ├── __init__.py
            ├── test_vendor_model.py
            ├── test_vendor_api.py
            └── test_vendor_workflow.py
```

Konfigurasi __init__.py untuk tests:

```python
# tests/__init__.py
from . import test_vendor_model
from . import test_vendor_api
from . import test_vendor_workflow
```

Module yang mendaftarkan tests dalam manifest:

```python
# __manifest__.py
{
    'name': 'Vendor Management',
    'version': '19.0.1',
    'depends': ['base', 'account'],
    'data': [
        # ... other data files
    ],
    'demo': [
        # ... demo data
    ],
    'test': [
        'tests/test_vendor_model.xml',  # XML tests if any
    ],
    'installable': True,
    'application': True,
}
```

### 2.2 Test Classes

Struktur test class yang direkomendasikan:

```python
# tests/test_vendor_model.py
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from odoo.addons.base.tests.common import TransactionCaseWithUserDemo


class TestVendorBase(TransactionCase):
    """Base class untuk vendor tests"""

    def create_test_vendor(self, **vals):
        """Helper method untuk create vendor"""
        defaults = {
            'name': 'Test Vendor',
            'email': 'test@vendor.com',
            'supplier_rank': 1,
        }
        defaults.update(vals)
        return self.env['res.partner'].create(defaults)


class TestVendorCRUD(TestVendorBase):
    """Test CRUD operations"""

    def test_vendor_create(self):
        """Test create vendor"""
        vendor = self.create_test_vendor()
        self.assertTrue(vendor.id)
        self.assertEqual(vendor.name, 'Test Vendor')

    def test_vendor_read(self):
        """Test read vendor"""
        vendor = self.create_test_vendor()
        read_result = vendor.read(['name', 'email'])
        self.assertEqual(read_result[0]['name'], 'Test Vendor')

    def test_vendor_write(self):
        """Test update vendor"""
        vendor = self.create_test_vendor()
        vendor.write({'name': 'Updated Vendor'})
        self.assertEqual(vendor.name, 'Updated Vendor')

    def test_vendor_unlink(self):
        """Test delete vendor"""
        vendor = self.create_test_vendor()
        vendor_id = vendor.id
        vendor.unlink()
        self.assertFalse(self.env['res.partner'].browse(vendor_id).exists())


class TestVendorWithDemoUser(TransactionCaseWithUserDemo):
    """Test dengan demo user"""

    def test_demo_user_can_create_vendor(self):
        """Test demo user can create vendor"""
        vendor = self.env['res.partner'].with_user(self.demo_user).create({
            'name': 'Demo Vendor',
            'supplier_rank': 1,
        })
        self.assertTrue(vendor.id)
```

### 2.3 Test Fixtures

Fixtures digunakan untuk menyediakan data test yang konsisten:

```python
# tests/common.py
from odoo.tests import TransactionCase


class TestVendorCommon(TransactionCase):
    """Common test data dan helpers"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        super(TestVendorCommon, cls).setUpClass()

        # Create test currency
        cls.currency_usd = cls.env.ref('base.USD')

        # Create test company
        cls.company = cls.env['res.company'].create({
            'name': 'Test Company',
            'currency_id': cls.currency_usd.id,
        })

        # Create test vendor
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Test Vendor',
            'email': 'test@vendor.com',
            'supplier_rank': 1,
        })

        # Create test product
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'list_price': 100.00,
        })

        # Create test invoice
        cls.invoice = cls.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': cls.vendor.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.product.id,
                'quantity': 10,
                'price_unit': 100.00,
            })],
        })

    def create_invoice(self, vendor=None, lines=None):
        """Helper untuk create invoice"""
        vendor = vendor or self.vendor
        invoice_data = {
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_date': fields.Date.today(),
        }

        if lines:
            invoice_data['invoice_line_ids'] = lines
        else:
            invoice_data['invoice_line_ids'] = [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': 100.00,
            })]

        return self.env['account.move'].create(invoice_data)
```

### 2.4 Common Test Patterns

Pola-pola umum dalam penulisan test:

```python
# Pattern 1: Test business logic
def test_vendor_discount_calculation(self):
    """Test vendor discount is calculated correctly"""
    # Given
    vendor = self.create_test_vendor(volume_discount=True)
    order = self.create_test_order(vendor=vendor, amount=10000)

    # When
    discount = vendor._calculate_volume_discount(order.amount)

    # Then
    self.assertEqual(discount, 1000)  # 10% discount

# Pattern 2: Test workflow
def test_vendor_approval_workflow(self):
    """Test vendor approval workflow"""
    # Given
    vendor = self.create_test_vendor(state='draft')

    # When
    vendor.action_submit()
    vendor.action_approve()

    # Then
    self.assertEqual(vendor.state, 'approved')

# Pattern 3: Test edge cases
def test_vendor_zero_amount_invoice(self):
    """Test handling of zero amount invoice"""
    invoice = self.create_invoice(amount=0)
    # Should handle gracefully
    self.assertTrue(invoice.id)

# Pattern 4: Test error conditions
def test_vendor_duplicate_reference(self):
    """Test duplicate reference raises error"""
    ref = 'VENDOR-001'
    self.create_test_vendor(ref=ref)

    with self.assertRaises(ValidationError) as ctx:
        self.create_test_vendor(ref=ref)

    self.assertIn('duplicate', str(ctx.exception).lower())
```

## Step 3: Analyze Coverage

### 3.1 Code Coverage Tools

Odoo dapat dikonfigurasi untuk menggunakan coverage tools:

```python
# Konfigurasi pytest untuk coverage
# pytest.ini atau pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = """
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    -v
"""
markers = [
    "standard: standard Odoo tests",
    "e2e: end-to-end tests",
    "api: API tests",
]

[tool.coverage.run]
source = ["models", "controllers", "wizards"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "pass",
    "logging.debug",
]
```

### 3.2 Critical Paths

Fokus pada coverage area kritis:

```python
# tests/test_critical_paths.py

class TestVendorCriticalPaths(TransactionCase):
    """Test critical business paths"""

    def test_01_vendor_creation_to_invoice(self):
        """
        Critical Path: Create vendor -> Create purchase order -> Receive goods -> Create invoice -> Pay
        """
        # 1. Create vendor
        vendor = self.create_test_vendor()
        self.assertTrue(vendor.id)

        # 2. Create purchase order
        po = self.env['purchase.order'].create({
            'partner_id': vendor.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 10,
                'price_unit': 100.00,
            })],
        })
        po.button_confirm()

        # 3. Receive goods
        picking = po.picking_ids[0]
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()

        # 4. Create invoice
        po.action_create_invoice()
        invoice = po.invoice_ids[0]
        invoice.action_post()

        # 5. Register payment
        payment = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=invoice.ids
        ).create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'cash')])[0].id,
        })._create_payments()

        # Verify complete flow
        self.assertEqual(invoice.payment_state, 'paid')

    def test_02_vendor_refund_workflow(self):
        """Test vendor refund workflow"""
        # Create invoice
        invoice = self.create_invoice()
        invoice.action_post()

        # Create credit note
        refund = self.env['account.move'].create({
            'move_type': 'in_refund',
            'partner_id': invoice.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 10,
                'price_unit': 100.00,
            })],
        })
        refund.action_post()

        # Verify
        self.assertEqual(refund.move_type, 'in_refund')

    def test_03_vendor_partial_payment(self):
        """Test partial payment handling"""
        # Create invoice
        invoice = self.create_invoice()
        invoice.action_post()

        # Pay partial
        payment = self.env['account.payment'].create({
            'partner_id': invoice.partner_id.id,
            'amount': 500.00,  # Half of 1000
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')])[0].id,
            'date': fields.Date.today(),
        })
        payment.action_post()

        # Reconcile partially
        (invoice.line_ids + payment.line_ids).filtered(
            lambda l: l.account_id == invoice.account_id
        ).reconcile()

        # Verify partial payment
        self.assertEqual(invoice.amount_residual, 500.00)
```

### 3.3 Edge Cases

Testing edge cases yang sering terlewat:

```python
# tests/test_edge_cases.py

class TestVendorEdgeCases(TransactionCase):
    """Test edge cases"""

    def test_empty_vendor_list(self):
        """Test empty vendor list handling"""
        vendors = self.env['res.partner'].search([('supplier_rank', '>', 0)])
        self.assertEqual(len(vendors), 0)

    def test_vendor_with_special_characters(self):
        """Test vendor name with special characters"""
        vendor = self.create_test_vendor(name="Vendor & Co. <test>")
        self.assertEqual(vendor.name, "Vendor & Co. <test>")

    def test_vendor_very_long_name(self):
        """Test vendor with very long name"""
        long_name = 'A' * 500
        vendor = self.create_test_vendor(name=long_name)
        self.assertEqual(len(vendor.name), 500)

    def test_vendor_unicode_name(self):
        """Test vendor with unicode name"""
        vendor = self.create_test_vendor(name='Vendor GmbH äöü')
        self.assertEqual(vendor.name, 'Vendor GmbH äöü')

    def test_zero_quantity_invoice_line(self):
        """Test invoice line with zero quantity"""
        invoice = self.create_invoice()
        invoice.write({
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 0,
                'price_unit': 100.00,
            })]
        })
        self.assertTrue(invoice.id)

    def test_negative_amount(self):
        """Test negative amount handling"""
        invoice = self.create_invoice()
        with self.assertRaises(ValidationError):
            invoice.write({'invoice_line_ids': [(0, 0, {
                'product_id': self.product.id,
                'quantity': 1,
                'price_unit': -100.00,
            })]})

    def test_future_invoice_date(self):
        """Test invoice with future date"""
        future_date = fields.Date.today() + timedelta(days=30)
        invoice = self.create_invoice()
        invoice.write({'invoice_date': future_date})
        self.assertTrue(invoice.id)

    def test_concurrent_vendor_updates(self):
        """Test concurrent updates to same vendor"""
        # This would require multi-user testing setup
        # Placeholder for concurrent access testing
        pass
```

### 3.4 Regression Prevention

Membangun test yang mencegah regression:

```python
# tests/test_regression_prevention.py
from odoo.tests import TransactionCase


class TestRegressionPrevention(TransactionCase):
    """Regression tests untuk known bugs"""

    def test_regression_001_vendor_deletion_with_invoice(self):
        """
        Regression Test: Vendor with posted invoices should not be deletable
        Bug ID: R-001
        """
        vendor = self.create_test_vendor()
        invoice = self.create_invoice(vendor=vendor)
        invoice.action_post()

        # Vendor has posted invoices
        with self.assertRaises(Exception):
            vendor.unlink()

    def test_regression_002_currency_conversion(self):
        """
        Regression Test: Currency conversion should handle missing rates
        Bug ID: R-002
        """
        # Create vendor with different currency
        vendor = self.create_test_vendor()
        # When currency rate is missing, should handle gracefully
        # This depends on implementation
        self.assertTrue(vendor.id)

    def test_regression_003_mass_mailing_limit(self):
        """
        Regression Test: Mass mailing should respect partner count limit
        Bug ID: R-003
        """
        # Create multiple vendors
        for i in range(150):
            self.create_test_vendor(name=f'Vendor {i}')

        # Should be limited in mass mailing
        vendors = self.env['res.partner'].search([('supplier_rank', '>', 0)])
        self.assertLessEqual(len(vendors), 100)  # Or whatever limit
```

## Step 4: Analyze Test Automation

### 4.1 Pytest Integration

Konfigurasi pytest untuk Odoo:

```python
# conftest.py
import pytest
from odoo.tests import TransactionCase


@pytest.fixture
def api_client():
    """Fixture untuk API testing"""
    # Setup API client
    client = APIClient()
    client.base_url = 'http://localhost:8069'
    return client


@pytest.fixture
def authenticated_client(api_client):
    """Authenticated API client"""
    api_client.authenticate('admin', 'admin')
    return api_client


# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

### 4.2 CI/CD Pipelines

Contoh konfigurasi CI/CD dengan GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Odoo Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: odoo
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Odoo tests
        run: |
          # Start Odoo in background
          python odoo-bin -c odoo.conf -d test_db --stop-after-init &

          # Wait for Odoo to start
          sleep 10

          # Run tests
          python odoo-bin -c odoo.conf -d test_db \
            --test-enable \
            --test-tags=vendor_module \
            --stop-after-init

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Run flake8
        run: |
          pip install flake8
          flake8 models/ tests/ --max-line-length=120

      - name: Run pylint
        run: |
          pip install pylint
          pylint models/ tests/ --disable=all --enable=E
```

### 4.3 Scheduled Tests

Konfigurasi scheduled tests dengan cron:

```python
# models/scheduled_tests.py
from odoo import models, fields, api
from odoo.tools import config


class ScheduledTest(models.Model):
    """Scheduled test configuration"""
    _name = 'scheduled.test'
    _description = 'Scheduled Test Configuration'

    name = fields.Char(required=True)
    test_model = fields.Char(required=True, help='Model to test')
    schedule = fields.Selection([
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ], default='daily')
    active = fields.Boolean(default=True)
    last_run = fields.Datetime(readonly=True)
    last_result = fields.Text(readonly=True)
    last_success = fields.Boolean(readonly=True)

    def run_test(self):
        """Execute scheduled test"""
        self.ensure_one()

        try:
            # Run test
            test_class = self._get_test_class()
            result = test_class().run_test()

            self.write({
                'last_run': fields.Datetime.now(),
                'last_result': 'Success',
                'last_success': True,
            })
        except Exception as e:
            self.write({
                'last_run': fields.Datetime.now(),
                'last_result': str(e),
                'last_success': False,
            })

            # Notify about failure
            self._notify_failure(str(e))

    def _get_test_class(self):
        """Get test class based on model"""
        # Implement dynamic test class selection
        pass

    def _notify_failure(self, error_message):
        """Notify about test failure"""
        # Send notification
        pass
```

### 4.4 Test Reporting

Reporting hasil test:

```python
# models/test_results.py
from odoo import models, fields
import json
import base64


class TestResult(models.Model):
    """Store test results"""
    _name = 'test.result'
    _description = 'Test Result'

    name = fields.Char(required=True)
    test_date = fields.Datetime(default=fields.Datetime.now)
    test_type = fields.Selection([
        ('unit', 'Unit Test'),
        ('integration', 'Integration Test'),
        ('e2e', 'End-to-End Test'),
    ])
    module = fields.Char()
    total_tests = fields.Integer()
    passed = fields.Integer()
    failed = fields.Integer()
    skipped = fields.Integer()
    duration = fields.Float(help='Duration in seconds')
    result_log = fields.Binary('Result Log')
    result_html = fields.Html('HTML Report')

    @api.model
    def create_from_test_result(self, test_data):
        """Create test result from test output"""
        return self.create(test_data)

    def get_summary(self):
        """Get test summary"""
        return {
            'total': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'pass_rate': (self.passed / self.total_tests * 100) if self.total_tests > 0 else 0,
        }
```

## Step 5: Document Testing Strategy

### 5.1 Test Pyramid

Dokumentasi test pyramid:

```markdown
# Testing Strategy - Test Pyramid

## Level Distribution

```
        /\
       /  \      E2E Tests (5-10%)
      /____\
     /      \
    /        \    Integration Tests (20-30%)
   /__________\
  /            \
 /              \  Unit Tests (60-70%)
/________________\
```

## Test Categories

| Level | Type | Coverage | Speed | Examples |
|-------|------|----------|-------|----------|
| Unit | Model logic | Core business rules | Fast (<1s) | Vendor creation, validation |
| Integration | Cross-model | Workflows | Medium (1-10s) | Invoice flow, payments |
| E2E | Full stack | User scenarios | Slow (>10s) | Portal login, ordering |
```

### 5.2 Coverage Goals

Target coverage berdasarkan area:

```markdown
# Coverage Goals

## Minimum Coverage Requirements

| Area | Minimum Coverage |
|------|------------------|
| Models | 80% |
| Business Logic | 90% |
| Wizards | 70% |
| Controllers | 60% |
| Overall | 75% |

## Critical Modules - Enhanced Coverage

| Module | Target Coverage |
|--------|-----------------|
| account | 90% |
| sale | 85% |
| purchase | 85% |
| custom_modules | 80% |
```

### 5.3 Automation Plan

Rencana otomasi testing:

```markdown
# Test Automation Plan

## Phase 1: Foundation (Week 1-2)
- [ ] Setup test environment
- [ ] Configure CI/CD pipeline
- [ ] Create base test classes
- [ ] Write unit tests for core models

## Phase 2: Core Coverage (Week 3-4)
- [ ] Write integration tests for key workflows
- [ ] Add regression tests for known bugs
- [ ] Achieve 60% overall coverage

## Phase 3: Advanced Testing (Week 5-6)
- [ ] Implement E2E tests
- [ ] Add performance tests
- [ ] Setup automated reporting
- [ ] Achieve 75% overall coverage

## Phase 4: Maintenance (Ongoing)
- [ ] Review test results daily
- [ ] Add tests for new features
- [ ] Refactor failing tests
- [ ] Maintain 75%+ coverage
```

### 5.4 Maintenance Plan

Rencana pemeliharaan test suite:

```markdown
# Test Maintenance Plan

## Regular Activities

### Daily
- Review test results from CI/CD
- Fix failing tests within 24 hours

### Weekly
- Review test coverage report
- Identify coverage gaps
- Add tests for new features

### Monthly
- Refactor slow tests
- Remove obsolete tests
- Update test documentation

### Quarterly
- Review test strategy
- Update test pyramid
- Assess automation effectiveness
```

## Output Format

## Testing Strategy

### Test Types

[Summary of recommended test types based on project requirements]

### Coverage Plan

[Detailed coverage targets for each module]

### Automation

[CI/CD setup dan automation plan]

### CI/CD Integration

[Specific CI/CD configuration recommendations]
