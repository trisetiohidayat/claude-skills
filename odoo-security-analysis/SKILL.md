---
name: odoo-security-analysis
description: |
  Analisis keamanan Odoo - ACL, record rules, XSS, SQL injection, access control,
  CSRF protection, data sanitization. Gunakan ketika:
  - User bertanya tentang security issues
  - Ingin review access control
  - Need to audit security
  - Ingin detect vulnerabilities
---

# Odoo Security Analysis Skill

## Overview

Skill ini membantu menganalisis dan mengoptimalkan keamanan aplikasi Odoo. Keamanan adalah aspek kritis dalam pengembangan aplikasi enterprise, dan Odoo menyediakan berbagai mekanisme keamanan yang harus dipahami dengan baik.

## When to Use This Skill

Gunakan skill ini ketika:
- User bertanya tentang security issues di Odoo
- Ingin melakukan security audit
- Need to review access control configuration
- Need to detect vulnerabilities
- Ingin implement security best practices
- Perlu validate module security

## Step 1: Analyze Access Control

### Understanding Access Control List (ACL)

Access Control List di Odoo mengontrol siapa yang dapat membaca, menulis, membuat, atau menghapus record. ACL didefinisikan dalam file `ir.model.access.csv`.

### ACL File Structure

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

### ACL Components

| Field | Description |
|-------|-------------|
| id | Unique identifier |
| name | Descriptive name |
| model_id:id | Reference ke model |
| group_id:id | Group yang diberi akses |
| perm_read | Read permission (1/0) |
| perm_write | Write permission (1/0) |
| perm_create | Create permission (1/0) |
| perm_unlink | Delete permission (1/0) |

### Analyzing ACL Issues

```python
# Check ACL untuk sebuah model
def check_acl(self, model_name):
    access = self.env['ir.model.access'].search([
        ('model_id.model', '=', model_name)
    ])
    for acc in access:
        print(f"Group: {acc.group_id.name}")
        print(f"  Read: {acc.perm_read}")
        print(f"  Write: {acc.perm_write}")
        print(f"  Create: {acc.perm_create}")
        print(f"  Unlink: {acc.perm_unlink}")
```

### Common ACL Mistakes

```csv
# BAD: Missing ACL - tidak ada yang bisa akses
# Kosong / tidak ada file access

# BAD: Overly permissive
access_my_model_all,my.model.all,model_my_model,,1,1,1,1
# Tanpa group = semua orang termasuk public!

# GOOD: Proper ACL
access_my_model_user,my.model.user,model_my_model,base.group_user,1,0,0,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

### Model Access Configuration

```python
# Konfigurasi default permissions di model
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    # Default: semua orang bisa baca, hanya admin bisa write
    _inherit = ['mail.thread']
    _mail_post_access = 'read'  # Siapa yang bisa post comment

# Konfigurasi khusus untuk private models
class PrivateModel(models.Model):
    _name = 'private.model'
    _description = 'Private Model'

    # Private model - perlu explicit ACL
    _auto_access = False  # Disable automatic access
```

## Step 2: Analyze Record Rules

### Understanding Record Rules

Record rules menyediakan keamanan tingkat record - mengontrol subset mana dari record yang bisa diakses oleh user tertentu.

### Record Rule Syntax

```xml
<record id="rule_my_model_user" model="ir.rule">
    <field name="name">My Model: multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Record Rule Components

| Component | Description |
|-----------|-------------|
| name | Descriptive name |
| model_id | Reference ke model |
| domain_force | Domain untuk filter records |
| groups | Group yang rule applies ke |
| perm_read, perm_write, etc. | Specific permissions |

### Analyzing Record Rules

```python
# Check record rules untuk model
def check_record_rules(self, model_name):
    model_id = self.env['ir.model'].search([
        ('model', '=', model_name)
    ])

    rules = self.env['ir.rule'].search([
        ('model_id', '=', model_id.id)
    ])

    for rule in rules:
        print(f"Rule: {rule.name}")
        print(f"  Groups: {rule.groups.mapped('name')}")
        print(f"  Domain: {rule.domain_force}")
        print(f"  Global: {rule.global_rule}")
```

### Common Record Rule Patterns

