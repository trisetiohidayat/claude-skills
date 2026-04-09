#!/usr/bin/env python3
"""
Find replacement candidates untuk removed models.

Usage:
    python3 find_replacement.py mail.wizard.invite /path/to/odoo-17.0 --output candidates.json
"""

import re
import json
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

# Import known deprecations
import sys
sys.path.insert(0, str(Path(__file__).parent))
from known_deprecations import get_deprecation


@dataclass
class ReplacementCandidate:
    model_name: str
    confidence: float
    match_type: str  # exact, fuzzy, field, known
    reason: str


def search_model_exact(model_name: str, odoo_path: Path) -> bool:
    """Check if model exists di versi baru."""
    # Search in models/*.py
    for py_file in odoo_path.glob('**/addons/*/models/*.py'):
        try:
            content = py_file.read_text()
            # Pattern: 'model_name' = ModelName
            if f"'{model_name}'" in content or f'"{model_name}"' in content:
                return True
        except Exception:
            pass
    return False


def search_model_fuzzy(removed_model: str, odoo_path: Path, threshold: float = 0.7) -> List[ReplacementCandidate]:
    """Search untuk similar model names."""
    candidates = []

    # Try fuzzy matching with difflib
    try:
        from difflib import SequenceMatcher
    except ImportError:
        return candidates

    # Get base name (去掉 prefix)
    base_name = removed_model.split('.')[-1].lower()

    # Search all model definitions
    model_defs = []
    for py_file in odoo_path.glob('**/addons/*/models/*.py'):
        try:
            content = py_file.read_text()
            # Find all model strings
            matches = re.findall(r"'([\w.]+)'", content)
            model_defs.extend(matches)
        except Exception:
            pass

    # Remove duplicates and check similarity
    seen = set()
    for model in model_defs:
        if model in seen or '.' not in model:
            continue
        seen.add(model)

        short_name = model.split('.')[-1].lower()
        ratio = SequenceMatcher(None, base_name, short_name).ratio()

        if ratio >= threshold and ratio < 1.0:  # Exclude exact matches
            candidates.append(ReplacementCandidate(
                model_name=model,
                confidence=ratio * 100,
                match_type='fuzzy',
                reason=f'Name similarity: {base_name} ↔ {short_name} ({ratio:.0%})'
            ))

    # Sort by confidence
    candidates.sort(key=lambda x: x.confidence, reverse=True)
    return candidates[:5]  # Top 5


def search_by_fields(removed_model: str, odoo_path: Path) -> List[ReplacementCandidate]:
    """Search models dengan similar fields."""
    # Ini adalah simplified version
    # Full implementation would compare field definitions
    return []


def find_replacement(removed_model: str, source_ver: str, target_ver: str, odoo_path: Path = None) -> List[ReplacementCandidate]:
    """Find replacement candidates untuk removed model."""
    candidates = []

    # 1. Check known deprecations database
    known = get_deprecation(source_ver, target_ver, removed_model)
    if known:
        candidates.append(ReplacementCandidate(
            model_name=known['replacement'],
            confidence=known['confidence'],
            match_type='known',
            reason=known.get('notes', 'Known deprecation mapping')
        ))

    # 2. If Odoo path provided, search in codebase
    if odoo_path and Path(odoo_path).exists():
        odoo_path = Path(odoo_path)

        # Check exact existence
        if search_model_exact(removed_model, odoo_path):
            candidates.append(ReplacementCandidate(
                model_name=removed_model,
                confidence=100,
                match_type='exact',
                reason='Model still exists in target version'
            ))

        # Add fuzzy matches
        fuzzy_matches = search_model_fuzzy(removed_model, odoo_path)
        candidates.extend(fuzzy_matches)

    # Remove duplicates and sort
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c.model_name not in seen:
            seen.add(c.model_name)
            unique_candidates.append(c)

    unique_candidates.sort(key=lambda x: x.confidence, reverse=True)
    return unique_candidates


def determine_confidence_level(confidence: float) -> str:
    """Determine confidence level category."""
    if confidence >= 90:
        return 'HIGH'
    elif confidence >= 70:
        return 'MEDIUM'
    else:
        return 'LOW'


def main():
    parser = argparse.ArgumentParser(description='Find replacement candidates')
    parser.add_argument('model', help='Model name yang akan diganti')
    parser.add_argument('odoo_path', help='Path ke Odoo versi baru')
    parser.add_argument('--source-ver', default='15.0', help='Source version')
    parser.add_argument('--target-ver', default='17.0', help='Target version')
    parser.add_argument('--output', '-o', help='Output JSON file')

    args = parser.parse_args()

    candidates = find_replacement(
        args.model,
        args.source_ver,
        args.target_ver,
        args.odoo_path
    )

    print(f"Found {len(candidates)} candidates for {args.model}:")

    for c in candidates:
        level = determine_confidence_level(c.confidence)
        icon = '✅' if level == 'HIGH' else '⚠️' if level == 'MEDIUM' else '❌'
        print(f"  {icon} {c.model_name} ({c.confidence:.0f}%) - {c.match_type}")
        print(f"      Reason: {c.reason}")

    result = {
        'model': args.model,
        'candidates': [
            {
                'model_name': c.model_name,
                'confidence': c.confidence,
                'level': determine_confidence_level(c.confidence),
                'match_type': c.match_type,
                'reason': c.reason
            }
            for c in candidates
        ]
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == '__main__':
    main()
