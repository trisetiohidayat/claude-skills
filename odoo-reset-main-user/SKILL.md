---
name: odoo-reset-main-user
description: Reset password user main_user (ID=2) ke "admin". Trigger ketika user meminta: "reset password main_user", "ganti password main_user", "reset main_user password", "ubah password main_user". Cukup masukkan nama database saja. Gunakan skill ini setiap kali ada request terkait reset password untuk user main_user.
version: 1.0.0
---

# Odoo Reset Main User Password

Skill ini untuk reset password user `main_user` (ID=2) ke password default `admin`. Hanya perlu masukkan nama database.

## Prerequisites

- Virtual environment `venv19` harus aktif
- Config file `odoo19.conf` ada di project root
- Database harus running dan accessible

## User Info

| Field | Value |
|-------|-------|
| User ID | 2 |
| Login | main_user |
| Default Password | admin |

## Steps

### 1. Verifikasi User

```bash
source venv19/bin/activate && echo "
user = env['res.users'].search([('id', '=', 2)])
if user:
    print(f'User found: id={user.id}, login={user.login}, name={user.name}')
else:
    print('User not found!')
" | python odoo19.0-roedl/odoo/odoo-bin shell -c odoo19.conf -d <DATABASE_NAME>
```

### 2. Reset Password ke "admin"

```bash
source venv19/bin/activate && echo "
user = env['res.users'].search([('id', '=', 2)])
if user:
    user.write({'password': 'admin'})
    env.cr.commit()
    print(f'Password reset for: id={user.id}, login={user.login}')
else:
    print('User not found!')
" | python odoo19.0-roedl/odoo/odoo-bin shell -c odoo19.conf -d <DATABASE_NAME>
```

## Usage

```
/odoo-reset-main-user roedl_upgraded_20260415
```

Output:
```
Password reset for: id=2, login=main_user
```

## Catatan

- Password default selalu `admin`
- User ID selalu 2 (main_user)
- Hanya perlu masukkan nama database
