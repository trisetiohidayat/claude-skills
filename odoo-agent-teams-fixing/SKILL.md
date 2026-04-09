---
name: odoo-agent-teams-fixing
description: |
  Workflow tim 5 agent Claude untuk Odoo testing dan development dengan SEQUENTIAL execution (DevOps dulu, baru QA/Click).
  DevOps WAJIB selesai duplicate database TERLEBIH DAHULU sebelum QA dan Click Tester mulai.
  Trigger saat: ingin menjalankan full testing workflow (click-anywhere + unit test) dengan agent teams,
  atau ingin automasi fix error setelah upgrade module.
  WAJIB gunakan Agent Teams Claude (TeamCreate, Agent, SendMessage) - bukan workflow manual.

  SETIAP AGENT START & STOP ODOO SENDIRI:
  - Lead: HANYA koordinasi, TIDAK start Odoo
  - DevOps: Start/stop Odoo sendiri untuk upgrade module
  - Click Tester: Start/stop Odoo sendiri untuk click-anywhere test
  - QA: Start/stop Odoo sendiri untuk unit test

  URUTAN EKSEKUSI WAJIB:
  1. DevOps: Clone Database (SEBELUM anything else)
  2. QA: Initial Test (SETELAH DevOps selesai)
  3. Click Tester: Run Click Test (SETELAH DevOps selesai)
  4. Architect: Pelajari Project (bisa parallel, tidak perlu database)

  TEAM MANAGEMENT (Wajib sesuai Claude docs):
  - WAIT for teammates to finish - Lead HARUS tunggu teammate selesai, bukan kerja sendiri
  - SHUTDOWN teammates dengan graceful shutdown (SendMessage shutdown_request)
  - CLEANUP team dengan TeamDelete setelah semua selesai

  KEAMANAN & RELIABILITY:
  - TIDAK PERNAH membuat atau memodifikasi production database
  - TIDAK PERNAH mengubah data pada database sumber
  - Database name WAJIB mengandung: test_, _test, backup_, _backup, _dev, _staging

  SELF-HEALING & CONFIDENCE:
  - Auto-recovery jika agent stuck (max 3x retry dengan exponential backoff)
  - Confidence scoring untuk setiap fix (0-100%) berdasarkan historical success rate
  - Verification step sebelum proceeding ke next iteration
  - Human checkpoint untuk keputusan kritis (rollback, stop, low confidence)
---

# Odoo Agent Teams Workflow

Skill ini menjalankan workflow testing dan development Odoo dengan **5 agent Claude** yang berkomunikasi secara SEQUENTIAL (DevOps dulu, baru QA/Click Tester).

> **Catatan**: Untuk detail implementasi fitur tertentu, lihat reference files:
> - `references/safety.md` - Security, rollback, cleanup
> - `references/monitoring.md` - Progress, ETA, state persistence
> - `references/self_healing.md` - Confidence, verification, human checkpoint

## Arsitektur Agent Teams

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TEAM: odoo-test-workflow                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │    QA      │  │   DEVOPS    │  │  DEVELOPER  │  │    ARCHITECT    │  │
│  │ (tester)   │  │  (upgrade)  │  │   (fix)     │  │    (analyze)    │  │
│  │ port: QA   │  │ port: DevOps│  │ custom_     │  │  odoo-base-     │  │
│  │             │  │             │  │ addons      │  │  understanding  │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
│         │                 │                 │                  │            │
│         └─────────────────┴────────┬────────┴──────────────────┘            │
│                                     │                                        │
│                                     ▼                                        │
│                           ┌─────────────────┐                              │
│                           │      LEAD       │                              │
│                           │  (koordinasi)   │                              │
│                           │                 │                              │
│                           └─────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## KEAMANAN WAJIB - Validasi Sebelum Eksekusi

**PERINGATAN: Semua tindakan WAJIB divalidasi sebelum eksekusi!**

### 🔴 ATURAN PENTING - Database WAJIB

**SETIAP AGENT WAJIB menggunakan HANYA database TEST hasil clone DevOps:**

| Agent | Boleh Akses | DILARANG Akses |
|-------|-------------|----------------|
| DevOps | ✅ Database sumber (untuk clone) + Test DB | ❌ Modifikasi data sumber |
| QA | ✅ HANYA Test DB | ❌ Database sumber/production |
| Click Tester | ✅ HANYA Test DB | ❌ Database sumber/production |
| Developer | ✅ HANYA custom addons (bukan DB) | ❌ Modifikasi production |
| Architect | ✅ Read-only ( CE/EE source code) | ❌ Modifikasi Apapun |

