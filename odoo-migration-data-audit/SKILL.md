---
name: odoo-migration-data-audit
description: |
  Comprehensive data audit antara Odoo v15 dan v19 database setelah migrasi. Melakukan:
  - Schema comparison (kolom yang hilang/bertambah antara versi)
  - Data integrity check (orphan records, NULL values, duplicates)
  - Accounting balance sheet comparison (total balance sheet, deteksi transaksi hilang)
  - Lost data column detection (data yang hilang/null setelah upgrade)
  - Security & access rights analysis

  Trigger phrases: "audit data v15 v19", "full migration audit", "cek seluruh data migration",
  "schema comparison v15 v19", "accounting balance sheet check", "lost data after upgrade",
  "data integrity audit", "migration gap analysis", "perbedaan struktur database",
  "transaksi hilang setelah migrasi", "balance sheet comparison"

  Database configurations (Roedl project):
  - v15: roedl_15_20260415 via MCP instance "roedl-odoo15"
  - v19: roedl_upgraded_20260415 via MCP instance "roedl-odoo19-local"
---

# Odoo v15 vs v19 Full Data Migration Audit

Comprehensive audit skill yang menganalisa seluruh perbedaan data antara Odoo v15 dan v19
setelah migrasi. Menghasilkan laporan detil untuk mengidentifikasi data yang hilang,
tidak konsisten, atau需要 perbaikan.

## Prerequisites

### MCP Instances

Verify dulu bahwa kedua instance accessible:

| Version | Database | MCP Instance | Port |
|---------|----------|--------------|------|
| Odoo 15 | `roedl_15_20260415` | `roedl-odoo15` | 8115 |
| Odoo 19 | `roedl_upgraded_20260415` | `roedl-odoo19-local` | 8133 |

Test connection:
```python
# v15
mcp__rust-mcp__odoo_search_read(
    instance="roedl-odoo15",
    model="res.users",
    domain=[["id", "=", 2]],
    fields=["id", "login", "name"]
)

# v19
mcp__rust-mcp__odoo_search_read(
    instance="roedl-odoo19-local",
    model="res.users",
    domain=[["id", "=", 2]],
    fields=["id", "login", "name"]
)
```

### Report Output Directory

Create directory jika belum ada:
```
docs/v19-comparison/
```

---

## Phase 1: Model Overview (Record Counts)

**Goal:** Dapatkan overview jumlah records di setiap model utama kedua database.

### SQL: Count Records per Model

Jalankan di **kedua database** (v15 dan v19):

```sql
-- Core models
SELECT 'res_partner' as tbl, COUNT(*) as cnt FROM res_partner
UNION ALL SELECT 'res_users', COUNT(*) FROM res_users
UNION ALL SELECT 'res_company', COUNT(*) FROM res_company
UNION ALL SELECT 'res_partner_bank', COUNT(*) FROM res_partner_bank
UNION ALL
-- Accounting
SELECT 'account_account', COUNT(*) FROM account_account
UNION ALL SELECT 'account_move', COUNT(*) FROM account_move
UNION ALL SELECT 'account_move_line', COUNT(*) FROM account_move_line
UNION ALL SELECT 'account_journal', COUNT(*) FROM account_journal
UNION ALL SELECT 'account_payment', COUNT(*) FROM account_payment
UNION ALL
-- HR
SELECT 'hr_employee', COUNT(*) FROM hr_employee
UNION ALL SELECT 'hr_department', COUNT(*) FROM hr_department
UNION ALL SELECT 'hr_contract', COUNT(*) FROM hr_contract
UNION ALL
-- Sales/Purchase
SELECT 'sale_order', COUNT(*) FROM sale_order
UNION ALL SELECT 'purchase_order', COUNT(*) FROM purchase_order
UNION ALL
-- Project
SELECT 'project_project', COUNT(*) FROM project_project
UNION ALL SELECT 'project_task', COUNT(*) FROM project_task
UNION ALL
-- Product
SELECT 'product_product', COUNT(*) FROM product_product
UNION ALL SELECT 'product_template', COUNT(*) FROM product_template
UNION ALL
-- Inventory
SELECT 'stock_picking', COUNT(*) FROM stock_picking
UNION ALL SELECT 'stock_move', COUNT(*) FROM stock_move
UNION ALL
-- CRM
SELECT 'crm_lead', COUNT(*) FROM crm_lead
UNION ALL
-- Attachments
SELECT 'ir_attachment', COUNT(*) FROM ir_attachment
ORDER BY tbl;
```