```python
# Pattern 1: Company-based multi-company
# Records hanya bisa diakses oleh user di company yang sama
domain_force = "[('company_id', 'in', company_ids)]"

# Pattern 2: Owner-based
# User hanya bisa akses record yang mereka buat
domain_force = "[('user_id', '=', user.id)]"

# Pattern 3: Department-based
# User hanya bisa akses record di department mereka
domain_force = "[('department_id', 'in', user.employee_ids.department_id.ids)]"

# Pattern 4: Partner-based
# Partner hanya bisa akses data mereka sendiri
domain_force = "[('partner_id', '=', user.partner_id.id)]"

# Pattern 5: Group-based visibility
# Group tertentu hanya bisa lihat certain records
domain_force = "[('state', 'in', ['done', 'approved'])]"
```

### Record Rule Debugging

```python
# Debug: See what records a user can see
def debug_record_rules(self, user_id, model_name):
    user = self.env['res.users'].browse(user_id)
    model = self.env[model_name]

    # Get effective domain
    domain = model._compute_domain(model_name, 'read')

    # Count accessible records
    accessible = model.search(domain)
    print(f"User {user.name} can see {len(accessible)} of {model.search_count([])} records")
```

## Step 3: Detect Vulnerabilities

### Common Vulnerability Types

#### 1. SQL Injection

SQL injection terjadi ketika user input digunakan langsung dalam query tanpa sanitasi yang tepat.

```python
# VULNERABLE: Direct string concatenation
def search_vulnerable(self, search_term):
    query = f"SELECT * FROM my_model WHERE name LIKE '%{search_term}%'"
    self.env.cr.execute(query)  # DANGER!

# SAFE: Using parameterized queries
def search_safe(self, search_term):
    self.env.cr.execute(
        "SELECT * FROM my_model WHERE name LIKE %s",
        (f'%{search_term}%',)
    )

# SAFE: Using Odoo ORM
def search_orm(self, search_term):
    return self.search([('name', 'ilike', search_term)])
```

#### 2. Cross-Site Scripting (XSS)

XSS terjadi ketika user input ditampilkan tanpa sanitasi.

```python
# VULNERABLE: Raw HTML insertion
def set_description(self, description):
    # Tidak ada sanitasi
    self.description = description

# SAFE: Using sanitized HTML
from odoo import tools
def set_description(self, description):
    self.description = tools.html_sanitize(description)

# Di XML views, gunakan sanitized fields
<field name="description" widget="html" options="{'sanitize': True}"/>
```

#### 3. Code Injection (eval/exec)

```python
# VULNERABLE: Using eval with user input
def execute_code(self, code_string):
    result = eval(code_string)  # DANGER!

# VULNERABLE: Using exec with user input
def execute_command(self, command):
    exec(f"print('{command}')")  # DANGER!

# SAFE: Restrictive execution
# Jika benar-benar perlu, gunakan AST dengan restricted globals
import ast
def safe_eval(expr):
    # Whitelist allowed operations
    allowed_names = {
        'sum': sum,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
    }
    return eval(expr, {"__builtins__": {}}, allowed_names)
```

#### 4. Path Traversal

```python
# VULNERABLE: Direct path from user input
def read_file(self, filename):
    path = f"/tmp/uploads/{filename}"
    with open(path) as f:  # Bisa jadi /etc/passwd
        return f.read()

# SAFE: Validate and sanitize path
import os
from pathlib import Path

def safe_read_file(self, filename):
    # Only allow alphanumeric and safe chars
    if not all(c.isalnum() or c in '-_' for c in filename):
        raise ValueError("Invalid filename")

    base = Path("/tmp/uploads").resolve()
    path = (base / filename).resolve()

    # Ensure path is within base directory
    if not path.is_relative_to(base):
        raise ValueError("Path traversal detected")

    return path.read_text()
```

#### 5. Insecure Direct Object Reference (IDOR)

```python
# VULNERABLE: No ownership check
def delete_record(self, record_id):
    record = self.env['my.model'].browse(record_id)
    record.unlink()  # Siapa saja bisa hapus!

# SAFE: Check ownership
def delete_record(self, record_id):
    record = self.env['my.model'].browse(record_id)
    if record.create_uid != self.env.user:
        raise AccessError("Cannot delete others' records")
    record.unlink()

# SAFE: Using record rules
# Record rules akan secara otomatis memfilter
def delete_record(self, record_id):
    # akan menggunakan record rules
    record = self.env['my.model'].browse(record_id)
    if record:
        record.unlink()
```

### Web Controller Security

