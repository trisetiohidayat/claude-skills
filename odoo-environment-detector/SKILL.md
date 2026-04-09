---
name: odoo-environment-detector
description: |
  Deteksi dan pilih Python environment serta odoo-bin path untuk project Odoo.
  Auto-detect semua environment yang tersedia, tampilkan ke user, dan biarkan user memilih.
  WAJIB gunakan sebelum memulai workflow Odoo agent teams.

  Trigger saat: perlu menentukan Python environment dan odoo-bin path untuk Odoo project.
skills:
  - odoo-path-resolver
---

# Odoo Environment Detector

Skill ini mendeteksi Python environments dan odoo-bin paths yang tersedia di project Odoo, lalu membiarkan user memilih mana yang akan digunakan.

---

## Kapan Menggunakan Skill Ini

- Sebelum memulai `/odoo-agent-teams-v3`
- Saat perlu menentukan environment untuk operasi Odoo
- Saat user ingin切换 ke environment berbeda

---

## Output Format

Skill ini akan me-return dictionary dengan:

```python
{
    'python_env': {
        'name': 'venv19',
        'path': '/path/to/venv19/bin/python',
        'version': 'Python 3.10'
    },
    'odoo_bin': {
        'path': '/path/to/odoo-bin',
        'version': 19,
        'source': 'config: odoo19.conf'
    },
    'project_dir': '/path/to/project',
    'config_file': '/path/to/odoo19.conf'
}
```

---

## LANGKAH-LANGKAH DETEKSI

### Step 1: Load Base Paths dari odoo-path-resolver

```python
# Di awal, gunakan odoo-path-resolver untuk dapat base paths
from odoo_path_resolver import resolve

def get_base_paths():
    """
    Load base paths dari odoo-path-resolver.
    Ini memberikan project root, config, dan path-path dasar.
    """
    try:
        paths = resolve()
        return {
            'project_root': paths['project']['root'],
            'config_file': paths['project']['config'],
            'odoo_bin': paths['odoo']['bin'],
            'python_path': paths['odoo']['python'],
            'database': paths['database'],
            'server': paths['server'],
            'addons': paths['addons'],
        }
    except Exception as e:
        # Fallback jika resolve gagal
        return None

# Usage:
base = get_base_paths()
if base:
    project_root = base['project_root']
    # Gunakan untuk deteksi lebih lanjut
```

### Step 2: Deteksi Python Environments

```python
import os
import sys
import glob
import subprocess

def detect_python_environments(project_dir):
    """
    Deteksi semua Python environment yang tersedia.
    Gunakan paths dari resolve() sebagai base, lalu cari lebih banyak.
    """
    from odoo_path_resolver import resolve

    envs = []

    # 1. Load base paths dari odoo-path-resolver
    try:
        base_paths = resolve()
        if base_paths.get('odoo', {}).get('python'):
            # Python dari config
            python_path = base_paths['odoo']['python']
            envs.append({
                'name': 'venv19 (from config)',
                'path': python_path,
                'version': get_python_version(python_path),
                'type': 'venv',
                'source': 'odoo-path-resolver'
            })
    except:
        pass

    # 2. System Python
    system_python = sys.executable
    envs.append({
        'name': 'System Python',
        'path': system_python,
        'version': f"Python {sys.version_info.major}.{sys.version_info.minor}",
        'type': 'system'
    })

    # 3. Virtual Environments (venv) - cari lebih banyak
    venv_patterns = [
        os.path.join(project_dir, "**/venv"),
        os.path.join(project_dir, "**/.venv"),
        os.path.join(project_dir, "**/env"),
        os.path.join(project_dir, "**/venv19"),
        os.path.join(project_dir, "**/venv*"),
    ]

    for pattern in venv_patterns:
        for venv_path in glob.glob(pattern, recursive=True):
            python_path = os.path.join(venv_path, "bin", "python")
            if os.path.exists(python_path):
                # Skip jika sudah ada di list
                if any(e['path'] == python_path for e in envs):
                    continue

                version = get_python_version(python_path)
                venv_name = os.path.basename(venv_path)
                parent_dir = os.path.basename(os.path.dirname(venv_path))
                if parent_dir and parent_dir not in ['venv', 'env', '.venv']:
                    name = f"{parent_dir}/{venv_name}"
                else:
                    name = venv_name

                envs.append({
                    'name': name,
                    'path': python_path,
                    'version': version,
                    'type': 'venv'
                })

    # 4. Conda environments
    conda_envs = os.environ.get('CONDA_PREFIX')
    if conda_envs:
        conda_python = os.path.join(conda_envs, "bin", "python")
        if os.path.exists(conda_python):
            envs.append({
                'name': 'Conda Base',
                'path': conda_python,
                'version': 'Conda',
                'type': 'conda'
            })

    return envs


def get_python_version(python_path):
    """Dapatkan versi Python dari executable."""
    try:
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.stdout.strip() or result.stderr.strip()
    except:
        return "Unknown"
```

