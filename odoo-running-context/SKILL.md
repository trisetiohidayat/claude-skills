---
name: odoo-running-context
description: |
  Berikan context tentang Odoo yang sedang berjalan/dikonfigurasi berdasarkan launch.json di VS Code.
  Auto-load configuration dari .vscode/launch.json dan tampilkan informasi lengkap tentang Odoo instances yang tersedia.

  TRIGGER saat:
  - User bertanya tentang Odoo yang sedang berjalan
  - Perlu tahu Odoo version, port, database yang aktif
  - Mau switch antara Odoo 15 dan Odoo 19
  - Debug session information needed

  CONTEXT: Skill ini membaca .vscode/launch.json untuk dapat configuration yang sudah disetup di VS Code.
---

# Odoo Running Context Skill

Skill ini memberikan context tentang konfigurasi Odoo yang tersedia di project berdasarkan file `.vscode/launch.json`.

---

## Kapan Menggunakan Skill Ini

- Saat user bertanya "Odoo mana yang sedang jalan?" atau "Odoo versi berapa yang aktif?"
- Sebelum debugging atau development untuk memastikan environment yang benar
- Saat perlu switch antara Odoo 15 dan Odoo 19
- Untuk memberikan context di awal percakapan tentang konfigurasi Odoo project

---

## LANGKAH-LANGKAH

### Step 1: Read launch.json

```python
import json
import os

def get_launch_configurations():
    """
    Baca .vscode/launch.json dan extract semua konfigurasi Odoo.
    """
    # Cari launch.json
    possible_paths = [
        '.vscode/launch.json',
        os.path.expanduser('~/.claude/projects/-Users-tri-mac-project-roedl/.vscode/launch.json'),
    ]

    # Cek dari project root
    cwd = os.getcwd()
    project_root = find_project_root()

    launch_paths = [
        os.path.join(project_root, '.vscode', 'launch.json'),
        os.path.join(cwd, '.vscode', 'launch.json'),
        '/Users/tri-mac/project/roedl/.vscode/launch.json',  # Hardcoded fallback
    ]

    for launch_path in launch_paths:
        if os.path.exists(launch_path):
            with open(launch_path, 'r') as f:
                data = json.load(f)
            return parse_launch_configurations(data, launch_path)

    return None


def find_project_root():
    """Cari project root berdasarkan indicator Odoo."""
    cwd = os.getcwd()
    patterns = ['.conf', 'odoo', 'enterprise', 'custom_addons']

    # Cek dari cwd ke atas
    current = cwd
    for _ in range(5):  # Max 5 level up
        if any(os.path.exists(os.path.join(current, p)) for p in patterns):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return cwd
```

### Step 2: Parse Konfigurasi

```python
def parse_launch_configurations(data, source_path):
    """
    Parse launch.json configurations menjadi struktur yang mudah dibaca.
    """
    configs = []

    for config in data.get('configurations', []):
        parsed = {
            'name': config.get('name', 'Unknown'),
            'type': config.get('type', 'unknown'),
            'request': config.get('request', 'unknown'),
            'python_path': config.get('python', None),
            'program': config.get('program', None),
            'args': config.get('args', []),
            'env': config.get('env', {}),
            'console': config.get('console', 'unknown'),
        }

        # Extract Odoo version dari name atau program path
        parsed['odoo_version'] = extract_odoo_version(config)
        parsed['http_port'] = extract_http_port(config.get('args', []))
        parsed['database'] = extract_database(config.get('args', []))
        parsed['config_file'] = extract_config_file(config.get('args', []))
        parsed['dev_mode'] = '--dev=xml' in ' '.join(config.get('args', []))

        configs.append(parsed)

    return {
        'source_file': source_path,
        'configurations': configs,
        'count': len(configs)
    }


def extract_odoo_version(config):
    """Extract Odoo version dari konfigurasi."""
    name = config.get('name', '').lower()
    program = config.get('program', '').lower()

    # Dari nama
    match = re.search(r'(\d+\.?\d*)', name)
    if match:
        return match.group(1)

    # Dari program path
    match = re.search(r'odoo(\d+)', program)
    if match:
        return match.group(1)

    return 'unknown'


def extract_http_port(args):
    """Extract http port dari args."""
    for arg in args:
        if '--http-port=' in arg:
            return arg.split('=')[1]
    return None


def extract_database(args):
    """Extract database name dari args."""
    for arg in args:
        if '--database=' in arg:
            return arg.split('=')[1]
    return None


def extract_config_file(args):
    """Extract config file path dari args."""
    for arg in args:
        if '--config=' in arg:
            return arg.split('=')[1]
    return None
```

### Step 3: Pilihan Konfigurasi

