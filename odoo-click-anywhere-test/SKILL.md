---
name: odoo-click-anywhere-test
description: |
  Menjalankan click anywhere test (click_all) di Odoo untuk mendeteksi JavaScript errors.
  Gunakan ketika user ingin:
  - "jalankan click anywhere test"
  - "run click everywhere test"
  - "test click all apps"
  - "cek JS errors dengan clickbot"
  - "test semua menu dan view di Odoo"
  Skill ini otomatis mendeteksi Odoo version dan konfigurasi dari environment.
---

# Odoo Click Anywhere Test Skill

## Path Resolution
GUNAKAN odoo-path-resolver untuk mendapatkan paths. Contoh:
```python
paths = resolve()
python = paths['odoo']['python']
odoo_bin = paths['odoo']['bin']
config = paths['project']['config']
db = paths['database']['name']
port = paths['server']['http_port']
```

## Overview

Skill ini menjalankan click anywhere/click_all test di Odoo. Test ini akan:
- Membuka setiap aplikasi
- Mengklik setiap menu
- Mengklik setiap filter
- Mendeteksi JavaScript errors

## Prerequisites

1. **Invoke odoo-env-checker skill terlebih dahulu** untuk mendapatkan:
   - Odoo version (15, 16, 17, 18, atau 19)
   - Path ke odoo-bin
   - Konfigurasi database
   - Virtual environment Python

2. **Pastikan Odoo tidak sedang running** di port test (default: port + 2)

## Step-by-Step

### Step 1: Dapatkan Environment Info

Gunakan odoo-env-checker untuk mendapatkan:
- `odoo_version`: versi Odoo (15-19)
- `python_path`: path ke Python di venv
- `odoo_bin`: path ke odoo-bin
- `config_file`: path ke odoo.conf
- `database`: nama database
- `port`: port Odoo yang sedang running

### Step 2: Cek/Buat User Admin

Sebelum menjalankan test, WAJIB cek apakah user admin ada. Jika tidak ada, buat user admin:

```bash
# Cek apakah admin exists
echo "
admin = env['res.users'].search([('login', '=', 'admin')])
if admin:
    print('Admin user found:', admin.id)
    admin.write({'password': 'admin'})
    print('Password updated to: admin')
else:
    print('Creating admin user...')
    admin = env['res.users'].create({
        'login': 'admin',
        'name': 'Administrator',
        'password': 'admin',
    })
    print('Admin user created:', admin.id)
env.cr.commit()
" | {python_path} {odoo_bin} shell -c {config_file} -d {database}
```

### Step 3: Tentukan Test Command

**Odoo 16-19 (benar):**
```bash
{python_path} -m odoo server -c {config_file} -d {database} --test-enable --test-tags click_all --http-port={test_port}
```

**Odoo 15 (menggunakan pytest):**
```bash
{python_path} -m pytest {odoo_dir}/odoo/addons/web/tests/test_click_everywhere.py -v
```

### Step 4: Jalankan Test

```bash
cd {odoo_dir}
{python_path} -m odoo server -c {config_file} -d {database} --test-enable --test-tags click_all --http-port={test_port}
```

**Catatan:**
- `{test_port}` harus berbeda dari port Odoo yang sedang running (misal: jika port 8133, gunakan 8135)
- Test bisa memakan waktu 5-30 menit tergantung jumlah apps

### Step 5: Interpretasi Hasil

- **Success**: "clickbot test succeeded" appears di logs
- **Failure**: JavaScript errors akan muncul di output dengan detail error dan stack trace

## Contoh Penggunaan

### Full Test
```
User: "jalankan click anywhere test di Odoo 19 pada database upgraded_test"
→ Invoke odoo-path-resolver
→ Dapatkan: python=paths['odoo']['python'], odoo_bin=paths['odoo']['bin'], config=paths['project']['config'], db=paths['database']['name'], port=paths['server']['http_port']
→ Test port: test_port = port + 2
→ Cek apakah admin ada, jika tidak buat
→ Jalankan: {python} -m odoo server -c {config} -d {database} --test-enable --test-tags click_all --http-port={test_port}
```

## Catatan Penting

1. **Timeout**: Click all test bisa memakan waktu 5-30 menit untuk full run
2. **Port**: Gunakan port BERBEDA dari Odoo yang sedang running (default: port + 2)
3. **User Admin**: WAJIB dicek sebelum running - jika tidak ada, test akan gagal dengan "Access Denied"
4. **Database**: Test akan mencoba login sebagai admin - pastikan credentials benar
5. **Exit Code**: Test akan exit dengan code 1 jika ada app yang gagal (bukan berarti semua gagal)

## Error Handling

### Access Denied (admin tidak ada)
1. Buat user admin seperti di Step 2
2. Atau gunakan user yang sudah ada (misal: demo)

### Port Conflict
1. Pastikan port test berbeda dari port Odoo running
2. Default: jika Odoo di port 8133, gunakan 8135

### FileNotFoundError (filestore)
- Ini bukan error kritis - hanya file attachment yang tidak ada
- Test tetap berjalan meskipun ada warning ini

### Test Gagal di App Tertentu
- Check error message untuk details
- обычно dari custom modules atau enterprise modules
- Report ke developer untuk fixing
