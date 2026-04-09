---
name: odoo-agent-teams-v2
description: |
  Workflow orchestration untuk Odoo testing & development dengan 5 agent teams.
  Menggunakan SEQUENTIAL execution - DevOps dulu (clone DB), baru QA/Click Tester.
  WAJIB gunakan Agent Teams Claude (TeamCreate, Agent, SendMessage).

  AGENT DOMAIN SKILLS (sudah tersedia):
  - Architect → odoo-base-understanding, odoo-business-process
  - Developer → odoo19-*, odoo-code-quality
  - DevOps → odoo-environment, odoo-db-management, odoo-module-install
  - QA → odoo-module-test, odoo-debug-tdd
  - Click Tester → odoo-click-anywhere-test

  Trigger saat: full testing workflow atau fix error setelah upgrade module.
  Input: module_name, source_db (target_db auto-generate: {source_db}_test_{yyyymmdd_hhmmss})
---

# Odoo Agent Teams v2

Skill ini mengorkestrasi workflow testing dan development Odoo dengan 5 agent yang berkomunikasi via SendMessage.

> **Catatan**: Untuk detail, lihat reference files di folder `references/`

---

## LEAD RULES (WAJIB follows)

### ⚠️ ATURAN PENTING: REUSE AGENT

**JANGAN spawn agent baru!** Dalam satu workflow:
1. Sekali buat team dengan 5 agents (Architect, Developer, DevOps, QA, Click Tester)
2. Kirim pesan ke agent yang SUDAH ADA (yang idle)
3. Agent akan kembali ke mode idle setelah selesai
4. Kirim pesan lagi ke agent yang sama untuk task berikutnya
5. Baru TeamDelete setelah SEMUA phase selesai

**SALAH (jangan lakukan):**
- ❌ Kirim pesan → agent selesai → spawn agent baru
- ❌ Setiap task spawn agent berbeda

**BENAR (lakukan):**
- ✅ Sekali TeamCreate → 5 agents
- ✅ Kirim ke DevOps → selesai → idle
- ✅ Kirim LAGI ke DevOps → masih agent yang sama
- ✅ Semua phase selesai → baru TeamDelete

---

### Lead BOLEH:
1. ✅ Kirim pesan/instruksi ke agents
2. ✅ Tunggu agent selesai
3. ✅ Tanya user (human checkpoint)
4. ✅ Intervensi jika agent stuck > 3 menit (retry/max 2x)
5. ✅ **Cek status agents** via message/notification

### Lead TIDAK BOLEH:
1. ❌ Eksekusi task langsung (jalanin command, clone DB, dll)
2. ❌ Buat decision tanpa persetujuan agent
3. ❌ Skip agent dan kerjakan sendiri

### Monitor Agent Status

Lead WAJIB monitor agents via:

1. **Cek message/notification** - agent akan mengirim status saat selesai
2. **Cek idle state** - agent masuk mode idle saat selesai
3. **Cek task output** - lihat output yang dikembalikan

Pattern yang benar:
```
Lead: "DevOps, clone database X"
DevOps: [Working...]
Lead: [TUNGGU - cek message/notifikasi secara periodik]
DevOps: [Selesai - mengirim message/status]
Lead: [Terima hasil, lanjut ke step berikutnya]
```

### Jika Agent Stuck:
1. Kirim reminder: "Silakan eksekusi task"
2. Tunggu 1 menit
3. Jika masih stuck → Kirim instruksi ulang dengan detail lebih spesifik
4. Baru boleh intervensi (bukan eksekusi sendiri, tapi bantu troubleshooting)

---

> **Catatan**: Untuk detail, lihat reference files di folder `references/`

## Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│  Lead (Orchestration) - TIDAK start Odoo              │
├─────────┬─────────┬─────────┬─────────┬───────────────┤
│ Architect│ Developer│ DevOps  │   QA    │ Click Tester │
│ → skill │ → skill │ → skill │ → skill │   → skill    │
│ base-   │ odoo19- │ environ-│ module- │ click-       │
│ underst │ *       │ ment    │ test    │ anywhere     │
└─────────┴─────────┴─────────┴─────────┴───────────────┘
```

## Agent Domain Skills

Setiap agent menggunakan skill yang sesuai:

| Agent | Skills untuk Agent |
|-------|------------------|
| **Architect** | `odoo-base-understanding`, `odoo-business-process`, `odoo-error-analysis` |
| **Developer** | `odoo19-model-*`, `odoo19-field-*`, `odoo-code-quality`, `odoo-security-review` |
| **DevOps** | `odoo-environment`, `odoo-db-management`, `odoo-module-install` |
| **QA** | `odoo-module-test`, `odoo-debug-tdd` |
| **Click Tester** | `odoo-click-anywhere-test` |

## Quick Reference

| Topic | Reference |
|-------|-----------|
| Step-by-step execution | `references/phases.md` |
| **Communication protocol** | **`references/protocols.md`** ← CONCRETE examples ada di sini! |
| Security & database rules | `references/safety.md` |

## Input Format

Saat memanggil skill, wajib informasi:

| Parameter | Contoh | Deskripsi |
|-----------|--------|-----------|
| `module_name` | `roedl_custom` | Nama module yang akan ditest/upgrade |
| `source_db` | `roedl` | Database sumber (production) |
| `target_db` | **AUTO-GENERATE** | Lead generate: `{source_db}_test_{yyyymmdd_hhmmss}` |

Contoh pemanggilan:
```
/odoo-agent-teams-v2 --module roedl_custom --source-db roedl
```

Lead GENERATE target_db otomatis:
```
roedl_test_20260317_143022
```

## Urutan Eksekusi WAJIB

### SEBELUM MEMULAI WORKFLOW
1. Generate target_db: `{source_db}_test_{yyyymmdd_hhmmss}`
   Contoh: source_db=`upgraded_test` → target_db=`upgraded_test_test_20260317_120000`
2. Inisialisasi files:
   - **Checkpoint**: `{"phase": "init", "source_db": "...", "target_db": "...", "module": "..."}`
   - **Fix Log**: `{"fixes": []}` → `/tmp/odoo_workflow_fix_log.json`
3. Simpan ke checkpoint: `{phase: "init", source_db, target_db, module}`

### LANGKAH-LANGKAH
1. **DevOps**: Kirim pesan ke DevOps dengan instruksi Clone Database
   - TUNGGU hingga DevOps selesai (cek via SendMessage response)
   - Jika DevOps idle > 2 menit → Kirim instruksi ulang ATAU eksekusi langsung via skill
2. **SETELAH DevOps SELESAI** (QA ditunda ke Phase 3):
   - Kirim pesan ke Click Tester: "Jalankan Click Test dengan database {target_db}"
   - Kirim pesan ke Architect: "Pelajari project {module}"
   - WAIT hingga semua selesai
   > **Catatan**: QA akan dijalankan SETELAH Developer apply fix + DevOps upgrade (Phase 3)
3. **Architect**: parallel - bisa dimulai setelah DevOps selesai
4. **JIKA ADA ERROR**: Confidence < 50% → Tanya user: proceed atau abort?
5. **Developer**: Apply fix
6. **Quality Gate**: Developer submit ke Architect untuk review (Phase 3.2.5)
   - Architect jalankan `odoo-security-review` + `odoo-code-quality`
   - Jika APPROVED → Lanjut ke DevOps upgrade
   - Jika REJECTED → Kembali ke Developer

## Architect Dependencies

- Architect BISA mulai early untuk memahami struktur module
- Namun jika perlu hasil analisis lengkap, WAIT hingga Architect selesai
- Lead wajib track kapan Architect membutuhkan dependencies dari agent lain

## Team Management

- **WAIT** for teammates to finish - Lead HARUS tunggu
- **REUSE** agents yang sudah dibuat - JANGAN spawn agent baru!
- **SHUTDOWN** via SendMessage shutdown_request
- **CLEANUP** dengan TeamDelete setelah SEMUA phase selesai

> **PENTING**: Sekali TeamCreate untuk 5 agents, lalu REUSE agents tersebut di phase-phase berikutnya

## Keamanan WAJIB

- **TIDAK PERNAH** modifikasi production database
- Database name WAJIB: `test_`, `_test`, `backup_`, `_dev`, `_staging`
- QA & Click Tester WAJIB gunakan database hasil clone DevOps

## Emergency Stop

```bash
touch /tmp/odoo_workflow_stop
```

### Recovery Steps (WAJIB follow)

Ketika workflow dihentikan via emergency stop:

1. **Tanya Lead**: "Workflow stopped. Choose action:"
   - `[resume]` - Lanjutkan dari checkpoint terakhir
   - `[abort]` - Langsung ke Phase 5 (Cleanup)
   - `[rollback]` - DevOps restore DB, Developer revert code

2. **Resume**: Load state dari checkpoint terakhir
3. **Abort**: Langsung ke Cleanup phase
4. **Rollback**:
   - DevOps: Restore test database ke kondisi sebelum workflow
   - Developer: Revert semua code changes

## Checkpoint Writing (WAJIB)

Setiap phase transition, Lead WAJIB tulis ke `/tmp/odoo_workflow_checkpoint.json`:

```python
# Phase 1.1 selesai - DevOps clone
{"phase": 1.1, "status": "completed", "target_db": "upgraded_test_test_20260317_120000", "module": "xxx"}

# Phase 1.2 selesai - QA + Click Test done
{"phase": 1.2, "status": "completed", "qa_errors": [...], "click_errors": [...]}
```

### Checkpoint Saving

Lead WAJIB simpan state SEBELUM setiap phase transition:

| Checkpoint | Simpan |
|------------|--------|
| Setelah DevOps clone DB | Current phase, agent statuses |
| Setelah Click Test | JS errors |
| Sebelum Developer apply fix | Fix instructions |
| Setelah DevOps upgrade | Success/failure status |
| Setelah QA Verify Fix | Test results after fix |

File checkpoint: `/tmp/odoo_workflow_checkpoint.json`

---

### Fix Record / Change Log (WAJIB)

Setiap fix yang berhasil WAJIB dicatat ke fix log:

**File**: `/tmp/odoo_workflow_fix_log.json`

**Format**:
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

**Kapan WAJIB update**:
1. Setelah Developer apply fix
2. Setelah QA Verify Fix PASSED
3. Setiap fix yang berhasil

**Untuk akses fix sebelumnya**:
```bash
# Lihat semua fix
cat /tmp/odoo_workflow_fix_log.json

# Lihat fix terbaru
cat /tmp/odoo_workflow_fix_log.json | jq '.fixes[-1]'
```

### Status Command

```bash
# Cek status workflow
cat /tmp/odoo_workflow_status

# Cek checkpoint
cat /tmp/odoo_workflow_checkpoint.json

# Cek fix log
cat /tmp/odoo_workflow_fix_log.json
```
