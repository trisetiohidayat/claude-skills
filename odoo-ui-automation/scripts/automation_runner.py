#!/usr/bin/env python3
"""
Odoo UI Automation Runner
=========================
Menjalankan aksi Odoo melalui Playwright browser automation.
Bukan via DB atau XML-RPC, tapi menggunakan browser seolah-olah user sungguhan.

Usage:
    python automation_runner.py --action create_product --login B64_LOGIN --password B64_PASSWORD
    python automation_runner.py --action edit_record --model product.product --id 123
    python automation_runner.py --action click_button --model purchase.request --id 456 --button approve

Requirements:
    pip install playwright
    playwright install chromium
"""

import argparse
import asyncio
import base64
import json
import sys
import os
from typing import Optional, Dict, Any

# Add current dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class OdooUIautomation:
    """Main automation class untuk Odoo UI operations"""

    def __init__(self, url: str, db_name: str, headless: bool = True):
        self.url = url.rstrip('/')
        self.db_name = db_name
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None

    async def __aenter__(self):
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def login(self, login: str, password: str) -> Dict[str, Any]:
        """Login ke Odoo dengan credentials"""
        print(f"[INFO] Logging in to {self.url}/web")

        await self.page.goto(f"{self.url}/web/login", wait_until="networkidle")

        # Fill login form
        await self.page.fill('input[name="login"]', login)
        await self.page.fill('input[name="password"]', password)

        # Submit
        await self.page.click('button[type="submit"]')
        await self.page.wait_for_load_state("networkidle", timeout=30000)

        # Check if logged in successfully
        if "/web" in self.page.url and "login" not in self.page.url:
            print("[SUCCESS] Login successful")
            return {"success": True, "message": "Logged in successfully"}
        else:
            error = await self._get_error_message()
            return {"success": False, "error": error or "Login failed"}

    async def navigate_to_model(self, model: str) -> bool:
        """Navigate ke model menggunakan search"""
        print(f"[INFO] Navigating to {model}")

        # Click menu toggle
        await self.page.click('button[data-menu-toggle="all"]', timeout=5000)
        await asyncio.sleep(0.5)

        # Type in search
        search_input = self.page.locator('.o_searchview_input')
        await search_input.fill(model)
        await asyncio.sleep(1)

        # Click first result
        result = self.page.locator('.o_search_result').first
        if await result.is_visible(timeout=5000):
            await result.click()
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            print(f"[SUCCESS] Navigated to {model}")
            return True

        print(f"[WARN] Could not find menu for {model}")
        return False

    async def create_record(self, model: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Buat record baru"""
        print(f"[INFO] Creating {model} record")

        # Navigate to model
        await self.navigate_to_model(model)

        # Click Create button
        create_btn = self.page.locator('.o_list_button_add')
        if await create_btn.is_visible(timeout=5000):
            await create_btn.click()
        else:
            # Try alternative selector
            await self.page.click('button[data-action="model_create"]', timeout=5000)

        await self.page.wait_for_load_state("networkidle", timeout=10000)

        # Fill form fields
        for field_name, value in data.items():
            print(f"[DEBUG] Filling {field_name} = {value}")
            await self._fill_field(field_name, value)

        # Save
        await self.page.click('button.o_form_button_save')
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        # Check for errors
        error = await self._get_error_message()
        if error:
            return {"success": False, "error": error}

        # Get created record ID from URL
        record_id = self._extract_id_from_url()
        print(f"[SUCCESS] Record created with ID: {record_id}")

        return {
            "success": True,
            "record_id": record_id,
            "url": f"{self.url}/web#model={model}&id={record_id}&view_type=form"
        }

    async def edit_record(self, model: str, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Edit existing record"""
        print(f"[INFO] Editing {model} ID:{record_id}")

        # Navigate directly to record
        await self.page.goto(
            f"{self.url}/web#model={model}&id={record_id}&view_type=form",
            wait_until="networkidle",
            timeout=30000
        )

        # Wait for form to load
        await self.page.wait_for_selector('.o_form_view', state='visible', timeout=10000)

        # Edit fields
        for field_name, value in data.items():
            print(f"[DEBUG] Editing {field_name} = {value}")
            await self._fill_field(field_name, value)

        # Save
        await self.page.click('button.o_form_button_save')
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        # Check for errors
        error = await self._get_error_message()
        if error:
            return {"success": False, "error": error}

        print(f"[SUCCESS] Record {record_id} edited")
        return {"success": True, "record_id": record_id}

    async def click_button(self, model: str, record_id: int, button_name: str) -> Dict[str, Any]:
        """Klik button pada record"""
        print(f"[INFO] Clicking '{button_name}' on {model} ID:{record_id}")

        # Navigate to record
        await self.page.goto(
            f"{self.url}/web#model={model}&id={record_id}&view_type=form",
            wait_until="networkidle",
            timeout=30000
        )

        await self.page.wait_for_selector('.o_form_view', state='visible', timeout=10000)

        # Find and click button
        btn = self.page.locator(f'button:has-text("{button_name}")')
        if await btn.is_visible(timeout=5000):
            await btn.click()
        else:
            # Try in header
            btn = self.page.locator(f'.o_form_button:has-text("{button_name}")')
            if await btn.is_visible(timeout=5000):
                await btn.click()

        # Wait for action
        await self.page.wait_for_load_state("networkidle", timeout=15000)

        # Check for errors
        error = await self._get_error_message()
        if error:
            return {"success": False, "error": error}

        print(f"[SUCCESS] Button '{button_name}' clicked")
        return {"success": True, "message": f"Button '{button_name}' clicked"}

    async def delete_record(self, model: str, record_id: int) -> Dict[str, Any]:
        """Delete record"""
        print(f"[INFO] Deleting {model} ID:{record_id}")

        # Navigate to record
        await self.page.goto(
            f"{self.url}/web#model={model}&id={record_id}&view_type=form",
            wait_until="networkidle",
            timeout=30000
        )

        # Click Action menu
        await self.page.click('button.dropdown-toggle:has-text("Action")')
        await asyncio.sleep(0.5)

        # Click Delete
        delete_btn = self.page.locator('a:has-text("Delete")')
        if await delete_btn.is_visible(timeout=5000):
            await delete_btn.click()

            # Confirm in dialog
            await self.page.click('.modal-dialog .btn-danger')
            await self.page.wait_for_load_state("networkidle", timeout=10000)

        print(f"[SUCCESS] Record {record_id} deleted")
        return {"success": True, "message": "Record deleted"}

    async def search_and_select(self, model: str, domain: Dict[str, Any]) -> Optional[int]:
        """Cari record dan return ID"""
        print(f"[INFO] Searching {model} with {domain}")

        # Navigate to model
        await self.navigate_to_model(model)

        # Apply search filters if provided
        # For now, return first record ID
        row = self.page.locator('tr.o_data_row').first
        if await row.is_visible(timeout=5000):
            # Get ID from data-id
            record_id = await row.get_attribute('data-id')
            print(f"[DEBUG] Found record ID: {record_id}")
            return int(record_id) if record_id else None

        return None

    async def _fill_field(self, field_name: str, value: str):
        """Fill field based on type"""
        # Try standard field selector
        selector = f'[name="{field_name}"]'

        # Check if field exists
        field = self.page.locator(selector)
        if await field.is_visible(timeout=3000):
            # Clear and fill
            await field.clear()
            await field.fill(str(value))
            return

        # Try textarea
        selector = f'textarea[name="{field_name}"]'
        field = self.page.locator(selector)
        if await field.is_visible(timeout=1000):
            await field.fill(str(value))
            return

        # Try by label
        label = self.page.locator(f'label:has-text("{field_name}")')
        if await label.is_visible(timeout=1000):
            parent = label.locator("..")
            input_field = parent.locator('input, textarea, select')
            if await input_field.is_visible(timeout=1000):
                await input_field.fill(str(value))
                return

        print(f"[WARN] Could not fill field: {field_name}")

    async def _get_error_message(self) -> Optional[str]:
        """Get error message from Odoo UI"""
        # Check notification error
        error_el = self.page.locator('.o_notification.error, .alert-danger')
        if await error_el.is_visible(timeout=2000):
            return await error_el.inner_text()

        # Check inline error
        invalid_el = self.page.locator('.o_field_invalid, .text-danger')
        if await invalid_el.is_visible(timeout=2000):
            return f"Invalid field: {await invalid_el.inner_text()}"

        # Check toast
        toast_el = self.page.locator('.o_toast, .o_notification')
        if await toast_el.is_visible(timeout=2000):
            return await toast_el.inner_text()

        return None

    def _extract_id_from_url(self) -> Optional[int]:
        """Extract record ID from current URL"""
        url = self.page.url
        # URL format: /web#model=XXX&id=123
        import re
        match = re.search(r'id=(\d+)', url)
        if match:
            return int(match.group(1))
        return None

    async def take_screenshot(self, path: str):
        """Ambil screenshot untuk debugging"""
        await self.page.screenshot(path=path, full_page=True)
        print(f"[DEBUG] Screenshot saved to {path}")


async def main():
    parser = argparse.ArgumentParser(description="Odoo UI Automation via Playwright")
    parser.add_argument('--url', default='http://localhost:8069', help='Odoo URL')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--action', required=True,
                        choices=['create', 'edit', 'click', 'delete', 'login'],
                        help='Action to perform')
    parser.add_argument('--login', required=True, help='Base64 encoded login')
    parser.add_argument('--password', required=True, help='Base64 encoded password')
    parser.add_argument('--model', help='Model name (e.g., product.product)')
    parser.add_argument('--id', type=int, help='Record ID (for edit/delete/click)')
    parser.add_argument('--data', help='JSON string with field data')
    parser.add_argument('--button', help='Button name (for click action)')
    parser.add_argument('--screenshot', help='Save screenshot on error')

    args = parser.parse_args()

    # Decode credentials
    try:
        login_str = base64.b64decode(args.login).decode('utf-8')
        password_str = base64.b64decode(args.password).decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Invalid base64 encoding: {e}")
        sys.exit(1)

    # Parse data
    data = {}
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON data: {e}")
            sys.exit(1)

    # Run automation
    async with OdooUIautomation(args.url, args.db) as automation:
        # Login first
        result = await automation.login(login_str, password_str)
        if not result.get('success'):
            print(f"[ERROR] Login failed: {result.get('error')}")
            sys.exit(1)

        # Execute action
        if args.action == 'create':
            if not args.model:
                print("[ERROR] --model required for create action")
                sys.exit(1)
            result = await automation.create_record(args.model, data)

        elif args.action == 'edit':
            if not args.model or not args.id:
                print("[ERROR] --model and --id required for edit action")
                sys.exit(1)
            result = await automation.edit_record(args.model, args.id, data)

        elif args.action == 'click':
            if not args.model or not args.id or not args.button:
                print("[ERROR] --model, --id, and --button required for click action")
                sys.exit(1)
            result = await automation.click_button(args.model, args.id, args.button)

        elif args.action == 'delete':
            if not args.model or not args.id:
                print("[ERROR] --model and --id required for delete action")
                sys.exit(1)
            result = await automation.delete_record(args.model, args.id)

        elif args.action == 'login':
            result = {"success": True, "message": "Already logged in"}

        # Output result
        print(json.dumps(result, indent=2))

        # Take screenshot on error
        if not result.get('success') and args.screenshot:
            await automation.take_screenshot(args.screenshot)

        # Exit with appropriate code
        sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    asyncio.run(main())