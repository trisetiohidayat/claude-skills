---
name: odoo-agent-teams-v3
description: |
  Odoo testing & development workflow dengan 5 agent teams - Architect, Developer, DevOps, QA, dan Click Tester.
  Menggunakan PARALLEL execution - agents bekerja bersamaan sesuai best practice Claude Agent Teams.
  WAJIB gunakan Agent Teams (TeamCreate, Agent, SendMessage) dengan shared task list.

  Trigger saat: user ingin test/fix Odoo module dengan workflow tim 5 agents.
  Input: module_name, source_db, odoo_version (default: 19)
---

# Odoo Agent Teams v3

Skill ini mengorkestrasi workflow testing dan fixing Odoo dengan 5 agent yang berkomunikasi langsung via SendMessage dan menggunakan shared task list.

> v3 ini mengikuti Claude Agent Teams best practices: PARALLEL execution, shared task list, natural language communication.

---

## KEUNGGULAN v3 vs v2

| v2 (Lama) | v3 (Baru) |
|-----------|-----------|
| Sequential: DevOps dulu baru lain | Parallel: Semua bisa kerja bersamaan |
| Lead sebagai bottleneck | Shared task list + self-claim |
| Complex JSON protocol | Natural language communication |
| Rigid 5 phases | Flexible task dependencies |
| Manual checkpoint writing | Auto task tracking |

---

## Arsitektur

```
┌─────────────────────────────────────────────────────┐
│  Lead - Orchestrator (bukan executor)               │
│  - Create team + tasks                              │
│  - Monitor progress via task list                   │
│  - Wait for teammates to finish                    │
│  - Synthesize results                              │
├─────────┬─────────┬─────────┬─────────┬─────────────┤
│Architect│ Developer│ DevOps  │   QA    │ Click Tester│
│ → skill │ → skill │ → skill │ → skill │   → skill  │
└─────────┴─────────┴─────────┴─────────┴─────────────┘
```

---

## Agent Domain Skills

| Agent | Skills |
|-------|--------|
| **Architect** | `odoo-base-understanding`, `odoo-business-process`, `odoo-error-analysis` |
| **Developer** | `odoo19-model-*`, `odoo19-field-*`, `odoo-code-quality`, `odoo-security-review` |
| **DevOps** | `odoo-db-management`, `odoo-module-install` |
| **QA** | `odoo-module-test`, `odoo-debug-tdd` |
| **Click Tester** | `odoo-click-anywhere-test` |

---

## Input Format

| Parameter | Contoh | Deskripsi |
|-----------|--------|-----------|
| `module_name` | `{module_name}` atau `all` | Nama module, atau `all` untuk semua custom modules |
| `source_db` | (dari config atau input) | Database sumber - bisa dari config atau input user |
| `config_file` | (auto-detect) | Path ke config file Odoo (jika tidak diisi, auto-scan) |
| `odoo_version` | (auto-detect) | Versi Odoo - dideteksi dari config |

**module_name options:**
- `{specific_module}` - Nama module spesifik yang akan ditest/fix
- `custom-installed` - Custom modules yang terinstall di database
- `all-installed` - Semua modules yang terinstall di database (termasuk default Odoo)
- `custom-all` - Semua modules di custom addons directory (bukan default addons, tidak perlu install)

**Ketika `module_name = "custom-all"`:**
- Scan semua directories di addons_path yang BUKAN Odoo base/enterprise addons
- Include: modules di custom_addons/, bukan di odoo/addons/ atau enterprise/

**Konfigurasi dibaca dari file config Odoo** (tidak hardcoded):
- Port (84xx range, dari config)
- Database credentials (host, port, user, password, db_name dari config)
- Addons path (CE, EE, custom dari config)
- Default database name (bisa digunakan sebagai source_db)

Contoh pemanggilan:
```
/odoo-agent-teams-v3 --module my_custom_module
/odoo-agent-teams-v3 --module custom-installed    # custom modules yang terinstall
/odoo-agent-teams-v3 --module all-installed       # SEMUA terinstall (custom + default Odoo)
/odoo-agent-teams-v3 --module custom-all          # semua di custom addons directory (belum tentu install)
/odoo-agent-teams-v3 --module my_custom_module --source-db roedl
/odoo-agent-teams-v3 --module custom-all --config-file /path/to/odoo19.conf
```

---

## Input Validation (WAJIB)

