---
name: odoo-user-context
description: >
  Gunakan skill ini setiap kali user menanyakan operasi step-by-step di Odoo
  (misal: "cara konfigurasi purchase order", "langkah approval SO"),
  ATAU setiap kali perlu tahu apa yang bisa/cannot dilakukan oleh user Odoo
  tertentu (misal: "apa akses user X", "permission Purchase Manager").

  Trigger juga saat user menyebut nama user/role spesifik dan butuh konteks
  aksesnya. SELALU tanya DB dan versi Odoo jika belum diketahui.

 的工具: odoo-mcp (rust-mcp)
  Output: structured user access context untuk guiar AI memberikan panduan sesuai batasan user
---

# Odoo User Context Skill

Skill ini membangun konteks akses user Odoo secara menyeluruh — access rights, groups,
record rules, company, dan versi DB — agar AI bisa memberikan panduan step-by-step
yang sesuai dengan batasan aktual user tersebut.

## Kapan Trigger

- User meminta step-by-step operasi Odoo (purchase, sale, inventory, dll)
- User menanyakan apa yang bisa dilakukan oleh user/role tertentu
- User menyebut nama user atau group spesifik (misal: "Purchase Manager", "Admin Gudang")
- AI perlu memberikan panduan yang dibatasi oleh access control

> **CATATAN**: Konteks ini TIDAK selalu dimuat. Hanya dimuat saat task
> benar-benar memerlukan informasi akses user Odoo. Untuk pertanyaan umum
> Odoo tanpa konteks user spesifik, skill ini TIDAK perlu digunakan.

## Workflow

### Langkah 0 — Cek Konteks Tersimpan

Sebelum memulai, cek apakah sudah ada konteks user di memory files:
- Cek `/Users/tri-mac/.claude/projects/-Users-tri-mac-Obsidian-Vault-Odoo-19/memory/` untuk file
  yang menyimpan `odoo_db`, `odoo_version`, `target_user` terakhir.

Jika sudah ada dan user tidak menyebutkan user/DB berbeda, boleh gunakan konteks tersimpan
tanpa menanyakan ulang.

### Langkah 1 —收集 Informasi (Tanya User Jika Belum Ada)

Tanya user dengan bahasa Indonesia (atau bahasa yang digunakan user) untuk info yang belum ada:

```
🔍 Untuk memberikan panduan yang tepat, saya perlu beberapa informasi:

1. **Database Odoo** — DB mana yang akan digunakan?
2. **Versi Odoo** — (misal: 18 atau 19)
3. **User Target** — user/role siapa yang ingin ditanyakan?
   (nama login atau display name, misal: "admin", "purchase.manager", "Admin Gudang")

Opsional:
4. **Company** — apakah perlu fokus ke company tertentu? (untuk multi-company)
```

Gunakan `AskUserQuestion` tool jika perlu, atau tanya langsung via text.

### Langkah 2 — Query Odoo DB

Gunakan MCP `rust-mcp` (odoo_search_read / odoo_execute) untuk query data.

**Tools yang tersedia:**
- `mcp__rust-mcp__odoo_search_read` — search + read dalam satu langkah
- `mcp__rust-mcp__odoo_read` — read by IDs
- `mcp__rust-mcp__odoo_execute` — panggil custom method/model function
- `mcp__rust-mcp__odoo_search` — search records

#### 2a. Identifikasi User Target

Cari user berdasarkan nama login atau display name:

```json
{
  "model": "res.users",
  "instance": "<db_name>",
  "domain": [
    ["login", "ilike", "<username>"],
    "OR",
    ["name", "ilike", "<username>"]
  ],
  "fields": ["id", "name", "login", "company_id", "company_ids", "active", "create_uid"]
}
```

Ambil ID user pertama yang ditemukan.

#### 2b. Ambil Info Dasar User

