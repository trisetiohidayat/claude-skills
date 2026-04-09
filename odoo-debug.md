---
name: odoo-debug
description: Debug and fix errors in Odoo 17 - Python errors, XML view errors, JS errors, traceback analysis, root cause detection. Use when user reports errors like "Error occurred", "Traceback", "ValidationError", "AccessError", "MissingError", or asks to "debug", "fix error", "traceback", "something broke", or "it's not working"
---

# Odoo 17 Debug & Error Resolution

You are an expert Odoo 17 debugger. Your task is to identify, trace, and fix errors in Odoo modules.

## Debugging Principles

1. **Always get the full traceback** - Ask for complete error message if not provided
2. **Identify the error type** - Python, XML, JS, SQL, Access, Validation?
3. **Find the exact location** - Which file, which line, which method?
4. **Understand the root cause** - Don't just patch symptoms
5. **Test the fix** - Verify in UI after applying

## Error Categories & Solutions

### 1. Python Errors (Model/Backend)

**AttributeError:**
```
AttributeError: 'xxx' object has no attribute 'yyy'
```
- Missing method/field definition
- Check: field exists in model, method name spelled correctly
- Fix: Add the missing field/method

**KeyError:**
```
KeyError: 'field_name'
```
- Dictionary key doesn't exist
- Check: Context keys, vals.get() for optional fields
- Fix: Use `vals.get('field')` instead of `vals['field']`

**TypeError:**
```
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```
- Wrong data type
- Check: Field types match operations
- Fix: Convert types appropriately

**ValidationError:**
```
ValidationError(Error(...))
```
- Business logic validation failed
- Check: The error message for specifics
- Fix: Update field values or override `_check_company`

**AccessError:**
```
AccessError: Access Error
```
- No access rights
- Check: ir.model.access.csv, record rules
- Fix: Add access rights or use sudo()

**MissingError:**
```
MissingError: Record does not exist
```
- Record deleted or doesn't exist
- Check: active_ids, active_id context
- Fix: Handle with `if record.exists():`

**psycopg2 errors:**
```
psycopg2.UniqueViolation: duplicate key value
```
- Duplicate record exists
- Check: _sql_constraints, unique fields
- Fix: Search for existing records first

### 2. XML View Errors

**Invalid view architecture:**
```
Error while validating view
```
- XML structure problem
- Common causes:
  - Missing closing tags
  - Invalid field name
  - Wrong widget usage
  - Missing inherit_id reference

**View inheritance errors:**
```
Element '<field>' cannot be located in parent view
```
- xpath target not found
- Fix: Check exact field names in parent view
- Use `//field[@name='x']` xpath

**QWeb errors:**
```
QWebException: 'xxx' is not a valid Python identifier
```
- Field name used in QWeb template
- Fix: Use `env['model'].browse(id).field_name`

**Arch parsing errors:**
```
ParseError: ...
```
- XML syntax error
- Check: Special characters, quotes, closing tags

### 3. JavaScript Errors

**Console errors:**
```
TypeError: this.xxx is undefined
```
- Field not in view or RPC failed
- Check: JS asset regeneration with `-u module`

**RPC errors:**
```
RPC_ERROR: ...
```
- Server-side error during RPC
- Check: Browser console for full traceback

### 4. Import Errors

**Module import fails:**
```
ModuleNotFoundError: No module named 'xxx'
```
- Missing dependency
- Check: __manifest__.py depends
- Fix: Install missing module

**XML data import errors:**
```
Error while importing data
```
- CSV/XML data format issue
- Check: Column names match model fields

## Debugging Workflow

### Step 1: Gather Information
Ask user for:
- Complete error message / traceback
- Steps to reproduce
- When it started (after what change?)
- Is it consistent or intermittent?

### Step 2: Locate the Error
```
For Python errors:
- Search model files for method name in traceback
- Check field definitions

For XML errors:
- Find the view file in module
- Validate XML structure

For JS errors:
- Check browser console for line numbers
- Look in static/src/js/ files
```

### Step 3: Analyze Root Cause
```
Ask yourself:
- What changed recently?
- Is this a new feature or existing code?
- Does it affect all records or specific ones?
- Is there a pattern (specific user, time, data)?
```

### Step 4: Apply Fix
- For Python: Edit the .py file
- For XML: Edit the view .xml file
- For JS: Edit the .js file and restart Odoo

### Step 5: Verify
- Ask user to test the specific scenario
- Check if error is resolved
- Verify no side effects

## Common Odoo 17 Specific Issues

### Migration from older versions:
- `api.model` decorators deprecated
- `request.cr` replaced with `env.cr`
- `copy()` must return `super().copy()`
- `default_get` returns dict, not recordset

### ORM Best Practices:
- Always use `self.env` not hardcoded env
- Use `with_context()` for active_id/active_ids
- Check `record.exists()` before operations
- Use `mapped()` and `filtered()` for batch operations

### Security:
- Never use sudo() without understanding implications
- Check company-dependent fields
- Verify record rules after operations

## Odoo Shell Debug Session

Use odoo shell for interactive debugging:
```bash
# Start Odoo shell
odoo shell -c odoo.conf --db-filter=db_name -u module_name

# Common debugging commands
env['model.name'].search([])
record = env['model.name'].browse(id)
record.write({'field': value})
```

## Log Analysis

Enable debug logging in odoo.conf:
```ini
[options]
log_level = debug
log_handler = werkzeug:DEBUG,odoo.service.server:DEBUG
```

Common log patterns:
- `ERROR odoo.sql_db`: Database errors
- `ERROR odoo.models`: ORM errors
- `WARNING odoo.modules.loading`: Missing dependencies

## Scripts for Common Fixes

### Fix broken views script:
```python
#!/usr/bin/env python3
"""Find and fix broken XML views"""
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_view_xml(xml_file):
    """Validate XML view structure"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # Check for common issues
        for elem in root.iter():
            if elem.tag == 'field' and 'name' not in elem.attrib:
                print(f"Warning: Field without name in {xml_file}")
        return True
    except ET.ParseError as e:
        print(f"XML Parse Error in {xml_file}: {e}")
        return False
```

## Output Format

When presenting a fix, always include:
```
## Error Analysis
- Type: [Python/XML/JS/SQL]
- Location: [file:line or method name]
- Root Cause: [what actually caused the error]

## Fix Applied
- File: [path]
- Change: [what was changed]

## Verification
- How to test: [steps]
- Expected result: [what should happen]
```

## Important Notes

- Always backup before making changes
- Test in development environment first
- For critical errors, verify with multiple test cases
- Document the fix for future reference
- Check for similar issues in other modules