### Step 3: Deteksi Odoo Config File

```python
import os
import glob
import re

def find_odoo_configs(project_dir):
    """
    Cari semua file konfigurasi Odoo di project.
    Gunakan paths dari resolve() sebagai base.
    """
    from odoo_path_resolver import resolve

    configs = []

    # 1. Ambil config dari odoo-path-resolver (prioritas utama)
    try:
        base_paths = resolve()
        if base_paths.get('project', {}).get('config'):
            config_path = base_paths['project']['config']
            configs.append({
                'path': config_path,
                'name': os.path.basename(config_path),
                'version': extract_version_from_config(config_path),
                'source': 'odoo-path-resolver'
            })
    except:
        pass

    # 2. Cari config lain di project
    skip_patterns = ['test', 'sample', 'docker', 'devops', 'qa']

    for conf_file in glob.glob(os.path.join(project_dir, "*.conf")):
        basename = os.path.basename(conf_file).lower()

        # Skip jika ada pattern yang diabaikan
        if any(p in basename for p in skip_patterns):
            continue

        # Skip jika sudah ada di list
        if any(c['path'] == conf_file for c in configs):
            continue

        version = extract_version_from_config(conf_file)

        configs.append({
            'path': conf_file,
            'name': os.path.basename(conf_file),
            'version': version
        })

    return configs


def extract_version_from_config(config_path):
    """Ekstrak versi Odoo dari nama config file."""
    basename = os.path.basename(config_path).lower()
    version_match = re.search(r'odoo(\d+)', basename)
    return int(version_match.group(1)) if version_match else None
```

### Step 4: Deteksi Odoo-bin dari Config

```python
import os
import re
import glob as g

def detect_odoo_bins(project_dir):
    """
    Deteksi semua odoo-bin paths yang tersedia.
    Gunakan paths dari resolve() sebagai base.
    """
    from odoo_path_resolver import resolve

    odoo_bins = []

    # 1. Ambil dari odoo-path-resolver (prioritas utama)
    try:
        base_paths = resolve()
        if base_paths.get('odoo', {}).get('bin'):
            bin_path = base_paths['odoo']['bin']
            version = extract_version_from_path(bin_path)
            odoo_bins.append({
                'path': bin_path,
                'version': version,
                'source': 'odoo-path-resolver'
            })
    except:
        pass

    # 2. Deteksi dari config file (jika ada banyak config)
    config_files = find_odoo_configs(project_dir)
    for config in config_files:
        if config.get('source') == 'odoo-path-resolver':
            continue

        bin_path = detect_odoo_bin_from_config(config['path'])
        if bin_path and not any(b['path'] == bin_path for b in odoo_bins):
            odoo_bins.append({
                'path': bin_path,
                'version': config.get('version'),
                'source': f"config: {config['name']}"
            })

    # 3. Directory scan (fallback)
    for bin_path in g.glob(os.path.join(project_dir, "**/odoo-bin"), recursive=True):
        if 'site-packages' in bin_path or 'test' in bin_path.lower():
            continue
        if any(b['path'] == bin_path for b in odoo_bins):
            continue

        version = extract_version_from_path(bin_path)
        odoo_bins.append({
            'path': os.path.abspath(bin_path),
            'version': version,
            'source': 'directory scan'
        })

    return odoo_bins


def detect_odoo_bin_from_config(config_path):
    """
    Deteksi odoo-bin path dari config file.
    """
    if not os.path.exists(config_path):
        return None

    with open(config_path, 'r') as f:
        content = f.read()

    match = re.search(r'addons_path\s*=\s*(.+)', content)
    if not match:
        return None

    addons_path_str = match.group(1).strip()
    addons_paths = [p.strip() for p in addons_path_str.split(',')]

    if not addons_paths:
        return None

    first_addon_path = addons_paths[0]

    possible_locations = [
        os.path.join(os.path.dirname(first_addon_path), 'odoo-bin'),
        os.path.join(os.path.dirname(os.path.dirname(first_addon_path)), 'odoo-bin'),
        os.path.join(first_addon_path, 'odoo', 'odoo-bin'),
    ]

    for bin_path in possible_locations:
        if os.path.exists(bin_path):
            return os.path.abspath(bin_path)

    return None


def extract_version_from_path(path):
    """Ekstrak versi Odoo dari path."""
    version_match = re.search(r'odoo(\d+)', path.lower())
    return int(version_match.group(1)) if version_match else None
```

