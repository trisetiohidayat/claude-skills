---
name: odoo-path-resolver
description: |
  Resolve dan detect Odoo paths, environment configuration, dan project structure secara dinamis.
  Gunakan skill ini KETIKA MEMERLUKAN PATH untuk:
  - Odoo bin, Python, venv paths
  - CE, EE, custom addons paths
  - Database credentials dari config
  - Port dan service configuration
  - Project structure detection

  ⚠️ PENTING: SKILL INI TIDAK AUTO-LOAD! WAJIB DI-INVOKE EXPLICIT sebelum digunakan.

  CARA MENGGUNAKAN:
  1. Invoke dengan `Skill: odoo-path-resolver` (wajib!)
  2. Setelah di-invoke, baru bisa gunakan `paths = resolve()` untuk dapat dictionary paths
  3. Gunakan paths['odoo']['python'], paths['odoo']['bin'], etc.

  JANGAN hardcode path seperti /Users/tri-mac/project/roedl/... - SELALU gunakan resolve().

skills: []
---

# Odoo Path Resolver Skill

## Overview

Skill ini menyediakan fungsi untuk resolve path Odoo secara dinamis dari project structure atau config file.

## FUNCTIONS

### 1. get_odoo_config()

```python
def get_odoo_config():
    """
    Auto-detect Odoo configuration dari project.

    Returns:
        dict: {
            'project_root': '/path/to/project',
            'config_file': 'odoo19.conf',
            'python_path': '/path/to/venv/bin/python',
            'odoo_bin': '/path/to/odoo-bin',
            'db_host': 'localhost',
            'db_port': '5432',
            'db_user': 'odoo',
            'db_password': 'odoo',
            'db_name': 'roedl',
            'http_port': '8133',
            'addons_paths': [...]
        }
    """
```

### 2. get_addons_paths()

```python
def get_addons_paths():
    """
    Get semua addons paths dari config.

    Returns:
        dict: {
            'ce_path': '/path/to/odoo/addons',
            'ee_path': '/path/to/enterprise',
            'custom_paths': ['/path/to/custom1', '/path/to/custom2']
        }
    """
```

### 3. get_module_path(module_name)

```python
def get_module_path(module_name):
    """
    Cari module di semua addons paths.

    Args:
        module_name: Nama module yang dicari

    Returns:
        str: Full path ke module, atau None jika tidak ditemukan
    """
```

### 4. get_project_structure()

```python
def get_project_structure():
    """
    Deteksi struktur project Odoo.

    Returns:
        dict: {
            'odoo_versions': [15, 19],
            'has_ce': True,
            'has_ee': True,
            'custom_addons_dirs': ['custom_addons_19', 'custom_addons_15'],
            'config_files': ['odoo19.conf', 'odoo.conf']
        }
    """
```

---

## Step-by-Step Detection

### Step 1: Find Project Root

```python
import os
import glob

def find_project_root():
    """
    Cari project root secara otomatis.

    Strategy:
    1. Cek current working directory
    2. Cek parent directories untuk .conf files
    3. Cek untuk folder patterns: odoo*, enterprise*, custom_addons*
    """
    cwd = os.getcwd()

    # Pattern yang menunjukkan Odoo project
    patterns = [
        '*.conf',           # odoo.conf, odoo19.conf
        'odoo*.conf',       # odoo15.conf, etc
        '*odoo*.conf',      # custom odoo configs
    ]

    # Cek di current directory
    for pattern in patterns:
        matches = glob.glob(os.path.join(cwd, pattern))
        if matches:
            return os.path.dirname(matches[0])

    # Cek di parent directories
    parent = os.path.dirname(cwd)
    for pattern in patterns:
        matches = glob.glob(os.path.join(parent, pattern))
        if matches:
            return os.path.dirname(matches[0])

    return cwd
```

### Step 2: Find Config File

```python
def find_config_file(project_root):
    """
    Cari file konfigurasi Odoo.

    Priority:
    1. odoo19.conf (Odoo 19)
    2. odoo18.conf (Odoo 18)
    3. odoo17.conf (Odoo 17)
    4. odoo16.conf (Odoo 16)
    5. odoo15.conf (Odoo 15)
    6. odoo.conf (generic)
    """
    config_priority = [
        'odoo19.conf', 'odoo18.conf', 'odoo17.conf',
        'odoo16.conf', 'odoo15.conf', 'odoo.conf'
    ]

    for config_name in config_priority:
        config_path = os.path.join(project_root, config_name)
        if os.path.exists(config_path):
            return config_path

    # Fallback: cari file .conf pertama
    configs = glob.glob(os.path.join(project_root, '*.conf'))
    return configs[0] if configs else None
```

### Step 3: Parse Config

