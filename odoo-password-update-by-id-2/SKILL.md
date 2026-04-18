---
name: odoo-password-update-by-id-2
description: Ganti password user Odoo dengan ID=2 (atau custom). Trigger ketika user meminta: "ganti password user id 2", "reset password user id=2", "change password user id 2". Jika ada ID lain, override dengan ID yang diberikan user. Default password adalah "admin" jika tidak specified.
version: 1.0.0
---

# Odoo Password Update by User ID (Default ID=2)

Skill ini untuk mengganti password user Odoo. Default ke ID=2, tapi bisa override dengan ID lain.

## Default User

| Field | Value |
|-------|-------|
| User ID | 2 (default) |
| Password Default | admin |

## Parameters

| Parameter | Default | Required |
|----------|---------|----------|
| USER_ID | 2 | No (override jika diberikan) |
| DATABASE_NAME | - | Yes |
| NEW_PASSWORD | admin | No |

## Steps

### 1. Verifikasi User

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

## Usage Examples

```
/odoo-password-update-by-id-2 roedl_upgraded_20260415
```
→ Reset password user ID=2 ke "admin"

```
/odoo-password-update-by-id-2 roedl_upgraded_20260415 3 secret123
```
→ Set password user ID=3 ke "secret123"

## Important Notes

1. **Default ID=2** - jika tidak angegeben, pakai ID 2
2. **Default password "admin"** - jika tidak disebutkan
3. **Gunakan Odoo Shell** - bukan SQL langsung
4. **Selalu verifikasi user** sebelum update
