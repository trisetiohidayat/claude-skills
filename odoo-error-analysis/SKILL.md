---
name: odoo-error-analysis
description: |
  Systematic error analysis dan root cause identification untuk Odoo. Gunakan skill ini ketika:
  - Error terjadi setelah upgrade module
  - Error tidak jelas sumbernya
  - Perlu analisa mendalam untuk找到 root cause
  - Error di custom modules atau core modules
  - Migration errors

  Fokus pada menemukan MENGAPA error terjadi, bukan hanya APA.
---

# Odoo Error Analysis Skill

## Overview

Skill ini membantu melakukan systematic error analysis untuk menemukan root cause dari error di Odoo. Tujuannya adalah menjelaskan MENGAPA error terjadi, bukan hanya APA.

## Error Analysis Framework

### Step 1: Categorize Error

| Error Type | Indicators | Primary Investigation |
|------------|-----------|----------------------|
| **ImportError** | "No module named X" | Check dependencies, __manifest__.py |
| **AttributeError** | "X has no attribute Y" | Check inheritance, method existence |
| **ValidationError** | User-facing validation | Check constraints, onchanges |
| **AccessError** | "Access denied" | Check ACL, record rules |
| **DatabaseError** | PostgreSQL errors | Check SQL, constraints |
| **RuntimeError** | Python runtime | Trace execution flow |

### Step 2: Gather Information

#### A. Error Message Analysis

```python
# Example error patterns:

# ImportError
"Module 'web' has not been installed"
→ Check: dependencies, __manifest__.py, module state

# AttributeError
"'res.partner' object has no attribute 'sale_count'"
→ Check: field existence, compute method, _depends

# ValidationError
"Error: Customer is required"
→ Check: @api.constrains, required=True

# AccessError
"Access Error: Access rights violation"
→ Check: ir.model.access.csv, record rules
```

#### B. Traceback Analysis

```
Traceback (most recent call last):
  File "/path/to/model.py", line 45, in method
    self.write({'field': value})
  File "/path/to/model.py", line 30, in wrapper
    return original_method(recs, *args, **kwargs)
```

**Analyze:**
- Which file? → `model.py`
- Which line? → line 45
- Which method? → `method`
- What called it? → wrapper (often `super()`)

### Step 3: Identify Root Cause

#### Common Root Causes

| Symptom | Likely Root Cause | How to Fix |
|---------|------------------|------------|
| Missing field | Field not in model, not computed | Add field or check compute |
| Method not found | Not inherited properly | Check _inherit |
| Access denied | ACL not defined | Add ir.model.access.csv |
| Constraint error | Validation failed | Check @api.constrains |
| Upgrade error | Old version not compatible | Migrate code |

### Step 4: Fix Strategy

#### A. Import Errors

```python
# Error: ImportError: No module named 'something'

# Check:
1. Is module in addons_path?
2. Is __init__.py present?
3. Is dependency in __manifest__.py?
4. Is module installed?

# Solution:
- Add to addons_path
- Create __init__.py
- Add to dependencies
- Install module
```

#### B. Attribute Errors

```python
# Error: AttributeError: 'X' object has no attribute 'y'

# Check:
1. Field exists in model?
2. Compute method defined?
3. @api.depends correct?
4. Field loaded in __init__.py?

# Solution:
- Add missing field
- Implement compute method
- Fix @api.depends
- Add to __init__.py
```

#### C. Validation Errors

```python
# Error: ValidationError: message

# Check:
1. Which constraint triggered?
2. What condition failed?
3. Is data valid?

# Solution:
- Fix constraint logic
- Clean invalid data
- Update validation if needed
```

#### D. Access Errors

```python
# Error: Access Error: Access rights violation

# Check:
1. ir.model.access.csv exists?
2. Has correct permissions?
3. Record rule blocking?

# Solution:
- Create/update ACL
- Add correct group
- Fix record rule domain
```

## Systematic Analysis Process

### 1. Reproduce the Error

```python
# Try to reproduce in Odoo shell:
env['model.name'].create({...})

# Or via test:
class TestError(models.TransactionCase):
    def test_error_reproduction(self):
        with self.assertRaises(Exception) as context:
            self.env['model'].some_method()
        print(context.exception)
```

### 2. Trace the Call Stack

```
Where is the error?
    ↓
What called it?
    ↓
What called that?
    ↓
... (until origin)
```

