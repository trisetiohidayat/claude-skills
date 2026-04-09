#!/usr/bin/env python3
"""
Known Odoo Model Deprecations Database

Database mapping model yang sudah diketahui deprecated/removed antar versi.
Confidence score berdasarkan kepastian replacement.
"""

KNOWN_DEPRECATIONS = {
    # Odoo 14 → 15
    ('14.0', '15.0'): {
        'account.invoice': {
            'replacement': 'account.move',
            'notes': 'Invoice digabung ke Move di v15',
            'confidence': 95
        },
    },
    # Odoo 15 → 16
    ('15.0', '16.0'): {
        'account.invoice': {
            'replacement': 'account.move',
            'notes': 'Full migration to moves',
            'confidence': 95
        },
    },
    # Odoo 15 → 17
    ('15.0', '17.0'): {
        'mail.wizard.invite': {
            'replacement': 'mail.wizard.followers',
            'notes': 'Wizard digabung ke followers editor',
            'confidence': 85
        },
        'account.invoice': {
            'replacement': 'account.move',
            'notes': 'Invoice sudah di-migrate ke Move',
            'confidence': 95
        },
        'account.invoice.line': {
            'replacement': 'account.move.line',
            'notes': 'Invoice line sekarang di Move line',
            'confidence': 95
        },
        'sale.order': {
            'replacement': 'sale.order',  # Still exists, but workflow changed
            'notes': 'Model still exists, check workflow changes',
            'confidence': 100,
            'workflow_change': True
        },
    },
    # Odoo 16 → 17
    ('16.0', '17.0'): {
        'account.invoice': {
            'replacement': 'account.move',
            'notes': 'Invoice digabung ke Move',
            'confidence': 95
        },
        'mail.wizard.invite': {
            'replacement': 'mail.wizard.followers',
            'notes': 'Wizard digabung ke followers editor',
            'confidence': 85
        },
    },
    # Odoo 17 → 18
    ('17.0', '18.0'): {
        'mail.wizard.invite': {
            'replacement': 'mail.wizard.followers',
            'notes': 'Deprecated since v17',
            'confidence': 90
        },
    },
    # Odoo 15 → 19 (Major Changes)
    ('15.0', '19.0'): {
        'hr_payroll': {
            'replacement': 'hr_payroll',
            'notes': 'Module ini sekarang HANYA tersedia di Enterprise Edition. Tidak tersedia di CE.',
            'confidence': 100,
            'ee_only': True
        },
        'hr_contract': {
            'replacement': 'hr (integrated)',
            'notes': 'Module hr_contract tidak ada单独的 di Odoo 19 - sudah diintegrasikan ke hr module',
            'confidence': 100,
            'status': 'removed'
        },
        'hr_work_entry_contract_enterprise': {
            'replacement': 'hr_work_entry_enterprise',
            'notes': 'Sekarang bagian dari hr_work_entry_enterprise (EE only)',
            'confidence': 100,
            'ee_only': True
        },
        'account.invoice': {
            'replacement': 'account.move',
            'notes': 'Full migration to account.move since v15',
            'confidence': 95
        },
        'account.invoice.line': {
            'replacement': 'account.move.line',
            'notes': 'Invoice line sekarang di Move line',
            'confidence': 95
        },
        'hr_holidays': {
            'replacement': 'hr_leave',
            'notes': 'hr_holidays renamed to hr_leave di Odoo 16+',
            'confidence': 100
        },
    },
}


def get_deprecation(source_ver: str, target_ver: str, model_name: str) -> dict | None:
    """Get deprecation info for a specific model and version pair."""
    version_key = (source_ver, target_ver)
    if version_key in KNOWN_DEPRECATIONS:
        return KNOWN_DEPRECATIONS[version_key].get(model_name)
    return None


def get_all_deprecations(source_ver: str, target_ver: str) -> dict:
    """Get all known deprecations for a version pair."""
    version_key = (source_ver, target_ver)
    return KNOWN_DEPRECATIONS.get(version_key, {})


