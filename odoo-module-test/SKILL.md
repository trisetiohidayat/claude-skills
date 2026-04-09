---
name: odoo-module-test
description: |
  Test Odoo modules (custom atau built-in) dengan COMPREHENSIVE analysis dan DETAILED test plan.
  Compatible untuk main agent DAN subagent.

  Gunakan skill ini ketika:
  - User meminta "test module X"
  - User meminta "run tests untuk module Odoo"
  - User ingin menjalankan TransactionCase/HttpCase tests
  - User ingin test custom modules atau module bawaan Odoo
  - User ingin migrate atau verify module compatibility
  - User ingin test BANYAK MODULE SECARA PARALEL (batching)
  - Subagent perlu menjalankan test module Odoo

  **FITUR PARALEL EXECUTION:**
  - Supports parallel testing untuk multiple modules
  - Setiap module ditest secara independen oleh subagent berbeda
  - Batch 3-4 modules sekaligus (tergantung resources)
  - Main agent sebagai coordinator - collects results dari semua subagents

  PENTING: Skill ini TIDAK HANYA menjalankan test yang sudah ada, tapi juga:
  1. **Analisa module secara mendalam** - semua models, fields, methods, business logic
  2. **Identifikasi dependencies** - module lain yang terkait
  3. **Sugesti test baru** - fitur yang belum ditest
  4. **Perbaiki test yang kurang tepat** - existing tests yang perlu diupdate
  5. **Generate detailed test plan** dengan:
     - Apa yang diuji (test purpose)
     - Langkah-langkah test (test steps)
     - Models yang digunakan
     - Assertions yang dilakukan
     - Expected results

  Execution dilakukan sesuai test plan yang diapprove user.

  Supports Odoo versi 10-19, CE dan EE.
  Subagent: auto-approve, absolute paths.
---

## Path Resolution
GUNAKAN odoo-path-resolver untuk mendapatkan paths. Contoh:
```python
# Load paths
paths = resolve()

# Get values
python = paths['odoo']['python']  # /path/to/python
odoo_bin = paths['odoo']['bin']  # /path/to/odoo-bin
config = paths['project']['config']  # /path/to/odoo.conf
custom_paths = paths['addons']['custom']  # list of custom addons paths
project_root = paths['project']['root']
```

# Odoo Module Test Skill

## Overview

Skill ini menjalankan tests untuk module Odoo dengan dua mode:

### Mode 1: Sequential (Single Module)
1. **Analyze** - Analisa module untuk menentukan test plan
2. **Plan** - Buat test plan list
3. **Approve** - User approve/modify plan
4. **Execute** - Jalankan tests yang sudah diapprove
5. **Report** - Generate dokumentasi hasil testing

### Mode 2: Parallel (Multiple Modules) - REKOMENDASI
1. **Batch Modules** - Bagi modules menjadi batch 3-4 modules
2. **Spawn Subagents** - Jalankan subagent secara paralel (tiap subagent test 1 module)
3. **Analysis + Existing Tests** - Jalankan existing tests + analisa module
4. **Create Missing Tests (JIKA PERLU)** - Jika analisa menemukan fitur belum ditest, buat dan jalankan test baru
5. **Collect Results** - Kumpulkan hasil dari semua subagents
6. **Generate Summary** - Buat ringkasan dari semua module

**KEUNTUNGAN PARALLEL MODE:**
- Tidak perlu menunggu analisis semua module selesai
- Test dimulai segera setelah subagent menerima tugas
- Lebih efisien untuk testing banyak module
- Setiap subagent Independen - bisa gagal/sukes tanpa mempengaruhi others

## Step 0: Mode Selection (WAJIB)

**Tanyakan ke user mode yang diinginkan:**

Gunakan AskUserQuestion:
```json
{
  "questions": [{
    "question": "Pilih mode testing yang diinginkan:",
    "header": "Mode",
    "options": [
      {"label": "Parallel (Recommended)", "description": "Test 3-4 module sekaligus secara paralel dengan subagents"},
      {"label": "Sequential", "description": "Test satu per satu secara berurutan"}
    ],
    "multiSelect": false
  }]
}
```

**REKOMENDASI:**
- Jika testing > 1 module → Gunakan **Parallel Mode**
- Parallel Mode jauh lebih efisien karena subagents bekerja bersamaan

---

## Step 0B: Parallel Mode - Batch Modules

**JIKA USER MEMILIH PARALLEL MODE:**

### 0B.1 Identifikasi Modules dengan Test Files

Cek modules yang memiliki test files:
```bash
find <modules_folder> -name "test_*.py" 2>/dev/null | xargs dirname | sort -u
```

### 0B.2 Bagi Modules ke dalam Batches

**BATASAN:**
- Maksimal **4 subagents paralel** dalam satu batch (untuk menghindari overload)
- Jika > 4 modules, bagi menjadi beberapa batches

**Contoh:**
- 10 modules → Batch 1 (4) + Batch 2 (4) + Batch 3 (2)
- 3 modules → 1 batch saja