### Output: Model Overview Table

| Model | v15 Count | v19 Count | Diff | Diff % | Status |
|-------|-----------|-----------|------|--------|--------|
| res_partner | X | X | ±X | ±X% | ✅/⚠️ |
| account_move_line | X | X | ±X | ±X% | ✅/❌ |
| ... | | | | | | |

**Threshold:** Flag sebagai ⚠️ jika Diff % > 5% atau Diff absolute > 10 records.

---

## Phase 2: Schema Comparison

**Goal:** Bandingkan struktur kolom antara v15 dan v19 untuk setiap model kritis.

### Key Models untuk Dicek

| Model | Kenapa Kritis |
|-------|-------------|
| `res_partner` | Customer/vendor contacts |
| `account_account` | Chart of accounts - account_type berubah |
| `account_move` | Invoice → Move consolidation |
| `account_move_line` | Line items |
| `product_product` | Product variants |
| `hr_employee` | Employee data |

### SQL: Get Columns

Jalankan di **masing-masing database**:

```sql
-- Get semua columns untuk model tertentu
SELECT column_name, data_type, is_nullable, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'account_account'
ORDER BY ordinal_position;
```

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'account_move_line'
ORDER BY ordinal_position;
```

### Output: Schema Changes Table

**Lost Columns (ada di v15, hilang di v19):**

| Model | Column | Type (v15) | Nullable? |
|-------|--------|-----------|----------|

**New Columns (ada di v19, tidak ada di v15):**

| Model | Column | Type (v19) | Nullable? |
|-------|--------|-----------|----------|

### Known Schema Changes (Odoo 15 → 19)

| Aspect | Odoo 15 | Odoo 19 |
|--------|---------|---------|
| Invoice model | `account_invoice` | `account_move` (move_type) |
| Account type ref | Join ke `account_account_type` model | `account_type` direct field |
| View tag | `<tree>` | `<list>` |
| Field attrs | `attrs`, `states` | `invisible`, `readonly` |

---

## Phase 3: Data Integrity Check

**Goal:** Deteksi orphan records, NULL values bermasalah, dan duplicates.

### A. Orphan Records Detection

```sql
-- Bank accounts tanpa company_id (KNOWN ISSUE post-upgrade)
SELECT 'res_partner_bank' as tbl, id, acc_number, partner_id, company_id
FROM res_partner_bank
WHERE company_id IS NULL;

-- Partners dengan "(deleted)" suffix (migration artifact)
SELECT 'res_partner' as tbl, id, name, email, active
FROM res_partner
WHERE name LIKE '%(deleted)%';

-- Attachments tanpa valid res_id
SELECT a.id, a.name, a.res_model, a.res_id
FROM ir_attachment a
WHERE a.res_id IS NOT NULL
AND a.res_model = 'res.partner'
AND NOT EXISTS (
    SELECT 1 FROM res_partner p
    WHERE p.id = a.res_id
);
```

### B. Required Field NULL Check

```sql
-- Partners (customers) tanpa email
SELECT id, name, email, customer_rank
FROM res_partner
WHERE email IS NULL AND customer_rank > 0;

-- Employees tanpa department
SELECT id, name, department_id
FROM hr_employee
WHERE department_id IS NULL AND active = true;

-- Bank accounts tanpa partner
SELECT id, acc_number, partner_id
FROM res_partner_bank
WHERE partner_id IS NULL;

-- Bank accounts tanpa company
SELECT id, acc_number, partner_id, company_id
FROM res_partner_bank
WHERE company_id IS NULL;
```

### C. Duplicate Detection

```sql
-- Account codes duplicate
SELECT code, name, COUNT(*) as cnt
FROM account_account
GROUP BY code, name
HAVING COUNT(*) > 1;

-- Product codes duplicate
SELECT default_code, COUNT(*) as cnt
FROM product_product
WHERE default_code IS NOT NULL
GROUP BY default_code
HAVING COUNT(*) > 1;