### Database Naming Rules

Nama database WAJIB mengandung suffix/prefix berikut:

| Tipe | Contoh | Status |
|------|--------|--------|
| ✅ Valid | `roedl_test_20260315`, `backup_production_20260315`, `roedl_dev` | OK |
| ❌ Tidak Valid | `roedl` (production), `upgraded` (tidak jelas) | DITOLAK |

### Operation Rules

**DILARANG keras:**
- ❌ `UPDATE`, `INSERT`, `DELETE` ke database sumber/asli
- ❌ Mengakses database production untuk testing
- ❌ QA dan Click Tester разрешается hanya pada database TEST saja
- ❌ Nama database sumber TIDAK BOLEH digunakan oleh agent lain (kecuali DevOps)

**BOLEH:**
- ✅ Clone/duplicate database untuk testing (HANYA DevOps)
- ✅ Read-only operations untuk analisis
- ✅ Semua perubahan dicatat di log file
- ✅ Semua agent (kecuali DevOps) wajib gunakan nama database dari DevOps

### Safety Validation Checklist

Sebelum eksekusi APAPUN, wajib checklist:

- [ ] Apakah ini database TEST/BACKUP?
- [ ] Apakah nama database sesuai aturan (mengandung test_, _test, backup_, dll)?
- [ ] Apakah ada backup sebelum perubahan?
- [ ] Apakah sudah dicek di `SAFETY LIMITS`?
- [ ] **Apakah QA/Click Tester menggunakan database hasil clone DevOps?**
- [ ] **Apakah TIDAK ada query/akses ke database sumber?**

### Audit Trail

Setiap aksi WAJIB di-log dengan:

```python
log(f"[{timestamp}] ACTION: {action}")
log(f"  Database: {database_name}")  # WAJIB: harus nama test DB, BUKAN sumber
log(f"  Module: {module_name}")
log(f"  Result: {result}")
```

## Agent Definitions

### Lead
- **Tugas**: Koordinasi workflow, validasi consensus QA+Architect, putuskan proceed/stop
- **Output**: Consensus decision + approved fix instructions

**Output Format WAJIB:**
```json
{
  "consensus": "approved|rejected",
  "error_summary": ["list of errors to fix"],
  "fix_instructions": "Developer instruction yang disepakati",
  "confidence": "low|medium|high",
  "human_approval_needed": true|false
}
```

- ✅ WAJIB: Verifikasi QA findings cocok dengan Architect analysis
- ✅ WAJIB: Putuskan proceed/stop berdasarkan confidence
- ✅ WAJIB: Berikan approved fix instructions ke Developer

### 1. QA Tester
- **Tugas**: Backend functional testing (NON-GUI)
- **Port**: QA Port (default 8134)
- **Tools**: odoo-module-test
- **Output**: Test report dengan passed/failed cases
- **Database**: WAJIB menggunakan HANYA database TEST hasil clone DevOps

- ❌ TIDAK: Browser automation, click testing, form interaction
- ❌ TIDAK: Akses ke database sumber/production
- ✅ WAJIB: Unit test, integration test, business logic validation
- ✅ WAJIB: Security testing (OWASP)
- ✅ WAJIB: Verifikasi nama database mengandung test_/backup_/_dev sebelum menjalankan test

### 2. DevOps Agent
- **Tugas**: Database operations DAN Upgrade module di test database
- **Port**: DevOps Port (default 8135)
- **Tools**: odoo-module-install, PostgreSQL tools
- **Python Environment**: Menggunakan Python venv dari project (lihat di odoo-environment)
- **Output**: Database operation dan upgrade success/failure report
- **Database**: SATU-SATUNYA agent yang BOLEH akses database sumber (untuk clone)

- ✅ Duplicate/cloning database untuk testing (dari sumber ke test)
- ✅ Create new database
- ✅ Drop test database (cleanup)
- ✅ Upgrade module di test database
- ✅ Restart Odoo instances
- ❌ DILARANG: Modifikasi data di database sumber/asli
- ❌ DILARANG: Langsung upgrade module di production

### 3. Click Tester
- **Tugas**: Click-anywhere test untuk deteksi JS errors
- **Port**: User Port (default 8136)
- **Tools**: odoo-click-anywhere-test
- **Output**: JS error report
- **Database**: WAJIB menggunakan HANYA database TEST hasil clone DevOps