### 0B.3 Prepare Subagent Tasks (ROBUST MODE)

Untuk setiap batch, spawn subagents secara **PARALEL** dengan prompt:
```
Test module <module_name> di Odoo 19 EE dengan database <database_name>.
Gunakan skill odoo-module-test.

Modules folder: paths['addons']['custom'][0] + '/'

TUGAS UTAMA:
1. ANALISA module - pahami semua models, fields, methods, business logic
2. JALANKAN existing tests - transactioncase dan httpcase
3. IDENTIFIKASI missing tests - fitur yang BELUM ditest
4. BUAT test baru jika perlu - untuk fitur yang belum diuji
5. JALANKAN test baru tersebut
6. GENERATE report dengan coverage analysis

PENTING: Module dianggap "READY" hanya jika:
- Semua existing tests PASS
- Semua fitur sudah ditest (existing + new)
- Coverage analysis menyatakan COMPLETE
```

**ROBUST MODE - Setiap subagent WAJIB:**
- Setiap subagent.handle SATU module saja
- Subagent akan: analyze → test existing → identify gaps → create/run new tests → report
- **JANGAN skip pembuatan test baru jika analisa menemukan fitur belum ditest**
- Main agent hanya mengkoordinir dan collect results

### 0B.4 Execute Parallel

**Gunakan Agent tool untuk spawn multiple subagents:**

```python
# Batch 1 - 4 modules
Agent(subagent_type="general-purpose", prompt="Test module X...")
Agent(subagent_type="general-purpose", prompt="Test module Y...")
Agent(subagent_type="general-purpose", prompt="Test module Z...")
Agent(subagent_type="general-purpose", prompt="Test module W...")

# Tunggu semua selesai, baru lanjut ke batch berikutnya
```

### 0B.5 Collect Results

Setelah semua subagent selesai:
1. Terima result dari setiap subagent
2. Generate ringkasan dari semua module
3. Simpan ke file summary

---

## Step 1: Clarifikasi Requirements Awal

**Untuk Subagent:** Jika dijalankan dari subagent, skip clarifikasi dan gunakan default:
- Module: dari task description
- Version: dari project context (cek odoo.conf)
- Edition: EE (default) jika tidak yakin
- Database: dari project context

**Untuk Main Agent:** Tanyakan ke user jika belum jelas:

1. **Module yang mau ditest:**
   - Custom module: dari folder custom_addons_19, custom_addons_19_new, custom_addons_19_new2
   - Built-in module: hr, sale, purchase, dll

2. **Odoo version dan edition:**
   - Community Edition (CE) atau Enterprise Edition (EE)
   - Versi: 10, 11, 12, 13, 14, 15, 16, 17, 18, atau 19

3. **Database untuk testing (WAJIB ditanyakan):**
   CEK dulu database yang tersedia:
   ```bash
   psql -h localhost -p 5432 -U odoo -lqt | cut -d \| -f 1 | grep -w <database>
   ```

   Tanyakan ke user dengan options:
   - **Gunakan database existing**: Pilih dari list database yang ada (cek dulu dengan psql)
   - **Buat database baru**: Buat database baru untuk testing (naming convention: <module>_test_<version>, misal: hr_course_test_19)
   - **Restore dari backup**: Jika user punya backup file

   GUNAKAN AskUserQuestion untuk tanya user:
   ```json
   {
     "questions": [{
       "question": "Database mana yang akan digunakan untuk testing?",
       "header": "Database",
       "options": [
         {"label": "Gunakan existing", "description": "Pilih dari database yang sudah ada"},
         {"label": "Buat baru", "description": "Buat database baru untuk testing"},
         {"label": "Restore backup", "description": "Restore dari file backup"}
       ],
       "multiSelect": false
     }]
   }
   ```

   Jika user pilih "Gunakan existing", tampilkan list database yang tersedia dan minta pilih.

   Jika user pilih "Buat baru":
   - Tanya nama database yang diinginkan ATAU generate otomatis dengan format `<module>_test_<version>`, misal: `hr_course_test_19`
   - Buat database menggunakan Odoo:
     ```bash
     createdb -h localhost -p 5432 -U odoo <database_name>
     ```
   - Atau jalankan Odoo untuk membuat database secara otomatis saat pertama kali start

   Jika user pilih "Restore backup":
   - Tanya lokasi file backup (format .zip atau .dump)
   - Gunakan skill `odoo-db-restore` untuk restore database
   - Atau gunakan command:
     ```bash
     # Restore dari zip backup
     unzip -p <backup.zip> database.sql | psql -h localhost -p 5432 -U odoo -d <database_name>
     ```

## Step 2: Analyze Module

**PRIORITAS UTAMA - ALWAYS RUN FRESH TESTS:**
- JANGAN pernah skip running tests karena ada dokumentasi yang sudah ada
- Dokumentasi yang ada mungkin outdated atau tidak akurat
- Selalu jalankan test ulang (fresh test) setiap kali skill ini dipanggil
- Abaikan status/dokumentasi yang sudah ada sebelumnya

