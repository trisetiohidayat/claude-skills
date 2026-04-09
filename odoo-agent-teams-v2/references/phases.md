# Phases - Step-by-Step Execution

---

## Lead Execution Rules

Lead **TIDAK BOLEH** eksekusi task langsung. Urutan:

1. Kirim pesan ke agent dengan instruksi JELAS
2. Tunggu agent selesai (max 3 menit)
3. Jika agent stuck → Kirim reminder/instruksi ulang
4. Baru boleh intervensi jika sudah retry 2x tetap gagal

**BENAR**:
- "DevOps: Clone database upgraded_test ke upgraded_test_test_xxx" → TUNGGU

**SALAH**:
- Kirim pesan ke DevOps → Langsung jalankan clone sendiri

---

## Human Checkpoint Scenarios (WAJIB tanya Lead)

Lead HARUS tanya ke user (Lead manusia) pada kondisi berikut:

| # | Kondisi | Tindakan |
|---|---------|----------|
| 1 | **Confidence < 50%** | Tanya: proceed atau abort? |
| 2 | **Fix menyebabkan error baru** | Tanya: continue atau rollback? |
| 3 | **Semua 5 iterasi habis** | Tanya: extend (max 3x) atau stop? |
| 4 | **Database clone gagal** | Tanya: retry (max 3x) atau abort? |
| 5 | **Module upgrade gagal berkali-kali** | Tanya: force install atau skip module? |
| 6 | **Architect membutuhkan hasil dari agent lain** | Tanya: wait atau proceed tanpa info? |
| 7 | **QA/Click Tester menemukan error kritis** | Tanya: fix sekarang atau schedule later? |

## Error Handling Rules

| Error | Respons WAJIB |
|-------|---------------|
| DevOps gagal clone DB | Stop → Tanya Lead: retry atau abort |
| QA/Click Tester timeout | Stop → Tanya Lead: retry atau skip |
| Module upgrade gagal | Retry max 3x → Jika still fail, tanya Lead |
| Developer fix error | Verify dulu → Jika cause new error, revert |

---

## PHASE 1: Setup & Test Discovery

**SEQUENTIAL - DevOps harus selesai dulu:**

### 1.1 DevOps: Clone Database
- Duplicate database sumber ke test database
- Nama: `{original}_test_{date}` atau `backup_{original}_{date}`
- Verifikasi cloning berhasil
- **TUNGGU hingga selesai** - QA dan Click Tester TIDAK bisa mulai

### 1.2 SETELAH DevOps SELESAI (TANPA QA - QA di Phase 3):

**a) Click Tester: Run Click Test**
- Click anywhere test untuk deteksi JS errors
- **WAJIB gunakan database dari DevOps**

**b) Architect: Pelajari Project** (parallel)
- Pahami struktur module
- Pahami module di CE atau EE
- Gunakan: `odoo-base-understanding`, `odoo-business-process`

> **Catatan**: QA Testing DITUNDA ke Phase 3 (setelah Developer apply fix + DevOps upgrade)

---

## PHASE 2: Error Analysis

**SETELAH Click Tester menemukan error:**

> **Catatan**: QA Testing DITUNDA - akan dijalankan di Phase 3 setelah fix

### 2.1 Architect: Analisa Error
- Terima error dari Click Tester (JS errors)
- Jelaskan MENGAPA terjadi (bukan hanya APA)
- Berikan confidence score (0-100%)

### 2.2 Architect: Formulate Fix Instructions
- Ubah analysis jadi instruction untuk Developer

### 2.3 Lead: Konsolidasikan & Sepakati
- Verifikasi analysis masuk akal
- Confidence < 50% → HUMAN CHECKPOINT wajib
- Output: consensus + approved fix instructions

---

## PHASE 3: Fix & Verify

### 3.1 Lead: Berikan Instruksi ke Developer
- Error apa, Mengapa, Bagaimana fix
- **WAJIB catat** error ke Fix Log dengan status `PENDING`

### 3.2 Developer: Apply Fix
- Modify code berdasarkan instruksi
- Gunakan skill: `odoo-code-quality`, `odoo-security-review`

### 3.2.5 Quality Gate: Code Review (WAJIB)
- Developer SUBMIT fix ke Architect untuk review
- Architect JALANKAN review:
  - **Security Check**: Jalankan `odoo-security-review` skill
  - **Quality Check**: Jalankan `odoo-code-quality` skill
  - **Root Cause Match**: Verify fix sesuai dengan root cause analysis
- Architect OUTPUT hasil review:
  ```json
  {
    "review_status": "APPROVED|REJECTED|REVISION_NEEDED",
    "security_issues": [],
    "code_quality_issues": [],
    "root_cause_match": true|false,
    "comments": "..."
  }
  ```