- ❌ TIDAK: Akses ke database sumber/production
- ✅ WAJIB: Verifikasi nama database mengandung test_/backup_/_dev sebelum menjalankan test

### 4. Developer
- **Tugas**: Fix error berdasarkan solusi Architect
- **Location**: (lihat di odoo-environment - custom addons path)
- **Tools**: Edit, Write - fix kode di custom addons

**Security WAJIB:**
- ❌ DILARANG: `eval()`, `exec()`, `os.system()`, `subprocess` dengan user input
- ❌ DILARANG: SQL query concatenation (gunakan parameterized queries)
- ❌ DILARANG: menyimpan credentials di kode
- ✅ WAJIB: Input validation, Output encoding, CSRF tokens
- ✅ WAJIB: Access control checks di backend (bukan hanya frontend)
- ✅ WAJIB: Sanitasi semua user input sebelum display (XSS prevention)

### 5. Architect
- **Tugas**: Pahami Odoo architecture & workflow, JELASKAN mengapa error terjadi
- **Keluaran**: Root cause analysis + Fix instructions

**Output Format WAJIB:**
```json
{
  "errors": [
    {
      "error": "Error description",
      "why": "MENGAPA terjadi (root cause)",
      "where": "file/module/line",
      "how_to_fix": "langkah fix",
      "confidence": 85
    }
  ],
  "summary": "Ringkasan analisis"
}
```

- **WAJIB**: Pahami module ada di CE atau EE, bukan keduanya; pahami module structure, inheritance, business flow
- ✅ WAJIB: Pelajari codebase sebelum analisa (di PHASE 1)
- ✅ WAJIB: Berikan penjelasan MENGAPA bukan hanya APA yang error
- ✅ WAJIB: Berikan confidence score (0-100%) untuk setiap analisis
- ✅ WAJIB: Analisa error dari Click Tester DAN QA Test Results
- ✅ WAJIB: Confidence < 50% = HUMAN CHECKPOINT wajib
- ❌ TIDAK: Mulai analisa sebelum Click Tester menemukan error

## Step-by-Step Execution

**IMPORTANT - Peran Lead:**
- Lead **HANYA koordinasi** - TIDAK menjalankan test atau operasi database
- Lead **memerintahkan** agent lain untuk melakukan tugas
- Lead **tidak memiliki port Odoo** sendiri

### PHASE 1: Setup & Test Discovery (Lead orchestrates)

**SEQUENTIAL EXECUTION - DevOps harus selesai dulu:**

1. **DevOps: Clone Database** (Lead MEMERINTAHKAN DevOps, DevOps MENJALANKAN)
   - Duplicate database sumber ke test database
   - Nama database: `{original}_test_{date}` atau `backup_{original}_{date}`
   - Verifikasi cloning berhasil
   - **TUNGGU hingga selesai** - QA dan Click Tester TIDAK bisa mulai sebelum ini selesai
   - **SEMUA agent (QA, Click Tester, DevOps) menggunakan database test yang sama ini**

2. **SETELAH DevOps SELESAI, baru bisa jalankan:**

   a. **QA: Initial Test** (Lead MEMERINTAHKAN QA, QA MENJALANKAN)
      - Jalankan unit tests untuk get BASELINE
      - Identifikasi failures yang SUDAH ADA sebelum module diupgrade
      - Baseline = kondisi awal, bukan target fix
      - **QA harus tunggu DevOps selesai!**

   b. **Click Tester: Run Click Test** (Lead MEMERINTAHKAN Click Tester, Click Tester MENJALANKAN)
      - Click anywhere test untuk deteksi JS errors
      - Ini adalah sumber error utama untuk diperbaiki
      - **Click Tester harus tunggu DevOps selesai!**
      - **Lead TIDAK menjalankan ini sendiri!**

3. **Architect: Pelajari Project** (PARALLEL dengan QA/Click jika sudah ada database)
   - Pahami struktur module
   - Pahami module ada di CE atau EE (bukan keduanya)
   - Pahami business flow
   - Gunakan: odoo-base-understanding, odoo-business-process
   - TIDAK perlu tunggu error - belajar saat phase ini

### PHASE 2: Error Analysis (Lead orchestrates)

**SETELAH Click Tester menemukan error (PHASE 1) DAN Architect sudah pelajari project:**