### Step 5: Parse Config untuk Info Lengkap

```python
import configparser

def parse_config(config_path):
    """
    Parse config file dan ekstrak semua nilai penting.
    Gunakan resolve() sebagai base, lalu override dengan config spesifik.
    """
    from odoo_path_resolver import resolve

    result = {
        'http_port': None,
        'db_host': 'localhost',
        'db_port': '5432',
        'db_user': 'odoo',
        'db_password': '',
        'db_name': '',
        'addons_path': '',
    }

    # 1. Ambil dari odoo-path-resolver (base)
    try:
        base_paths = resolve()
        if base_paths.get('database'):
            result.update({
                'db_host': base_paths['database'].get('host', 'localhost'),
                'db_port': base_paths['database'].get('port', '5432'),
                'db_user': base_paths['database'].get('user', 'odoo'),
                'db_password': base_paths['database'].get('password', ''),
                'db_name': base_paths['database'].get('name', ''),
            })
        if base_paths.get('server'):
            result['http_port'] = base_paths['server'].get('http_port')
    except:
        pass

    # 2. Override dengan parsing config file langsung
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)

        if 'options' in config:
            for key in ['http_port', 'db_host', 'db_port', 'db_user', 'db_password', 'db_name', 'addons_path']:
                if config.has_option('options', key):
                    value = config.get('options', key)
                    if value:
                        result[key] = value

    # 3. Deteksi versi dari filename
    filename = os.path.basename(config_path).lower()
    match = re.search(r'odoo(\d+)', filename)
    result['odoo_version'] = int(match.group(1)) if match else 19

    return result
```

---

## TAMPILKAN KE USER

### Format Tampilan

```
═══════════════════════════════════════════════════════════════
              ENVIRONMENT DETECTION RESULTS
═══════════════════════════════════════════════════════════════

📁 Project: <PROJECT_ROOT>
📄 Config: odoo19.conf

─────────────────────────────────────────────────────────────
                    PYTHON ENVIRONMENTS
─────────────────────────────────────────────────────────────
[1] venv19 (Python 3.10)
    Path: <PROJECT_ROOT>/venv19/bin/python
    Type: venv

[2] System Python (Python 3.12)
    Path: /usr/local/bin/python3
    Type: system

─────────────────────────────────────────────────────────────
                      ODOO-BIN PATHS
─────────────────────────────────────────────────────────────
[A] Odoo 19 (from config)
    Path: <PROJECT_ROOT>/odoo19.0-roedl/odoo/odoo-bin
    Source: odoo19.conf

[B] Odoo 15 (from directory)
    Path: <PROJECT_ROOT>/odoo15.0-roedl/odoo/odoo-bin
    Source: directory scan

═══════════════════════════════════════════════════════════════

PILIH PYTHON ENVIRONMENT (1-2): 1
PILIH ODOO-BIN PATH (A-B): A

✅ Environment Selected:
  - Python: venv19 (Python 3.10)
  - Odoo-bin: Odoo 19
  - Config: odoo19.conf
═══════════════════════════════════════════════════════════════
```