```python
import configparser

def parse_config(config_path):
    """
    Parse Odoo config file.

    Returns:
        dict dengan semua konfigurasi
    """
    config = configparser.ConfigParser()
    config.read(config_path)

    result = {
        'config_file': config_path,
        'http_port': config.get('options', 'http_port', fallback='8069'),
        'db_host': config.get('options', 'db_host', fallback='localhost'),
        'db_port': config.get('options', 'db_port', fallback='5432'),
        'db_user': config.get('options', 'db_user', fallback='odoo'),
        'db_password': config.get('options', 'db_password', fallback=''),
        'db_name': config.get('options', 'db_name', fallback=''),
        'addons_path': config.get('options', 'addons_path', fallback=''),
    }

    # Deteksi versi dari filename
    result['odoo_version'] = detect_version(config_path, result.get('addons_path', ''))

    return result
```

### Step 4: Detect Version

```python
import re

def detect_version(config_path, addons_path):
    """
    Deteksi versi Odoo dari config atau addons_path.

    Returns:
        int: Version number (15, 16, 17, 18, 19)
    """
    # Dari filename
    match = re.search(r'odoo(\d+)', os.path.basename(config_path).lower())
    if match:
        return int(match.group(1))

    # Dari addons_path
    for version in [15, 16, 17, 18, 19, 20]:
        if f'odoo{version}' in addons_path.lower():
            return version

    # Default
    return 19
```

### Step 5: Get Addons Paths

```python
def parse_addons_paths(addons_path_string):
    """
    Parse addons_path string menjadi komponen.

    Returns:
        dict dengan ce_path, ee_path, custom_paths
    """
    paths = addons_path_string.split(',')

    result = {
        'ce_path': None,
        'ee_path': None,
        'custom_paths': [],
        'all_paths': []
    }

    for path in paths:
        path = path.strip()
        if not path:
            continue

        result['all_paths'].append(path)

        # Deteksi tipe path dari name
        path_lower = path.lower()
        if '/odoo/addons' in path_lower or '/odoo/odoo/addons' in path_lower:
            result['ce_path'] = path
        elif '/enterprise' in path_lower:
            result['ee_path'] = path
        elif '/custom' in path_lower or '/addons' in path_lower:
            result['custom_paths'].append(path)

    return result
```

---

## Complete Resolver Class

```python
import os
import re
import glob
import configparser

class OdooPathResolver:
    """
    Centralized path resolver untuk Odoo project.
    Gunakan skill ini untuk mendapatkan semua path secara dinamis.
    """

    def __init__(self):
        self.project_root = None
        self.config_path = None
        self.config = {}
        self.addons_info = {}

    def resolve_all(self):
        """Resolve semua paths secara otomatis."""
        self.project_root = self.find_project_root()
        self.config_path = self.find_config_file(self.project_root)

        if self.config_path:
            self.config = self.parse_config(self.config_path)
            self.addons_info = self.parse_addons_paths(
                self.config.get('addons_path', '')
            )

        return self.get_all_paths()

    def find_project_root(self):
        """Cari project root."""
        cwd = os.getcwd()

        # Cek untuk Odoo project indicators
        indicators = ['*.conf', 'odoo*', 'enterprise*', 'custom_addons*']

        # Cek current dan parent
        for check_dir in [cwd, os.path.dirname(cwd)]:
            for indicator in indicators:
                if '*' in indicator:
                    if glob.glob(os.path.join(check_dir, indicator)):
                        return check_dir
                elif os.path.exists(os.path.join(check_dir, indicator)):
                    return check_dir

        return cwd

    def find_config_file(self, project_root):
        """Cari config file."""
        priority = ['odoo19.conf', 'odoo18.conf', 'odoo17.conf',
                   'odoo16.conf', 'odoo15.conf', 'odoo.conf']

        for name in priority:
            path = os.path.join(project_root, name)
            if os.path.exists(path):
                return path

        # Fallback
        configs = glob.glob(os.path.join(project_root, '*.conf'))
        return configs[0] if configs else None

    def parse_config(self, config_path):
        """Parse config file."""
        config = configparser.ConfigParser()
        config.read(config_path)

        options = config['options'] if 'options' in config else {}

        return {
            'config_file': config_path,
            'project_root': self.project_root,
            'odoo_version': self.detect_version(config_path, options.get('addons_path', '')),
            'http_port': options.get('http_port', '8069'),
            'longpolling_port': options.get('longpolling_port', '8072'),
            'db_host': options.get('db_host', 'localhost'),
            'db_port': options.get('db_port', '5432'),
            'db_user': options.get('db_user', 'odoo'),
            'db_password': options.get('db_password', ''),
            'db_name': options.get('db_name', ''),
            'addons_path': options.get('addons_path', ''),
        }

    def detect_version(self, config_path, addons_path):
        """Deteksi versi Odoo."""
        match = re.search(r'odoo(\d+)', os.path.basename(config_path).lower())
        if match:
            return int(match.group(1))

        for v in [15, 16, 17, 18, 19, 20]:
            if f'odoo{v}' in addons_path.lower():
                return v

        return 19

    def parse_addons_paths(self, addons_path_string):
        """Parse addons path."""
        paths = addons_path_string.split(',')
        result = {'ce': None, 'ee': None, 'custom': []}

        for path in paths:
            path = path.strip()
            if not path:
                continue

            path_lower = path.lower()
            if '/odoo/addons' in path_lower or '/odoo/odoo/addons' in path_lower:
                result['ce'] = path
            elif '/enterprise' in path_lower:
                result['ee'] = path
            else:
                result['custom'].append(path)

        return result

    def get_all_paths(self):
        """Return semua paths."""
        return {
            'project': {
                'root': self.project_root,
                'config': self.config_path,
            },
            'odoo': {
                'version': self.config.get('odoo_version', 19),
                'bin': self.find_odoo_bin(),
                'python': self.find_python(),
            },
            'database': {
                'host': self.config.get('db_host', 'localhost'),
                'port': self.config.get('db_port', '5432'),
                'user': self.config.get('db_user', 'odoo'),
                'password': self.config.get('db_password', ''),
                'name': self.config.get('db_name', ''),
            },
            'server': {
                'http_port': self.config.get('http_port', '8069'),
                'longpolling_port': self.config.get('longpolling_port', '8072'),
            },
            'addons': self.addons_info,
        }

    def find_odoo_bin(self):
        """Cari odoo-bin executable."""
        if not self.project_root:
            return None

        patterns = [
            os.path.join(self.project_root, 'odoo*/odoo/odoo-bin'),
            os.path.join(self.project_root, 'odoo*/odoo-bin'),
        ]

        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]

        return None

    def find_python(self):
        """Cari Python executable."""
        if not self.project_root:
            return None

        patterns = [
            os.path.join(self.project_root, 'venv*/bin/python'),
            os.path.join(self.project_root, 'odoo*/venv/bin/python'),
        ]

        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]

        return None

    def find_module(self, module_name):
        """Cari module di addons paths."""
        for path in self.addons_info.get('custom', []):
            module_path = os.path.join(path, module_name)
            if os.path.exists(module_path):
                return module_path

        # Cek di CE
        if self.addons_info.get('ce'):
            module_path = os.path.join(self.addons_info['ce'], module_name)
            if os.path.exists(module_path):
                return module_path

        # Cek di EE
        if self.addons_info.get('ee'):
            module_path = os.path.join(self.addons_info['ee'], module_name)
            if os.path.exists(module_path):
                return module_path

        return None


# Quick access functions
def resolve():
    """Quick resolve semua paths."""
    resolver = OdooPathResolver()
    return resolver.resolve_all()


def get_addons_path():
    """Get addons paths saja."""
    resolver = OdooPathResolver()
    resolver.resolve_all()
    return resolver.addons_info


def find_module(module_name):
    """Cari module."""
    resolver = OdooPathResolver()
    resolver.resolve_all()
    return resolver.find_module(module_name)
```

