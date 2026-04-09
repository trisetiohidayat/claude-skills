# Communication Protocol

Semua komunikasi WAJIB melalui SendMessage tool.

## Cara Pakai SendMessage (WAJIB INI)

### Template Dasar SendMessage

```python
SendMessage(
    message={
        "action": "ACTION_NAME",
        "context": {...},
        "output": {...}
    },
    summary="Brief summary of what agent should do",
    to="agent_name"  # architect, developer, devops, qa, click_tester
)
```

### Pola Respons - WAIT for Response

Lead HARUS menunggu response dari agent:

```python
# KIRIM PESAN
SendMessage(to="devops", message={...}, summary="Clone database")

# TUNGGU - cek message/notification secara periodik
# Agent akan mengirim response saat selesai

# TERIMA RESPONSE - dari message notification
# Response berupa JSON sesuai format di bawah
```

---

## CONCRETE EXAMPLES - Lead → Agent

### Contoh 1: Kirim ke DevOps (Clone Database)

```python
# Lead: Kirim pesan ke DevOps untuk clone database
SendMessage(
    to="devops",
    summary="Clone database roedl to test database",
    message={
        "action": "CLONE_DATABASE",
        "context": {
            "source_db": "roedl",
            "target_db": "roedl_test_20260318_150000",
            "operation": "clone"
        },
        "output": {
            "status": "PENDING"
        }
    }
)
```

**Setelah Agent Selesai**, terima response:

```python
# Response dari DevOps (melalui notification/message):
{
    "action": "DATABASE_OPERATION",
    "result": "success",
    "operation": "clone",
    "database_name": "roedl_test_20260318_150000",
    "timestamp": "2026-03-18T15:00:25Z"
}
```

### Contoh 2: Kirim ke Click Tester

```python
# Lead: Kirim ke Click Tester SETELAH DevOps selesai
SendMessage(
    to="click_tester",
    summary="Run click test on test database",
    message={
        "action": "RUN_CLICK_TEST",
        "context": {
            "module": "roedl_custom",
            "database": "roedl_test_20260318_150000",
            "test_type": "initial"
        },
        "output": {
            "status": "STARTING"
        }
    }
)
```

**Response dari Click Tester:**

```python
{
    "action": "CLICK_TEST_RESULTS",
    "context": {
        "test_type": "initial",
        "js_errors": [
            {
                "error_id": "JS_ERROR_001",
                "message": "Uncaught TypeError: Cannot read property 'name' of undefined",
                "file": "static/src/js/custom_view.js",
                "line": 42,
                "trigger": "Click on sale order form"
            }
        ],
        "database": "roedl_test_20260318_150000"
    },
    "output": {
        "total_clicks": 87,
        "js_errors_found": 1,
        "pages_tested": ["sale.order", "purchase.order", "account.move"],
        "summary": "Found 1 JS error in custom_view.js when opening sale order"
    }
}
```

### Contoh 3: Kirim ke Architect (Analisa Error)

```python
# Lead: Kirim error dari Click Tester ke Architect
SendMessage(
    to="architect",
    summary="Analyze JS error from click tester",
    message={
        "action": "ANALYZE_ERRORS",
        "context": {
            "click_tester_errors": [
                {
                    "error_id": "JS_ERROR_001",
                    "message": "Uncaught TypeError: Cannot read property 'name' of undefined",
                    "file": "static/src/js/custom_view.js",
                    "line": 42,
                    "trigger": "Click on sale order form"
                }
            ],
            "module": "roedl_custom"
        },
        "output": {
            "status": "ANALYSIS_REQUESTED"
        }
    }
)
```

**Response dari Architect:**

```python
{
    "action": "ANALYZE_ERRORS",
    "context": {
        "errors_analyzed": 1
    },
    "output": {
        "errors": [
            {
                "error_id": "JS_ERROR_001",
                "error": "Uncaught TypeError: Cannot read property 'name' of undefined",
                "why": "Variable 'record' is undefined karena this.record tidak di-set sebelum render dipanggil. Ini terjadi karena onload method tidak menyelesaikan promise sebelum render dieksekusi.",
                "where": "roedl_custom/static/src/js/custom_view.js:42",
                "how_to_fix": "Tambahkan await sebelum this._super() di line 40, atau simpan record ke variabel terlebih dahulu sebelum akses",
                "confidence": 85,
                "severity": "HIGH"
            }
        ],
        "summary": "1 error found - root cause adalah async/await issue di custom view. Fix dengan menambahkan await sebelum render."
    }
}
```