1. **QA: Run Tests** (Lead MEMERINTAHKAN QA, QA MENJALANKAN)
   - Bedakan dari Initial Test: ini untuk dapat error YANG AKAN DIFIX
   - **Lead TIDAK menjalankan ini sendiri!**

2. **Architect: Analisa Error** (Lead MEMERINTAHKAN Architect, Architect MENJALANKAN)
   - Terima error dari Click Tester (JS errors) - dari PHASE 1
   - Terima error dari QA Tests (Python/backend errors)
   - Karena sudah belajar project, langsung bisa analisa
   - Jelaskan MENGAPA error terjadi (bukan hanya APA)
   - Identifikasi module ada di CE atau EE (bukan keduanya)
   - Berikan confidence score (0-100%) untuk setiap analisis

3. **Architect: Formulate Fix Instructions**
   - Ubah analysis jadi instruction yang jelas untuk Developer
   - Instruction WAJIB: Error apa, Mengapa, Bagaimana fix

4. **Lead: Konsolidasikan & Sepakati**
   - Verifikasi: Apakah findings QA sesuai dengan analisa Architect?
   - Jika confidence < 50% → HUMAN CHECKPOINT wajib (stop, minta approval manual)
   - Jika confidence 50-70% → proceed dengan caution
   - Jika confidence > 70% → proceed normal
   - Jika tidak cocok → Architect review ulang
   - Jika cocok → Output: consensus + approved fix instructions

### PHASE 3: Fix & Verify (Lead orchestrates)

1. **Lead: Berikan Instruksi ke Developer** (Lead MENULIS instruksi, Lead MENGERIMKAN ke Developer)
   - Instruksi WAJIB sudah disepakati QA + Architect
   - Jelaskan: Error apa, Mengapa terjadi, Bagaimana fix
   - **Lead TIDAK melakukan fix!**

2. **Developer: Apply Fix** (Lead MEMERINTAHKAN Developer, Developer MENJALANKAN)
   - Modify code berdasarkan instruksi yang disepakati

3. **DevOps: Upgrade Module** (Lead MEMERINTAHKAN DevOps, DevOps MENJALANKAN)
   - Apply changes ke test DB
   - **Lead TIDAK melakukan upgrade!**
   - IF upgrade fails:
     - Architect: Analisa error (kenapa upgrade gagal)
     - Developer: Fix code
     - DevOps: Retry upgrade
     - Max 3 retry

4. **Click Tester: Retest** (Lead MEMERINTAHKAN Click Tester, Click Tester MENJALANKAN)
   - Verifikasi error sudah diperbaiki

5. **QA: Verify Fix** (Lead MEMERINTAHKAN QA, QA MENJALANKAN)
   - Retest untuk confirm

6. **Lead: Cek Hasil Retest** - Jika ada ERROR BARU (tidak ada sebelumnya):
   - ERROR BARU = fix sebelumnya menyebabkan masalah baru
   - Architect: Analisa mengapa fix menyebabkan error baru
   - Kembalikan ke step Developer untuk fix error baru
   - Jika ERROR LAMA masih ada → iterasi ulang

### PHASE 4: Iteration Loop

**Retry hingga semua error fixed ATAU safety limit reached:**

```
WHILE errors_remain AND within_safety_limits:
    1. Click Tester: Run click test → CEK ERROR (yang belum terfix + error baru)
    2. QA: Run Tests → CEK ERROR LAIN (yang belum terfix + error baru)
    3. Architect: Refresh project knowledge jika perlu (sudah dipelajari di PHASE 1)
    4. Architect: Analisa error (MENGAPA terjadi) + confidence score
    5. Architect: Formulate Fix Instructions
    6. Lead: Konsolidasikan & Sepakati (QA + Architect)
    7. Developer: Apply fix
    8. DevOps: Upgrade module
    9. Click Tester: Retest
   10. IF errors_fixed:
         ✅ SUCCESS - exit loop
```

### PHASE 5: Cleanup (Lead orchestrates)

1. **DevOps: Stop Odoo instances**
2. **DevOps: Drop test database** (atau ask user)
3. **Lead: TeamCleanup** - Shutdown all agents

---

## Communication Protocol

**Semua komunikasi WAJIB melalui SendMessage:**

### Architect → Lead Message
```python
{
    "action": "ANALYZE_ERRORS",
    "context": {
        "click_tester_errors": [...],
        "qa_test_errors": [...]
    },
    "output": {
        "errors": [
            {
                "error": "Error description",
                "why": "MENGAPA terjadi",
                "where": "file/module/line",
                "how_to_fix": "langkah fix",
                "confidence": 85
            }
        ],
        "summary": "Ringkasan analisis"
    }
}
```