- **JIKA REJECTED/REVISION_NEEDED**: Kembali ke Developer → Revise → Submit ulang
- **JIKA APPROVED**: Lanjut ke Phase 3.3

> **Catatan**: Quality Gate SEBELUM DevOps upgrade untuk avoid wasting time

### 3.3 DevOps: Upgrade Module
- Apply changes ke test DB
- Max 3 retry jika gagal

### 3.4 Click Tester: Retest
- Verifikasi error sudah diperbaiki

### 3.5 QA: Verify Fix
- Retest untuk confirm

### 3.6 Lead: Cek Hasil + Update Fix Log
- Jika **PASSED**: Update Fix Log dengan status `SUCCESS`
- Jika **FAILED**: Update Fix Log dengan status `FAILED` + catat new_errors
- ERROR BARU = fix menyebabkan masalah baru
- Architect: Analisa mengapa error baru
- Kembali ke Developer jika ada error baru

---

## PHASE 4: Iteration Loop

```
WHILE errors_remain AND within_safety_limits:
    1. Click Tester: Run click test
    2. Architect: Analisa error (dari Click Tester)
    3. Lead: Konsolidasikan
    4. Developer: Apply fix
    5. DevOps: Upgrade module
    6. QA: Verify Fix (setelah DevOps upgrade)
    7. Click Tester: Retest
    8. IF errors_fixed: SUCCESS
```

> **Catatan**: QA berjalan SETELAH DevOps upgrade di setiap iterasi

---

## PHASE 5: Cleanup

1. **DevOps**: Stop Odoo instances
2. **DevOps**: Drop test database
3. **Lead**: TeamCleanup - Shutdown all agents
4. **Lead**: Hapus checkpoint files

---

## Checkpoint Save Points

Lead WAJIB simpan state ke `/tmp/odoo_workflow_checkpoint.json` pada:

| Phase |checkpoint | Data Disimpan |
|-------|------------|---------------|
| 1.1 | Setelah DevOps clone DB | `current_phase`, `target_db`, `module`, `agents_status` |
| 1.2 | Setelah QA + Click Test | `errors_found`, `baseline_results` |
| 2 | Setelah Architect analisis | `fix_instructions`, `confidence_scores` |
| 3.2 | Setelah Developer apply fix | `fix_id`, `files_modified`, `fix_summary` |
| 3.2.5 | Setelah Quality Gate review | `review_status`, `security_issues`, `code_quality_issues` |
| 3.3 | Setelah DevOps upgrade | `upgrade_success`, `errors_after_fix` |
| 3.6 | Setelah retest | `errors_fixed`, `new_errors` |

Format checkpoint:
```json
{
  "timestamp": "2026-03-17T10:30:00Z",
  "phase": 3,
  "module": "roedl_custom",
  "target_db": "roedl_test_20260317",
  "agents_status": {...},
  "errors": [...]
}
```

---

## Fix Record Logging (WAJIB)

Setiap fix yang berhasil WAJIB dicatat:

### Kapan WAJIB update:
1. Setelah Developer apply fix (Phase 3.2)
2. Setelah QA Verify Fix PASSED (Phase 3.5)
3. Setiap fix yang dianggap berhasil

### File: `/tmp/odoo_workflow_fix_log.json`

### Format:
```json
{
  "fixes": [
    {
      "fix_id": "FIX_001",
      "timestamp": "2026-03-18T10:30:00Z",
      "module": "roedl_custom",
      "iteration": 1,
      "error": {
        "error_id": "JS_ERROR_001",
        "description": "Uncaught TypeError: Cannot read property 'name' of undefined",
        "source": "click_tester",
        "location": "static/src/js/custom_view.js:42"
      },
      "fix": {
        "files_modified": ["static/src/js/custom_view.js"],
        "summary": "Added null check for record.name before accessing",
        "confidence": 90
      },
      "developer": "Developer agent",
      "approved_by": "Lead",
      "test_results": {
        "qa_verify": "PASSED",
        "click_retest": "PASSED",
        "new_errors": []
      },
      "status": "SUCCESS"
    }
  ]
}
```

### Cara Penggunaan:
```bash
# Lihat semua fix
cat /tmp/odoo_workflow_fix_log.json

# Lihat fix terbaru
cat /tmp/odoo_workflow_fix_log.json | jq '.fixes[-1]'

# Lihat fix yang gagal
cat /tmp/odoo_workflow_fix_log.json | jq '.fixes | map(select(.status == "FAILED"))'
```