Sebelum memulai workflow, Lead WAJIB deteksi konfigurasi secara dinamis:

### 1. Auto-Detect Config File

```python
import os
import glob
import re

def find_odoo_config(base_dir=None):
    """
    Cari file konfigurasi Odoo secara dinamis.
    base_dir: direktori project Odoo (default: cwd)
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Pattern nama config yang umum
    config_patterns = [
        "*.conf",           # odoo.conf, odoo19.conf
        "*odoo*.conf",      # odoo19.conf
        "*.cfg",            # odoo.cfg
    ]

    # Prioritas: cari di root dan subdirectory umum
    search_paths = [
        base_dir,
        os.path.join(base_dir, ".."),
    ]

    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        for pattern in config_patterns:
            matches = glob.glob(os.path.join(search_path, pattern))
            for match in matches:
                # Filter file yang mungkin bukan Odoo config
                filename = os.path.basename(match).lower()
                if 'test' in filename or 'sample' in filename:
                    continue
                return match

    return None
```

### 2. Parse Config Odoo

```python
import configparser

def parse_odoo_config(config_path):
    """
    Parse file konfigurasi Odoo dan ekstrak parameter yang diperlukan.
    """
    config = configparser.ConfigParser()
    config.read(config_path)

    # Ekstrak nilai-nilai penting
    result = {
        'http_port': config.get('options', 'http_port', fallback=None),
        'db_host': config.get('options', 'db_host', fallback='localhost'),
        'db_port': config.get('options', 'db_port', fallback='5432'),
        'db_user': config.get('options', 'db_user', fallback='odoo'),
        'db_password': config.get('options', 'db_password', fallback=''),
        'db_name': config.get('options', 'db_name', fallback=''),
        'addons_path': config.get('options', 'addons_path', fallback=''),
    }

    # Deteksi versi Odoo dari addons_path atau config file name
    result['odoo_version'] = detect_odoo_version(config_path, result.get('addons_path', ''))

    return result

def detect_odoo_version(config_path, addons_path):
    """
    Deteksi versi Odoo dari nama file config atau addons_path.
    """
    filename = os.path.basename(config_path).lower()

    # Cek dari nama file: odoo15.conf, odoo16.conf, etc.
    match = re.search(r'odoo(\d+)', filename)
    if match:
        return int(match.group(1))

    # Cek dari addons_path
    for version in [15, 16, 17, 18, 19, 20]:
        if f'odoo{version}' in addons_path.lower():
            return version
        if f'/odoo/{version}' in addons_path.lower():
            return version

    # Default ke 19 jika tidak terdeteksi
    return 19
```

### 3. KONFIRMASI CONFIG (WAJIB - Tanya User!)

**Setelah auto-detect dan parse config, Lead WAJIB tanya user untuk konfirmasi:**

```python
def confirm_config(config, detected_config_path):
    """
    Tampilkan konfigurasi yang terdeteksi dan minta konfirmasi dari user.
    """
    config_summary = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║           KONFIGURASI TERDETEKSI                          ║
    ╠═══════════════════════════════════════════════════════════╣
    ║ Config File: {detected_config_path}
    ║ Odoo Version: {config.get('odoo_version')}
    ║ HTTP Port: {config.get('http_port')}
    ║ Database Host: {config.get('db_host')}
    ║ Database Port: {config.get('db_port')}
    ║ Database User: {config.get('db_user')}
    ║ Database Name: {config.get('db_name')}
    ║ Addons Path: {config.get('addons_path')[:80]}...
    ╚═══════════════════════════════════════════════════════════╝
    """

    # Tanya user
    question = f"""
    {config_summary}

    Apakah konfigurasi di atas benar? Ketik:
    - 'ya' / 'y' / 'ok' untuk lanjut
    - 'tidak' / 'n' untuk abort
    - Atau masukkan nilai baru untuk override (misal: port=8133, db=roedl)
    """

    return user_response
```

**Contoh output ke user:**
```
═══════════════════════════════════════════════════════════════
           KONFIGURASI TERDETEKSI
═══════════════════════════════════════════════════════════════
  Config File: <PROJECT_ROOT>/odoo19.conf
  Odoo Version: 19
  HTTP Port: 8133
  Database Host: localhost
  Database Port: 5432
  Database User: odoo
  Database Name: roedl
  Addons Path: <PROJECT_ROOT>/enterprise-roedl-19.0/...
═══════════════════════════════════════════════════════════════

Ketik 'ya' untuk lanjut, 'tidak' untuk abort, atau masukkan override:
```

