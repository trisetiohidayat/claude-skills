#!/usr/bin/env python3
"""
Odoo Database Connection Helper
Connects to Odoo PostgreSQL database to get module information.
Requires: pip install psycopg2-binary
"""
import os
import sys
import json
import configparser
from pathlib import Path


def parse_odoo_conf(conf_path):
    """Parse odoo.conf file and extract connection parameters."""
    if not os.path.exists(conf_path):
        print(f"ERROR: Config file not found: {conf_path}")
        return None

    config = configparser.ConfigParser()
    config.read(conf_path)

    db_config = {}
    if 'options' in config:
        opts = config['options']
        db_config['host'] = opts.get('db_host', 'localhost')
        db_config['port'] = opts.get('db_port', '5432')
        db_config['user'] = opts.get('db_user', 'odoo')
        db_config['password'] = opts.get('db_password', 'odoo')
        db_config['database'] = opts.get('db_name', 'odoo')

        # Parse addons_path
        addons_path = opts.get('addons_path', '')
        db_config['addons_path'] = [p.strip() for p in addons_path.split(',') if p.strip()]

    return db_config


def get_installed_modules(db_config):
    """Query installed modules from database."""
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        return None

    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        cur = conn.cursor()

        # Get all modules with their states
        cur.execute("""
            SELECT name, state, version, depends
            FROM ir_module_module
            ORDER BY name
        """)

        modules = []
        for row in cur.fetchall():
            depends = row[3]
            module_depends = []
            if depends:
                # depends is stored as a string representation of list
                # e.g., "['base', 'sale']"
                try:
                    import ast
                    module_depends = ast.literal_eval(depends) if depends else []
                except:
                    module_depends = []

            modules.append({
                'name': row[0],
                'state': row[1],
                'version': row[2],
                'depends': module_depends
            })

        cur.close()
        conn.close()

        return modules
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return None


def get_module_dependencies(modules):
    """Build dependency graph from module list."""
    dep_graph = {}

    for module in modules:
        name = module['name']
        dep_graph[name] = {
            'depends_on': module.get('depends', []),
            'required_by': []
        }

    # Calculate reverse dependencies
    for name, deps in dep_graph.items():
        for dep in deps['depends_on']:
            if dep in dep_graph:
                dep_graph[dep]['required_by'].append(name)

    return dep_graph


def main():
    if len(sys.argv) < 2:
        print("Usage: python db_connect.py <odoo.conf> [output_json]")
        print("")
        print("Example:")
        print("  python db_connect.py /etc/odoo/odoo.conf")
        print("  python db_connect.py /etc/odoo/odoo.conf modules.json")
        sys.exit(1)

    conf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Parsing config: {conf_path}")
    db_config = parse_odoo_conf(conf_path)

    if not db_config:
        sys.exit(1)

    print(f"Database: {db_config['database']}@{db_config['host']}:{db_config['port']}")
    print(f"Addons path: {db_config.get('addons_path', [])}")

    print("\nFetching installed modules...")
    modules = get_installed_modules(db_config)

    if modules is None:
        sys.exit(1)

    # Separate installed from others
    installed = [m for m in modules if m['state'] in ('installed', 'to upgrade', 'to install')]

    print(f"\nTotal modules: {len(modules)}")
    print(f"Installed modules: {len(installed)}")

    # Build dependency graph
    dep_graph = get_module_dependencies(installed)

    result = {
        'db_config': {
            'host': db_config['host'],
            'port': db_config['port'],
            'database': db_config['database'],
            'addons_path': db_config.get('addons_path', [])
        },
        'total_modules': len(modules),
        'installed_modules': len(installed),
        'modules': installed,
        'dependencies': dep_graph
    }

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nOutput saved to: {output_path}")
    else:
        print("\n--- Installed Modules ---")
        for m in installed[:20]:
            deps = m.get('depends', [])
            deps_str = f" (depends: {', '.join(deps)})" if deps else ""
            print(f"  - {m['name']} v{m.get('version', '?')}{deps_str}")
        if len(installed) > 20:
            print(f"  ... and {len(installed) - 20} more")

        print("\n--- Dependency Analysis ---")
        # Find critical modules (required by many)
        critical = [(name, len(data['required_by'])) for name, data in dep_graph.items() if data['required_by']]
        critical.sort(key=lambda x: -x[1])
        print("Modules required by many others:")
        for name, count in critical[:10]:
            print(f"  - {name}: required by {count} modules")


if __name__ == '__main__':
    main()