### Contoh 4: Kirim ke Developer (Apply Fix)

```python
# Lead: Berikan instruksi fix ke Developer
SendMessage(
    to="developer",
    summary="Apply fix for JS error in custom_view.js",
    message={
        "action": "APPLY_FIX",
        "context": {
            "fix_id": "FIX_001",
            "error": {
                "error_id": "JS_ERROR_001",
                "description": "Uncaught TypeError: Cannot read property 'name' of undefined",
                "location": "roedl_custom/static/src/js/custom_view.js:42"
            },
            "fix_instructions": {
                "summary": "Tambahkan await sebelum this._super() di render method",
                "detailed_steps": [
                    "Buka file static/src/js/custom_view.js",
                    "Cari method _render() di line ~38",
                    "Tambahkan 'await' sebelum 'return this._super()'",
                    "Pastikan method adalah async: async _render()"
                ],
                "files_to_modify": ["static/src/js/custom_view.js"]
            },
            "confidence": 85
        },
        "output": {
            "status": "FIX_REQUESTED"
        }
    }
)
```

**Response dari Developer:**

```python
{
    "action": "APPLY_FIX",
    "result": "success",
    "context": {
        "fix_id": "FIX_001",
        "files_modified": ["static/src/js/custom_view.js"]
    },
    "output": {
        "status": "FIX_APPLIED",
        "changes_made": [
            "Changed line 38: async _render()",
            "Changed line 42: await return this._super()"
        ],
        "test_command": "Restart Odoo and upgrade module"
    }
}
```

### Contoh 5: Kirim ke DevOps (Upgrade Module)

```python
# Lead: Minta DevOps upgrade module setelah Developer fix
SendMessage(
    to="devops",
    summary="Upgrade roedl_custom module in test database",
    message={
        "action": "UPGRADE_MODULE",
        "context": {
            "module": "roedl_custom",
            "database": "roedl_test_20260318_150000",
            "operation": "upgrade"
        },
        "output": {
            "status": "UPGRADE_REQUESTED"
        }
    }
)
```

**Response dari DevOps:**

```python
{
    "action": "UPGRADE_MODULE",
    "result": "success",
    "operation": "upgrade",
    "database_name": "roedl_test_20260318_150000",
    "output": {
        "module": "roedl_custom",
        "status": "UPGRADED",
        "log": "Modules loaded: roedl_custom (1/1)"
    }
}
```

### Contoh 6: Kirim ke QA (Verify Fix)

```python
# Lead: Minta QA verify fix setelah DevOps upgrade
SendMessage(
    to="qa",
    summary="Verify fix for JS error in custom_view.js",
    message={
        "action": "VERIFY_FIX",
        "context": {
            "module": "roedl_custom",
            "database": "roedl_test_20260318_150000",
            "fix_id": "FIX_001",
            "original_error": "JS_ERROR_001",
            "test_type": "verify"
        },
        "output": {
            "status": "VERIFY_REQUESTED"
        }
    }
)
```

**Response dari QA:**

```python
{
    "action": "TEST_RESULTS",
    "context": {
        "test_type": "verify",
        "database": "roedl_test_20260318_150000",
        "tests_run": [
            {"name": "test_sale_order_form_load", "result": "PASSED"},
            {"name": "test_custom_field_access", "result": "PASSED"}
        ],
        "passed": ["test_sale_order_form_load", "test_custom_field_access"],
        "failed": []
    },
    "output": {
        "total_passed": 2,
        "total_failed": 0,
        "summary": "All tests PASSED - fix verified successfully"
    }

}
```

---

## Response Format Reference