```python
def present_configuration_choice(config_data):
    """
   处理多配置情况：
    - 1 config: langsung tampilkan
    - >1 configs: tanyakan user mau pakai yang mana
    """
    if not config_data or not config_data.get('configurations'):
        return None, "Tidak ada konfigurasi Odoo di launch.json"

    configs = config_data['configurations']
    count = len(configs)

    if count == 1:
        # Hanya 1 config, langsung gunakan
        return configs[0], None

    # count > 1: tampilkan semua opsi dan minta pilih
    return None, "CHOOSE_CONFIG"  # Signal untuk tampilkan pilihan


def display_odoo_context(config_data, selected_index=None):
    """
    Tampilkan context Odoo dalam format yang mudah dibaca.
    Jika selected_index diberikan, hanya tampilkan konfigurasi tersebut.
    Jika None, tampilkan semua.
    """
    if not config_data or not config_data.get('configurations'):
        return "Tidak ada konfigurasi Odoo di launch.json"

    configs = config_data['configurations']

    # Filter jika ada yang dipilih
    if selected_index is not None and 0 <= selected_index < len(configs):
        configs = [configs[selected_index]]

    output = []
    output.append("═" * 70)
    output.append("                    ODOO RUNNING CONTEXT")
    output.append("═" * 70)
    output.append(f"Source: {config_data['source_file']}")
    output.append("")

    for i, config in enumerate(config_data['configurations'], 1):
        is_selected = (selected_index is not None and i - 1 == selected_index)
        marker = "▶ " if is_selected else "  "

        output.append(f"{'─' * 70}")
        output.append(f"  [{i}] {marker}{config['name']}")
        output.append(f"{'─' * 70}")

        # Version badge
        version = config.get('odoo_version', '?')
        output.append(f"  📦 Odoo Version : {version}")

        # Port
        port = config.get('http_port') or 'default (8069)'
        output.append(f"  🌐 HTTP Port    : {port}")

        # Database
        db = config.get('database') or 'default'
        output.append(f"  🗄️  Database     : {db}")

        # Config file
        config_file = config.get('config_file')
        if config_file:
            output.append(f"  📄 Config File  : {os.path.basename(config_file)}")

        # Dev mode
        if config.get('dev_mode'):
            output.append(f"  ⚡ Dev Mode     : XML auto-reload enabled")

        # Python path
        if config.get('python_path'):
            python_name = os.path.basename(os.path.dirname(os.path.dirname(config['python_path'])))
            output.append(f"  🐍 Python Env   : {python_name}")

        # Program
        program = config.get('program', '')
        if program:
            output.append(f"  📍 Program      : {program}")

        output.append("")

    if selected_index is None:
        output.append("═" * 70)
    else:
        output.append("═" * 70)
        output.append(f"  ✓ Aktif: {configs[0]['name']}")

    return "\n".join(output)
```

---

## ALUR MULTI-CONFIG

Ketika ditemukan **lebih dari 1 konfigurasi**, skill ini menggunakan `AskUserQuestion` untuk meminta user memilih:

```
1. Read launch.json → parse semua konfigurasi
2. Jika count == 1 → langsung tampilkan dan gunakan
3. Jika count > 1 → tampilkan daftar + AskUserQuestion untuk pilih
4. Setelah user pilih → tampilkan hanya config yang dipilih
```

### Contoh AskUserQuestion (count > 1)

```python
# Build options untuk AskUserQuestion
questions = [{
    "question": "Ditemukan beberapa konfigurasi Odoo. Yang mana yang ingin digunakan?",
    "header": "Pilih Odoo",
    "options": [
        {
            "label": "Odoo 19.0 (port 8119)",
            "description": "Database: upgraded_test, Dev mode ON"
        },
        {
            "label": "Odoo 15.0 (port 8115)",
            "description": "Database: roedl, Dev mode ON"
        }
    ],
    "multiSelect": False
}]
```

### Respons Flow

```
User: "Odoo mana yang aktif?"
  → Skill: Read launch.json, ditemukan 2 konfigurasi
  → Skill: AskUserQuestion → user pilih [1]
  → Skill: Display hanya config[0] + return selected config
  → Done
```

### Structured Data

```python
{
    'source_file': '/path/to/launch.json',
    'configurations': [
        {
            'name': 'Odoo roedl 19.0',
            'odoo_version': '19.0',
            'http_port': '8119',
            'database': 'upgraded_test',
            'config_file': '/path/to/odoo19.conf',
            'python_path': '/path/to/venv19/bin/python',
            'program': '/path/to/odoo-bin',
            'dev_mode': True,
            'args': [
                '--config=/path/to/odoo19.conf',
                '--dev=xml',
                '--http-port=8119',
                '--database=upgraded_test'
            ],
            'env': {
                'PYTHONPATH': '/path/to/odoo:/path/to/project'
            }
        },
        {
            'name': 'Odoo roedl 15.0',
            'odoo_version': '15.0',
            'http_port': '8115',
            'database': 'roedl',
            'config_file': '/path/to/odoo.conf',
            'python_path': '/path/to/venv/bin/python',
            'program': '/path/to/odoo-bin',
            'dev_mode': True,
            'args': [...],
            'env': {...}
        }
    ],
    'count': 2,
    'selected_index': 0,        # Index yang dipilih user (0-based)
    'selected_config': {         # Config object yang sudah dipilih
        'name': 'Odoo roedl 19.0',
        'odoo_version': '19.0',
        ...
    }
}

# Single-config response (count == 1): auto-pilih tanpa AskUserQuestion
{
    'source_file': '/path/to/launch.json',
    'configurations': [...],
    'count': 1,
    'selected_index': 0,
    'selected_config': {...}
}
```