**Jika user Override:**
- Parse override values (format: key=value, key2=value2)
- Update config dengan nilai override
- Tampilkan config yang sudah di-update
- Tanya konfirmasi lagi

**Jika user Response tidak valid:**
- Tanya ulang dengan jelas

### 4. Validate module_name

```python
import os

def find_module_in_addons(module_name, addons_path):
    """
    Cari module di addons path (bisa multiple paths dipisahkan koma).
    """
    paths = addons_path.split(',')
    for path in paths:
        path = path.strip()
        # Cek di root addons
        module_path = os.path.join(path, module_name)
        if os.path.exists(module_path):
            return module_path

        # Cek di subdirectory (misal: custom_addons/roedl/module)
        for root, dirs, files in os.walk(path):
            if module_name in dirs:
                return os.path.join(root, module_name)

    return None

# Usage setelah parse config
module_path = find_module_in_addons(module_name, config['addons_path'])
if not module_path:
    # Tanya user: module tidak ditemukan, lanjut atau abort?
    pass
```

### 5. Validate source_db

```python
import subprocess

def check_database_exists(db_name, db_config):
    """
    Cek apakah database ada di PostgreSQL.
    """
    cmd = [
        "psql",
        "-h", db_config['db_host'],
        "-p", db_config['db_port'],
        "-U", db_config['db_user'],
        "-lqt"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, 'PGPASSWORD': db_config['db_password']}
    )

    db_list = [line.split("|")[0].strip() for line in result.stdout.split("\n") if line.strip()]
    return db_name in db_list

# Usage
if not check_database_exists(source_db, config):
    # Tanya user: database tidak ditemukan
    pass
```

**Jika validasi gagal**: Tanya user sebelum proceed.

---

## Display Mode

**Default: in-process** - semua teammates berjalan dalam terminal yang sama.

Gunakan Shift+Down untuk cycling antar teammates.

Jika ingin split panes (setiap teammate dapat pane sendiri), Lead bisa specify:
```
Display mode: split-panes (memerlukan tmux atau iTerm2)
```

---

## LANGKAH-LANGKAH WORKFLOW

### Step 1: Generate Target Database Name

```python
from datetime import datetime
target_db = f"{source_db}_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
# Contoh: roedl_test_20260318_143022
```

### Step 2: Create Team

```python
TeamCreate(
    team_name="odoo-fix-team",
    description="Odoo module testing dan fixing team untuk module {module_name}"
)
```

Spawn 5 teammates dengan detailed spawn prompts:

**1. Architect**
```
Prompt: "You are Odoo Architect, responsible for analyzing errors and finding root causes.
- Use skills: odoo-base-understanding, odoo-business-process, odoo-error-analysis
- Module: {module_name}, Odoo version: {odoo_version}
- Analyze JS errors found by Click Tester
- Explain WHY it happens (root cause), not just WHAT
- Give confidence score (0-100%)
- Provide specific fix steps
Report format: {error: "...", why: "...", confidence: 85, fix_steps: [...]}"
```

**2. Developer**
```
Prompt: "You are Odoo Developer, responsible for applying code fixes.
- Use skills: odoo-code-quality, odoo-security-review
- Module: {module_name}, Odoo version: {odoo_version}
- Apply fix based on Architect's analysis
- Only modify files in custom_addons, do not modify Odoo core code
- Ensure code follows Odoo 19 best practices
- If fix is complex, require plan approval"
Require: plan_approval (complex fixes need Lead approval)
```

**3. DevOps**
```
Prompt: "You are Odoo DevOps, responsible for database and module management.
- Use skills: odoo-db-management, odoo-module-install
- Odoo version: {odoo_version}
- Clone database: {source_db} -> {target_db}
- Upgrade module: {module_name}
- Verify operation success
- Clean up test database (after workflow ends)"
```

**4. QA**
```
Prompt: "You are Odoo QA, responsible for verifying fixes.
- Use skills: odoo-module-test, odoo-debug-tdd
- Database: {target_db}
- Module: {module_name}
- Run tests to verify fixes
- Check for regressions
- Report: {passed: [...], failed: [...], summary: "..."}"
```

**5. Click Tester**
```
Prompt: "You are Odoo Click Tester, responsible for detecting JS errors.
- Use skill: odoo-click-anywhere-test
- Database: {target_db}
- Odoo version: {odoo_version}
- Run click anywhere test
- Report all JS errors: {error_type, location, stack_trace}"
```

