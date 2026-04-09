#!/usr/bin/env python3
"""
Run tests for migrated Odoo modules.

Usage:
    # Run all enabled tests
    python3 run_module_tests.py \
        --module module_name \
        --test-type syntax,load,integration \
        --odoo-path /path/to/odoo-17.0 \
        --module-path /path/to/custom_modules \
        --output ./module_migration/module_name/test_results.md

    # Run specific test only
    python3 run_module_tests.py \
        --module module_name \
        --test-type syntax
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class TestRunner:
    def __init__(self, module_name, module_path, odoo_path, test_types, output_path):
        self.module_name = module_name
        self.module_path = Path(module_path) / module_name if module_path else None
        self.odoo_path = Path(odoo_path) if odoo_path else None
        self.test_types = [t.strip() for t in test_types.split(',')] if isinstance(test_types, str) else test_types
        self.output_path = output_path
        self.results = {
            'module': module_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

    def run_syntax_test(self):
        """Run Python syntax validation using py_compile."""
        print("\n" + "="*60)
        print("📋 SYNTAX VALIDATION TEST")
        print("="*60)

        results = []
        passed = 0
        failed = 0

        if not self.module_path or not self.module_path.exists():
            print(f"⚠️  Module path not found: {self.module_path}")
            return {'status': 'SKIP', 'details': 'Module path not found'}

        # Find all Python files
        py_files = list(self.module_path.rglob('*.py'))
        print(f"Found {len(py_files)} Python files")

        for py_file in py_files:
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"  ✅ {py_file.relative_to(self.module_path)}")
                    passed += 1
                    results.append({
                        'file': str(py_file.relative_to(self.module_path)),
                        'status': 'PASS'
                    })
                else:
                    print(f"  ❌ {py_file.relative_to(self.module_path)}: {result.stderr}")
                    failed += 1
                    results.append({
                        'file': str(py_file.relative_to(self.module_path)),
                        'status': 'FAIL',
                        'error': result.stderr
                    })
            except subprocess.TimeoutExpired:
                print(f"  ⏱️  {py_file.relative_to(self.module_path)}: TIMEOUT")
                failed += 1
                results.append({
                    'file': str(py_file.relative_to(self.module_path)),
                    'status': 'TIMEOUT'
                })
            except Exception as e:
                print(f"  ❌ {py_file.relative_to(self.module_path)}: {str(e)}")
                failed += 1
                results.append({
                    'file': str(py_file.relative_to(self.module_path)),
                    'status': 'ERROR',
                    'error': str(e)
                })

        status = 'PASS' if failed == 0 else 'FAIL'
        print(f"\n📊 Syntax Test Result: {passed} passed, {failed} failed")

        return {
            'status': status,
            'passed': passed,
            'failed': failed,
            'files': results
        }

    def run_load_test(self):
        """Run module load test - try importing the module in Odoo environment."""
        print("\n" + "="*60)
        print("📋 MODULE LOAD TEST")
        print("="*60)

        if not self.odoo_path or not self.odoo_path.exists():
            print(f"⚠️  Odoo path not found: {self.odoo_path}")
            print("   Skipping load test - requires --odoo-path")
            return {'status': 'SKIP', 'details': 'Odoo path not provided or not found'}

        # Check if Odoo can be imported
        test_code = f"""
import sys
sys.path.insert(0, '{self.odoo_path}')
try:
    import odoo
    print('ODOO_VERSION:', getattr(odoo, 'release', 'unknown'))
    # Try importing the module
    import {self.module_name}
    print('MODULE_IMPORT: SUCCESS')
except ImportError as e:
    print('MODULE_IMPORT: FAILED')
    print('ERROR:', str(e))
    sys.exit(1)