### Display Output (multi-config, setelah user pilih)

```
══════════════════════════════════════════════════════════════
                    ODOO RUNNING CONTEXT
══════════════════════════════════════════════════════════════
Source: /Users/tri-mac/project/roedl/.vscode/launch.json

──────────────────────────────────────────────────────────────
  [1] ▶ Odoo roedl 19.0          ← marker ▶ menunjukkan yang dipilih
──────────────────────────────────────────────────────────────
  📦 Odoo Version : 19.0
  🌐 HTTP Port    : 8119
  🗄️  Database     : upgraded_test
  📄 Config File  : odoo19.conf
  ⚡ Dev Mode     : XML auto-reload enabled
  🐍 Python Env   : venv19
  📍 Program      : /path/to/odoo-bin

══════════════════════════════════════════════════════════════
  ✓ Aktif: Odoo roedl 19.0
══════════════════════════════════════════════════════════════
```

### Display Output (single-config, count == 1)

```
══════════════════════════════════════════════════════════════
                    ODOO RUNNING CONTEXT
══════════════════════════════════════════════════════════════
Source: /Users/tri-mac/project/roedl/.vscode/launch.json

──────────────────────────────────────────────────────────────
  [1] Odoo roedl 19.0
──────────────────────────────────────────────────────────────
  📦 Odoo Version : 19.0
  🌐 HTTP Port    : 8119
  🗄️  Database     : upgraded_test
  📄 Config File  : odoo19.conf
  ⚡ Dev Mode     : XML auto-reload enabled
  🐍 Python Env   : venv19
  📍 Program      : /path/to/odoo-bin

══════════════════════════════════════════════════════════════
  ✓ Aktif: Odoo roedl 19.0
══════════════════════════════════════════════════════════════
```

> **Note:** Untuk single-config, tidak perlu AskUserQuestion karena hanya ada 1 opsi.

---

## CONTOH PENGGUNAAN

### Prompt 1: Tanya context (multi-config)
```
User: "Odoo mana yang sedang jalan?"
→ Skill: Read launch.json → ditemukan 2 konfigurasi
→ Skill: Tampilkan daftar + AskUserQuestion "Pilih Odoo yang ingin digunakan"
→ User pilih [1] Odoo 19.0
→ Skill: Display hanya Odoo 19.0 + return selected config
→ Done
```

### Prompt 2: Tanya context (single config)
```
User: "Odoo mana yang aktif?"
→ Skill: Read launch.json → hanya 1 konfigurasi ditemukan
→ Skill: Langsung tampilkan tanpa bertanya
→ Done
```

### Prompt 3: Debug specific version
```
User: "Saya mau debug Odoo 19"
→ Skill: Read launch.json → ditemukan 2 konfigurasi
→ Skill: AskUserQuestion (user bisa pilih langsung Odoo 19.0)
→ Skill: Display config Odoo 19.0
→ Done
```

### Prompt 4: Specify version explicitly
```
User: "Gunakan Odoo 15 context"
→ Skill: Read launch.json → ditemukan 2 konfigurasi
→ Skill: Langsung gunakan yang match "15" tanpa AskUserQuestion
→ Display Odoo 15.0 config
→ Done
```

---

## INTEGRASI DENGAN SKILL LAIN

### Dengan odoo-environment-detector

```
Skill ini memberikan VIEW (display context)
odoo-environment-detector memberikan ACTION (pilih environment)

Keduanya saling melengkapi:
- odoo-running-context: "Berikut konfigurasi yang tersedia..."
- odoo-environment-detector: "Pilih yang mana untuk digunakan..."
```

### Dengan odoo-path-resolver

```
odoo-running-context membaca launch.json (VS Code config)
odoo-path-resolver membaca .conf file (Odoo config)

Gunakan keduanya bersamaan untuk informasi lengkap:
- launch.json: Debug/runtime configuration
- odoo.conf: Full server configuration
```

---

## ERROR HANDLING

| Error | Handling |
|-------|----------|
| launch.json tidak ada | Tampilkan "Tidak ada .vscode/launch.json" dan saran |
| JSON tidak valid | Parse error message dan tampilkan |
| Tidak ada konfigurasi Odoo | Tampilkan "Tidak ada konfigurasi Odoo ditemukan" |
| Path tidak ditemukan | Tampilkan warning, tetap tampilkan info lain |

---

## CATATAN

1. **Hanya baca** - Skill ini tidak memodifikasi launch.json
2. **VS Code specific** - Membaca konfigurasi VS Code debugger
3. **Display focused** - Fokus pada menampilkan informasi dengan jelas
4. **Komplementer** - Gunakan dengan odoo-environment-detector untuk informasi lengkap
