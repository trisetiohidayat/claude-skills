---
name: odoo-security-review
description: |
  Security review dan checklist untuk Odoo code. Gunakan skill ini ketika:
  - Review code untuk security vulnerabilities
  - Audit custom modules untuk security issues
  - Validasi input sanitization
  - Check access rights implementation
  - Identifikasi potential security risks di Odoo

  Fokus pada OWASP Top 10 untuk web applications dan Odoo-specific security concerns.
---

# Odoo Security Review Skill

## Overview

Skill ini membantu melakukan security review terhadap code Odoo untuk mengidentifikasi potential vulnerabilities dan security issues.

## Security Checklist

### 1. Input Validation

#### ✅ WAJIB: Always Validate Input

| Check | Description | Example |
|-------|-------------|---------|
| **Field Type** | Pastikan field type sesuai input | `fields.Char` untuk text, bukan Integer |
| **Required** | Field yang WAJIB harus ada `required=True` | `name = fields.Char(required=True)` |
| **Constraints** | Gunakan `@api.constrains` untuk validasi kompleks | Validasi email, phone, dll |
| **Size Limits** | Batasi panjang input | `size=255` untuk Char |

#### ❌ DILARANG

```python
# SALAH - Tidak ada validasi
def set_name(self, name):
    self.name = name  # Langsung assign tanpa validasi

# BENAR - Dengan validasi
@api.constrains('name')
def _check_name(self):
    for rec in self:
        if not rec.name or len(rec.name) < 3:
            raise ValidationError("Name must be at least 3 characters")
```

### 2. SQL Injection Prevention

#### ✅ WAJIB: Use ORM Instead of Raw SQL

| Pattern | Safe | Unsafe |
|---------|------|--------|
| **Search** | `self.env['model'].search([('name', '=', name)])` | `self.env.cr.execute(f"SELECT * FROM model WHERE name = '{name}'")` |
| **Write** | `record.write({'field': value})` | `self.env.cr.execute(f"UPDATE model SET field = '{value}'")` |
| **Read** | `self.env['model'].browse(ids).read(fields)` | Raw SQL |

#### ❌ DILARANG - Never Do This

```python
# SALAH - SQL Injection vulnerable
def search_by_name(self, name):
    query = f"SELECT id FROM {self._table} WHERE name = '{name}'"
    self.env.cr.execute(query)

# BENAR - Using ORM
def search_by_name(self, name):
    return self.search([('name', '=', name)])
```

#### ⚠️ If Raw SQL Required

```python
# Only if absolutely necessary - use parameterized query
def search_by_name(self, name):
    query = "SELECT id FROM %s WHERE name = %%s" % self._table
    self.env.cr.execute(query, (name,))
```

### 3. Access Control (ACL)

#### ✅ WAJIB: Implement Proper Access Rights

| File | Purpose | Example |
|------|---------|---------|
| `security/ir.model.access.csv` | Define access rights | |
| `security/res_groups.xml` | Define groups | |
| `models/res_groups.py` | Group inheritance | |

#### Access Control Checklist

- [ ] Setiap model punya `ir.model.access.csv`
- [ ] Setiap field sensitive punya access rule
- [ ] Override `check_access_rights()` jika perlu
- [ ] Override `check_access_rule()` untuk custom logic
- [ ] Gunakan `sudo()` hanya jika perlu dan aman

#### ❌ DILARANG

```python
# SALAH - Elevation of Privilege
def get_all_records(self):
    # Tanpa check access
    return self.env['secret.model'].sudo().search([])

# BENAR - Dengan access check
def get_all_records(self):
    self.check_access_rights('read')
    return self.search([])
```

### 4. XSS Prevention

#### ✅ WAJIB: Sanitize User Input

| Context | Protection |
|---------|------------|
| **QWeb Views** | Gunakan `esc()` untuk escape |
| **Email Templates** | Gunakan `html_escape()` |
| **JSON Fields** | Validasi JSON structure |

#### ❌ DILARANG

```python
# SALAH - XSS vulnerable
@api.depends('description')
def _compute_html(self):
    for rec in self:
        rec.html_description = "<script>alert('xss')</script>" + rec.description

# BENAR - With sanitization
import html
@api.depends('description')
def _compute_html(self):
    for rec in self:
        rec.html_description = html.escape(rec.description or '')
```

### 5. File Upload Security

#### ✅ WAJIB: Validate File Uploads

```python
# BENAR - Validate file
@api.constrains('attachment')
def _check_attachment(self):
    for rec in self:
        if rec.attachment:
            # Check file extension
            allowed_ext = ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx']
            ext = os.path.splitext(rec.attachment.filename)[1].lower()
            if ext not in allowed_ext:
                raise ValidationError(f"Extension {ext} not allowed")

            # Check file size (max 10MB)
            if rec.attachment.file_size > 10 * 1024 * 1024:
                raise ValidationError("File size exceeds 10MB limit")
```