### Step 3: Create Tasks (Optimized - 5-6 tasks per agent)

Buat tasks di task list - agents akan self-claim:

```python
# Task 1: Clone DB (DevOps - blocker untuk banyak task lain)
task_clone_db = TaskCreate(
    subject="Clone database {source_db} ke {target_db}",
    description=f"""
    - Clone database {source_db} ke {target_db}
    - Verifikasi cloning berhasil
    - Jangan modifikasi database sumber
    - Odoo version: {odoo_version}
    """,
    addBlockedBy=[]
)

# Task 2: Study Module (Architect - parallel, tidak perlu DB)
task_study = TaskCreate(
    subject=f"Pelajari struktur module {module_name}",
    description=f"""
    - Cari module {module_name} di custom_addons
    - Pahami struktur: models, views, controllers, static/src
    - Identifikasi file yang mungkin bermasalah
    - Odoo version: {odoo_version}
    """,
    addBlockedBy=[]
)

# Task 3: Click Test (Click Tester - depends on DB)
task_click_test = TaskCreate(
    subject="Run click anywhere test",
    description=f"""
    - Jalankan click test di database {target_db}
    - Gunakan Odoo version {odoo_version}
    - Deteksi semua JS errors
    - Catat: error type, location, stack trace
    """,
    addBlockedBy=[task_clone_db]
)

# Task 4: Analyze Error (Architect - depends on Click Test)
task_analyze = TaskCreate(
    subject="Analisa error dan root cause",
    description=f"""
    - Terima error dari Click Tester
    - Analisa MENGAPA terjadi (bukan hanya APA)
    - Berikan confidence score (0-100%)
    - Berikan langkah fix yang spesifik
    """,
    addBlockedBy=[task_click_test]
)

# Task 5: Apply Fix (Developer - depends on Analyze)
# COMPLEX FIX = require plan approval
task_apply_fix = TaskCreate(
    subject="Apply code fix",
    description=f"""
    - Apply fix berdasarkan instruksi Architect
    - Gunakan skill: odoo-code-quality
    - Jangan modifikasi production
    - Module: {module_name}, Odoo version: {odoo_version}
    - Complex fix: require plan approval from Lead
    """,
    addBlockedBy=[task_analyze]
)

# Task 6: Upgrade Module (DevOps - depends on Apply Fix)
task_upgrade = TaskCreate(
    subject="Upgrade module di test DB",
    description=f"""
    - Upgrade module {module_name} di database {target_db}
    - Odoo version: {odoo_version}
    - Verifikasi upgrade berhasil
    """,
    addBlockedBy=[task_apply_fix]
)

# Task 7: QA Verify (QA - depends on Upgrade)
task_qa_verify = TaskCreate(
    subject="Verify fix dengan QA test",
    description=f"""
    - Jalankan QA tests untuk verify fix
    - Database: {target_db}
    - Module: {module_name}
    - Verifikasi tidak ada regression
    """,
    addBlockedBy=[task_upgrade]
)
```

### Step 4: Execution - PARALLEL

**KEY PRINCIPLE**: WAIT FOR TEAMMATES TO FINISH.

```
Lead: "Wait for your teammates to complete their tasks before proceeding"
```

Task Dependencies (visual):
```
[Task 1: Clone DB] ──────────► [Task 3: Click Test] ────────► [Task 4: Analyze]
        │                              │                              │
        │                              │                              ▼
        │                              │                     [Task 5: Apply Fix]
        │                              │                              │
        │                              │                              ▼
        │                              │                     [Task 6: Upgrade]
        │                              │                              │
        ▼                              │                              ▼
[Task 2: Study Module] ───────────────┴─────────────────► [Task 7: QA Verify]
```

Execution:
- Task 1 & 2: Parallel (tidak saling blocking)
- Task 3: Depends on Task 1 (DB harus ada)
- Task 4: Depends on Task 3 (harus dapat error dulu)
- Task 5: Depends on Task 4 (fix instruction dari Architect)
- Task 6: Depends on Task 5 (code sudah di-fix)
- Task 7: Depends on Task 6 (module sudah di-upgrade)

---

## Communication Patterns

### Natural Language (Bukan JSON!)