# Additional Deprecated Methods
DEPRECATED_METHODS = {
    # Odoo 15 → 19
    ('15.0', '19.0'): {
        '_onchange_price_subtotal': {
            'replacement': '_onchange_amount',
            'notes': 'Method _onchange_price_subtotal dihapus di Odoo 19, diganti dengan _onchange_amount',
            'confidence': 100
        },
    },
    # Odoo 15 → 19 - Module/Tech Changes
    ('15.0', '19.0_migration'): {
        'hr_contract_module': {
            'replacement': 'integrated in hr module',
            'notes': 'Module hr_contract tidak ada单独的 di Odoo 19. Contract functionality sudah terintegrasi ke hr module.',
            'confidence': 100,
            'status': 'removed'
        },
        'mail_wizard_invite': {
            'replacement': 'mail_followers_edit or other wizard',
            'notes': 'mail.wizard.invite wizard tidak ada di Odoo 19. View mail.mail_wizard_invite_form tidak exist.',
            'confidence': 100,
            'status': 'removed'
        },
    }
}

# Fields yang dihapus di Odoo 19
REMOVED_FIELDS = {
    # Odoo 15 → 19
    ('15.0', '19.0'): {
        'account.analytic.line': {
            'validated': {
                'replacement': None,
                'notes': 'Field validated dihapus dari account.analytic.line di Odoo 19. Perlu cari alternatif lain (gunakan state atau field lain).',
                'confidence': 100
            }
        },
        'hr.contract': {
            'model_removed': {
                'replacement': 'hr module (integrated)',
                'notes': 'Model hr.contract tidak ada单独的 di Odoo 19. Contract functionality sudah terintegrasi ke hr module.',
                'confidence': 100
            }
        }
    }
}

# Deprecated attrs/parameters
DEPRECATED_PARAMS = {
    ('15.0', '19.0'): {
        '@api.multi': {
            'replacement': 'Hapus @api.multi (tidak needed di Odoo 16+)',
            'notes': 'Di Odoo 16+, @api.multi tidak lagi needed karena recordset sudah implicit',
            'confidence': 100
        },
        'inherit_id': {
            'hr_contract.hr_contract_view_form': {
                'replacement': 'Cek struktur hr contract di Odoo 19',
                'notes': 'hr_contract module tidak ada单独的 di Odoo 19',
                'confidence': 100
            },
            'hr_payroll.hr_salary_rule_form': {
                'replacement': 'Hanya tersedia di Enterprise Edition',
                'notes': 'hr_payroll adalah module Enterprise, view ini tidak tersedia di CE',
                'confidence': 100,
                'ee_only': True
            }
        },
        'parent': {
            'hr_work_entry_contract_enterprise.menu_hr_payroll_configuration': {
                'replacement': 'Hanya tersedia di Enterprise Edition',
                'notes': 'Menu ini hanya ada di EE',
                'confidence': 100,
                'ee_only': True
            },
            'hr_work_entry_contract_enterprise.menu_hr_payroll_root': {
                'replacement': 'Hanya tersedia di Enterprise Edition',
                'notes': 'Menu ini hanya ada di EE',
                'confidence': 100,
                'ee_only': True
            }
        }
    }
}


def get_deprecation_method(source_ver: str, target_ver: str, method_name: str) -> dict | None:
    """Get method deprecation info."""
    version_key = (source_ver, target_ver)
    if version_key in DEPRECATED_METHODS:
        return DEPRECATED_METHODS[version_key].get(method_name)
    return None


def get_removed_field(source_ver: str, target_ver: str, model_name: str, field_name: str) -> dict | None:
    """Get removed field info."""
    version_key = (source_ver, target_ver)
    if version_key in REMOVED_FIELDS:
        model_info = REMOVED_FIELDS[version_key].get(model_name, {})
        return model_info.get(field_name)
    return None


def get_deprecated_param(source_ver: str, target_ver: str, param_type: str, param_value: str) -> dict | None:
    """Get deprecated parameter info."""
    version_key = (source_ver, target_ver)
    if version_key in DEPRECATED_PARAMS:
        param_info = DEPRECATED_PARAMS[version_key].get(param_type, {})
        return param_info.get(param_value)
    return None


if __name__ == '__main__':
    # Test
    result = get_deprecation('15.0', '17.0', 'mail.wizard.invite')
    print(result)

    # Test method deprecation
    method_result = get_deprecation_method('15.0', '19.0', '_onchange_price_subtotal')
    print("Method:", method_result)

    # Test removed field
    field_result = get_removed_field('15.0', '19.0', 'account.analytic.line', 'validated')
    print("Field:", field_result)
