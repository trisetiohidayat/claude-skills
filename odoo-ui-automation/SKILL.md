---
name: odoo-ui-automation
description: |
  Gunakan ketika user meminta AI untuk OPERASIKAN ODOO secara langsung melalui web UI (bukan via DB/XML-RPC).
  Contoh: "buatkan produk baru di Odoo", "edit data karyawan", "klik tombol confirm", "submit form", dll.

  SKILL INI SANGAT PENTING karena:
  - Berbeda dengan XML-RPC yang bypass UI, skill ini menangkap ERROR VALIDATION, WARNING, dan UX issues
  - Action dilakukan seperti USER sungguhan (browser automation via Playwright)
  - Error Odoo (validation, access rights, constraint) akan muncul dan bisa dilaporkan ke user
  - Cocok untuk: create record, edit form, klik button, navigasi menu, submit wizard

  Trigger phrases:
  - "buatkan produk di Odoo"
  - "edit user di Odoo"
  - "klik tombol approve"
  - "submit purchase request"
  - "buat sales order"
  - "import data ke Odoo"
  - "update product price"
  - "delete record"
  - "cari product di Odoo"
  - " buka form purchase request"
  - dll (semua operasi yang melibatkan interaksi Odoo UI)

  JANGAN gunakan skill ini untuk:
  - Query/Read data saja (bisa pakai XML-RPC atau DB langsung)
  - Install/upgrade module
  - Debug code

  Dependency: WAJIB load odoo-path-resolver duluan untuk get environment info.
---

# Odoo UI Automation via Playwright

## Overview

Skill ini automating Odoo UI menggunakan Playwright CLI. Alih-alih insert DB langsung atau XML-RPC, kita menggunakan browser automation yang:
- **Meniru aksi user sungguhan** - click, fill form, submit
- **Menangkap error Odoo** - validation error, access denied, constraint violation
- **Memberikan feedback real-time** - seperti user melihat di browser

## Prerequisites

1. **Load odoo-path-resolver** - untuk get environment (port, db, odoo-bin)
2. **Playwright installed** - `pip install playwright && playwright install chromium`
3. **Odoo running** - pastikan instance Odoo aktif
4. **Credentials** - user/password untuk login (base64 encoded untuk keamanan)

## Step-by-Step Workflow

### Step 0: Load Environment

```python
# Invoke odoo-path-resolver skill duluan
paths = resolve()

# Environment yang diperlukan:
# - http_port: port Odoo (misal 8201)
# - db_name: nama database
# - python: path ke Python venv
# - odoo_bin: path ke odoo-bin
```

### Step 1: Get/Validate Credentials

Credentials harus di-request dari user. Format:

```json
{
  "login": "base64_encoded_login",
  "password": "base64_encoded_password"
}
```

**Jangan hardcode credentials.** Request dari user sebelum memulai automation.

Untuk decode (di script):
```bash
echo "base64_string" | base64 -d
```

### Step 2: Determine Odoo Action

Analisa request user untuk tentukan:

| User says | Odoo Action | URL Pattern |
|-----------|-------------|-------------|
| "buatkan produk" | Create Product | /web#menu_id=&action=product.product_action |
| "edit purchase request" | Edit Record | /web#model=purchase.request&id=XXX |
| "klik approve" | Click Button | Submit form + button click |
| "delete product" | Delete Record | Form view → Action → Delete |
| "import data" | Import Wizard | /web#model=XXX&view_type=list |

### Step 3: Build Playwright Script

**Script Template:**

```python
#!/usr/bin/env python3
"""
Odoo UI Automation via Playwright
Generated for: {action_description}
"""

import asyncio
import base64
import sys
from playwright.async_api import async_playwright

ODOO_URL = "http://localhost:{port}"
DB_NAME = "{database}"

async def login(page, login_str, password_str):
    """Login ke Odoo"""
    await page.goto(f"{ODOO_URL}/web/login")
    await page.fill('input[name="login"]', base64.b64decode(login_str).decode())
    await page.fill('input[name="password"]', base64.b64decode(password_str).decode())
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")

async def navigate_to_model(page, model_name, action=None):
    """Navigate ke model tertentu"""
    # Menggunakan menu search
    await page.click('button[data-menu-toggle="all"]')
    await page.fill('.o_searchview_input', model_name)
    await page.wait_for_timeout(1000)

    # Klik result
    await page.click('.o_search_result')

async def create_record(page, model, data):
    """Buat record baru"""
    # Navigate ke model
    await navigate_to_model(page, model)

    # Klik Create
    await page.click('button.o_list_button_add')
    await page.wait_for_load_state("networkidle")

    # Fill form fields
    for field, value in data.items():
        # Handle different field types
        selector = f'[name="{field}"]'
        await page.fill(selector, str(value))

    # Klik Save
    await page.click('button.o_form_button_save')
    await page.wait_for_load_state("networkidle")

    # Cek apakah ada error
    error_selector = '.o_notification.error, .o_error_message, .alert-danger'
    error_element = await page.query_selector(error_selector)
    if error_element:
        error_text = await error_element.inner_text()
        return {"success": False, "error": error_text}

    return {"success": True, "message": "Record created successfully"}

async def main(credentials, action, params):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login
        await login(page, credentials['login'], credentials['password'])

        # Execute action
        if action == 'create':
            result = await create_record(page, params['model'], params['data'])
        # ... handle other actions

        await browser.close()
        return result

if __name__ == "__main__":
    # Parse args
    # Execute automation
```

### Step 4: Execute dan Report

```bash
# Run automation script
{python_path} {script_path} --login {encoded_login} --password {encoded_password} --action {action}

# Parse output
# Report ke user
```