### 3. Check the Chain

#### For Import Errors:
```bash
# Check module structure
ls -la module_name/
# Should have: __init__.py, __manifest__.py

# Check dependencies
grep "depends" __manifest__.py
```

#### For Attribute Errors:
```bash
# Check field exists
grep "field_name" models/*.py

# Check compute method
grep "def _compute_" models/*.py
```

#### For Access Errors:
```bash
# Check ACL
cat security/ir.model.access.csv

# Check record rules
grep -r "ir.rule" security/
```

### 4. Verify Assumptions

```python
# Test each assumption:
# 1. Does field exist?
'field_name' in env['model']._fields

# 2. Does method exist?
hasattr(env['model'], 'method_name')

# 3. Is module installed?
module = env['ir.module.module'].search([('name', '=', 'module_name')])
module.state == 'installed'
```

### 5. Form Hypothesis

| Observation | Hypothesis | Test |
|------------|-----------|------|
| Field missing | Not in model | Check _fields |
| Method error | Not inherited | Check _inherit |
| Access denied | No ACL | Check access.csv |

### 6. Validate & Fix

```python
# After identifying root cause:
# 1. Apply fix
# 2. Test fix
# 3. Document root cause
```

## Error Patterns

### Pattern 1: After Module Upgrade

**Symptoms:**
- Module worked before upgrade
- Error after upgrading

**Analysis:**
1. Check manifest dependencies changed?
2. Check field definitions changed?
3. Check compute methods changed?

**Common Causes:**
- API changes in new version
- Deprecated methods
- Required fields added

### Pattern 2: After Migration

**Symptoms:**
- Error after migrating from Odoo 15 to 19

**Analysis:**
1. Check Python 2 → 3 syntax
2. Check field types
3. Check views compatibility

**Common Causes:**
- String must be bytes or unicode
- XML arch changes
- Field type changes

### Pattern 3: Custom Module Issues

**Symptoms:**
- Error in custom module only

**Analysis:**
1. Check module structure
2. Check inheritance
3. Check dependencies

**Common Causes:**
- Missing __init__.py
- Wrong _inherit
- Missing dependencies

### Pattern 4: Database/ORM Issues

**Symptoms:**
- CRUD operations fail

**Analysis:**
1. Check model definition
2. Check field types
3. Check constraints

**Common Causes:**
- Wrong field type
- Constraint violation
- Locked records

## Root Cause Analysis Template

```
## Error Report

### Error Message
[Paste error message]

### Traceback
[Full traceback]

### Steps to Reproduce
1. ...
2. ...

### Root Cause
[Why did this happen?]

### Fix Applied
[What was changed]

### Verification
[Test results]
```

## Investigation Tools

### 1. Odoo Shell

```bash
./odoo-bin shell -c odoo19.conf -d database
```

```python
# Check model
env['model.name']._fields

# Check methods
dir(env['model.name'])

# Check module state
env['ir.module.module'].search([('name', '=', 'module_name')]).state
```

### 2. Database Queries

```sql
-- Check installed modules
SELECT name, state FROM ir_module_module WHERE name LIKE '%custom%';

-- Check access rights
SELECT * FROM ir_model_access WHERE model_id IN (SELECT id FROM ir_model WHERE model = 'model.name');

-- Check constraints
SELECT * FROM ir_constraint WHERE model IN (SELECT id FROM ir_model WHERE model = 'model.name');
```

### 3. File Analysis

```bash
# Check manifest
cat __manifest__.py

# Check imports
grep "from" *.py | head -20

# Check field definitions
grep "fields\." models/*.py
```

## Confidence Scoring

| Confidence | Criteria | Action |
|------------|----------|--------|
| **90-100%** | Root cause clearly identified | Proceed with fix |
| **70-89%** | Most likely cause identified | Proceed with caution |
| **50-69%** | Possible causes | Need more investigation |
| **< 50%** | Unclear | Request more info |

## Output Format

```json
{
  "error_summary": "Short description",
  "root_cause": "Why it happened",
  "location": "file/module/line",
  "confidence": 85,
  "fix_instructions": "How to fix",
  "verification": "How to verify fix"
}
```

## Related Skills

- `odoo-debug-tdd`: Debug with tests
- `odoo-base-understanding`: Understand code
- `odoo-module-migration`: Migration issues
- `odoo-security-review`: Security-related errors