### Architect → Lead Response
```python
{
    "action": "ANALYZE_ERRORS",
    "context": {
        "click_tester_errors": [...],  # dari Click Tester
        "qa_test_errors": [...]        # dari QA (optional)
    },
    "output": {
        "errors": [
            {
                "error_id": "JS_ERROR_001",
                "error": "Error description",
                "why": "MENGAPA terjadi (root cause)",
                "where": "file/module/line",
                "how_to_fix": "langkah fix",
                "confidence": 85,
                "severity": "HIGH|MEDIUM|LOW"
            }
        ],
        "summary": "Ringkasan analisis"
    }
}
```

### QA → Lead Response
```python
{
    "action": "TEST_RESULTS",
    "context": {
        "test_type": "initial|verify|regression",
        "passed": ["test_name_1", "test_name_2"],
        "failed": ["test_name_3"],
        "database": "test_db_name"
    },
    "output": {
        "total_passed": 10,
        "total_failed": 2,
        "summary": "Test summary"
    }
}
```

### Click Tester → Lead Response
```python
{
    "action": "CLICK_TEST_RESULTS",
    "context": {
        "js_errors": [
            {
                "error_id": "JS_ERROR_001",
                "message": "Error message",
                "file": "path/to/file.js",
                "line": 42,
                "trigger": "Action yang menyebabkan error"
            }
        ],
        "database": "test_db_name"
    },
    "output": {
        "total_clicks": 100,
        "js_errors_found": 5,
        "pages_tested": ["sale.order", "purchase.order"],
        "summary": "Click test summary"
    }
}
```

### DevOps → Lead Response
```python
{
    "action": "DATABASE_OPERATION",
    "result": "success|error",
    "operation": "clone|upgrade|drop|create",
    "database_name": "test_db_name",
    "error_message": "jika gagal",
    "timestamp": "2026-03-18T15:00:25Z"
}
```

### Developer → Lead Response
```python
{
    "action": "APPLY_FIX",
    "result": "success|error",
    "context": {
        "fix_id": "FIX_001",
        "files_modified": ["path/to/file.py"]
    },
    "output": {
        "status": "FIX_APPLIED|FIX_FAILED",
        "changes_made": ["description of changes"],
        "error_message": "jika gagal"
    }
}
```

---

## Error Handling in Communication

### Jika Agent Tidak Merespons (>3 menit)

```python
# Kirim reminder
SendMessage(
    to="devops",
    summary="Reminder: Clone database task pending",
    message={
        "action": "REMINDER",
        "context": {
            "original_task": "CLONE_DATABASE",
            "waiting_since": "2026-03-18T15:00:00Z"
        }
    }
)
```

### Jika Response Mengandung Error

```python
# Response error dari DevOps:
{
    "action": "DATABASE_OPERATION",
    "result": "error",
    "operation": "clone",
    "error_message": "Database roedl does not exist",
    "database_name": "roedl"
}

# TINDAK: Tanya user - retry atau abort?
```

---

## Message Format Rules (WAJIB)

1. **Selalu gunakan JSON** dengan format di atas
2. **Include context** - apa yang sudah dilakukan
3. **Include output** - apa yang dihasilkan
4. **Include database name** - untuk QA dan Click Tester WAJIB
5. **Selalu gunakan `to`** - nama agent yang dituju
6. **Selalu gunakan `summary`** - ringkasan singkat untuk notifikasi
7. **Response SELALU ada `action`** - sama dengan request

---

## Quick Reference: Urutan SendMessage

```
1. DevOps: CLONE_DATABASE
   → response: {action: "DATABASE_OPERATION", result: "success"}

2. Click Tester: RUN_CLICK_TEST (parallel dengan Architect)
   → response: {action: "CLICK_TEST_RESULTS", js_errors: [...]}

3. Architect: ANALYZE_ERRORS
   → response: {action: "ANALYZE_ERRORS", errors: [...]}

4. Lead: APPROVE_FIX (ke Developer)

5. Developer: APPLY_FIX
   → response: {action: "APPLY_FIX", result: "success"}

6. DevOps: UPGRADE_MODULE
   → response: {action: "DATABASE_OPERATION", result: "success"}

7. QA: VERIFY_FIX
   → response: {action: "TEST_RESULTS", total_passed: X}

8. Click Tester: RETEST
   → response: {action: "CLICK_TEST_RESULTS", js_errors: []}
```