**BENAR**:
```
Lead: "DevOps, clone database roedl ke roedl_test_20260318_143022"
DevOps: [working...]
Lead: "Architect, sementara DevOps clone DB, kamu bisa mulai pelajari struktur module {module_name}"
```

**SALAH** (v2 style):
```json
{
  "action": "CLONE_DB",
  "database": "roedl_test_xxx"
}
```

### Direct Agent Communication

Agents bisa communicate langsung, tidak perlu selalu lewat Lead:

```
Click Tester: "Architect, saya nemu JS error di custom_view.js:42 - undefined property"
Architect: "Oke, saya analisa - itu karena record.name belum ready waktu onload"
Architect: "Developer, fix-nya: tambahkan if (!record.name) return; di awal onload"
Developer: "Oke, saya apply"
```

---

## Lead Responsibilities

### BOLEH:
1. ✅ Create tasks dan assign
2. ✅ Monitor task list progress via TaskList
3. ✅ Kirim reminder ke agents yang idle
4. ✅ Tanya user (human checkpoint)
5. ✅ Synthesize results dari agents
6. ✅ Wait for teammates to finish (JANGAN eksekusi sendiri!)

### TIDAK BOLEH:
1. ❌ Eksekusi task langsung (jalanin command, clone DB, dll)
2. ❌ Skip agent dan kerjakan sendiri
3. ❌ Micro-manage setiap step

### ⏰ WAIT FOR TEAMMATES

**PENTING**: Lead HARUS tunggu agents selesai sebelum melanjutkan.

Jika Lead terdeteksi menjalankan task sendiri:
```
"Tunggu sampai teammates selesai sebelum melanjutkan work"
```

---

## Plan Approval untuk Complex Fixes

Untuk fix yang kompleks/berisiko, Developer WAJIB minta approval dari Lead:

**Kapan require plan approval:**
- Modifikasi database schema
- Menambah/menghapus field di production
- Perubahan yang mempengaruhi multiple modules
- Fix dengan confidence < 70%

**Proses:**
```
Developer: "Fix ini kompleks, saya perlu buat plan dulu"
Lead: "Oke, buat plan dulu"

Developer (plan mode): "Plan: 1. Backup, 2. Modify X, 3. Test Y"
Lead: "Approved - proceed"

ATAU

Lead: "Plan ini kurang, tambahkan rollback mechanism"
Developer: [revise plan] -> Lead: "Approved"
```

---

## Agent Stuck Handling

Jika agent stuck atau idle > 3 menit:

1. **Kirim reminder**: "Silakan eksekusi task atau kabari jika ada masalah"
2. **Tunggu 1 menit**
3. **Jika masih stuck**:
   - Tanya agent: "Apa yang kamu tunggu? Ada blocker?"
   - Jika agent tidak responsif → TaskUpdate dengan status `blocked` dan jelaskan issue
4. **Intervention** (jika perlu):
   - Lead BOLEH interven tapi TIDAK boleh eksekusi
   - Contoh: "Architect, DevOps butuh 5 menit lagi. Sementara itu, kamu bisa review module structure dulu"

---

## Human Checkpoint Scenarios

Tanya user pada kondisi:

| Kondisi | Tindakan |
|--------|----------|
| Confidence < 50% | Proceed atau abort? |
| Fix menyebabkan error baru | Continue atau rollback? |
| Semua 5 iterasi habis | Extend atau stop? |
| DB clone gagal | Retry atau abort? |
| Module upgrade gagal | Force install atau skip? |
| Complex fix (plan approval) | Approve plan atau give feedback? |

---

## Safety Rules

- **TIDAK PERNAH** modifikasi production database
- Database name WAJIB: `test_`, `_test`, `backup_`, `_dev`
- QA & Click Tester WAJIB gunakan database hasil clone DevOps
- Max 5 iterations

---

## Cleanup (WAJIB)

**PERINGATAN: Cleanup HANYA boleh dilakukan setelah SEMUA tasks selesai!**

### Step 0: Verifikasi Semua Tasks Selesai
```python
# CEK DULU - jangan pernah cleanup jika ada tasks yang belum selesai
from TaskList import TaskList
tasks = TaskList()
pending_tasks = [t for t in tasks if t['status'] != 'completed']

if pending_tasks:
    print(f"⚠️  Ada {len(pending_tasks)} task yang belum selesai:")
    for t in pending_tasks:
        print(f"  - {t['subject']} ({t['status']})")
    print("\n⏸️  TUNGGU sampai semua tasks selesai sebelum cleanup!")
    print("Jika ingin FORCELESS cleanup, ketik 'force' untuk melanjutkan")
    # JANGAN eksekusi cleanup jika ada tasks pending!
```

