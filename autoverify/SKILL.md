---
name: autoverify
description: Verify Odoo module documentation against code. TRIGGER when user says "/autoverify", "verify module", "check documentation", "verify stock module", or "verify [module] docs against code"
---

# AutoResearch - Verify Specific Module

## Trigger
`/autoverify module=stock` - Verify specific module documentation

## Options
- `module=stock` - Module to verify
- `model=stock.quant` - Specific model (optional)
- `deep` - Run full L1-L4 depth
- `quick` - Run L1-L2 only

## Behavior
1. Load module documentation
2. Compare with actual code using verification_engine.py
3. Report discrepancies
4. Update verification status
5. Flag outdated entries
6. Add to backlog if gaps found

## Output
- Verification report for module
- List of verified fields/methods
- List of outdated entries
- List of new gaps found