except Exception as e:
    print('MODULE_IMPORT: ERROR')
    print('ERROR:', str(e))
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                ['python3', '-c', test_code],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.odoo_path.parent)
            )

            output = result.stdout + result.stderr
            print(f"Output: {output}")

            if 'MODULE_IMPORT: SUCCESS' in output:
                print("✅ Module can be imported in Odoo environment")
                return {'status': 'PASS', 'details': output}
            else:
                print("❌ Module import failed")
                return {'status': 'FAIL', 'details': output}

        except subprocess.TimeoutExpired:
            print("⏱️  Load test timeout")
            return {'status': 'TIMEOUT', 'details': 'Test timed out after 60 seconds'}
        except Exception as e:
            print(f"❌ Load test error: {str(e)}")
            return {'status': 'ERROR', 'details': str(e)}

    def run_integration_test(self):
        """Run full integration test - install/update module in test database."""
        print("\n" + "="*60)
        print("📋 INTEGRATION TEST")
        print("="*60)

        if not self.odoo_path or not self.odoo_path.exists():
            print(f"⚠️  Odoo path not found: {self.odoo_path}")
            print("   Skipping integration test - requires --odoo-path")
            return {'status': 'SKIP', 'details': 'Odoo path not provided or not found'}

        print("""
⚠️  INTEGRATION TEST REQUIREMENTS:
    1. Running Odoo server
    2. Test database created
    3. Module path added to addons

To run manually:
    odoo-bin -d test_db -u {module} --test-enable

Or use this command:
    python3 {odoo_path}/odoo-bin -d <test_db> -u {module} --test-enable
""".format(module=self.module_name, odoo_path=self.odoo_path))

        return {
            'status': 'MANUAL',
            'details': 'Integration test requires manual execution with running Odoo server'
        }

    def run_all_tests(self):
        """Run all enabled tests."""
        print(f"\n🔬 Running tests for module: {self.module_name}")
        print(f"   Test types: {', '.join(self.test_types)}")
        print(f"   Module path: {self.module_path}")
        print(f"   Odoo path: {self.odoo_path}")

        # Run tests based on type
        if 'syntax' in self.test_types:
            self.results['tests']['syntax'] = self.run_syntax_test()

        if 'load' in self.test_types:
            self.results['tests']['load'] = self.run_load_test()

        if 'integration' in self.test_types:
            self.results['tests']['integration'] = self.run_integration_test()

        return self.results

    def generate_report(self):
        """Generate test results markdown report."""
        md = f"""# Test Results: {self.module_name}

## Summary

| Test Type | Status | Details |
|-----------|--------|---------|
"""

        overall_status = 'PASS'
        for test_type, result in self.results['tests'].items():
            status = result.get('status', 'UNKNOWN')
            if status in ['FAIL', 'ERROR']:
                overall_status = 'FAIL'
            elif status == 'MANUAL':
                overall_status = 'MANUAL'

            details = result.get('details', '')
            if len(details) > 50:
                details = details[:50] + '...'

            md += f"| {test_type.capitalize()} | {status} | {details} |\n"

        md += f"""
**Overall Status:** {overall_status}
**Timestamp:** {self.results['timestamp']}

---

## Detailed Results

"""

        # Syntax details
        if 'syntax' in self.results['tests']:
            result = self.results['tests']['syntax']
            md += f"### Syntax Validation\n"
            md += f"- Status: **{result.get('status', 'N/A')}**\n"
            md += f"- Passed: {result.get('passed', 0)}\n"
            md += f"- Failed: {result.get('failed', 0)}\n\n"

            if result.get('files'):
                md += "**Files:**\n"
                for f in result['files']:
                    icon = '✅' if f['status'] == 'PASS' else '❌'
                    md += f"- {icon} {f['file']}\n"
                md += "\n"

        # Load details
        if 'load' in self.results['tests']:
            result = self.results['tests']['load']
            md += f"### Module Load Test\n"
            md += f"- Status: **{result.get('status', 'N/A')}**\n"
            md += f"- Details: {result.get('details', 'N/A')}\n\n"

        # Integration details
        if 'integration' in self.results['tests']:
            result = self.results['tests']['integration']
            md += f"### Integration Test\n"
            md += f"- Status: **{result.get('status', 'N/A')}**\n"
            md += f"- Details: {result.get('details', 'N/A')}\n\n"

        # Next steps
        md += """## Next Steps

"""
        if overall_status == 'PASS':
            md += """✅ **All tests passed!**
- Module is ready for deployment
- Continue with next module migration (if any)
- Update MIGRATION_STATUS.md with test results
"""
        elif overall_status == 'MANUAL':
            md += """⚠️ **Manual testing required**
- Run integration test manually
- Verify module works in test environment
- Update MIGRATION_STATUS.md after testing
"""
        else:
            md += """❌ **Tests failed!**
- Fix the issues before proceeding
- Re-run tests after fixes
- Do NOT proceed to next module until tests pass
"""

        # Ensure output directory exists
        if self.output_path:
            Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, 'w') as f:
                f.write(md)
            print(f"\n📄 Test report saved to: {self.output_path}")

        return overall_status


def main():
    parser = argparse.ArgumentParser(
        description='Run tests for migrated Odoo modules'
    )

    parser.add_argument('--module', type=str, required=True,
                        help='Module name to test')
    parser.add_argument('--module-path', type=str,
                        help='Path to custom modules directory')
    parser.add_argument('--odoo-path', type=str,
                        help='Path to Odoo installation')
    parser.add_argument('--test-type', type=str, default='syntax',
                        help='Comma-separated test types (syntax,load,integration)')
    parser.add_argument('--output', type=str,
                        help='Output path for test results markdown')

    args = parser.parse_args()

    # Run tests
    runner = TestRunner(
        module_name=args.module,
        module_path=args.module_path,
        odoo_path=args.odoo_path,
        test_types=args.test_type,
        output_path=args.output
    )

    results = runner.run_all_tests()
    overall_status = runner.generate_report()

    # Exit with appropriate code
    if overall_status == 'PASS':
        print(f"\n✅ ALL TESTS PASSED")
        sys.exit(0)
    elif overall_status == 'MANUAL':
        print(f"\n⚠️  MANUAL TESTING REQUIRED")
        sys.exit(0)
    else:
        print(f"\n❌ TESTS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
