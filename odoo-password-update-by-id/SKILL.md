---
name: odoo-password-update-by-id
description: Ganti password user Odoo berdasarkan user ID. Trigger ketika user meminta update password dengan ID user, contoh: "ganti password user id 2", "change password user with id=3", "update password for user 2 on database X". Selalu gunakan skill ini saat ada request terkait mengganti password Odoo user.
version: 1.0.0
---

# Odoo Password Update by User ID

Skill ini digunakan untuk mengganti password user Odoo berdasarkan user ID. Selalu gunakan Odoo Shell untuk operasi password - **JANGAN pernah gunakan SQL langsung**.

## Prerequisites

- Virtual environment `venv19` harus aktif
- Config file `odoo19.conf` harus ada di project root
- Database harus running dan accessible

## Steps

### 1. Verifikasi User ID

Sebelum mengganti password, selalu verifikasi dulu user yang akan diupdate:

```bash
source venv19/bin/activate && echo "
user = env['res.users'].search([('id', '=', <USER_ID>)])
if user:
    print(f'User found: id={user.id}, login={user.login}, name={user.name}')
else:
    print('User not found!')
" | python odoo19.0-roedl/odoo/odoo-bin shell -c odoo19.conf -d <DATABASE_NAME>
```

### 2. Update Password

Gunakan Odoo Shell untuk update password:

```bash
source venv19/bin/activate && echo "
user = env['res.users'].search([('id', '=', <USER_ID>)])
if user:
    user.write({'password': '<NEW_PASSWORD>'})
    env.cr.commit()
    print(f'Password changed for user: id={user.id}, login={user.login}')
else:
    print('User not found!')
" | python odoo19.0-roedl/odoo/odoo-bin shell -c odoo19.conf -d <DATABASE_NAME>
```

## Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `USER_ID` | User ID di Odoo (misal: 2) | Yes |
| `DATABASE_NAME` | Nama database target | Yes |
| `NEW_PASSWORD` | Password baru (default: admin) | No (default: admin) |

## Usage Examples

**Contoh 1: Ganti password user ID=2**
```
User: "ganti password user id=2 di db roedl_upgraded_20260415"
→ Update password user dengan id=2 ke "admin"
```

**Contoh 2: Ganti password dengan password custom**
```
User: "ganti password user id=3 di db roedl_upgraded_20260415 ke 'secret123'"
→ Update password user dengan id=3 ke "secret123"
```

## Important Notes

1. **SELALU verifikasi user dulu** sebelum update - pastikan user ID benar
2. **Gunakan Odoo Shell** - ini adalah cara yang benar dan aman
3. **JANGAN pernah generate SHA hash manual** - Odoo akan auto-hash password dengan `write()`
4. **Commit transaksi** dengan `env.cr.commit()` setelah write

## Error Handling

Jika user tidak ditemukan:
```
User not found! - Verifikasi user ID dengan query SELECT id, login, name FROM res_users WHERE id = <USER_ID>;
```

Jika error koneksi database:
```
Pastikan Odoo config正确 dan database accessible
```