### Lead Response (Consensus)
```python
{
    "consensus": "approved|rejected",
    "error_summary": ["list of errors to fix"],
    "fix_instructions": "Developer instruction yang disepakati",
    "confidence": "low|medium|high",
    "human_approval_needed": true|false,
    "reason": "penjelasan jika rejected"
}
```

### Developer Message
```python
{
    "action": "APPLY_FIX",
    "context": {
        "fix_instructions": "dari Lead",
        "files_to_modify": [...]
    }
}
```

### DevOps Message
```python
{
    "action": "UPGRADE_MODULE",
    "result": "success|error",
    "error_message": "jika gagal",
    "retry_count": 0-3
}
```

---

## Configuration

**Base Configuration** - Untuk config dasar (database, paths, credentials, Python venv):
- Gunakan skill `odoo-environment`
- Ini mengambil config standar dari environment termasuk Python venv yang sudah ada
- Setiap agent menggunakan **venv yang sama** dari project (tidak membuat baru)

**Database yang Digunakan:**
- Semua agent menggunakan **database test yang sama** (hasil duplicate dari DevOps)
- Hanya satu database test untuk seluruh workflow
- Setiap agent menjalankan Odoo instance sendiri di port berbeda, tapi pointing ke database yang sama
- **🔴 PERINGATAN: QA dan Click Tester WAJIB menggunakan nama database yang diberikan DevOps!**

**Agent Ports** (berbeda dari base config):
| Agent | Port | Catatan |
|-------|------|---------|
| QA Tester | 8134 | Port untuk Odoo instance testing |
| DevOps | 8135 | Port untuk upgrade module |
| Click Tester | 8136 | Port untuk click-anywhere test |

**⚠️ PERINGATAN PENTING:**
- **JANGAN pernah** menggunakan nama database sumber/production
- **QA dan Click Tester**: Verifikasi nama database mengandung `test_`, `backup_`, `_dev` sebelum memulai
- DevOps akan memberikan nama database test SETELAH cloning selesai
- Lead WAJIB memberikan nama database test ke QA dan Click Tester

---

## Exit Criteria

Workflow SELESAI ketika:
1. ✅ QA test passed
2. ✅ Click-anywhere-test passed (0 JS errors)
3. ✅ Module ter-install/upgraded dengan sukses
4. ✅ Tidak ada error tersisa

ATAU jika mencapai SAFETY LIMITS:
5. ⚠️ MAX_ITERATIONS tercapai (5 iterasi)
6. ⚠️ MAX_DURATION tercapai (2 jam)
7. ⚠️ UNFIXABLE_ERRORS terdeteksi

---

## SAFETY LIMITS - WAJIB

**PERINGATAN: Batas ini WAJIB diikuti untuk mencegah infinite loop!**

### Quick Reference

| Limit | Value | Check Function |
|-------|-------|----------------|
| Max Iterations | 5 | `check_iteration_limit()` |
| Max Duration | 2 jam | `check_duration_limit()` |
| Max Agent Timeout | 5 menit | Agent timeout param |
| Min Fix Rate | 30% per iterasi | `check_convergence()` |

### When to Use References

**Untuk implementasi detail, lihat reference files:**

| Reference | Contains |
|-----------|----------|
| `references/safety.md` | Rollback mechanism, error handling, cleanup |
| `references/monitoring.md` | Progress reporting, time estimation, state persistence |
| `references/self_healing.md` | Confidence scoring, fix verification, human checkpoint |

---

## Catatan Penting

1. **Gunakan TeamCreate** - Jangan spawn agent tanpa team
2. **SEQUENTIAL EXECUTION WAJIB**:
   - DevOps SELESAI cloning database DULU
   - Baru QA dan Click Tester bisa mulai
   - Architect bisa parallel (tidak perlu database)
3. **Always communicate via SendMessage** - Jangan skip komunikasi formal
4. **Track tasks** - Gunakan TaskUpdate untuk status
5. **WAJIB Gunakan Safety Limits** - Selalu cek iteration/duration limits
6. **Emergency Stop** - User bisa menjalankan `touch /tmp/odoo_workflow_stop`

### Quick Reference: Emergency Stop

```bash
# Untuk stop workflow:
touch /tmp/odoo_workflow_stop
```