```python
# Secure controller implementation
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/secure_endpoint', type='json', auth='user')
    def secure_endpoint(self):
        # auth='user' ensures user is logged in
        # request.env.user gives current user
        return {
            'user': request.env.user.name,
            'company': request.env.company.name,
        }

    @http.route('/my/secure_form', type='http', auth='user',
                csrf=True, website=True)
    def submit_form(self, **post):
        # CSRF protection enabled
        # Authenticated user only
        return request.render('my_module.thank_you')

    # Prevent CSRF on forms without website
    @http.route('/my/api/endpoint', type='json', auth='user',
                csrf=False, cors='*')
    def api_endpoint(self):
        # CSRF disabled for API - but use token auth
        return {'status': 'ok'}
```

### Model Method Security

```python
class MyModel(models.Model):
    _name = 'my.model'

    # Force access rights check
    @api.model
    def _compute_domain(self, name, op):
        # This will respect record rules
        return super()._compute_domain(name, op)

    # Check access before operations
    def unlink(self):
        # Manual access check
        for record in self:
            if not record._check_access('unlink'):
                raise AccessError('Cannot delete')
        return super().unlink()

    def _check_access(self, operation):
        try:
            self.check_access_rights(operation)
            self.check_access_rule(operation)
            return True
        except:
            return False
```

## Step 4: Audit Security

### Security Checklist

- [ ] ACL defined untuk semua models
- [ ] Record rules untuk sensitive data
- [ ] Input sanitization untuk user inputs
- [ ] CSRF protection enabled
- [ ] Password policies enforced
- [ ] Session management configured
- [ ] API authentication required
- [ ] No eval/exec dengan user input
- [ ] No SQL injection vulnerabilities
- [ ] XSS protection in place

### Password Policy Implementation

```python
# Implement password policy di res.users
from odoo import models, fields, api
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _check_password_policy(self, password):
        # Minimum length
        if len(password) < 8:
            return False

        # Require uppercase
        if not any(c.isupper() for c in password):
            return False

        # Require lowercase
        if not any(c.islower() for c in password):
            return False

        # Require digit
        if not any(c.isdigit() for c in password):
            return False

        # Require special character
        if not any(c in '!@#$%^&*()' for c in password):
            return False

        return True

    def write(self, vals):
        if 'password' in vals:
            if not self._check_password_policy(vals['password']):
                raise UserError(
                    'Password must be at least 8 characters and contain '
                    'uppercase, lowercase, digit, and special character'
                )
        return super().write(vals)
```

### Session Management

```python
# Konfigurasi session di odoo.conf
# [session]
# timeout = 3600  # 1 hour
# max_count = 100  # Max sessions per user

# Session security di controller
class SecureController(http.Controller):

    @http.route('/secure/action', type='json', auth='user')
    def secure_action(self):
        # Check session validity
        if not request.session.check_security():
            raise http.SessionExpiredException("Session expired")

        # Continue with action
        return {'status': 'ok'}
```

### API Authentication

```python
# Require authentication untuk API
class ApiController(http.Controller):

    # Auth dengan api key
    @http.route('/api/data', type='json', auth='api_key')
    def get_data(self):
        # API key authentication
        return {'data': 'secret'}

    # Auth dengan JWT
    @http.route('/api/jwt_data', type='json', auth='jwt')
    def jwt_data(self):
        # JWT token authentication
        return {'data': 'jwt_secret'}

    # Multi-auth
    @http.route('/api/multi', type='json', auth='public')
    def multi_auth(self):
        if not request.env.user:
            # Require login untuk certain operations
            raise AccessError("Authentication required")
```

### Audit Logging

```python
# Track sensitive operations
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Enable tracking untuk sensitive fields
    name = fields.Char(track_visibility='always')
    amount = fields.Float(track_visibility='always')
    state = fields.Selection(track_visibility='always')

    # Log semua akses
    def read(self, fields=None):
        # Log who accessed what
        for record in self:
            self.env['audit.log'].create({
                'user_id': self.env.uid,
                'model': self._name,
                'record_id': record.id,
                'action': 'read',
                'fields': fields,
            })
        return super().read(fields)

    def unlink(self):
        # Log deletion
        for record in self:
            self.env['audit.log'].create({
                'user_id': self.env.uid,
                'model': self._name,
                'record_id': record.id,
                'action': 'unlink',
            })
        return super().unlink()
```

## Security Best Practices

### Model Development