### 2.1 Deteksi Odoo Configuration

Cek configuration yang tersedia:

1. **Cek launch.json** (jika ada):
   ```
   .vscode/launch.json
   ```
   Extract: port, database, python path, odoo-bin

2. **Cek odoo.conf:**
   ```
   odoo19.conf (Odoo 19)
   odoo.conf (Odoo 15)
   ```
   Extract: db_host, db_port, db_user, db_password, addons_path

3. **Tentukan command:**
   - Odoo 19: `./odoo-bin -c odoo19.conf -d <db>`
   - Odoo 15: `./odoo-bin -c odoo.conf -d <db>`
   - Gunakan Python venv yang sesuai (venv19 untuk Odoo 19, venv untuk Odoo 15)

### 2.2 Analisa Module Structure

Lakukan analisis mendalam terhadap module:

1. **Cek module location:**
   ```
   custom_addons_19_new2/roedl/<module_name>/
   custom_addons_19/roedl/<module_name>/
   odoo19.0-roedl/odoo/addons/<module_name>/
   enterprise-roedl-19.0/enterprise/<module_name>/
   ```

2. **Identifikasi Test Files:**
   ```
   <module>/tests/test_*.py
   ```

3. **Cek Test Classes:**
   Dari setiap test file, identify:
   - TransactionCase tests (backend)
   - HttpCase tests (frontend)
   - Portal tests
   - Other test types

4. **Cek Test Tags:**
   Dari @tagged decorator, extract tags seperti:
   - `post_install`, `at_install`
   - Module name tags
   - Category tags (http, portal, etc.)

5. **Cek Models yang ditest:**
   Identify semua model yang digunakan dalam tests

6. **Cek Dependencies:**
   - Module dependencies dari __manifest__.py
   - External dependencies (libraries, services)

### 2.3 Comprehensive Module Analysis (WAJIB - JANGAN SKIP!)

**PENTING: Agent harus memahami module SECARA MENyeluruh, tidak hanya melihat test yang sudah ada.**

**JANGAN LUPA: Ini adalah STEP PALING PENTING dalam skill ini!**

Analisis ini WAJIB dilakukan untuk:
1. Memahami apa saja funcionalidad module (bukan hanya test yang sudah ada)
2. Mengidentifikasi fitur yang BELUM ditest
3. Menentukan apakah test yang ada SUDAH COVERAGE atau KURANG
4. Memberikan rekomendasi improvement jika test kurang memadai

**Jika diminta beberapa module sekaligus (multiple modules), agent HARUS:**
1. Analisa SETIAP module secara individual
2. Identifikasi fitur apa saja yang ada di setiap module
3. Bandingkan dengan test yang sudah ada
4. Jika test coverage KURANG, suggested improvements

Lakukan analisis mendalam untuk memahami module:

#### A. Analisa Models (dari files .py di module)

1. **Cek semua model di module:**
   ```
   <module>/models/*.py
   ```
   - Model apa saja yang didefinisikan
   - Fields apa saja di setiap model
   - Methods apa saja di setiap model

2. **Identifikasi Business Logic:**
   - Workflow/state machine
   - Computed fields
   - Onchange methods
   - Constraint methods (@api.constrains)
   - Action methods (def action_xxx)
   - Override methods dari module lain

3. **Cek Dependencies dan Extensions:**
   - Model mana yang inherits dari module lain
   - Field extensions dari module lain
   - Override methods

#### B. Analisa Views (dari files .xml di module)

1. **Cek form views, tree views, kanban views:**
   ```
   <module>/views/*.xml
   ```
   - Fields apa saja yang ditampilkan
   - Buttons apa saja yang tersedia
   - Business logic dari button actions

2. **Cek Wizards:**
   ```
   <module>/wizard/*.py
   ```
   - Wizard models yang tersedia
   - Actions yang dilakukan wizard

#### C. Analisa Existing Tests

1. **Cek test files yang ada:**
   ```
   <module>/tests/test_*.py
   ```

2. **Evaluasi existing tests:**
   - Test apa saja yang sudah ada
   - Apakah sudah cover semua functionality?
   - Apakah ada gap/fitur yang belum ditest?
   - Apakah test assertions sudah tepat?

3. **Jalankan existing tests dulu:**
   - Jalankan test yang sudah ada untuk memastikan baseline works
   - Catat hasil: pass/fail/error
   - Ini jadi dasar untuk menentukan apa yang perlu ditambah

#### D. Identifikasi ALL Features vs Tested Features (CRITICAL!)

**PENTING: Langkah ini WAJIB untuk menentukan coverage yang SEBENARNYA!**

Setelah analisis model di section A dan existing tests di section C, buat tabel PERBANDINGAN:

1. **List SEMUA method/feature yang ada di module:**
   - Semua `def action_*` methods
   - Semua `def *_onchange` methods
   - Semua `def _compute_*` methods
   - Semua `@api.constrains` methods
   - Semua button handlers
   - Semua workflow methods
   - Semua override methods dari parent class

2. **Cek apa yang SUDAH ditest:**
   - Bandingkan dengan test methods yang ada di test_*.py
   - Setiap test method, identifikasi method apa yang di-test

3. **Hasil: Tabel Features vs Tested:**

   | # | Feature/Method | Ada di Module? | Sudah Ditest? | Status |
   |---|----------------|----------------|---------------|--------|
   | 1 | account.move.print_inv_timesheet | ✅ | ❌ | BELUM |
   | 2 | account.move.getNetAmount | ✅ | ❌ | BELUM |
   | 3 | sale.order._change_order_line | ✅ | ❌ | BELUM |

4. **Hitung Coverage:**
   - Total features: X
   - Already tested: Y
   - Not tested: Z
   - Coverage: (Y/X) * 100%

#### E. Identifikasi Missing Tests (Sugesti Baru)

Berdasarkan analisis komprehensif, identifikasi:

1. **Fitur yang BELUM ditest:**
   - Model/method baru yang belum ada test
   - Edge cases yang belum di-cover
   - Workflow transitions yang belum ditest
   - Constraint validations yang belum diuji

2. **Test yang KURANG TEPAT:**
   - Test yang tidak sesuai dengan current implementation
   - Test yang missing important assertions
   - Test yang perlu diupdate karena perubahan kode

3. **Sugesti test baru:**
   - Nama test yang建议
   - Apa yang harus ditest
   - Langkah-langkah test
   - Expected results

### 2.4 Generate Test Plan

**PENTING: Untuk setiap test method, Anda HARUS membaca file test dan mengekstrak deskripsi dari docstring.**

Gunakan Grep atau Read untuk mendapatkan docstring dari setiap test method:

```bash
grep -A 2 "def test_" <module>/tests/test_*.py
```

Atau baca langsung file test dan extract:
- Test method name
- Docstring (jika ada)
- Apa yang di-test (create, write, unlink, workflow, dll)
- Model yang digunakan
- Assertion yang dilakukan

Berdasarkan analisis komprehensif, buat test plan dalam format detail:

```markdown
## Test Plan untuk [Module Name]

### Environment
| Item | Value |
|------|-------|
| Odoo Version | X.X |
| Edition | CE/EE |
| Database | db_name |
| Python Path | /path/to/python |
| Odoo Bin | /path/to/odoo-bin |
| Addons Path | /path/to/addons |

### Module Analysis Summary

**CATATAN: Section ini WAJIB berisi hasil ANALISA modul yang BENAR-BENAR DILAKUKAN, bukan copy dari dokumentasi yang ada.**

#### A. Models yang didefinisikan di module ini
- **Model 1**: hr.course
  - Fields: name, category_id, permanence, permanence_time, dll
  - Methods: _onchange_permanence(), dll
- **Model 2**: hr.course.category
- **Model 3**: hr.course.schedule

#### B. Dependencies
- Depends on: hr, project, account
- Extended by: module lain

#### C. Business Logic
- Workflow: draft → waiting_attendees → in_progress → in_validation → completed
- Constraints: end_date harus >= start_date
- Onchanges: permanence field change triggers permanence_time update

### Proposed Tests

#### 1. Existing Tests (yang sudah ada)

##### TransactionCase Tests (Backend)
| # | Test Class | Test Method | Apa yang Diuji | Detail Test | Expected Result |
|---|------------|-------------|----------------|-------------|-----------------|
| 1 | TestHrCourse | test_hr_course | Test onchange permanence | 1. Set permanence=False 2. Trigger _onchange_permanence() 3. Assert permanence_time=False | permanence_time kosong |
| 2 | TestHrCourse | test_hr_course_schedule | Test schedule workflow | 1. Create schedule 2. Validate end_date error 3. Test state transitions | All transitions work |

##### HttpCase Tests (Frontend)
| # | Test Class | Test Method | Apa yang Diuji | Detail Test | HTTP Status |
|---|------------|-------------|----------------|-------------|---------------|
| 1 | TestHrCourseHttp | test_course_list_view | Test list view loads | Authenticate, access /web | 200 |

#### 2. Missing Tests (Sugesti Test Baru)

Berdasarkan analisis module, test berikut BELUM ada tapi PERLU:

| # | Test Name | Apa yang Belum Ditest | Mengapa Perlu | Sugesti Langkah |
|---|-----------|----------------------|---------------|-----------------|
| 1 | test_course_category_delete | Delete category dengan course aktif | Constraint: tidak bisa hapus jika ada course | Test hapus category, assert error |
| 2 | test_schedule_attendant_limit | Batas maksimal attendee | Business rule: max 30 orang | Test tambah 31 attendee, assert error |

#### 3. Test yang Perlu Diperbaiki

| # | Test Name | Masalah | Sugesti Perbaikan |
|---|-----------|---------|------------------|
| 1 | test_hr_course_schedule | Missing assertion untuk attendee count | Tambah assert len(attendant_ids) == 2 |

### Detail Setiap Test

#### [Test Method 1]
- **File**: tests/test_xxx.py
- **Kelas**: TestClass
- **Method**: test_method_name
- **Models Used**: model1, model2
- **Apa yang dilakukan**:
  1. Langkah 1 - create/load data
  2. Langkah 2 - execute action
  3. Langkah 3 - assertion
- **Assertions**: assertEqual(x, y), assertTrue(z), dll

[Ulangi untuk setiap test method]

### Test Commands
TransactionCase:
```bash
<python_path> <odoo_bin> -c <odoo.conf> -d <database> \
  --test-enable --stop-after-init --http-port=<port> \
  --test-tags <module_name> 2>&1 | tail -50