-- Partner names duplicate
SELECT name, COUNT(*) as cnt
FROM res_partner
WHERE active = true
GROUP BY name
HAVING COUNT(*) > 1;
```

### Output: Integrity Issues Table

| # | Model | Issue Type | Affected IDs | Severity | Count |
|---|-------|-----------|-------------|----------|-------|

**Severity:**
- **Critical:** Data loss risk, financial impact
- **High:** Functional issues, broken relations
- **Medium:** Data quality, cosmetic issues

---

## Phase 4: Accounting Balance Sheet Comparison (CRITICAL)

**Goal:** PASTIKAN tidak ada transaksi yang hilang saat migrasi. Ini adalah check paling penting.

### A. Grand Total Summary

Jalankan di **kedua database**:

```sql
-- Overall accounting totals
SELECT
    COUNT(DISTINCT aml.move_id) as total_moves,
    COUNT(aml.id) as total_lines,
    SUM(aml.debit) as grand_debit,
    SUM(aml.credit) as grand_credit,
    ROUND(SUM(aml.debit) - SUM(aml.credit), 2) as net_balance
FROM account_move_line aml
WHERE aml.company_id = 1;
```

**Expected:** `grand_debit` HARUS SAMA dengan `grand_credit` (±0.01 tolerance).

### B. Balance by Account Type

```sql
-- Balance per account type
SELECT
    aa.account_type,
    SUM(aml.debit) as total_debit,
    SUM(aml.credit) as total_credit,
    ROUND(SUM(aml.debit) - SUM(aml.credit), 2) as balance
FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
WHERE aml.company_id = 1
GROUP BY aa.account_type
ORDER BY aa.account_type;
```

### C. Balance per Account (Detail)

```sql
-- Detail balance per account
SELECT
    aa.id,
    aa.code,
    aa.name,
    aa.account_type,
    SUM(aml.debit) as total_debit,
    SUM(aml.credit) as total_credit,
    ROUND(SUM(aml.debit) - SUM(aml.credit), 2) as balance
FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
WHERE aml.company_id = 1
GROUP BY aa.id, aa.code, aa.name, aa.account_type
ORDER BY aa.code;
```

### D. Comparison Table

| Metric | v15 | v19 | Diff | Diff % | Status |
|--------|-----|-----|------|--------|--------|
| Total Moves | X | X | ±X | ±X% | ✅/❌ |
| Total Lines | X | X | ±X | ±X% | ✅/❌ |
| Grand Debit | X | X | ±X | ±0.01% | ✅/❌ |
| Grand Credit | X | X | ±X | ±0.01% | ✅/❌ |
| **Asset Total** | X | X | ±X | ±0.01% | ✅/❌ |
| **Liability Total** | X | X | ±X | ±0.01% | ✅/❌ |
| **Equity Total** | X | X | ±X | ±0.01% | ✅/❌ |
| **Revenue Total** | X | X | ±X | ±0.01% | ✅/❌ |
| **Expense Total** | X | X | ±X | ±0.01% | ✅/❌ |

**Tolerance:** ±0.01% untuk rounding differences.

### E. Transaction Gap Detection

Untuk account dengan discrepancy > 0.01%, investigate lebih lanjut:

```sql
-- Compare specific account balance over time
SELECT
    aa.code,
    aa.name,
    EXTRACT(YEAR FROM am.date) as year,
    SUM(aml.debit) as year_debit,
    SUM(aml.credit) as year_credit,
    ROUND(SUM(aml.debit) - SUM(aml.credit), 2) as year_balance
FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
JOIN account_move am ON aml.move_id = am.id
WHERE aml.company_id = 1
AND aa.account_type IN ('asset', 'liability', 'equity')
GROUP BY aa.code, aa.name, EXTRACT(YEAR FROM am.date)
ORDER BY aa.code, year;
```

### F. Move Line Count by Journal

```sql
-- Count moves per journal
SELECT
    aj.code,
    aj.name,
    COUNT(DISTINCT am.id) as move_count,
    COUNT(aml.id) as line_count,
    SUM(aml.debit) as total_debit,
    SUM(aml.credit) as total_credit