---

## Usage dalam Skill/Agent Lain

### Contoh 1: Di skill lain

```python
# Di awal skill, load dulu odoo-path-resolver
# Kemudian gunakan:

# Get semua paths
paths = resolve()
print(paths['odoo']['bin'])  # /path/to/odoo-bin
print(paths['addons']['ce'])  # /path/to/odoo/addons
print(paths['addons']['ee'])  # /path/to/enterprise
print(paths['database']['host'])  # localhost

# Cari module
module_path = find_module('sale')
```

### Contoh 2: Di agent

```
# Agent dapat langsung menggunakan:
- Invoke odoo-path-resolver untuk get paths
- Gunakan paths dari result untuk operasi
```

---

## Output Format

```json
{
  "project": {
    "root": "/Users/tri-mac/project/roedl",
    "config": "/Users/tri-mac/project/roedl/odoo19.conf"
  },
  "odoo": {
    "version": 19,
    "bin": "/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/odoo-bin",
    "python": "/Users/tri-mac/project/roedl/venv19/bin/python"
  },
  "database": {
    "host": "localhost",
    "port": "5432",
    "user": "odoo",
    "password": "odoo",
    "name": "roedl"
  },
  "server": {
    "http_port": "8133",
    "longpolling_port": "8072"
  },
  "addons": {
    "ce": "/Users/tri-mac/project/roedl/odoo19.0-roedl/odoo/addons",
    "ee": "/Users/tri-mac/project/roedl/enterprise-roedl-19.0/enterprise",
    "custom": [
      "/Users/tri-mac/project/roedl/custom_addons_19/roedl"
    ]
  }
}
```

---

## Integration Guide

### Untuk Agent:

Tambahkan ke skills list:
```yaml
skills:
  - odoo-path-resolver  # WAJIB - load dulu
  - odoo-base-understanding
  - odoo-error-analysis
  ...
```

### Untuk Skill lain:

Di awal skill, gunakan function dari skill ini:
```python
# Load paths
paths = resolve()

# Gunakan
odoo_bin = paths['odoo']['bin']
python = paths['odoo']['python']
```

---

## Catatan Penting

1. **WAJIB di-load duluan** sebelum skill lain yang memerlukan path
2. **JANGAN hardcode path** - gunakan skill ini
3. **Auto-detect** - mampu deteksi berbagai struktur project
4. **Fallback** - punya nilai default jika tidak ditemukan