### Step 1: Shutdown Agents
```python
# Lewat Lead
SendMessage(to="*", message={"type": "shutdown_request", "reason": "Workflow complete"})
```

### Step 2: Stop Odoo Service

```python
# Stop Odoo service berdasarkan port dari config
def stop_odoo_service(http_port):
    """
    Stop Odoo service berdasarkan port yang digunakan.
    """
    import subprocess
    # Kill process yang menggunakan port tersebut
    subprocess.run(["pkill", "-f", f"odoo.*{http_port}"], check=False)

    # Alternative: via lsof
    # result = subprocess.run(["lsof", "-ti", f":{http_port}"], capture_output=True, text=True)
    # if result.stdout:
    #     pids = result.stdout.strip().split('\n')
    #     for pid in pids:
    #         subprocess.run(["kill", "-9", pid], check=False)

# Usage
stop_odoo_service(config['http_port'])
```

### Step 3: Drop Test Database (WAJIB KONFIRMASI)
```python
# ⛔ WAJIB KONFIRMASI SEBELUM DROP DATABASE!
# Jangan pernah auto-drop tanpa konfirmasi user

def drop_test_database(db_config, target_db):
    """
    Drop test database dengan konfirmasi.
    """
    print(f"\n⚠️  AKAN MELAKUKAN DROP DATABASE:")
    print(f"   Database: {target_db}")
    print(f"\nKetik 'ya' atau 'y' untuk CONFIRM drop")
    print("Ketik 'tidak' atau 'n' untuk BATAL (database tetap ada)")
    print("Ketik 'skip' untuk SKIP (tidak drop tapi lanjut cleanup lain)")

    # ⛔ JANGAN eksekusi langsung - minta konfirmasi!
    return  # Returns early - calling code harus handle confirmation

# ⛔ JANGAN PANGGIL fungsi ini langsung!
# Gunakan AskUserQuestion untuk konfirmasi:
"""
Question: "DevOps akan drop database test {target_db}. Lanjutkan?"
Options:
- ya - Drop database (hapus test database)
- tidak - Batal (database tetap ada)
- skip - Skip drop saja (stop Odoo & shutdown agents)
"""
```

```bash
# HANYA eksekusi jika user sudah KONFIRMASI 'ya':
# Via psql - perlu terminate active connections dulu
psql -U odoo -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '{target_db}' AND pid <> pg_backend_pid();
"

psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS {target_db};"
echo "✅ Database {target_db} berhasil dihapus"
```

### Step 4: Cleanup Team
```python
TeamDelete()
```

### Step 5: Verify Cleanup
```python
# Verify Odoo tidak running di port yang diharapkan
import subprocess
import os

def verify_odoo_stopped(http_port):
    """Verify Odoo tidak running di port."""
    result = subprocess.run(
        ["lsof", "-i", f":{http_port}"],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip()) == 0

def verify_database_dropped(db_config, target_db):
    """Verify database sudah dihapus."""
    cmd = [
        "psql",
        "-h", db_config['db_host'],
        "-p", db_config['db_port'],
        "-U", db_config['db_user'],
        "-lqt"
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, 'PGPASSWORD': db_config['db_password']}
    )
    db_list = [line.split("|")[0].strip() for line in result.stdout.split("\n") if line.strip()]
    return target_db not in db_list

# Usage
if not verify_odoo_stopped(config['http_port']):
    print("Warning: Odoo may still be running")
if not verify_database_dropped(config, target_db):
    print("Warning: Database may still exist")
```

**Kenapa WAJIB cleanup:**
1. Test database uses disk space
2. Odoo service harus di-stop agar tidak conflict di lain waktu
3. Agents harus di-shutdown agar tidak consume resources

---

## Error Recovery

| Error | Recovery |
|-------|----------|
| DB Clone gagal | Retry max 3x → Tanya user: abort atau skip? |
| Module upgrade gagal | Retry max 3x → Tanya user: force atau skip? |
| Click Test timeout | Retry 1x → Tanya user: skip atau continue? |
| Developer fix failed | Revert code → Tanya Architect untuk solusi lain |
| QA test failed | Analyse → Developer fix → DevOps upgrade → QA retry |

---

## Timeout Configuration