```

HttpCase:
```bash
<python_path> <odoo_bin> -c <odoo.conf> -d <database> \
  --test-enable --stop-after-init --http-port=<port> \
  --test-tags <module_name>.http 2>&1 | tail -50
```

### Execution Plan
1. [ ] Prepare environment (database, password)
2. [ ] Run TransactionCase tests first
3. [ ] Analyze TransactionCase results
4. [ ] Run HttpCase tests
5. [ ] Analyze HttpCase results
6. [ ] Generate documentation

### Notes
- [Catatan penting dari analisis]
```

## Step 3: User Approval

### Subagent Mode
Jika dijalankan dari subagent, gunakan auto-approve dengan mencatat di output:
```
[Subagent Mode] Auto-approving test plan based on subagent execution context
```

Lanjutkan ke execution tanpa minta interaktif approval.

### Main Agent Mode

#### 3.1 Present Test Plan

**PENTING: Test plan yang disajikan ke user HARUS berisi detail lengkap tentang setiap test.**

Tampilkan test plan ke user dengan format yang jelas dan detail:

```
## Test Plan - [Module Name]

### Summary
- Total TransactionCase Tests: X
- Total HttpCase Tests: X
- Estimated Duration: X minutes

### Environment
- **Odoo Version**: X.X (Edition)
- **Database**: db_name
- **Test Type**: TransactionCase/HttpCase

### Proposed Tests

#### TransactionCase Tests (Backend)

| # | Test Class | Test Method | Apa yang Diuji | Detail Test | Expected Result |
|---|------------|-------------|----------------|-------------|-----------------|
| 1 | TestClass | test_method | Deskripsi spesifik | Langkah-langkah test | Expected outcome |

#### HttpCase Tests (Frontend)

| # | Test Class | Test Method | Apa yang Diuji | Detail Test | HTTP Status |
|---|------------|-------------|----------------|-------------|---------------|
| 1 | TestClass | test_method | Deskripsi spesifik | Langkah-langkah test | 200/302/etc |

### Detail Setiap Test (Expanded)

#### [Test Method 1: test_hr_course]
- **File**: tests/test_hr_course.py
- **Kelas**: TestHrCourse
- **Models Used**: hr.course, hr.course.category, hr.course.schedule
- **Apa yang dilakukan**:
  1. Membuat course category baru
  2. Membuat employee
  3. Membuat course dengan category
  4. Membuat course schedule
  5. Toggle permanence field dan trigger onchange
  6. Verifikasi permanence_time kosong saat permanence=False
- **Assertions**: assertFalse(), _onchange_permanence()

[Ulangi untuk setiap test method dengan format yang sama]

### Actions
- [ ] Approve all tests
- [ ] Add custom tests
- [ ] Remove specific tests
- [ ] Run with custom parameters
```

### 3.2 Minta Approval

Gunakan AskUserQuestion untuk minta approval:

```json
{
  "questions": [{
    "question": "Apakah approve test plan di atas?",
    "header": "Approval",
    "options": [
      {"label": "Approve All", "description": "Jalankan semua test sesuai plan"},
      {"label": "Modify Plan", "description": "Tambah/kurang test tertentu"},
      {"label": "Cancel", "description": "Batalkan testing"}
    ],
    "multiSelect": false
  }]
}
```

### 3.3 Handle Modifications

Jika user ingin modify:
- Tambah test: Identifikasi test yang ingin ditambahkan
- Kurang test: Hapus dari plan
- Custom test: Tambah custom test cases

Update plan dan minta approval lagi.

## Step 4: Execute Tests

**PENTING: JANGAN HANYA MEMBACA TEST YANG ADA - BENAR-BENAR JALANKAN TEST!**

- Tests HARUS benar-benar di-run menggunakan Odoo test runner
- Output dari test runner adalah bukti bahwa test sudah dijalankan
- JANGAN percaya bahwa test "pass" hanya karena ada di dokumentasi
- Selalu jalankan ulang (fresh run) setiap kali skill dipanggil

**PENTING: Jalankan test HANYA sesuai dengan plan yang sudah diapprove oleh user.**