```json
{
  "model": "res.users",
  "instance": "<db_name>",
  "ids": [<user_id>],
  "fields": ["id", "name", "login", "company_id", "company_ids", "active",
             "groups_id", "image_1920", "share"]
}
```

#### 2c. Ambil Groups (Detail)

```json
{
  "model": "res.groups",
  "instance": "<db_name>",
  "domain": [],
  "fields": ["id", "name", "category_id", "full_name", "users"]
}
```

Filter groups yang memiliki user target di `users` field.
Alternatif via `read_group`:

```json
{
  "model": "res.groups",
  "instance": "<db_name>",
  "domain": [["users", "in", [<user_id>]]],
  "fields": ["id", "name", "category_id"],
  "groupby": ["category_id"]
}
```

#### 2d. Ambil Access Rights (ir.model.access)

```json
{
  "model": "ir.model.access",
  "instance": "<db_name>",
  "domain": [],
  "fields": ["id", "name", "model_id", "group_id", "perm_read", "perm_write",
             "perm_create", "perm_unlink", "active"]
}
```

Filter access rights yang terkait dengan group IDs user target.
Gunakan `read_group` untuk mapping group → access rights:

```json
{
  "model": "ir.model.access",
  "instance": "<db_name>",
  "domain": [["group_id", "in", <group_ids>]],
  "fields": ["id", "name", "model_id:name", "perm_read", "perm_write",
             "perm_create", "perm_unlink", "group_id:name"],
  "groupby": ["group_id"]
}
```

#### 2e. Ambil Record Rules (ir.rule)

```json
{
  "model": "ir.rule",
  "instance": "<db_name>",
  "domain": [["groups", "in", <group_ids>]],
  "fields": ["id", "name", "model_id", "domain_force", "groups", "perm_read",
             "perm_write", "perm_create", "perm_unlink"]
}
```

#### 2f. Ambil Company Info

```json
{
  "model": "res.company",
  "instance": "<db_name>",
  "ids": <company_ids>,
  "fields": ["id", "name", "currency_id", "street", "email", "phone"]
}
```

#### 2g. Cek Model Metadata (untuk понимание apa yang bisa diakses)

Untuk setiap model yang sering diakses user, cek fields yang visible:

```json
{
  "model": "ir.model",
  "instance": "<db_name>",
  "domain": [["model", "in", ["purchase.order", "stock.picking",
                               "sale.order", "account.move",
                               "mrp.production", "crm.lead"]]],
  "fields": ["id", "name", "model", "field_id"]
}
```

### Langkah 3 — Buat Konteks Ringkasan

Susun hasil query menjadi struktur konteks berikut. SIMPAN ke memory file
agar tidak perlu query ulang untuk session yang sama.

#### Simpan ke Memory

```markdown
# Odoo User Context

**DB**: `<db_name>`
**Odoo Version**: `<version>`
**Generated**: <timestamp>

## User Target

- **Login**: `<login>`
- **Display Name**: `<name>`
- **ID**: `<id>`
- **Active**: `<yes/no>`
- **Is Share User**: `<yes/no>`

## Companies

<list companies>

## Groups

| Group ID | Group Name | Category |
|----------|-----------|----------|
| ... | ... | ... |

## Access Rights Summary

| Model | Read | Write | Create | Unlink |
|-------|------|-------|--------|--------|
| ... | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |

## Record Rules (pemblokir akses)

| Rule | Model | Domain |
|------|-------|--------|
| ... | ... | ... |

## Model Permissions Detail

<per-model breakdown>

## Catatan Konteks

<any special constraints or observations>
```

Path memory: `/Users/tri-mac/.claude/projects/-Users-tri-mac-Obsidian-Vault-Odoo-19/memory/odoo_user_context.md`

### Langkah 4 — Berikan Respons

Gunakan konteks yang sudah dibangun untuk:

1. **Jika user bertanya "apa yang bisa dilakukan user X"**:
   - Tampilkan ringkasan akses
   - Highlight capability utama
   - Tunjukkan keterbatasan (record rules, missing groups)

