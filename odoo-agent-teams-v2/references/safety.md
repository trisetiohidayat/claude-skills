# Security & Safety Rules

## Database Access Rules

| Agent | Boleh Akses | DILARANG Akses |
|-------|-------------|----------------|
| DevOps | ✅ Database sumber (untuk clone) + Test DB | ❌ Modifikasi data sumber |
| QA | ✅ HANYA Test DB | ❌ Database sumber/production |
| Click Tester | ✅ HANYA Test DB | ❌ Database sumber/production |
| Developer | ✅ HANYA custom addons (bukan DB) | ❌ Modifikasi production |
| Architect | ✅ Read-only (CE/EE source code) | ❌ Modifikasi Apapun |

## Database Naming Rules

Nama database WAJIB mengandung:

| Prefix/Suffix | Contoh | Status |
|---------------|--------|--------|
| `test_` | `roedl_test_20260315` | ✅ Valid |
| `_test` | `backup_test` | ✅ Valid |
| `backup_` | `backup_production_20260315` | ✅ Valid |
| `_dev` | `roedl_dev` | ✅ Valid |
| `_staging` | `roedl_staging` | ✅ Valid |

❌ **TIDAK Valid**: `roedl` (production), `upgraded` (tidak jelas)

## Operation Rules

### DILARANG Keras:
- ❌ `UPDATE`, `INSERT`, `DELETE` ke database sumber/asli
- ❌ Mengakses database production untuk testing
- ❌ QA dan Click Tester akses database sumber/production
- ❌ Nama database sumber digunakan oleh agent lain (kecuali DevOps)

### BOLEH:
- ✅ Clone/duplicate database untuk testing (HANYA DevOps)
- ✅ Read-only operations untuk analisis
- ✅ Semua perubahan dicatat di log file

---

## Safety Validation Checklist

Sebelum eksekusi APAPUN, wajib checklist:

- [ ] Apakah ini database TEST/BACKUP?
- [ ] Apakah nama database sesuai aturan (mengandung test_, _test, backup_, dll)?
- [ ] Apakah ada backup sebelum perubahan?
- [ ] Apakah sudah dicek di `SAFETY LIMITS`?
- [ ] **Apakah QA/Click Tester menggunakan database hasil clone DevOps?**
- [ ] **Apakah TIDAK ada query/akses ke database sumber?**

---

## SAFETY LIMITS

| Limit | Value |
|-------|-------|
| Max Iterations | 5 |
| Max Duration | 2 jam |
| Max Agent Timeout | 5 menit |
| Min Fix Rate | 30% per iterasi |

---

## Audit Trail

Setiap aksi WAJIB di-log:

```python
log(f"[{timestamp}] ACTION: {action}")
log(f"  Database: {database_name}")  # WAJIB: harus test DB
log(f"  Module: {module_name}")
log(f"  Result: {result}")
```