FROM account_move am
JOIN account_move_line aml ON am.id = aml.move_id
JOIN account_journal aj ON am.journal_id = aj.id
WHERE am.company_id = 1
AND am.state = 'posted'
GROUP BY aj.code, aj.name
ORDER BY move_count DESC;
```

---

## Phase 5: Lost Data Detection (Post-Upgrade)

**Goal:** Identifikasi data yang hilang atau menjadi NULL setelah upgrade.

### A. Known Post-Upgrade Issues

| Model | Issue | Severity | Affected Count | Fix Action |
|-------|-------|----------|--------------|------------|
| res.partner.bank | company_id = NULL | Critical | Check via query | Write company_id back |
| res.partner | "(deleted)" records | Medium | Check via query | Archive or merge |
| account.account | Type reference broken | High | Check via query | Update account_type field |

### B. Field-Level NULL Percentage

```sql
-- Percentage NULL per critical field
SELECT
    'res_partner' as tbl, 'phone' as field, COUNT(*) as total,
    SUM(CASE WHEN phone IS NULL THEN 1 ELSE 0 END) as nulls,
    ROUND(SUM(CASE WHEN phone IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as null_pct
FROM res_partner
UNION ALL
SELECT 'res_partner', 'mobile', COUNT(*),
    SUM(CASE WHEN mobile IS NULL THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN mobile IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2)
FROM res_partner
UNION ALL
SELECT 'res_partner', 'email', COUNT(*),
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2)
FROM res_partner
UNION ALL
SELECT 'hr_employee', 'department_id', COUNT(*),
    SUM(CASE WHEN department_id IS NULL THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN department_id IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2)
FROM hr_employee
UNION ALL
SELECT 'res_partner_bank', 'company_id', COUNT(*),
    SUM(CASE WHEN company_id IS NULL THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN company_id IS NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2)
FROM res_partner_bank
ORDER BY tbl, field;
```

### C. Data Migration Window Check

```sql
-- Records created during migration (suspect timeframe)
SELECT
    'account_move' as tbl,
    COUNT(*) as cnt,
    MIN(create_date) as first_created,
    MAX(create_date) as last_created
FROM account_move
WHERE create_date BETWEEN '2024-03-01' AND '2024-04-30';

SELECT
    'ir_attachment' as tbl,
    COUNT(*) as cnt,
    MIN(create_date) as first_created,
    MAX(create_date) as last_created
FROM ir_attachment
WHERE create_date BETWEEN '2024-03-01' AND '2024-04-30';
```

---

## Phase 6: Security & Access Rights

```sql
-- User count by group
SELECT
    rg.name as group_name,
    COUNT(DISTINCT r.uid) as user_count
FROM res_groups_users_rel r
JOIN res_groups rg ON r.gid = rg.id
GROUP BY rg.name
ORDER BY user_count DESC;

-- ACL coverage per model
SELECT
    rm.name as model,
    COUNT(DISTINCT a.id) as acl_count,
    SUM(CASE WHEN a.perm_read = true THEN 1 ELSE 0 END) as can_read,
    SUM(CASE WHEN a.perm_write = true THEN 1 ELSE 0 END) as can_write,
    SUM(CASE WHEN a.perm_create = true THEN 1 ELSE 0 END) as can_create,
    SUM(CASE WHEN a.perm_unlink = true THEN 1 ELSE 0 END) as can_unlink
FROM ir_model_access a
JOIN ir_model rm ON a.model_id = rm.id
GROUP BY rm.name
ORDER BY acl_count;
```

---

## Phase 7: Report Generation

### Output Directory

Create jika belum ada:
```
docs/v19-comparison/
```

### Filename Format

```
YYYY-MM-DD-HHMMSS-full-audit.md
```

Contoh: `2026-04-17-143000-full-audit.md`

### Report Template

```markdown
# Odoo v15 vs v19 Full Migration Audit Report

**Generated:** {timestamp}
**Analyst:** Claude Code
**Skill:** odoo-migration-data-audit

## Database Configuration

| Version | Database | MCP Instance |
|---------|----------|-------------|
| Odoo 15 | `roedl_15_20260331` | `roedl-odoo15` |
| Odoo 19 | `roedl_upgraded_20260415` | `roedl-odoo19-local` |

---

## Executive Summary

[2-3 sentences overview of overall migration health]

**Overall Status:**
- ✅ Data integrity: GOOD / ⚠️ ISSUES FOUND / ❌ CRITICAL PROBLEMS
- ✅ Accounting balance: BALANCED / ⚠️ MINOR DISCREPANCY / ❌ SIGNIFICANT GAP
- ✅ Transactions: ALL ACCOUNTED / ⚠️ X RECORDS MISSING / ❌ CRITICAL LOSS

---

## 1. Model Overview

| Model | v15 | v19 | Diff | Diff % | Status |
|-------|-----|-----|------|--------|--------|

**Summary:**
- Total models scanned: X
- Models with significant diff: X
- Models missing in target: X

---

## 2. Schema Changes

### 2.1 Lost Columns (v15 → v19)

| Model | Column | v15 Type | Nullable |
|-------|--------|----------|---------|

### 2.2 New Columns (v15 → v19)

| Model | Column | v19 Type | Nullable |
|-------|--------|----------|---------|

---

## 3. Data Integrity Issues

| # | Model | Issue | Severity | Count | Action |
|---|-------|-------|----------|-------|--------|

**Summary:**
- Critical: X | High: X | Medium: X
- Total: X issues

---

## 4. Accounting Balance Sheet (CRITICAL)

### 4.1 Grand Total Comparison

| Metric | v15 | v19 | Diff | Diff % | Status |
|--------|-----|-----|------|--------|--------|

**Balance Check:** ✅ BALANCED / ❌ IMBALANCED

### 4.2 Balance by Account Type

| Type | v15 Balance | v19 Balance | Diff | Diff % | Status |
|------|------------|-------------|------|--------|--------|

### 4.3 Transaction Gap Analysis

[Detail accounts dengan discrepancy > 0.01%]

**Gap Summary:**
- Accounts with perfect match: X
- Accounts with minor diff (<0.01%): X
- Accounts with significant diff (>0.01%): X

---

## 5. Lost Data Columns (Post-Upgrade)

| # | Model | Field | Issue | Affected | Fix Approach |
|---|-------|-------|-------|---------|-------------|

---

## 6. Security Analysis

| Group | v15 Users | v19 Users | Diff |
|-------|----------|----------|------|

**ACL Coverage:** X models with ACL / Y total models

---

## 7. Action Items

### Critical (Must Fix - Before Go-Live)

1. **[Issue]** — [Impact] — [Fix approach] — Owner: TBD

### High Priority (Fix Within 1 Week)

1. **[Issue]** — [Impact] — [Fix approach]

### Medium Priority (Fix Within 1 Month)

1. **[Issue]** — [Impact] — [Fix approach]

---

## Appendix: Raw Query Results

### v15 Database Results
```
[paste raw SQL results here]
```

### v19 Database Results
```
[paste raw SQL results here]
```

---

**Report generated by:** odoo-migration-data-audit skill
**Timestamp:** {timestamp}
**Next Steps:** Review Action Items and execute fixes in priority order
```

---

## Execution Checklist

Run phases secara berurutan:

- [ ] **Phase 1:** Model Overview — Get record counts dari kedua DB
- [ ] **Phase 2:** Schema Comparison — Compare column structures
- [ ] **Phase 3:** Data Integrity — Run orphan/NULL/duplicate checks
- [ ] **Phase 4:** Accounting Balance — Compare totals (CRITICAL - run first if short on time)
- [ ] **Phase 5:** Lost Data Detection — Identify post-upgrade issues
- [ ] **Phase 6:** Security Analysis — Check access rights
- [ ] **Phase 7:** Generate Report — Save ke `docs/v19-comparison/`

## Quick Execution (If Short on Time)

Jika hanya ada waktu untuk satu phase, jalankan **Phase 4 (Accounting Balance)** dulu karena:
1. Most critical for business continuity
2. Quick to run (single query per DB)
3. Clear pass/fail criteria

---

## Usage

```bash
# Invoke via Claude Code
/skill odoo-migration-data-audit

# Or in conversation
"jalankan full audit data migration v15 ke v19"

# Quick accounting check only
"cek accounting balance sheet antara v15 dan v19"
```

## Notes

- Always compare same `company_id` (usually 1) across databases
- Balance sheet tolerance: ±0.01% untuk mengakomodasi rounding
- MCP instances may change — verify dengan `odoo-rust-mcp-list` first
- Untuk database dengan EE features, beberapa check mungkin perlu penyesuaian