### Step 5: Handle Errors

**Common Odoo UI Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "Access Denied" | User tidak punya permission | Request access atau pakai user lain |
| "Validation Error" | Data tidak valid | Baca error message, fix data |
| "Required field" | Field wajib kosong | Fill required fields |
| "Constraint violation" | Data duplicate/conflict | Check existing data |
| "Network error" | Odoo tidak responsif | Check Odoo status |

**Error Detection Pattern:**
```python
# Cek notification error
error = await page.query_selector('.o_notification.error')
if error:
    return await error.inner_text()

# Cek inline error
inline_error = await page.query_selector('.o_field_invalid')
if inline_error:
    return f"Invalid field: {await inline_error.get_attribute('name')}"
```

## Script Location

Simpan automation scripts di `scripts/` directory:

```
odoo-ui-automation/
├── SKILL.md
└── scripts/
    ├── automation_runner.py    # Main runner
    ├── odoo_actions.py         # Action templates
    └── helpers.py             # Utility functions
```

## Action Templates

### 1. Create Record

```python
async def create_record(page, model, fields_data):
    # Navigate
    await page.goto(f"{ODOO_URL}/web#menu_id=&action=XXX")

    # Click Create
    await page.click('button[data-type="action"]' or '.o_list_button_add')

    # Wait form load
    await page.wait_for_selector('.o_form_view', state='visible')

    # Fill fields
    for name, value in fields_data.items():
        selector = f'[name="{name}"]'
        await page.fill(selector, value)

    # Save
    await page.click('button.o_form_button_save')

    # Wait for save completion
    await page.wait_for_load_state('networkidle', timeout=10000)
```

### 2. Edit Record

```python
async def edit_record(page, model, record_id, fields_data):
    # Open record
    await page.goto(f"{ODOO_URL}/web#model={model}&id={record_id}&view_type=form")

    await page.wait_for_selector('.o_form_view', state='visible')

    # Edit fields
    for name, value in fields_data.items():
        selector = f'[name="{name}"]'
        await page.fill(selector, value)

    # Save
    await page.click('button.o_form_button_save')
```

### 3. Click Button/Action

```python
async def click_button(page, button_name):
    # Find and click button
    await page.click(f'button:has-text("{button_name}")')

    # Wait for action
    await page.wait_for_load_state('networkidle')

    # Check for confirmation dialog
    confirm = await page.query_selector('.modal-dialog')
    if confirm:
        # Handle confirmation if needed
        pass
```

### 4. Submit Wizard

```python
async def submit_wizard(page, wizard_name, fields_data):
    # Open wizard
    await page.click(f'button:has-text("{wizard_name}")')

    # Wait wizard dialog
    await page.wait_for_selector('.modal-dialog', state='visible')

    # Fill wizard fields
    for name, value in fields_data.items():
        await page.fill(f'.modal-dialog [name="{name}"]', value)

    # Click Ok/Submit
    await page.click('.modal-dialog button.btn-primary')
```

## Credential Handling

**Security Best Practices:**

1. **Never store plain passwords** - always base64 encode
2. **Request credentials interactively** - don't hardcode
3. **Clear after use** - overwrite variables

**User Flow:**

```
User: "buatkan produk baru di Odoo"
AI: "Untuk melakukan aksi di Odoo, saya butuh credentials Anda.
     Tolong provide login dan password (akan di-base64 encode untuk keamanan):

     Format:
     login: <base64_encoded>
     password: <base64_encoded>

     Contoh (jangan pakai ini):
     login: YWRtaW4=
     password: YWRtaW4xMjM="
```

## Common Odoo Selectors

### Navigation
- Menu toggle: `button[data-menu-toggle="all"]`
- Search bar: `.o_searchview_input`
- Breadcrumb: `.breadcrumb`

### Form
- Create button: `.o_list_button_add`
- Save: `button.o_form_button_save`
- Edit: `button.o_form_button_edit`
- Discard: `button.o_form_button_cancel`

### List View
- Row: `tr.o_data_row`
- Checkbox: `input[type="checkbox"]`
- Action button: `button.dropdown-toggle`

### Dialog/Modal
- Dialog: `.modal-dialog`
- Confirm: `.modal-dialog .btn-primary`
- Cancel: `.modal-dialog .btn-secondary`

### Notifications
- Error: `.o_notification.error`
- Warning: `.o_notification.warning`
- Success: `.o_notification`

## Report Format

Setelah automation selesai, laporkan hasil:

```markdown
## Odoo Automation Result

**Action:** {action_description}
**Status:** ✅ Success / ❌ Failed

**Details:**
- Record ID: {id if created}
- URL: {odoo_url}/web#model=XXX&id=YYY

**Errors (if any):**
- {error message}

**Next Steps:**
- {suggestion untuk user}
```

## Troubleshooting

### "Element not found"
- Check selector - Odoo sometimes changes class names
- Wait for element: `await page.wait_for_selector(selector, state='visible', timeout=10000)`

### "Page timeout"
- Odoo taking too long - increase timeout
- Check if Odoo is responding: `curl http://localhost:{port}`

### "Login failed"
- Credentials incorrect
- Check if user has access to database

### "Access Denied"
- User doesn't have permission for this model
- Request access from admin

## Notes

1. **Always use headless=True** untuk automation
2. **Network idle wait** setelah setiap aksi untuk pastikan Odoo selesai processing
3. **Error detection** penting - Odoo sering tampilkan error dalam notification, bukan di Python trace
4. **Screenshot on error** - sangat membantu untuk debugging