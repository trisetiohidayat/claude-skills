#!/usr/bin/env python3
"""
Odoo UI Action Helpers
=======================
Pre-built templates untuk common Odoo actions.
"""

import base64
import json
import asyncio
from typing import Dict, Any, List, Optional

# Common Odoo model actions mapping
ODOO_MENU_ACTIONS = {
    'product.product': 'product.product_action',
    'product.template': 'product.product_action',
    'res.partner': 'contacts.action_contacts',
    'res.users': 'base.action_res_users',
    'purchase.request': 'purchase_request.purchase_request_action',
    'purchase.order': 'purchase.purchase_order_action',
    'stock.request.order': 'stock_request.stock_request_order_action',
    'stock.picking': 'stock.action_picking_tree',
    'sale.order': 'sale.action_orders',
    'account.move': 'account.action_move_journal_line',
}


def get_action_for_model(model: str) -> Optional[str]:
    """Get action ID for model"""
    return ODOO_MENU_ACTIONS.get(model)


# Action Templates

async def create_product(page, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create product record"""
    # Navigate to product menu
    await page.click('button[data-menu-toggle="all"]')
    await page.fill('.o_searchview_input', 'Products')
    await asyncio.sleep(0.5)

    # Click product result
    result = page.locator('.o_search_result').first
    if await result.is_visible(timeout=5000):
        await result.click()

    # Wait for list view
    await page.wait_for_load_state("networkidle")

    # Click Create
    await page.click('.o_list_button_add')
    await page.wait_for_load_state("networkidle")

    # Fill required fields
    if 'name' in data:
        await page.fill('[name="name"]', data['name'])
    if 'default_code' in data:
        await page.fill('[name="default_code"]', data['default_code'])
    if 'list_price' in data:
        await page.fill('[name="list_price"]', str(data['list_price']))
    if 'standard_price' in data:
        await page.fill('[name="standard_price"]', str(data['standard_price']))
    if 'type' in data:
        # Select field - click to open dropdown
        await page.click('[name="type"]')
        await asyncio.sleep(0.3)
        await page.click(f'.o_dropdown_item:has-text("{data["type"]}")')

    # Save
    await page.click('button.o_form_button_save')
    await page.wait_for_load_state("networkidle")

    # Check for errors
    error_el = await page.query_selector('.o_notification.error')
    if error_el:
        return {"success": False, "error": await error_el.inner_text()}

    # Get record ID from URL
    import re
    match = re.search(r'id=(\d+)', page.url)
    return {
        "success": True,
        "record_id": int(match.group(1)) if match else None,
        "url": page.url
    }


async def search_product(page, name: str) -> Optional[int]:
    """Search product by name and return first result ID"""
    await page.goto("/web#menu_id=&action=product.product_action", wait_until="networkidle")

    # Search
    await page.fill('.o_searchview_input', name)
    await asyncio.sleep(1)

    # Click first result
    row = page.locator('tr.o_data_row').first
    if await row.is_visible(timeout=5000):
        await row.click()
        await page.wait_for_load_state("networkidle")

        # Get ID from URL
        import re
        match = re.search(r'id=(\d+)', page.url)
        return int(match.group(1)) if match else None

    return None


async def approve_purchase_request(page, pr_id: int) -> Dict[str, Any]:
    """Approve a purchase request"""
    # Navigate to PR
    await page.goto(f"/web#model=purchase.request&id={pr_id}&view_type=form", wait_until="networkidle")

    # Wait for form
    await page.wait_for_selector('.o_form_view', state='visible', timeout=10000)

    # Click Approve button
    approve_btn = page.locator('button:has-text("Approve")')
    if await approve_btn.is_visible(timeout=5000):
        await approve_btn.click()
        await page.wait_for_load_state("networkidle")
        return {"success": True, "message": "Purchase request approved"}

    # Try alternative - might be "Confirm"
    confirm_btn = page.locator('button:has-text("Confirm")')
    if await confirm_btn.is_visible(timeout=5000):
        await confirm_btn.click()
        await page.wait_for_load_state("networkidle")
        return {"success": True, "message": "Purchase request confirmed"}

    return {"success": False, "error": "Approve button not found"}


async def create_purchase_request(page, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create purchase request"""
    # Navigate to PR
    await page.goto("/web#menu_id=&action=purchase_request.purchase_request_action", wait_until="networkidle")

    # Create
    await page.click('.o_list_button_add')
    await page.wait_for_load_state("networkidle")

    # Fill fields
    if 'name' in data:
        await page.fill('[name="name"]', data['name'])

    # Add lines
    if 'line_ids' in data:
        for line in data['line_ids']:
            # Click add line
            await page.click('button:has-text("Add a line")')
            await asyncio.sleep(0.5)

            # Fill line fields
            if 'product_id' in line:
                # Open product dropdown
                await page.click('[name="product_id"]')
                await asyncio.sleep(0.3)
                await page.fill('.o_search_input', line['product_id'])
                await asyncio.sleep(0.3)
                await page.click('.dropdown-item')

            if 'product_qty' in line:
                await page.fill('[name="product_qty"]', str(line['product_qty']))

    # Save
    await page.click('button.o_form_button_save')
    await page.wait_for_load_state("networkidle")

    # Check errors
    error_el = await page.query_selector('.o_notification.error')
    if error_el:
        return {"success": False, "error": await error_el.inner_text()}

    import re
    match = re.search(r'id=(\d+)', page.url)
    return {
        "success": True,
        "record_id": int(match.group(1)) if match else None
    }


# Common field selectors by type

ODOO_FIELD_SELECTORS = {
    # Char/Text fields
    'char': '[name="{}"]',
    'text': 'textarea[name="{}"]',
    'html': 'textarea[name="{}"]',

    # Number fields
    'float': '[name="{}"]',
    'integer': '[name="{}"]',
    'monetary': '[name="{}"]',

    # Selection fields - need dropdown click
    'selection': '[name="{}"]',

    # Many2one - have search dropdown
    'many2one': '[name="{}"] input',

    # Many2many - checkbox list
    'many2many': '[name="{}"]',

    # Boolean - checkbox
    'boolean': '[name="{}"]',

    # Date/Datetime
    'date': '[name="{}"] .o_datepicker_input',
    'datetime': '[name="{}"] .o_datepicker_input',
}


async def fill_field(page, field_type: str, field_name: str, value: Any):
    """Fill field based on type"""
    selector = ODOO_FIELD_SELECTORS.get(field_type, '[name="{}"]').format(field_name)

    if field_type == 'many2one':
        # Open dropdown, search, select
        await page.click(selector)
        await asyncio.sleep(0.3)
        await page.fill('.o_search_input, .select2-search__field', str(value))
        await asyncio.sleep(0.3)
        await page.click('.select2-results__option, .dropdown-item')

    elif field_type == 'selection':
        await page.click(selector)
        await asyncio.sleep(0.3)
        await page.click(f'.o_dropdown_item:has-text("{value}")')

    elif field_type == 'boolean':
        if value:
            await page.check(selector)
        else:
            await page.uncheck(selector)

    elif field_type in ('date', 'datetime'):
        await page.click(selector)
        await asyncio.sleep(0.3)
        await page.fill(selector, str(value))
        await page.keyboard.press('Enter')

    else:
        await page.fill(selector, str(value))


# Utility functions

def encode_creds(login: str, password: str) -> tuple:
    """Encode credentials to base64"""
    return (
        base64.b64encode(login.encode()).decode(),
        base64.b64decode(password.encode()).decode()
    )


def decode_creds(encoded_login: str, encoded_password: str) -> tuple:
    """Decode credentials from base64"""
    return (
        base64.b64decode(encoded_login).decode(),
        base64.b64decode(encoded_password).decode()
    )


async def wait_for_notification(page, timeout: int = 5000) -> Optional[str]:
    """Wait for Odoo notification and return message"""
    try:
        await page.wait_for_selector('.o_notification', state='visible', timeout=timeout)
        return await page.inner_text('.o_notification')
    except:
        return None


async def take_debug_screenshot(page, path: str, label: str = ""):
    """Take screenshot for debugging"""
    await page.screenshot(path=path, full_page=True)
    print(f"[DEBUG] Screenshot: {label} -> {path}")


# Report template

def format_result(action: str, success: bool, data: Dict[str, Any], error: str = None) -> str:
    """Format automation result as markdown"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    output = f"""
## Odoo UI Automation Result

**Action:** {action}
**Status:** {status}

"""
    if success:
        if 'record_id' in data:
            output += f"**Record ID:** `{data['record_id']}`\n"
        if 'url' in data:
            output += f"**URL:** {data['url']}\n"
    else:
        output += f"**Error:** {error or data.get('error', 'Unknown error')}\n"

    output += "\n**Next Steps:**\n"
    if success:
        output += "- Verify the record in Odoo\n"
        if 'record_id' in data:
            output += f"- Edit at: {data.get('url', '#')}\n"
    else:
        output += "- Check the error message\n"
        output += "- Verify user permissions\n"
        output += "- Retry with corrected data\n"

    return output