Jika user menyetujui TransactionCase saja, jalankan TransactionCase. Jika HttpCase saja, jalankan HttpCase. Jika keduanya, jalankan keduanya sesuai urutan.

### 4.1 Prepare Environment

**CATATAN: Database sudah ditentukan di Step 1. Gunakan database yang sudah disepakati dengan user.**

#### A. Verify database exists

Jika Step 1 memilih "Buat baru" atau "Restore backup", pastikan database sudah tersedia:
```bash
psql -h localhost -p 5432 -U odoo -lqt | cut -d \| -f 1 | grep -w <database>
```

#### B. Setup admin user untuk HttpCase tests

**PENTING: JANGAN generate SHA hash manual!**

Gunakan Odoo Shell untuk set password:
```bash
echo "
user = env['res.users'].search([('login', '=', 'admin')])
user.write({'password': 'admin'})
env.cr.commit()
print('Password set for:', user.login)
" | paths['odoo']['python'] paths['odoo']['bin'] shell -c paths['project']['config'] -d <database>
```

### 4.2 Run Approved Tests

**Ikuti execution plan dari approved test plan:**

Gunakan `<database>` yang sudah ditentukan di Step 1 (bukan "roedl").

#### A. Jika TransactionCase Tests disetujui:

Jalankan berdasarkan detail dari test plan:
- **Test 1** (test_hr_course): Verifikasi course creation dan onchange
- **Test 2** (test_hr_course_schedule): Verifikasi schedule workflow (draft → waiting → in_progress → validation → completed)

```bash
cd paths['project']['root'] + '/odoo19.0-roedl/odoo'
paths['odoo']['python'] paths['odoo']['bin'] \
  -c paths['project']['config'] \
  -d <database> \
  --test-enable --stop-after-init --http-port=8170 \
  --test-tags <module_name> 2>&1 | tail -100
```

#### B. Jika HttpCase Tests disetujui:

Pastikan password admin sudah diset (lihat 4.1.B), lalu jalankan:

```bash
cd paths['project']['root'] + '/odoo19.0-roedl/odoo'
paths['odoo']['python'] paths['odoo']['bin'] \
  -c paths['project']['config'] \
  -d <database> \
  --test-enable --stop-after-init --http-port=8170 \
  --test-tags <module_name>.http 2>&1 | tail -100
```

#### C. Eksekusi Bertahap (sesuai test plan):

1. **Phase 1**: Jalankan TransactionCase tests
2. **Cek hasil**: Parse output dan catat yang pass/fail
3. **Phase 2**: Jalankan HttpCase tests
4. **Cek hasil**: Parse output dan catat yang pass/fail
5. **Compare**: Bandingkan dengan expected results dari test plan

### 4.3 Parse Test Results

Dari output, extract:
- Total tests
- Passed tests
- Failed tests
- Error tests
- Execution time
- Login status (untuk HttpCase)

Typical patterns:
```
INFO odoo.tests.stats: hr_course: 10 tests 0.83s 300 queries
ERROR odoo.tests.result: 0 failed, 2 error(s) of 6 tests
INFO migration_final_test odoo.addons.base.models.res_users: Login successful for login:admin
```

## Step 5: Generate Documentation

**PENTING: SATU FILE PER MODULE!**
- JANGAN membuat satu file gabungan untuk semua module
- Setiap module HARUS memiliki file dokumentasi sendiri
- Simpan di: `<module_path>/tests/TEST_RESULTS.md`

**CONTOH PENYIMPANAN YANG BENAR:**
```
custom_addons_19_new2/roedl/hr_course/tests/TEST_RESULTS.md
custom_addons_19_new2/roedl/asb_project/tests/TEST_RESULTS.md
custom_addons_19_new2/roedl/asb_calendar_feature/tests/TEST_RESULTS.md
```

**CONTOH PENYIMPANAN YANG SALAH:**
```
custom_addons_19_new2/docs/TEST_RESULTS.md  # ❌ SATU FILE UNTUK SEMUA
```

Buat file dokumentasi dengan format:

```markdown
# Test Results - [Module Name]

## Test Execution Information

| Item | Value |
|------|-------|
| **Odoo Version** | X.X (Edition) |
| **Database** | db_name |
| **Test Run Date** | YYYY-MM-DD HH:MM:SS UTC |
| **Module** | module_name |
| **Test Type** | TransactionCase/HttpCase/Both |

---

## Test Plan (Approved)

[Link ke approved test plan atau ringkasan]

---

## Test Results Summary

| Status | Count |
|--------|-------|
| ✅ PASS | X |
| ❌ FAIL | X |
| ⚠️ ERROR | X |

---

## Detailed Results

### TransactionCase Tests

| # | Test Name | Status | Notes |
|---|-----------|--------|-------|
| 1 | test_xxx | ✅ PASS | |

### HttpCase Tests

| # | Test Name | Status | Notes |
|---|-----------|--------|-------|
| 1 | test_xxx | ✅ PASS | Login: OK |

---

## Execution Details

- **Total Duration**: X.XX seconds
- **Total Queries**: X queries
- **Login Test**: ✅ Success / ❌ Failed

---

## Issues Found

- [Description jika ada]
- [Resolution jika ada]

---

## Notes

- [Catatan penting]
```