#### ❌ DILARANG

```python
# SALAH - No validation
def upload_file(self, file):
    file.save('/path/to/uploads/' + file.filename)  # Path traversal vulnerable
```

### 6. Authentication & Password

#### ✅ WAJIB: Secure Password Handling

```python
# BENAR - Use Odoo's password hashing
from odoo.addons.base.models.res_users import check_password

def set_password(self, password):
    # Odoo automatically hashes password
    self.write({'password': password})

# BENAR - Verify password
def verify_password(self, password):
    return self.env['res.users'].sudo()._check_password(password)
```

#### ❌ DILARANG

```python
# SALAH - Store plain password
def save_password(self, password):
    self.write({'password': password})  # Already hashed by Odoo - good!
    # But don't do:
    # self.write({'password_clear': password})  # NEVER store plain password
```

### 7. CSRF Protection

#### ✅ WAJIB: Use CSRF Tokens

```python
# In controllers
from odoo import http

class MyController(http.Controller):
    @http.route('/my/form', type='http', auth='user', csrf=True)
    def submit_form(self, **post):
        # CSRF token automatically validated
        pass
```

### 8. XML Security (View Inheritance)

#### ✅ WAJIB: Secure View Modifications

```python
# BENAR - Use position attributes safely
<field name="description" position="after">
    <field name="new_field"/>
</field>

# HATI-HATI dengan position="replace" - bisa break existing UI
```

### 9. Record Rules

#### ✅ WAJIB: Define Record Rules

```xml
<!-- security/ir.rule.xml -->
<record id="rule_own_records" model="ir.rule">
    <field name="name">Own Records Only</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="groups" eval="[(4, ref('group_user'))]"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

### 10. API Security

#### ✅ WAJIB: Secure External API

```python
# BENAR - Validate API keys
class ExternalAPI(http.Controller):
    @http.route('/api/data', type='json', auth='api_key', methods=['POST'])
    def get_data(self, **kwargs):
        # Check API key
        api_key = http.request.httprequest.headers.get('X-API-Key')
        if not self._validate_api_key(api_key):
            return {'error': 'Invalid API key'}

        # Process request
        return {'data': '...'}

    def _validate_api_key(self, key):
        # Validate against stored keys
        return self.env['api.key'].search([('key', '=', key)])
```

## Common Vulnerabilities in Odoo

| Vulnerability | Description | Prevention |
|---------------|-------------|------------|
| **SQL Injection** | Raw SQL with user input | Use ORM |
| **XSS** | Unsanitized output in views | Use `html.escape()` |
| **IDOR** | Access other user's data | Check access rights |
| **CSRF** | Cross-site request forgery | Use CSRF tokens |
| **Path Traversal** | Access unauthorized files | Validate file paths |
| **Broken Auth** | Weak password handling | Use Odoo's auth |
| **Sensitive Data Exposure** | Expose confidential data | Use access rules |

## Security Review Workflow

### Step 1: Identify Entry Points

```python
# Check these in your module:
# 1. Public controllers (auth='public')
# 2. API endpoints
# 3. Imported files
# 4. User input fields
```

### Step 2: Analyze Data Flow

```python
# Trace data from input to storage:
# 1. User input → Controller → Model
# 2. Model → Database
# 3. Database → View
```

### Step 3: Check Each Layer

| Layer | Checks |
|-------|--------|
| **Controller** | CSRF, auth, input validation |
| **Model** | Access rights, constraints, onchanges |
| **View** | XSS, field security |

### Step 4: Test Cases

```python
# Example security tests
def test_sql_injection_name(self):
    """Test SQL injection in name field"""
    with self.assertRaises(Exception):
        self.model.create({'name': "'; DROP TABLE res_users;--"})

def test_xss_in_description(self):
    """Test XSS in description"""
    record = self.model.create({'description': '<script>alert(1)</script>'})
    # Should be escaped when displayed
    assert '<script>' not in html_from_view

def test_unauthorized_access(self):
    """Test unauthorized access to records"""
    user2 = self.env['res.users'].create({...})
    with self.assertRaises(AccessError):
        user2.env['model'].search([])
```

## Quick Security Checklist

Before deploying a module, ensure:

- [ ] No raw SQL queries with user input
- [ ] All user inputs validated
- [ ] Access rights defined for all models
- [ ] Record rules for multi-user access
- [ ] Passwords handled via Odoo's mechanism
- [ ] File uploads validated (extension, size)
- [ ] XSS prevention in QWeb views
- [ ] CSRF enabled on controllers
- [ ] Sensitive data protected
- [ ] API endpoints authenticated

## Related Skills

- `odoo-debug-tdd`: For security-focused debugging
- `odoo-model-inherit`: For secure inheritance patterns