---

## USER SELECTION

### Tanya User dengan AskUserQuestion

```python
# Untuk Python Environment
AskUserQuestion(questions=[{
    "header": "Python Env",
    "multiSelect": False,
    "options": [
        {"label": env['name'], "description": f"{env['version']} - {env['path']}"}
        for env in python_envs
    ],
    "question": "Pilih Python environment yang akan digunakan:"
}])

# Untuk Odoo-bin
AskUserQuestion(questions=[{
    "header": "Odoo-bin",
    "multiSelect": False,
    "options": [
        {"label": f"Odoo {bin['version']}", "description": bin['path']}
        for bin in odoo_bins
    ],
    "question": "Pilih odoo-bin path yang akan digunakan:"
}])
```

### Default Selection

Jika hanya ada 1 environment, tetap tanyakan ke user tapi kasih opsi default:

```
Hanya terdeteksi 1 Python environment: venv19
Otomatis terpilih. Ketik 'ya' untuk lanjut, atau nomor untuk pilih yang lain.
```

---

## RETURN VALUE

Setelah user memilih, return dictionary (dengan paths dari resolve() sebagai base):

```python
{
    'python_env': {
        'name': 'venv19',
        'path': paths['odoo']['python'],  # Dari resolve()
        'version': 'Python 3.10',
        'type': 'venv'
    },
    'odoo_bin': {
        'path': paths['odoo']['bin'],  # Dari resolve()
        'version': 19,
        'source': 'odoo-path-resolver'
    },
    'config': {
        'path': paths['project']['config'],  # Dari resolve()
        'http_port': paths['server']['http_port'],  # Dari resolve()
        'db_host': paths['database']['host'],  # Dari resolve()
        'db_port': paths['database']['port'],  # Dari resolve()
        'db_user': paths['database']['user'],  # Dari resolve()
        'db_name': paths['database']['name'],  # Dari resolve()
        'odoo_version': paths['odoo']['version']  # Dari resolve()
    },
    'project_dir': paths['project']['root']  # Dari resolve()
}
```

**Catatan**: Return value menggunakan paths dari `resolve()` sebagai base - ini memastikan konsistensi dengan skill lain yang juga menggunakan odoo-path-resolver.

---

## CONTOH PENGGUNAAN

### Langsung (Standalone)
```
User: "Deteksi environment untuk project Odoo saya"
→ Skill mendeteksi → Tampilkan → User Pilih → Return result
```

### Dari Skill Lain (odoo-agent-teams-v3)
```
Lead: "먼저 environment detector untuk pilih Python dan odoo-bin"
→ Invoke skill ini → User pilih → Return result
→ Lanjut dengan workflow menggunakan environment yang dipilih
```

---

## ERROR HANDLING

| Error | Handling |
|-------|----------|
| odoo-path-resolver gagal | Fallback ke manual detection |
| Tidak ada Python venv | Tampilkan system Python sebagai default |
| Tidak ada config file | Tanya user input manual |
| Tidak ada odoo-bin | Tanya user input manual atau cari di PATH |
| Config tidak valid | Skip, cari alternatif |
| Resolve returns None | Manual detection tetap berjalan |

---

## CATATAN

- Skill ini TIDAK memodifikasi apapun - hanya deteksi dan suggest
- User SELALU punya keputusan akhir
- Hasil deteksi bisa di-cache untuk session yang sama
- **WAJIB menggunakan odoo-path-resolver** sebagai base untuk semua path references
- Gunakan `from odoo_path_resolver import resolve` di awal function
- Pattern: `paths = resolve()` lalu akses `paths['odoo']['python']`, `paths['odoo']['bin']`, dll
