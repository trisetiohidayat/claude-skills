---
name: postgres-kill-idle
description: Kill semua PostgreSQL idle connections. Trigger ketika user meminta: "kill postgres idle", "hapus koneksi idle postgres", "clean idle connections", "kill all idle postgres", "reset postgres connections", "terminate idle sessions". Gunakan skill ini untuk maintenance database PostgreSQL, terutama sebelum restore database atau saat ada too many connections error.
version: 1.1.0
---

# PostgreSQL Kill Idle Connections

Skill ini digunakan untuk membunuh (terminate) semua PostgreSQL idle connections. Sangat berguna untuk:
- Database maintenance sebelum restore
- Mengatasi "too many connections" error
- Membersihkan zombie connections

## Prerequisites

- Akses ke PostgreSQL via `psql`
- User postgres (superuser) - memiliki connection limit lebih tinggi
- macOS: Unix socket biasanya ada di `/tmp/.s.PGSQL.5432`

## CRITICAL: "Too Many Clients Already" Error

Jika error `FATAL: sorry, too many clients already`, gunakan approach single-command:

```bash
# GUNAKAN USER POSTGRES - bukan odoo
psql -h localhost -U postgres -d postgres -c "
DO \$\$
DECLARE
    r RECORD;
    killed_count INTEGER := 0;
BEGIN
    FOR r IN
        SELECT pid FROM pg_stat_activity
        WHERE state = 'idle'
        AND pid <> pg_backend_pid()
    LOOP
        PERFORM pg_terminate_backend(r.pid);
        killed_count := killed_count + 1;
    END LOOP;
    RAISE NOTICE 'Terminated % idle connections', killed_count;
END
\$\$;
"
```

## Recommended Workflow

### Step 1: Preview + Kill in ONE Command (Recommended)

Ini mencegah circular dependency - cukup 1 koneksi untuk semua operasi:

```bash
psql -h localhost -U postgres -d postgres -c "
DO \$\$
DECLARE
    r RECORD;
    killed_count INTEGER := 0;
    idle_count INTEGER;
BEGIN
    -- Count idle first
    SELECT COUNT(*) INTO idle_count FROM pg_stat_activity
    WHERE state = 'idle' AND pid <> pg_backend_pid();

    RAISE NOTICE 'Found % idle connections', idle_count;

    -- Terminate all idle
    FOR r IN
        SELECT pid FROM pg_stat_activity
        WHERE state = 'idle'
        AND pid <> pg_backend_pid()
    LOOP
        PERFORM pg_terminate_backend(r.pid);
        killed_count := killed_count + 1;
    END LOOP;

    RAISE NOTICE 'Terminated % idle connections', killed_count;
END
\$\$;
"
```

### Step 2: Verify (Optional)

```bash
psql -h localhost -U postgres -d postgres -c "
SELECT state, count(*) as total
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
GROUP BY state;
"
```

## Alternative: Unix Socket (Lebih Reliable)

Jika TCP connection bermasalah, gunakan unix socket:

```bash
psql -U postgres -h /tmp -d postgres -c "..."
```

## Options

### Kill Specific Database Idle Connections

```bash
psql -h localhost -U postgres -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND datname = 'NAMA_DATABASE'
AND pid <> pg_backend_pid();
"
```

### Kill ALL Connections to Specific Database (Including Active)

```bash
psql -h localhost -U postgres -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'NAMA_DATABASE'
AND pid <> pg_backend_pid();
"
```

### Cancel Instead of Terminate (Gentler)

```bash
psql -h localhost -U postgres -d postgres -c "
SELECT pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND pid <> pg_backend_pid();
"
```

## Usage Examples

**Contoh 1: Kill semua idle connections**
```
User: "kill semua postgres idle connection"
→ Kill semua idle connections di semua database
```

**Contoh 2: Kill idle connections di database tertentu**
```
User: "kill idle connections di database roedl_upgraded_20260415"
→ Kill hanya idle connections yang terhubung ke database tersebut
```

**Contoh 3: Reset database sebelum restore**
```
User: "reset koneksi postgres sebelum restore database"
→ Kill semua connections termasuk active ke database target
```

## Important Notes

1. **GUNAKAN USER POSTGRES** - memiliki connection limit lebih tinggi dari user biasa
2. **Single-command approach** - preview + kill dalam 1 perintah untuk menghindari circular dependency
3. **pg_backend_pid()** - mengecualikan connection sendiri
4. **Retry jika perlu** - jika still failing, tunggu 2 detik lalu retry

## Troubleshooting

### Error: too many clients already

**Solution:**
```bash
# 1. Coba unix socket
psql -U postgres -h /tmp -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND pid <> pg_backend_pid();"

# 2. Atau tunggu sebentar lalu retry
sleep 2
psql -h localhost -U postgres -d postgres -c "..."
```

### Permission Denied

```
ERROR: must be a superuser to terminate other server processes
```
→ Pastikan menggunakan user postgres (superuser)

### Still Getting Idle Connections After Kill

```
Kemungkinan ada services/cron yang membuat koneksi baru.
Kill Odoo services terlebih dahulu:
- Kill semua odoo processes
- Baru kill idle connections
```

## Expected Output

**Success:**
```
NOTICE: Found 10 idle connections
NOTICE: Terminated 10 idle connections
DO
----
(1 row)
```

**Verification:**
```
     state      | total
----------------+-------
 active         |     3
 idle           |     0
(2 rows)
```
