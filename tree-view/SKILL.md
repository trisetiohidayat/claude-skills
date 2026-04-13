---
name: tree-view
description: Menampilkan tree view struktur direktori dalam format tabel tanpa border dengan deskripsi untuk setiap file/folder. Gunakan ketika user meminta melihat struktur file, tree view, daftar direktori dengan penjelasan, atau ingin memahami isi proyek. Trigger juga saat user bertanya "ada folder apa saja", "struktur project", "tree view", "lihat semua file di [path]".
version: "1.4"
---

# Tree View Skill

Skill ini menampilkan tree view struktur direktori dalam format **tabel tanpa border** dengan deskripsi untuk setiap file/folder. Metadata (size, modified, accessed, created) hanya ditampilkan jika user secara spesifik memintanya.

## Default Output — 4 Kolom

| No | Type | Name | Description |
|----|------|------|-------------|
|    |      |      |             |

**Keterangan kolom:**
1. **No** — Nomor urut (1, 2, 3, ...)
2. **Type** — Icon tipe (📁 = folder, 📄 = file)
3. **Name** — Nama file/folder (tampilkan nama lengkap, tanpa truncation)
4. **Description** — Penjelasan singkat tentang fungsi file/folder

**Contoh output default:**
```
📁 /Users/tri-mac/project/roedl/ — Odoo Migration Project
```

No   Type   Name                     Description
1    📁     .claude                 Konfigurasi Claude Code
2    📁     raw                     Immutable source documents
3    📁     wiki                    LLM-generated wiki pages
4    📁     wiki/analysis           Answers filed dari queries
5    📁     wiki/concepts           Ideas, theories, patterns
6    📄     CLAUDE.md               Schema untuk wiki ini
7    📄     index.md                Catalog semua wiki pages
8    📄     log.md                  Activity log

Legend:  📁 = Folder  |  📄 = File

---

## Metadata Output — 8 Kolom (hanya saat diminta)

Tampilkan kolom Size, Modified, Accessed, Created **hanya jika** user secara eksplisit memintanya, misalnya:
- "tree view dengan size"
- "lihat tanggal modifikasi"
- "tampilkan ukuran file"
- "dengan metadata lengkap"

| No | Type | Name | Size | Description | Modified | Accessed | Created |
|----|------|------|------|-------------|----------|----------|---------|

**Keterangan kolom metadata:**
- **Size** — Ukuran file ("dir" untuk folder, "-" jika tidak tersedia)
- **Modified** — Tanggal modifikasi terakhir (YYYY-MM-DD HH:MM)
- **Accessed** — Tanggal akses terakhir (YYYY-MM-DD HH:MM, "-" jika tidak tersedia)
- **Created** — Tanggal pembuatan (YYYY-MM-DD HH:MM, "-" jika tidak tersedia)

**Contoh output dengan metadata:**
```
📁 /Users/tri-mac/project/roedl/ — Odoo 15 → 19 Migration Project
```

No   Type   Name                    Size        Description                                           Modified           Accessed         Created
1    📁     .claude                dir         Konfigurasi Claude Code                              2026-04-17 17:17   -                 -
2    📁     raw                    dir         Immutable source documents                           2026-04-13 07:43   2026-04-13 07:43   2026-04-13 07:43
3    📄     CLAUDE.md              8.9 KB      Schema/wiki maintainer guide                          2026-04-13 07:43   2026-04-13 07:43   2026-04-13 07:43
...

Legend:  📁 = Folder  |  📄 = File  |  - = Tidak tersedia

---

## Pengurutan (Sorting)

**WAJIB** urutkan dengan urutan berikut:

1. **Tipe dulu** — Folder (📁) semua ada di atas, baru File (📄)
2. **Abjad** — Dalam tiap kelompok, urutkan berdasarkan Name A-Z

---

## Aturan Formatting

1. **TIDAK pakai border tabel** (bukan markdown table, bukan ASCII box)
2. **Gunakan spasi** untuk memisahkan kolom
3. **Rata kiri** untuk Name, Description
4. **Rata kanan** untuk Size (jika ditampilkan)
5. **Nama file panjang** — tampilkan nama lengkap, tanpa truncation
6. **Jika tidak ada data** — gunakan tanda `-`

---

## Cara Penggunaan

### Basic Listing (default — tanpa metadata)

```bash
ls -la
```

### Listing dengan Metadata (hanya jika diminta)

```bash
# Recommended - detail lengkap
stat -x *
```

### Proses yang Harus Dilakukan

1. Ambil semua file/folder dari direktori target
2. **SELALU** berikan deskripsi untuk setiap file/folder
3. **OPSIONAL** ekstrak metadata (Size, Modified, Accessed, Created) — hanya jika user minta
4. **SORT**:
   - Kelompok 1: Folder (📁) → urutkan A-Z berdasarkan Name
   - Kelompok 2: File (📄) → urutkan A-Z berdasarkan Name
5. Format output sesuai template

---

## Deskripsi File/Folder

### Kategori Folder Umum

| Folder | Deskripsi |
|--------|-----------|
| `.claude/` | Konfigurasi Claude Code (settings, memory, hooks) |
| `.vscode/` | VS Code settings & debug configurations |
| `custom_addons_*` | Custom Odoo modules |
| `odoo*.0-*` | Odoo source code |
| `enterprise-*` | Odoo Enterprise modules |
| `venv*` | Virtual environment Python |
| `migration_*` | Data/scripts migrasi |
| `audit_*` | Hasil audit sistem |
| `docs/` | Dokumentasi proyek |
| `data/` | Data files & backup database |

### Kategori File Umum

| Ekstensi | Deskripsi |
|----------|-----------|
| `.md` | File dokumentasi |
| `.conf` | Konfigurasi aplikasi |
| `.zip` | File backup/archive |
| `.log` | Log aplikasi |
| `.py` | Script Python |
| `.sh` | Shell script |
| `.yml`, `.yaml` | Konfigurasi YAML |
| `__manifest__.py` | Odoo module manifest |

### Aturan Penulisan Deskripsi

1. **Singkat** — 1-2 kalimat (maks ~50 karakter)
2. **Kontekstual** — Jelaskan fungsi dalam konteks proyek
3. **Bahasa Indonesia** — Sesuai preferensi user
4. **Spesifik** — Hindari generic description

---

## Tips

1. **Double sort**: Tipe dulu (folder → file), lalu abjad dalam tiap kelompok
2. **Nama file panjang** — tampilkan nama lengkap, tanpa truncation
3. **Deskripsi informative** — bukan generic, tapi spesifik ke fungsi
4. **Metadata hanya saat diminta** — default tanpa metadata, lebih clean dan cepat
