---
name: portainer-mcp
description: >
  Every time you need to manage Portainer containers, Docker containers,
  inspect logs, exec into containers, manage stacks, check container status,
  or interact with Portainer environments — ALWAYS use this skill. Applies to
  ALL Portainer operations including dockerProxy calls, container management,
  stack operations, environment queries, and any Docker Engine API proxied calls
  through Portainer. This is the ONLY skill for Portainer interactions.
---

# Portainer MCP — Communication Guide

## Konfigurasi Environment

Konfirmasi dari `.mcp.json`:
- **Host:** `https://mac.dev.arkana.app`
- **Token:** `ptr_Xw0XBXHHDvW0pupMeR/a0QFiscs05Uf+k+kBOxli7Oc=` (API key, bukan JWT)
- **Local Endpoint ID:** `3` ( cek dari `listEnvironments` — `local` = ID 3)
- **Auth:** `x-api-key` header (bukan Bearer token)

---

## Aturan Wajib — Jangan Lakukan Kesalahan yang Sama

### ❌ SALAH (会导致 "malformed Content-Type header")

Menggunakan `dockerProxy` POST tanpa header atau dengan body saja:

```
TIDAK: dockerProxy(method="POST", dockerAPIPath="...", body={...})
      ↓ GAGAL: malformed Content-Type header
```

### ✅ BENAR

**Semua request POST dengan body — WAJIB include header `Content-Type`:**

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<NAME>/exec",
  environmentId: 3,
  headers: [{"key": "Content-Type", "value": "application/json"}],
  body: {"Cmd": ["/bin/sh","-c","whoami"], "User": "0"}
)
```

**GET requests — tidak perlu header:**

```json
dockerProxy(method: "GET", dockerAPIPath: "/containers/json", environmentId: 3)
```

---

## Docker Exec Pattern — 3-Step Workflow

Container exec di Portainer menggunakan pola 3-step:

### Step 1: Create Exec

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<CONTAINER_NAME>/exec",
  environmentId: 3,
  headers: [{"key": "Content-Type", "value": "application/json"}],
  body: {
    "Cmd": ["/bin/sh","-c","<COMMAND>"],
    "AttachStderr": true,
    "AttachStdout": true,
    "Tty": false,
    "User": "0"
  }
)
```

Response: `{ "Id": "<ExecID>" }`

**Penting:** Selalu gunakan `User: "0"` (root) untuk operasi yang butuh write access.

### Step 2: Start Exec

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/exec/<EXEC_ID>/start",
  environmentId: 3,
  headers: [{"key": "Content-Type", "value": "application/json"}],
  body: {
    "Detach": false,
    "Tty": false
  }
)
```

Response output langsung ada di response body (text).

### Step 3: Check Exit Code

Jika perlu tahu apakah command berhasil:
```json
dockerProxy(
  method: "GET",
  dockerAPIPath: "/exec/<EXEC_ID>/json",
  environmentId: 3
)
```

Cek field: `"ExitCode": 0` = sukses, `!= 0` = gagal.

---

## Common Operations

### List Containers

```json
dockerProxy(
  method: "GET",
  dockerAPIPath: "/containers/json",
  environmentId: 3
)
```

### Container Logs

```json
dockerProxy(
  method: "GET",
  dockerAPIPath: "/containers/<CONTAINER_ID>/logs?stdout=true&stderr=true&tail=100",
  environmentId: 3
)
```

### Inspect Container

```json
dockerProxy(
  method: "GET",
  dockerAPIPath: "/containers/<CONTAINER_ID>/json",
  environmentId: 3
)
```

### Get Git Remote (di dalam container)

```json
// Step 1: create exec
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<CONTAINER_NAME>/exec",
  environmentId: 3,
  headers: [{"key": "Content-Type", "value": "application/json"}],
  body: {
    "Cmd": ["/bin/sh","-c","cd <REPO_PATH> && git remote -v"],
    "AttachStderr": true,
    "AttachStdout": true,
    "Tty": false,
    "User": "0"
  }
)
```

### Docker Volume Path (jika tidak punya docker socket di host)

Volume di-mount ke container, tapi bisa di-inspect dari container inspect response:
- cari field `Mounts` → `Source` = path di host, `Destination` = path di container
- cari field `HostConfig.Binds` = format `<host>:<container>:rw`

---

## Troubleshooting

### "malformed Content-Type header"

→ Kamu FORGET menambahkan `headers` di POST request. Tambahkan:
```json
headers: [{"key": "Content-Type", "value": "application/json"}]
```

### Exec sudah selesai, tidak bisa start ulang

→ Setiap command baru butuh exec baru. Buat exec baru, jangan reuse ExecID yang sudah finish.

### "Invalid JWT token"

→ Token Portainer adalah API key, bukan JWT. Gunakan header `x-api-key` via MCP tool — jangan pakai curl dengan `Authorization: Bearer`. Tool `dockerProxy` sudah handle auth.

### Output exec kosong tapi ExitCode 0

→ Coba tambahkan `echo` separator di command, atau exec ulang dengan command berbeda.

---

## Error Pattern Reference

| Error | Cause | Fix |
|---|---|---|
| `malformed Content-Type header` | POST tanpa header | Tambah `headers` array |
| `Invalid JWT token` | Salah auth method | Gunakan API key, bukan Bearer |
| `Exec has already run` | Reusing finished ExecID | Buat exec baru |
| Output kosong ExitCode 0 | Command tidak print ke stdout | Gunakan echo separator |

---

## Checklist Sebelum Kirim dockerProxy Call

- [ ] GET atau POST?
  - **GET** → tanpa `headers`
  - **POST** → SELALU dengan `headers: [{"key": "Content-Type", "value": "application/json"}]`
- [ ] Body ada? (untuk POST) → dalam format JSON string
- [ ] `environmentId` sudah di-set? (default: 3 untuk local)
- [ ] ExecID sudah selesai (ExitCode != null)? Jika iya → buat exec baru
