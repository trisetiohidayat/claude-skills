#!/usr/bin/env python3
"""
Build Global Knowledge Base for Odoo Module Migration

Analyzes CE and EE source code to identify breaking changes between versions.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


# Known deprecations for different version transitions
KNOWN_DEPRECATIONS = {
    ("15.0", "16.0"): [
        {
            "type": "api_deprecation",
            "item": "@api.multi",
            "replacement": "@api.model",
            "applies_to": ["model methods"],
            "description": "@api.multi deprecated in Odoo 16"
        },
        {
            "type": "field_default",
            "item": "fields.date.today",
            "replacement": "fields.Date.today()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "field_default",
            "item": "fields.datetime.now",
            "replacement": "fields.Datetime.now()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "method_deprecation",
            "item": "self.ensure_one()",
            "replacement": "self.ensure_one()",
            "applies_to": ["record validation"],
            "description": "Still available but check usage"
        }
    ],
    ("16.0", "17.0"): [
        {
            "type": "api_change",
            "item": "request.cr",
            "replacement": "request.env.cr",
            "applies_to": ["controller methods"],
            "description": "Database cursor access changed"
        },
        {
            "type": "field_type",
            "item": "fields.Html(sanitize=False)",
            "replacement": "fields.Html(sanitize=False, strip_classes=True)",
            "applies_to": ["Html fields"],
            "description": "Additional sanitization parameters"
        },
        {
            "type": "import_change",
            "item": "from odoo.http import request",
            "replacement": "from odoo.http import request",
            "applies_to": ["controllers"],
            "description": "Import unchanged but context usage may vary"
        }
    ],
    ("17.0", "18.0"): [
        {
            "type": "api_change",
            "item": "report",
            "replacement": "report (with new architecture)",
            "applies_to": ["report actions"],
            "description": "Report rendering changes"
        }
    ],
    ("18.0", "19.0"): [
        {
            "type": "api_change",
            "item": "fields.Many2one(comodel_name=)",
            "replacement": "fields.Many2one(comodel_name=, ondelete='set null')",
            "applies_to": ["Many2one fields"],
            "description": "ondelete parameter more strictly enforced"
        }
    ],
    ("15.0", "17.0"): [
        # Combined changes from 15->16 and 16->17
        {
            "type": "api_deprecation",
            "item": "@api.multi",
            "replacement": "@api.model",
            "applies_to": ["model methods"],
            "description": "@api.multi deprecated in Odoo 16"
        },
        {
            "type": "field_default",
            "item": "fields.date.today",
            "replacement": "fields.Date.today()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "field_default",
            "item": "fields.datetime.now",
            "replacement": "fields.Datetime.now()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "api_change",
            "item": "request.cr",
            "replacement": "request.env.cr",
            "applies_to": ["controller methods"],
            "description": "Database cursor access changed in Odoo 16+"
        },
        {
            "type": "field_type",
            "item": "fields.Html(sanitize=False)",
            "replacement": "fields.Html(sanitize=False, strip_classes=True)",
            "applies_to": ["Html fields"],
            "description": "Additional sanitization parameters in Odoo 16+"
        }
    ],
    ("15.0", "18.0"): [
        # Combined from 15->16, 16->17, 17->18
        {
            "type": "api_deprecation",
            "item": "@api.multi",
            "replacement": "@api.model",
            "applies_to": ["model methods"],
            "description": "@api.multi deprecated in Odoo 16"
        },
        {
            "type": "field_default",
            "item": "fields.date.today",
            "replacement": "fields.Date.today()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "field_default",
            "item": "fields.datetime.now",
            "replacement": "fields.Datetime.now()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "api_change",
            "item": "request.cr",
            "replacement": "request.env.cr",
            "applies_to": ["controller methods"],
            "description": "Database cursor access changed"
        },
        {
            "type": "field_type",
            "item": "fields.Html(sanitize=False)",
            "replacement": "fields.Html(sanitize=False, strip_classes=True)",
            "applies_to": ["Html fields"],
            "description": "Additional sanitization parameters"
        },
        {
            "type": "api_change",
            "item": "report",
            "replacement": "report (new architecture)",
            "applies_to": ["report actions"],
            "description": "Report rendering changes"
        }
    ],
    ("15.0", "19.0"): [
        # All changes from 15->19
        {
            "type": "api_deprecation",
            "item": "@api.multi",
            "replacement": "@api.model",
            "applies_to": ["model methods"],
            "description": "@api.multi deprecated in Odoo 16"
        },
        {
            "type": "field_default",
            "item": "fields.date.today",
            "replacement": "fields.Date.today()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "field_default",
            "item": "fields.datetime.now",
            "replacement": "fields.Datetime.now()",
            "applies_to": ["field defaults"],
            "description": "Method call style required"
        },
        {
            "type": "api_change",
            "item": "request.cr",
            "replacement": "request.env.cr",
            "applies_to": ["controller methods"],
            "description": "Database cursor access changed"
        },
        {
            "type": "field_type",
            "item": "fields.Html(sanitize=False)",
            "replacement": "fields.Html(sanitize=False, strip_classes=True)",
            "applies_to": ["Html fields"],
            "description": "Additional sanitization parameters"
        },
        {
            "type": "api_change",
            "item": "fields.Many2one(comodel_name=)",
            "replacement": "fields.Many2one(comodel_name=, ondelete='set null')",
            "applies_to": ["Many2one fields"],
            "description": "ondelete parameter more strictly enforced"
        },
        # From Roedl Migration Analysis - Specific Issues
        {
            "type": "method_replacement",
            "item": "_onchange_price_subtotal()",
            "replacement": "_onchange_amount()",
            "applies_to": ["account.move.line", "account_move_line"],
            "description": "Roedl analysis: _onchange_price_subtotal method removed in Odoo 19"
        },
        {
            "type": "ondelete_required",
            "item": "Many2one fields without ondelete",
            "replacement": "Add explicit ondelete parameter",
            "applies_to": ["Many2one fields"],
            "description": "Roedl analysis: ondelete parameters may be removed during migration - add explicitly"
        },
        {
            "type": "view_reference_removed",
            "item": "hr_contract.hr_contract_view_form",
            "replacement": "NOT AVAILABLE - hr_contract merged",
            "applies_to": ["XML view inheritance"],
            "description": "Roedl analysis: hr_contract module no longer exists in Odoo 19"
        },
        {
            "type": "view_reference_removed",
            "item": "mail.mail_wizard_invite_form",
            "replacement": "mail.mail_followers_edit_form",
            "applies_to": ["XML view inheritance"],
            "description": "Roedl analysis: mail.wizard.invite replaced with mail.followers.edit"
        }
    ]
}

# Known model replacements
MODEL_REPLACEMENTS = {
    "account.invoice": {
        "new": "account.move",
        "version": "14.0",
        "note": "account.invoice renamed to account.move in v14"
    },
    "account.invoice.line": {
        "new": "account.move.line",
        "version": "14.0",
        "note": "account.invoice.line renamed to account.move.line"
    },
    "project.task": {
        "new": "project.task",
        "note": "Still exists, but some fields changed in v15+"
    },
    "sale.order": {
        "new": "sale.order",
        "note": "Still exists, workflow changes in v15+"
    },
    "sale.order.line": {
        "new": "sale.order.line",
        "note": "Still exists, some fields renamed"
    },
    "crm.lead": {
        "new": "crm.lead",
        "note": "Still exists, stage handling changed"
    },
    # From Roedl Migration Analysis - Odoo 15 to 19
    "hr.contract": {
        "new": "hr.contract (merged into hr module)",
        "version": "16.0+",
        "note": "hr.contract model no longer exists - integrated into hr module. Use hr.employee.contract_ids instead."
    }
}

# Known modules that are Enterprise-only in Odoo 19
EE_ONLY_MODULES = [
    "hr_payroll",
    "hr_payroll_account",
    "hr_work_entry_contract_enterprise",
    "account_accountant_enterprise",
    "sale_enterprise",
    "purchase_enterprise",
    "stock_enterprise",
    "project_enterprise",
    "hr_enterprise"
]

# Known modules that were merged/removed in Odoo 16+
REMOVED_MODULES = [
    "hr_contract",  # Merged into hr module in Odoo 16+
    "hr_timesheet",  # Merged into project_timesheet
    "mail_wizard_invite",  # Replaced with mail.followers.edit
]

# Known method replacements
METHOD_REPLACEMENTS = {
    "_onchange_price_subtotal": {
        "new": "_onchange_amount",
        "applies_to": ["account.move.line"],
        "note": "From Roedl analysis - _onchange_price_subtotal method removed in Odoo 19"
    }
}

# Known field removals (verified not exist in Odoo 19)
REMOVED_FIELDS = {
    ("account.analytic.line", "validated"): {
        "version": "19.0",
        "note": "Field 'validated' removed from account.analytic.line in Odoo 19. Use timesheet_validated instead."
    }
}

# Known view reference changes
VIEW_REFERENCE_CHANGES = {
    "hr_contract.hr_contract_view_form": {
        "new": "NOT AVAILABLE",
        "note": "hr_contract module merged into hr. Use hr.contract view if available in EE."
    },
    "hr_payroll.hr_salary_rule_form": {
        "new": "EE ONLY",
        "note": "hr_payroll is Enterprise-only in Odoo 19"
    },
    "mail.mail_wizard_invite_form": {
        "new": "mail.mail_followers_edit_form",
        "note": "mail.wizard.invite replaced with mail.followers.edit in Odoo 16+"
    }
}

# Common CE modules that might appear in dependencies
CE_MODULES = [
    'base', 'web', 'sale', 'sale_management', 'account', 'account_accountant',
    'purchase', 'purchase_requisition', 'stock', 'stock_account', 'mrp',
    'mrp_repair', 'project', 'project_timesheet', 'hr', 'hr_expense',
    'crm', 'marketing_automation', 'website', 'website_blog', 'website_sale',
    'pos', 'account_payment', 'account_invoicing', 'hr_recruitment',
    'fleet', 'maintenance', 'quality', 'repair', 'event', 'mass_mailing'
]

# Common EE modules
EE_MODULES = [
    'account_enterprise', 'sale_enterprise', 'purchase_enterprise',
    'stock_enterprise', 'project_enterprise', 'hr_enterprise',
    'account_accountant', 'account_accountant_enterprise'
]


def analyze_ce_difference(old_path: Path, new_path: Path) -> List[Dict]:
    """Analyze CE differences between versions."""
    changes = []
    # Implementation: compare key files between versions
    # This is a placeholder - real implementation would parse actual Odoo source
    return changes


def analyze_ee_difference(old_path: Path, new_path: Path) -> List[Dict]:
    """Analyze EE differences between versions."""
    changes = []
    # Implementation: compare EE-specific files
    return changes


def build_knowledge_base(
    source_ver: str,
    target_ver: str,
    ce_old_path: str = None,
    ce_new_path: str = None,
    ee_old_path: str = None,
    ee_new_path: str = None,
    output_path: str = None
) -> Dict[str, Any]:
    """Build complete knowledge base."""

    kb = {
        "source_version": source_ver,
        "target_version": target_ver,
        "breaking_changes": [],
        "ce_ee_differences": [],
        "model_replacements": [],
        "ce_modules": CE_MODULES,
        "ee_modules": EE_MODULES,
        "generated_at": datetime.now().isoformat()
    }

    # Get known deprecations
    version_key = (source_ver, target_ver)
    if version_key in KNOWN_DEPRECATIONS:
        kb["breaking_changes"] = KNOWN_DEPRECATIONS[version_key]
    else:
        # Try intermediate versions
        source_num = int(source_ver.split('.')[0])
        target_num = int(target_ver.split('.')[0])

        # Collect all changes from source to target
        all_changes = []
        for v in range(source_num, target_num):
            intermediate_key = (f"{v}.0", f"{v+1}.0")
            if intermediate_key in KNOWN_DEPRECATIONS:
                all_changes.extend(KNOWN_DEPRECATIONS[intermediate_key])

        kb["breaking_changes"] = all_changes

    # Add model replacements
    kb["model_replacements"] = MODEL_REPLACEMENTS

    # Analyze CE if paths provided
    if ce_old_path and ce_new_path:
        try:
            ce_changes = analyze_ce_difference(Path(ce_old_path), Path(ce_new_path))
            kb["breaking_changes"].extend(ce_changes)
        except Exception as e:
            print(f"Warning: Could not analyze CE differences: {e}")

    # Analyze EE if paths provided
    if ee_old_path and ee_new_path:
        try:
            ee_changes = analyze_ee_difference(Path(ee_old_path), Path(ee_new_path))
            kb["ce_ee_differences"] = ee_changes
        except Exception as e:
            print(f"Warning: Could not analyze EE differences: {e}")

    # Save to output
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(kb, f, indent=2)
        print(f"Knowledge base saved to: {output_path}")

    return kb


def main():
    parser = argparse.ArgumentParser(
        description="Build knowledge base for Odoo migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_knowledge_base.py --source 15.0 --target 17.0 --output kb.json
  python build_knowledge_base.py --source 15.0 --target 19.0 --ce-old /path/ce15 --ce-new /path/ce17 --output kb.json
        """
    )
    parser.add_argument("--source", required=True, help="Source version (e.g., 15.0)")
    parser.add_argument("--target", required=True, help="Target version (e.g., 17.0)")
    parser.add_argument("--ce-old", help="Path to old CE Odoo source")
    parser.add_argument("--ce-new", help="Path to new CE Odoo source")
    parser.add_argument("--ee-old", help="Path to old EE Odoo source")
    parser.add_argument("--ee-new", help="Path to new EE Odoo source")
    parser.add_argument("--output", help="Output JSON path")

    args = parser.parse_args()

    kb = build_knowledge_base(
        args.source,
        args.target,
        args.ce_old,
        args.ce_new,
        args.ee_old,
        args.ee_new,
        args.output
    )

    print(f"Knowledge base built: {len(kb['breaking_changes'])} breaking changes")
    print(f"Source: {kb['source_version']} -> Target: {kb['target_version']}")


if __name__ == "__main__":
    main()