#### Tambahan: Coverage Analysis Section

Dokumentasi HARUS juga包括:

```markdown
---

## Module Coverage Analysis

### Features yang Diuji (Berdasarkan Test Existing)
| # | Feature | Test Method | Status |
|---|---------|-------------|--------|
| 1 | Onchange permanence | test_hr_course | ✅ Tested |
| 2 | Schedule workflow | test_hr_course_schedule | ✅ Tested |

### Features yang TIDAK Diuji (Berdasarkan Analisa Module)
| # | Feature | Model/Method | Reason |
|---|---------|-------------|--------|
| 1 | Category cascade delete | hr.course.category | Constraint exists but not tested |
| 2 | Employee course count compute | hr.employee.count_courses | Method exists but not tested |

### Recommendations
- [ ] Add test for category delete constraint
- [ ] Add test for employee course count computation
```

### Simpan ke lokasi:
- Custom modules: `custom_addons_19_new2/roedl/<module_name>/tests/TEST_RESULTS.md`
- Atau: `docs/TEST_RESULTS_<module_name>.md`

### Coverage Status (ROBUST Mode)

Dokumentasi HARUS mencantumkan status:

```markdown
## Coverage Status

| Status | Kriteria |
|--------|----------|
| ✅ COMPLETE | Semua existing tests PASS + Semua fitur sudah ditest (existing + new tests) |
| ⚠️ PARTIAL | Semua existing tests PASS tapi ada fitur belum ditest |
| ❌ INCOMPLETE | Ada test yang FAIL atau ERROR |
```

**ROBUST MODE - Module dinyatakan "READY" hanya jika:**
- Coverage Status: **COMPLETE**
- Semua existing tests: **PASS**
- Semua fitur sudah ditest: **YES**
- New tests created (jika ada): **PASS**

## Step 6: Report ke User

**WAJIB include coverage analysis dalam report!**

Berikan summary ke user:
- Module yang ditest
- Test type yang dijalankan
- Hasil (pass/fail/error)
- Link ke dokumentasi lengkap (per module!)
- **Coverage Analysis:**
  - Features yang sudah diuji
  - Features yang BELUM diuji (berdasarkan analisa module)
  - Rekomendasi test baru jika coverage kurang
- Issues yang ditemukan (jika ada)
- Rekomendasi jika ada

## Troubleshooting

### Login failures pada HttpCase
1. Cek user admin ada: `SELECT login FROM res_users WHERE login='admin'`
2. Set password via Odoo Shell (bukan SHA manual)
3. Verify login: `grep "Login successful" <output>`

### Module not found
1. Cek addons_path benar
2. Module terinstall: `SELECT name FROM ir_module_module WHERE name='<module>'`

### Database connection errors
1. Cek PostgreSQL running: `pg_isready -h localhost -p 5432`
2. Cek credentials di odoo.conf

## Examples

### Example 1: Test custom module dengan approval
```
User: "test hr_course module di Odoo 19 EE"

→ Step 1: Clarify (module: hr_course, version: 19, EE)
→ Step 2: Analyze module structure:
   - Baca test_hr_course.py dan test_hr_course_http.py
   - Ekstrak docstring dari setiap test method
   - Identifikasi models yang digunakan
→ Step 3: Generate DETAILED test plan:
   ## Test Plan - hr_course

   ### TransactionCase Tests (Backend)
   | # | Test Class | Test Method | Apa yang Diuji | Detail Test | Expected Result |
   |---|------------|-------------|----------------|-------------|-----------------|
   | 1 | TestHrCourse | test_hr_course | Test onchange permanence | 1. Set permanence=False 2. Trigger _onchange_permanence() 3. Assert permanence_time=False | permanence_time kosong |
   | 2 | TestHrCourse | test_hr_course_schedule | Test schedule workflow | 1. Create schedule 2. Validate end_date error 3. Test state transitions (draft→cancelled→draft→waiting→in_progress→validation→completed) | All transitions work |

   ### HttpCase Tests (Frontend)
   | # | Test Class | Test Method | Apa yang Diuji | Detail Test | HTTP Status |
   |---|------------|-------------|----------------|-------------|---------------|
   | 1 | TestHrCourseHttp | test_course_list_view | Test list view loads | Authenticate, access /web, assert 200 | 200 |
   | 2 | TestHrCourseHttp | test_create_course | Test create course | Create course via ORM, assert exists | 200 |

→ Step 3b: Present ke user, minta approval
→ User approves
→ Step 4: Execute tests berdasarkan plan:
   - Jalankan TransactionCase: test_hr_course, test_hr_course_schedule
   - Parse hasil, bandingkan dengan expected
   - Jalankan HttpCase: test_course_list_view, test_create_course
   - Parse hasil
→ Step 5: Generate docs
→ Step 6: Report
```

