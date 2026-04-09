---
name: odoo-debug-tdd
description: |
  Debug dan fix Odoo bugs dengan Test-Driven Development (TDD). PASTIKAN gunakan skill ini saat:
  - User report bug/error/issue di Odoo module
  - User minta debugging dengan test reproduksi
  - Ada "TypeError", "AttributeError", "ValidationError", "403", "500" di Odoo
  - User ingin fix dengan approach "test dulu baru fix"
  - User bertanya tentang perbedaan CE vs EE yang menyebabkan error

  Ini BUKAN untuk create fitur baru atau general Odoo help. Hanya untuk debug + fix bugs.

  Workflow: Auto-detect Odoo path → Analyze issue → Write failing test → Fix code → Verify → MD Summary
compatibility: "Odoo 12-19, Python 3.8+, TransactionCase dan HttpCase, CE dan EE"
---

# Odoo Debug TDD Skill

Debug Odoo dengan pendekatan Test-Driven Development. Test dibuat DULU untuk mereproduksi bug, baru kemudian fix.

## Step 0: Detect CE vs EE (Wajib)

Sebelum debug, tentukan edition yang aktif:

### A. Auto-detect dari directory structure

Cari di working directory atau parent directories:

```
# CE indicators
odoo/addons/           # CE addons
odoo/odoo/addons/    # CE core

# EE indicators
enterprise/            # EE modules directory
```

### B. Dari module manifest

```python
# EE module memiliki 'license' key
{
    'name': 'Sale Enterprise',
    'license': 'OEEL',  # Enterprise license
}

# CE module tidak memiliki license
{
    'name': 'Sale',
    # no license key
}
```

### C. Version detection

```python
# Cari version dari odoo/__init__.py atau odoo/release.py
# Contoh: version = '19.0'
```

**CATATAN**: Selalu sebutkan CE/EE dan version dalam debug output.

## Step 1: Auto-Detect Odoo Path

**JANGAN tanya user dulu** - lakukan ini terlebih dahulu:

1. Cari odoo.conf di lokasi umum:
   ```
   /etc/odoo/odoo.conf
   ~/odoo.conf
   <current_dir>/odoo.conf
   <current_dir>/debian/odoo.conf
   ```

2. Jika ketemu, parse untuk dapat:
   - `addons_path` - untuk tahu letak modules
   - `data_dir` - untuk letak filestore

3. **JANGAN konfirmasi ke user** - jika path valid (ada addons folder), langsung proceed

4. **BARU tanya user** jika:
   - odoo.conf tidak ketemu
   - path tidak valid
   - perlu klarifikasi module yang bermasalah

## Step 2: Analyze + Write Test Simultaneously

### Quick Analysis (1-2 menit):
1. Identify model/controller yang terkait dari error message
2. Find existing test patterns di module tersebut
3. Tentukan test type: TransactionCase (model) atau HttpCase (controller/portal)

### Write Test DULU (TDD):
Buat file test yang AKAN fail:

```python
# <module>/tests/test_<feature>.py
from odoo.tests import TransactionCase  # atau HttpCase

class Test<Feature>(TransactionCase):
    def test_<scenario>(self):
        """Test yang mereproduksi bug - harus FAIL dulu"""
        # Arrange - setup data seperti di production
        # Act - eksekusi yang menyebabkan bug
        # Assert - expected behavior yang BENAR
        self.assertEqual(result, expected, "Bug description")
```

**PENTING**: Test ditulis untuk behavior yang BENAR, bukan untuk mereproduksi bug. Karena kode masih buggy, test akan FAIL - ini yang diharapkan di TDD.

## Step 3: Fix the Code

Setelah test Written (dan sudah pasti FAIL):
1. Analyze mengapa test fail
2. Apply fix di file yang sesuai:
   - Models: `<module>/models/<file>.py`
   - Controllers: `<module>/controllers/<file>.py`
   - Wizards: `<module>/wizard/<file>.py`

3. Fix harus membuat test PASS - JANGAN ubah test

## Step 4: Quick Verify

1. Test yang dibuat harus PASS
2. Check no regression di module lain (kalau ada test lain)
3. Jika test tidak pass, review fix - mungkin perlu adjustment

## Step 5: Generate MD Summary

Buat ringkas di output:

```markdown
# Debug Report: <Issue>

## Root Cause
<1-2 sentences>

## Test
- File: <module>/tests/test_<file>.py
- Method: test_<name>

## Fix
- File: <module>/path/to/file.py
- Change: <apa yang diubah>

## Verification
Test pass ✓
```

## Checklist

- [x] Odoo path auto-detected
- [x] Test written (FAIL expected)
- [x] Fix applied
- [x] Test PASS
- [x] MD summary generated

## Tips Speed

1. **Gunakan TransactionCase** untuk model logic - lebih cepat dari HttpCase
2. **1 test per bug** - jangan overboard dengan banyak test cases
3. **Langsung ke point** - tidak perlu terlalu banyak comments
4. **Skip exploration** kalau sudah tahu module yang bermasalah

## Error

Jika test tidak FAIL:
- Test tidak mereproduksi bug dengan benar
- Review steps to reproduce dari user
- Adjust test sampai fail dulu

Jika Stuck:
- Minta clarification ke user dengan spesifik
- Jangan spending terlalu banyak waktu di exploration

---

## CE/EE Debugging Quick Reference

### Common CE/EE Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `Module requires hr_payroll` | hr_payroll is EE-only in Odoo 19 | Use EE or find CE alternative |
| `Model 'hr.contract' does not exist` | Removed in Odoo 19 | Use hr.employee instead |
| `Field 'validated' does not exist` | Removed in Odoo 19 | Remove reference to field |
| `External ID not found: hr_contract.view_form` | View removed in Odoo 19 | Update module for Odoo 19 |

### Debugging CE/EE Specific Errors

```bash
# Check if module is EE-only
grep -l "license.*OEEL" addons/*/__manifest__.py

# Check model exists in CE
grep -r "class.*hr.contract" odoo/addons/hr_contract/models/

# Compare CE vs EE model
diff odoo/addons/module/models/ enterprise/module/models/

# Check removed fields
grep -r "validated" odoo/addons/account_analytic_line/
```

### Related Skills
- `odoo-ce-ee-understanding`: Untuk pemahaman CE/EE yang lebih mendalam
