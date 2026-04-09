#!/usr/bin/env python3
"""
Pre-Migration Checklist Script

Validates that all prerequisites are met before running Odoo migration.

Usage:
    python3 pre_migration_checklist.py <modules_path> <target_version>
    python3 pre_migration_checklist.py /path/to/modules 17.0
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class PreMigrationChecker:
    """Pre-migration validation checks."""

    def __init__(self, modules_path: str, target_version: str):
        self.modules_path = Path(modules_path).resolve()
        self.target_version = target_version
        self.target_num = int(target_version.split('.')[0])
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def check_python_version(self) -> bool:
        """Check Python version compatibility."""
        version = sys.version_info

        if self.target_num >= 17:
            required = (3, 8)
            if version < required:
                self.issues.append(
                    f"Python {required[0]}.{required[1]}+ required for Odoo {self.target_version}, "
                    f"found {version.major}.{version.minor}"
                )
                return False
            else:
                self.passed.append(f"Python version: {version.major}.{version.minor}.{version.micro}")
                return True

        # For older versions, Python 3.6+ is typically fine
        if version < (3, 6):
            self.issues.append(f"Python 3.6+ required, found {version.major}.{version.minor}")
            return False

        self.passed.append(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True

    def check_odoo_module_migrator(self) -> bool:
        """Check if odoo-module-migrator is installed."""
        try:
            result = subprocess.run(
                ['odoo-module-migrate', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.passed.append(f"odoo-module-migrator: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        except Exception:
            pass

        self.issues.append(
            "odoo-module-migrator not found. Install with: pip3 install odoo-module-migrator"
        )
        return False

    def check_modules_path(self) -> bool:
        """Check if modules path exists."""
        if not self.modules_path.exists():
            self.issues.append(f"Modules path does not exist: {self.modules_path}")
            return False

        # Check for __manifest__.py or __openerp__.py
        found_manifest = False
        for item in self.modules_path.rglob('*'):
            if item.is_file() and item.name in ['__manifest__.py', '__openerp__.py']:
                found_manifest = True
                break

        if not found_manifest:
            # Try subdirectories
            for item in self.modules_path.iterdir():
                if item.is_dir() and (item / '__manifest__.py').exists():
                    found_manifest = True
                    break

        if found_manifest:
            self.passed.append(f"Modules path valid: {self.modules_path}")
            return True
        else:
            self.warnings.append(f"No Odoo modules found in {self.modules_path}")
            return False

    def check_git_installed(self) -> bool:
        """Check if git is installed."""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.passed.append(f"Git: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass

        self.warnings.append("Git not found - may be needed for some operations")
        return False

    def check_database_backup(self) -> bool:
        """Check if database backup exists."""
        # Look for common dump file names
        possible_dumps = [
            'dump.sql',
            'dump.sql.gz',
            'database.sql',
            '*.dump'
        ]

        current_dir = Path.cwd()
        found_dumps = []

        for pattern in possible_dumps:
            found_dumps.extend(current_dir.glob(pattern))

        if found_dumps:
            for dump in found_dumps:
                self.passed.append(f"Found dump file: {dump.name}")
            return True
        else:
            self.warnings.append(
                "No database dump found. Create backup before migration with: "
                "pg_dump -Fc dbname > dump.sql"
            )
            return False

    def check_contract_file(self) -> bool:
        """Check if contract file exists for database upgrade."""
        contract_file = Path('.odoo_contract')

        if contract_file.exists():
            with open(contract_file, 'r') as f:
                contract = f.read().strip()
            if contract:
                self.passed.append("Contract file exists")
                return True
            else:
                self.warnings.append("Contract file is empty")
                return False
        else:
            self.warnings.append(
                "Contract file (.odoo_contract) not found. "
                "Required for database upgrade via upgrade.odoo.com"
            )
            return False

    def check_dependencies(self) -> bool:
        """Check for required Python dependencies."""
        required_modules = [
            'psycopg2',
        ]

        missing = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)

        if missing:
            self.warnings.append(f"Missing optional modules: {', '.join(missing)}")
            return False

        self.passed.append("Core dependencies available")
        return True

    def check_modules_manifests(self) -> Dict[str, Dict]:
        """Check module manifests for compatibility issues."""
        issues_by_module = {}

        for item in self.modules_path.rglob('__manifest__.py'):
            module_name = item.parent.name

            try:
                with open(item, 'r') as f:
                    content = f.read()

                issues = []

                # Check for version key
                if "'version'" not in content and '"version"' not in content:
                    issues.append("Missing 'version' in manifest")

                # Check for dependencies
                if "'depends'" not in content and '"depends"' not in content:
                    issues.append("No dependencies declared")

                if issues:
                    issues_by_module[module_name] = issues
                else:
                    self.passed.append(f"Module {module_name}: manifest OK")

            except Exception as e:
                issues_by_module[module_name] = [f"Error reading: {e}"]

        return issues_by_module

    def run_all_checks(self) -> bool:
        """Run all pre-migration checks."""
        print("=" * 60)
        print("ODOO PRE-MIGRATION CHECKLIST")
        print("=" * 60)
        print(f"Modules Path: {self.modules_path}")
        print(f"Target Version: {self.target_version}")
        print("=" * 60)
        print()

        # Run checks
        self.check_python_version()
        self.check_odoo_module_migrator()
        self.check_modules_path()
        self.check_git_installed()
        self.check_database_backup()
        self.check_contract_file()
        self.check_dependencies()

        # Check manifests
        manifest_issues = self.check_modules_manifests()

        # Print results
        if self.passed:
            print(f"{'[PASS]'.ljust(10)} PASSED CHECKS")
            for item in self.passed:
                print(f"            ✓ {item}")
            print()

        if self.warnings:
            print(f"{'[WARN]'.ljust(10)} WARNINGS")
            for item in self.warnings:
                print(f"            ⚠ {item}")
            print()

        if self.issues:
            print(f"{'[FAIL]'.ljust(10)} ISSUES - MIGRATION MAY FAIL")
            for item in self.issues:
                print(f"            ✗ {item}")
            print()

        if manifest_issues:
            print(f"{'[WARN]'.ljust(10)} MODULE MANIFEST ISSUES")
            for module, issues in manifest_issues.items():
                print(f"            Module: {module}")
                for issue in issues:
                    print(f"              - {issue}")
            print()

        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        total_checks = len(self.passed) + len(self.warnings) + len(self.issues)

        if not self.issues:
            print(f"✓ Ready for migration! ({len(self.passed)} checks passed)")
            if self.warnings:
                print(f"  ({len(self.warnings)} warnings - review recommended)")
            return True
        else:
            print(f"✗ Please fix {len(self.issues)} issue(s) before migration")
            return False


def main():
    if len(sys.argv) < 3:
        print("Usage: pre_migration_checklist.py <modules_path> <target_version>")
        print("Example: pre_migration_checklist.py /path/to/modules 17.0")
        sys.exit(1)

    modules_path = sys.argv[1]
    target_version = sys.argv[2]

    checker = PreMigrationChecker(modules_path, target_version)
    success = checker.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