### Example 2: Test dengan modification
```
User: "test hr_course module"

→ Generate plan dengan 8 tests
→ User: "saya hanya mau test yang HttpCase saja"
→ Update plan: 0 TransactionCase + 4 HttpCase
→ Minta approval lagi
→ User approves
→ Execute HttpCase only
→ Report
```

### Example 3: Parallel Testing (Multiple Modules) - ROBUST MODE
```
User: "test semua modul di custom_addons_19_new2/roedl/ - PASTIKAN semua fitur sudah ditest"

→ Step 0: Mode Selection
→ User pilih "Parallel (Recommended)" - ROBUST Mode

→ Step 0B.1: Identifikasi modules dengan test files
→ Ditemukan 10 modules dengan test files

→ Step 0B.2: Bagi modules ke batches
→ Batch 1: asb_account_reports, asb_calendar_feature, asb_project, asb_project_followers
→ Batch 2: asb_setting_accounting, asb_timesheets_invoice, asft_employee_attribut, asft_employee_payroll
→ Batch 3: hr_course, invoice_merging

→ Step 0B.3: Spawn subagents untuk Batch 1 (PARALEL) - ROBUST
→ Agent 1: Test asb_account_reports
   - Analyze module
   - Run existing tests
   - Identify missing tests
   - CREATE & RUN new tests if needed
   - Coverage: COMPLETE

→ Agent 2: Test asb_calendar_feature (parallel)
→ Agent 3: Test asb_project (parallel)
→ Agent 4: Test asb_project_followers (parallel)

→ Tunggu semua selesai

→ Step 0B.4: Spawn subagents untuk Batch 2 (parallel)
→ Agent 5-8: Test 4 modules berikutnya

→ Step 0B.5: Spawn subagents untuk Batch 3 (parallel)
→ Agent 9-10: Test 2 modules terakhir

→ Step 0B.6: Collect all results
→ Generate summary dari 10 modules dengan Coverage Status

→ Report ke user:
   - Module A: ✅ COMPLETE (5 existing + 2 new tests PASS)
   - Module B: ✅ COMPLETE (3 existing + 1 new test PASS)
   - Module C: ⚠️ PARTIAL (existing PASS, but feature X not tested)
   - ...
```

---

## Subagent Usage Notes

### For Subagent Invocation (Parallel Mode - ROBUST):

**PENTING: Setiap subagent HANYA menangani SATU module saja!**

1. **Always use absolute paths** - Subagent may not have relative path context:
   - Python: `paths['odoo']['python']`
   - Odoo bin: `paths['odoo']['bin']`
   - Config: `paths['project']['config']`

2. **Auto-approve mode** - Skip interactive approval:
   ```
   [Subagent Mode - ROBUST] Auto-approving test plan for module: <module_name>
   [Subagent Mode - ROBUST] Will create new tests if analysis finds missing coverage
   ```

3. **Single Module Focus** - Subagent hanya test 1 module:
   - Jangan test multiple modules dalam satu subagent
   - Jika ada 10 modules, spawn 10 subagents (dalam batches)

4. **ROBUST: Create & Run New Tests** - Jika analisa menemukan missing tests:
   - BUAT test method baru di file test yang sesuai
   - JALANKAN test baru tersebut
   - REPORT hasil termasuk test baru
   - **JANGAN skip step ini jika ada fitur belum ditest**

5. **Output to parent** - Return structured output for parent agent:
   - Module tested
   - Test results (pass/fail/error)
   - New tests created (list)
   - Documentation path
   - Coverage status: COMPLETE/INCOMPLETE
   - Issues found

### Example Subagent Prompt (Parallel Mode):
```
Test module hr_course di Odoo 19 EE dengan database upgraded_test.

Modules folder: paths['addons']['custom'][0] + '/'

Gunakan skill odoo-module-test.
Lakukan: analyze module → run tests → generate report → return results ke main agent.
```

### Main Agent Coordinator Notes:

1. **Spawn 3-4 subagents simultaneously** - Tidak lebih dari 4
2. **Wait for completion** - Semua subagent harus selesai sebelum next batch
3. **Collect structured results**:
   ```json
   {
     "module": "hr_course",
     "status": "PASS/FAIL/ERROR",
     "transactioncase": {"passed": 2, "failed": 0, "errors": 0},
     "httpcase": {"passed": 2, "failed": 0, "errors": 0},
     "docs_path": "path/to/TEST_RESULTS.md",
     "issues": []
   }
   ```

---

**Important Notes:**
- Selalu gunakan Odoo Shell untuk set password, JANGAN generate SHA manual
- HttpCase tests memerlukan user dengan password yang benar
- CE = Community Edition, EE = Enterprise Edition
- EE include semua fitur CE
- Test plan HARUS diapprove user sebelum execute (main agent)
- Subagent: auto-approve dan gunakan absolute paths
