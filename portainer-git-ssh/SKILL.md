---
name: portainer-git-ssh
description: Setup SSH git pull di container Portainer. Trigger ketika user ingin git pull/push di container tanpa HTTPS auth. Gunakan skill ini setiap kali user menyebut 'git pull di container', 'SSH git pull', 'git pull via SSH di [nama container]', atau ingin clone/pull repo GitHub dari container Portainer tanpa token. Pastikan Portainer MCP sudah terhubung sebelum menjalankan skill ini.
---

# Portainer Container SSH Git Pull

## Prerequisites

- Portainer MCP sudah terhubung dan `dockerProxy` tool tersedia
- Container target sedang running
- Container base image: Debian/Ubuntu (ada `apt`)
- GitHub account dengan akses ke repo target
- Repo sudah di-clone di dalam container

## Workflow

Skill ini menjalankan 6 step berurutan. Setiap step wajib tunggu output sebelum lanjut ke step berikutnya.

---

## Step 1: Tanya User — Identifikasi Target

Sebelum mulai, minta user jelaskan:

1. **Container name** — nama container target (misal: `nok-odoo17`)
2. **Repo path** — path absolut repo di dalam container (misal: `/mnt/extra-addons/nok-erp`)
3. **Repo SSH URL** — format `git@github.com:<OWNER>/<REPO>.git`
4. **Branch** — nama branch untuk pull (misal: `staging-nok`, `staging`, `main`)

Jika user tidak sebutkan semua, tanya dulu sebelum lanjut.

---

## Step 2: Generate SSH Key di Container

Container tidak punya `ssh-keygen` (base image slim). Generate pakai Python `cryptography` library yang sudah ada di Odoo container.

Gunakan `dockerProxy` untuk create exec:

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<CONTAINER_NAME>/exec",
  body: {
    "Cmd": ["/bin/sh", "-c", "python3 << 'PYEOF'\nfrom cryptography.hazmat.primitives.asymmetric import ed25519\nfrom cryptography.hazmat.backends import default_backend\nfrom cryptography.hazmat.primitives import serialization\nprivate = ed25519.Ed25519PrivateKey.generate()\npublic = private.public_key()\npem = private.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.OpenSSH, encryption_algorithm=serialization.NoEncryption())\nwith open('/root/.ssh/id_ed25519', 'wb') as f: f.write(pem)\npub_ssh = public.public_bytes(encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH)\nprint(pub_ssh.decode())\nPYEOF"],
    "AttachStdout": true,
    "AttachStderr": true,
    "Tty": false,
    "User": "0"
  }
)
```

**Penting:** `User: "0"` = root, karena SSH key harus di `/root/.ssh/`.

Ambil `ExecID` dari response JSON.

---

## Step 3: Get Public Key & Tampilkan ke User

Start exec untuk dapat output (public key):

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/exec/<EXEC_ID>/start",
  body: {"Detach": false, "Tty": false}
)
```

Output adalah public key SSH (format: `ssh-ed25519 AAAA...`).

**Tampilkan ke user:**
```
Public key berhasil di-generate!

Tambahkan ke GitHub:
1. Buka: https://github.com/settings/keys
2. Klik "New SSH key"
3. Title: <CONTAINER_NAME>-container
4. Key: <PUBLIC_KEY_DARI_OUTPUT>
5. Klik "Add SSH key"

Selesai? Kabari saya untuk lanjut.
```

**TUNGGU user mengkonfirmasi** sebelum lanjut ke Step 4.

---

## Step 4: Install openssh-client

Container Odoo slim tidak punya SSH client. Install via apt.

Create exec:

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<CONTAINER_NAME>/exec",
  body: {
    "Cmd": ["/bin/sh", "-c", "apt-get update -qq && apt-get install -y -qq openssh-client"],
    "AttachStdout": true,
    "AttachStderr": true,
    "Tty": false,
    "User": "0"
  }
)
```

Start exec, tunggu output sampai terlihat `openssh-client ... Setting up ...`.

---

## Step 5: Setup known_hosts & Switch Remote

Dalam satu exec, lakukan dua hal:

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<CONTAINER_NAME>/exec",
  body: {
    "Cmd": ["/bin/sh", "-c", "echo 'github.com,20.205.243.166 ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOKG4+w1LpRRqMywFEU=' > /root/.ssh/known_hosts && chmod 644 /root/.ssh/known_hosts && cd <REPO_PATH> && git remote set-url origin <REPO_SSH_URL> && git remote -v"],
    "AttachStdout": true,
    "AttachStderr": true,
    "Tty": false,
    "User": "0"
  }
)
```

Ganti:
- `<REPO_PATH>` — path repo di container
- `<REPO_SSH_URL>` — format `git@github.com:<OWNER>/<REPO>.git`

Start exec. Verify output menunjukkan remote sudah berubah ke SSH:
```
origin  git@github.com:<OWNER>/<REPO>.git (fetch)
origin  git@github.com:<OWNER>/<REPO>.git (push)
```

---

## Step 6: Git Pull

```json
dockerProxy(
  method: "POST",
  dockerAPIPath: "/containers/<CONTAINER_NAME>/exec",
  body: {
    "Cmd": ["/bin/sh", "-c", "cd <REPO_PATH> && GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no' git pull origin <BRANCH>"],
    "AttachStdout": true,
    "AttachStderr": true,
    "Tty": false,
    "User": "0"
  }
)
```

Ganti `<BRANCH>` dengan nama branch target.

Start exec. Output akan terlihat seperti:
```
From github.com:<OWNER>/<REPO>
 * branch            <BRANCH> -> FETCH_HEAD
Already up to date.
```

Atau jika ada update baru:
```
From github.com:<OWNER>/<REPO>
 * branch            <BRANCH> -> FETCH_HEAD
Updating abc123..def456
 Fast-forward
  file.py |  10 ++++++
```

---

## Error Handling

### "ssh: not found"
openssh-client belum terinstall. Kembali ke Step 4, pastikan apt-get selesai sepenuhnya.

### "Permission denied (publickey)"
Public key belum di-add ke GitHub. Tanya user apakah sudah menambahkan, jika belum minta ulangi Step 3.

### "Could not read Username"
Remote masih HTTPS. Verify Step 5 output, pastikan remote sudah berubah ke `git@github.com:`.

### "Host key verification failed"
known_hosts belum di-setup. Verify Step 5, pastikan file `/root/.ssh/known_hosts` sudah ada.

### python3 not found
Container tidak punya Python. Gunakan `ssh-keygen` dari openssl jika tersedia, atau install python3 dulu:
```json
dockerProxy(
  body: {
    "Cmd": ["/bin/sh", "-c", "apt-get install -y -qq python3"],
    ...
  }
)
```

---

## Catatan Penting

1. **SSH key tidak persistent** — hilang saat container di-recreate. Jika container di-recreate, ulangi semua step dari awal.

2. **openssh-client**是一次性 install — selama container tidak di-recreate, tidak perlu install ulang.

3. **`User: "0"` (root) wajib** — SSH key harus di `/root/.ssh/` dan git operations perlu write ke `.git/`.

4. **Tunggu setiap step selesai** — dockerProxy exec adalah asynchronous. Selalu start exec baru untuk setiap command.

5. **Simpan variabel** — catat container name, repo path, repo URL, branch untuk setiap session. Jika user tanya lagi untuk container berbeda, mulai dari Step 1.