2. **Jika user meminta step-by-step operasi Odoo**:
   - Konfirmasi dulu: "Saya akan memberikan panduan untuk user `<username>`"
   - Selalu verifikasi apakah operasi diperbolehkan oleh access rights
   - Jika ada record rule yang membatasi, sampaikan di setiap langkah
   - Jika user TIDAK memiliki permission, sampaikan dengan jelas:
     ```
     ⚠️ User `<username>` TIDAK memiliki akses `<operation>` pada `<model>`.
     Akses yang diperlukan: `<group>`.
     ```

3. **Jika operasi memerlukan group yang tidak dimiliki user**:
   - Jelaskan langkah yang diperlukan (misal: perlu menambahkan ke group)
   - Beri tahu siapa yang bisa memberikan akses tersebut

## Tips Penggunaan

- **Multi-company awareness**: Jika user memiliki akses ke beberapa company,
  pastikan setiap langkah menyebutkan company context yang benar
- **Record rules > Access rights**: Record rules bisa memblokir akses meskipun
  access rights mengizinkan. Prioritaskan pengecekan record rules.
- **Share users**: User dengan `share=True` memiliki keterbatasan khusus
  (biasanya tidak bisa mengakses backend models tertentu)
- **Cache**: Simpan konteks ke memory file agar tidak query ulang. Tapi
  jika user menanyakan user/DB berbeda, reset dan query ulang.

## Model Groups yang Sering Digunakan

Sebagai referensi cepat (berlaku untuk Odoo 18/19):

| Group Internal Name | Full Name | Typical Access |
|--------------------|-----------|----------------|
| `base.group_user` | Employee | Basic access |
| `base.group_partner_manager` | Contact Creation | Manage partners |
| `purchase.group_purchase_user` | Purchase User | PO workflow |
| `purchase.group_purchase_manager` | Purchase Manager | Full PO + config |
| `sales_team.group_sale_salesman` | Salesperson | SO workflow |
| `sales_team.group_sale_manager` | Sales Manager | Full SO + config |
| `stock.group_stock_user` | User | Stock operations |
| `stock.group_stock_manager` | Manager | Full stock + config |
| `mrp.group_mrp_user` | Manufacturing User | MO workflow |
| `mrp.group_mrp_manager` | Production Manager | Full MO + config |
| `account.group_account_invoice` | Invoice | Billing |
| `account.group_account_manager` | Accounting | Full accounting |
| `hr.group_hr_user` | Employee | HR self-service |
| `hr.group_hr_manager` | HR Manager | Full HR |
| `project.group_project_user` | Project User | Project tasks |
| `project.group_project_manager` | Project Manager | Full project |

## Handling Error / User Tidak Ditemukan

Jika user tidak ditemukan di `res.users`:
1. Coba variants nama (case insensitive, partial match)
2. Jika tetap tidak ada, informasikan ke user:
   ```
   ❌ User dengan nama `<nama>` tidak ditemukan di database `<db>`.
   Pastikan nama login atau display name sudah benar.
   ```
3. Minta user untuk memilih dari list user yang tersedia:
   ```json
   {
     "model": "res.users",
     "instance": "<db>",
     "domain": [["active", "=", true]],
     "fields": ["id", "name", "login", "company_id"]
   }
   ```

## Catatan Teknis

- Gunakan Odoo MCP tools (`rust-mcp`), BUKAN RPC atau XML-RPC langsung
- Untuk `ir.rule` `domain_force`, parse expression jika perlu — ini adalah
  domain Odoo yang menentukan record apa yang visible
- Beberapa record rules menggunakan `user_id` atau `company_id` dalam domain.
  Eksekusi `eval` secara manual untuk menentukan records yang blocking.
- Versi Odoo mempengaruhi nama field dan availability model. Contoh:
  - Odoo 18+: `image_1920` tersedia
  - Record rules di Odoo 17+ menggunakan `/` separator untuk model reference