Setiap operation memiliki maximum timeout:

| Operation | Timeout | Action Jika Timeout |
|-----------|---------|---------------------|
| DB Clone | 5 menit | Retry 1x → Tanya user |
| Module Upgrade | 3 menit | Retry 1x → Tanya user |
| Click Test | 5 menit | Retry 1x → Skip atau continue |
| QA Test | 5 menit | Retry 1x → Tanya user |
| Agent Stuck | 3 menit | Kirim reminder → Intervention |

**Implementasi Timeout:**

```python
# Contoh timeout handling untuk DevOps
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation exceeded timeout")

# Set timeout (5 menit = 300 detik)
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(300)

try:
    # Operation: clone database
    result = clone_database(source_db, target_db)
    signal.alarm(0)  # Cancel alarm
except TimeoutError:
    # Retry atau Tanya user
    pass
```

**LeadWAJIB monitor timeout dan Tanya user jika exceeded.**

---

## Quick Reference

| Topic | Notes |
|-------|-------|
| Parallel execution | Semua agent kerja bersamaan, bukan sequential |
| Shared task list | Agents self-claim available tasks |
| Natural language | Jangan pakai complex JSON protocol |
| Task dependencies | Gunakan addBlockedBy dengan task ID |
| Lead role | Orchestrator, bukan executor |
| Wait for teammates | JANGAN eksekusi sendiri, tunggu agents |
| Plan approval | Complex fixes perlu Lead approval |
| Auto-detect config | Scan project untuk *.conf file, parse nilai |
| Odoo version | Dideteksi dari config file name atau addons_path |
| Port | Dideteksi dari config (tidak hardcoded) |
| DB credentials | Dideteksi dari config (tidak hardcoded) |
| Cleanup | Drop DB + Stop Odoo + Shutdown agents |

---

## Example Workflow

```
User: "/odoo-agent-teams-v3 --module {module_name}"
# Atau untuk custom modules yang terinstall:
User: "/odoo-agent-teams-v3 --module custom-installed"
# Atau untuk SEMUA yang terinstall (custom + default Odoo):
User: "/odoo-agent-teams-v3 --module all-installed"
# Atau untuk semua module di custom directory:
User: "/odoo-agent-teams-v3 --module custom-all"

Lead:
1. Auto-detect config file:
   - Scan project directory untuk *.conf files
   -找到 odoo19.conf

2. Parse config:
   - http_port: 8133 (dari config)
   - db_host: localhost, db_port: 5432, db_user: odoo (dari config)
   - addons_path: /path/to/custom_addons (dari config)
   - odoo_version: 19 (dari filename)

3. **KONFIRMASI CONFIG** (Tanya User!):
   - Tampilkan semua nilai config yang terdeteksi
   - Tanya user: "Apakah konfigurasi di atas benar?"
   - Jika user override, update config dan tanya lagi
   - Jika user reject (tidak), abort workflow

5. target_db = roedl_test_20260318_143022

6. Validate:
   - Module exists di addons_path
   - Database roedl exists

7. TeamCreate dengan 5 agents (dengan detailed spawn prompts)
   - Pass config ke setiap agent

8. Display mode: in-process (default)

9. Create 7 tasks dengan dependencies:
   - Task 1 (clone_db): addBlockedBy=[]
   - Task 2 (study): addBlockedBy=[]
   - Task 3 (click_test): addBlockedBy=[Task 1]
   - Task 4 (analyze): addBlockedBy=[Task 3]
   - Task 5 (apply_fix): addBlockedBy=[Task 4], require plan_approval if complex
   - Task 6 (upgrade): addBlockedBy=[Task 5]
   - Task 7 (qa_verify): addBlockedBy=[Task 6]

8. ⏰ WAIT for teammates - JANGAN eksekusi sendiri!

9. Agents self-claim - Task 1 & 2 bisa diambil bersamaan

10. Monitor via TaskList - jika stuck > 3 min, kirim reminder

11. Synthesis results

12. Cleanup (WAJIB dengan verifikasi):
    - ⏰ CEK DULU: Pastikan SEMUA tasks sudah completed (TaskList)
    - Minta KONFIRMASI user sebelum drop database:
      - "Drop database {target_db}? [ya/tidak/skip]"
    - Shutdown agents
    - Stop Odoo service (berdasarkan port dari config)
    - Drop test database HANYA jika user konfirmasi 'ya'
    - TeamDelete
```