```python
# 1. Always use ORM methods
# BAD
self.env.cr.execute(f"DELETE FROM {self._table} WHERE id IN {ids}")

# GOOD
self.browse(ids).unlink()

# 2. Validate inputs
from odoo.osv import expression
from odoo.tools import float_compare

def write(self, vals):
    if 'amount' in vals:
        if vals['amount'] < 0:
            raise UserError("Amount cannot be negative")
    return super().write(vals)

# 3. Use constrained fields
amount = fields.Float(required=True)  # Force validation
unique_field = fields.Char(required=True)  # Force validation

# 4. Implement security in methods
def _ensure_not_cancelled(self):
    if self.state == 'cancel':
        raise AccessError("Cannot modify cancelled record")
```

### View Security

```xml
<!-- Hide sensitive fields based on group -->
<field name="salary" groups="base.group_hr_manager"/>
<field name="internal_notes" groups="base.group_system"/>

<!-- Prevent editing certain fields -->
<field name="state" readonly="1"/>

<!-- Use accessb64 untuk sensitive data -->
<field name="password" password="True"/>
```

### Data Migration Security

```python
# Secure data migration
def migrate_sensitive_data(self):
    # Encrypt sensitive data
    from odoo.addons.base.models import ir_config_parameter

    # Get encryption key dari secure config
    key = ir_config_parameter.get_param('encryption.key')

    # Encrypt
    for record in self:
        if record.sensitive_data:
            encrypted = self._encrypt(record.sensitive_data, key)
            record.sensitive_data = encrypted
```

## Common Security Issues and Solutions

### Issue 1: Public Access to Sensitive Data

```
Symptoms: Anonymous users can access private data
Root Cause: Missing auth on controller, wrong ACL
Solution:
- Add auth='user' to controllers
- Add proper ACL for sensitive models
- Add record rules untuk private data
```

### Issue 2: Privilege Escalation

```
Symptoms: Regular users can perform admin actions
Root Cause: Missing access checks, sudo() abuse
Solution:
- Use _check_access() methods
- Remove unnecessary sudo()
- Implement proper groups
```

### Issue 3: Data Leakage

```
Symptoms: Users can see other companies' data
Root Cause: Missing multi-company rules
Solution:
- Add company-dependent record rules
- Validate company_id on write
- Use company-dependent domains
```

### Issue 4: CSRF Vulnerabilities

```
Symptoms: Form submissions from external sites work
Root Cause: CSRF disabled atau misconfigured
Solution:
- Keep csrf=True (default)
- Use @http.route dengan proper auth
- Implement tokens untuk state-changing operations
```

## Security Testing

### Automated Testing

```python
# Test access rights
class TestAccessRights(unittest.TestCase):

    def test_unauthorized_read(self):
        """Test user cannot read without permission"""
        with self.assertRaises(AccessError):
            self.model.with_user(self.user_unauthorized).read([])

    def test_unauthorized_write(self):
        """Test user cannot write without permission"""
        with self.assertRaises(AccessError):
            self.model.with_user(self.user_unauthorized).write({
                'name': 'Hacked'
            })

    def test_record_rule_filtering(self):
        """Test record rules properly filter records"""
        user = self.user_regular
        records = self.model.with_user(user).search([])
        for record in records:
            self.assertIn(user.company_id, record.company_ids)
```

### Manual Testing Checklist

- [ ] Test dengan tidak ada user login
- [ ] Test dengan different user roles
- [ ] Test dengan different companies
- [ ] Test direct database access
- [ ] Test API endpoints
- [ ] Test file uploads
- [ ] Test email injections
- [ ] Test XSS payloads
- [ ] Test SQL injection payloads

## Output Format

 Ketika menggunakan skill ini, berikan output dengan format berikut:

## Security Analysis

### Vulnerabilities Found
1. **[Critical/High/Medium/Low]**: [Vulnerability Type] - [Location]
2. **[Critical/High/Medium/Low]**: [Vulnerability Type] - [Location]

### Risk Assessment
- Critical: Immediate action required
- High: Fix within sprint
- Medium: Plan for fix
- Low: Consider fixing

### Recommendations
1. [Recommendation 1] - [Impact]
2. [Recommendation 2] - [Impact]
3. [Recommendation 3] - [Impact]

### Security Checklist
- [ ] ACL reviewed
- [ ] Record rules verified
- [ ] Input sanitization added
- [ ] CSRF protection enabled
- [ ] Password policy implemented
- [ ] Audit logging added

### Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Notes

- Always follow principle of least privilege
- Regular security audits are essential
- Keep Odoo and modules updated
- Monitor for security advisories
- Implement defense in depth
