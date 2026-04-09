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
    # Odoo 18 → 19
    ('18.0', '19.0'): {
        # Add as discovered
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


if __name__ == '__main__':
    # Test
    result = get_deprecation('15.0', '17.0', 'mail.wizard.invite')
    print(result)
