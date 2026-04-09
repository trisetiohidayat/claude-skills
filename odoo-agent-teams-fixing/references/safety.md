# Safety Reference

This file contains safety mechanisms, rollback handling, and cleanup procedures.

## Table of Contents

1. [Rollback Mechanism](#rollback-mechanism)
2. [Partial Failure Handling](#partial-failure-handling)
3. [Disk Space Check](#disk-space-check)
4. [Parallel Operations Error Handling](#parallel-operations-error-handling)
5. [Resource Cleanup on Failure](#resource-cleanup-on-failure)
6. [Odoo Crash Detection](#odoo-crash-detection)
7. [Emergency Stop](#emergency-stop)

---

## Rollback Mechanism

If a fix introduces new errors that are worse, use rollback:

```python
import shutil
import git

class RollbackManager:
    """Manage rollbacks for code changes"""

    def __init__(self, custom_addons_path):
        self.custom_addons_path = custom_addons_path
        self.repo = git.Repo(custom_addons_path)
        self.backup_path = "/tmp/odoo_rollback_backups"

    def create_backup(self, module_name, iteration):
        """Create backup before applying fix"""
        backup_dir = f"{self.backup_path}/{module_name}_iter{iteration}"
        module_path = f"{self.custom_addons_path}/{module_name}"

        if os.path.exists(module_path):
            shutil.copytree(module_path, backup_dir)
            log(f"BACKUP: Created backup at {backup_dir}")
            return backup_dir
        return None

    def rollback(self, module_name, iteration):
        """Rollback to previous backup"""
        backup_dir = f"{self.backup_path}/{module_name}_iter{iteration}"
        module_path = f"{self.custom_addons_path}/{module_name}"

        if os.path.exists(backup_dir):
            if os.path.exists(module_path):
                shutil.rmtree(module_path)
            shutil.copytree(backup_dir, module_path)
            log(f"ROLLBACK: Restored {module_name} to iteration {iteration}")
            return True
        return False

    def should_rollback(self, old_error_count, new_error_count):
        """Determine if rollback is needed"""
        # Rollback if errors increase by > 50%
        if new_error_count > old_error_count * 1.5:
            log(f"ROLLBACK TRIGGERED: Errors increased from {old_error_count} to {new_error_count}")
            return True
        return False
```

### Rollback Triggers

Perform rollback if:
1. **Error count increases by > 50%** after fix
2. **Odoo total crash** after upgrade
3. **Critical data loss** detected
4. **Security vulnerability** introduced by fix

---

## Granular Rollback (Enhanced)

Track changes per-file and allow selective undo:

```python
class GranularRollbackManager:
    """Enhanced rollback manager with per-file tracking"""

    def __init__(self, custom_addons_path):
        self.custom_addons_path = custom_addons_path
        self.backup_path = "/tmp/odoo_granular_backups"
        self.file_changes = {}
        self.iteration_backups = {}

    def create_file_backup(self, module_name, iteration, file_path):
        """Backup individual file before modification"""
        import hashlib

        backup_dir = f"{self.backup_path}/{module_name}_iter{iteration}"
        os.makedirs(backup_dir, exist_ok=True)

        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()[:8]
        filename = os.path.basename(file_path)
        backup_file = f"{backup_dir}/{filename}_{file_hash}"
        shutil.copy2(file_path, backup_file)

        if iteration not in self.file_changes:
            self.file_changes[iteration] = {}
        if module_name not in self.file_changes[iteration]:
            self.file_changes[iteration][module_name] = []
        self.file_changes[iteration][module_name].append(file_path)

        if iteration not in self.iteration_backups:
            self.iteration_backups[iteration] = {}
        self.iteration_backups[iteration][file_path] = backup_file

    def rollback_file(self, file_path, iteration):
        """Rollback only specific file"""
        if iteration in self.iteration_backups:
            if file_path in self.iteration_backups[iteration]:
                backup_file = self.iteration_backups[iteration][file_path]
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, file_path)
                    return True
        return False
```

---

## Partial Failure Handling

If some tests passed and some failed:

```python
def handle_partial_failure(test_results):
    """Handle scenario with mixed test results"""
    passed = [t for t in test_results if t["status"] == "passed"]
    failed = [t for t in test_results if t["status"] == "failed"]

    log(f"PARTIAL RESULTS: {len(passed)} passed, {len(failed)} failed")

    report = {
        "status": "partial_failure",
        "passed": len(passed),
        "failed": len(failed),
        "failed_tests": [t["name"] for t in failed],
        "action": "Continue with failed tests only"
    }

    critical_passed = all(t in passed for t in CRITICAL_TESTS)
    if critical_passed and failed:
        log("Some non-critical tests failed, continuing...")
        return {"continue": True, "focus_on": failed}

    if not critical_passed:
        log("Critical tests failed - stopping")
        return {"continue": False, "reason": "critical_tests_failed"}

    return {"continue": True, "focus_on": failed}
```

---

## Disk Space Check

Check disk space before database duplication:

```python
import shutil

def check_disk_space(required_gb=10):
    """Check if enough disk space is available"""
    total, used, free = shutil.disk_usage("/")

    free_gb = free // (2**30)
    log(f"Disk space: {free_gb}GB free of {total // (2**30)}GB")

    if free_gb < required_gb:
        log(f"ERROR: Only {free_gb}GB available, need {required_gb}GB!")
        return False
    return True
```

---

## Parallel Operations Error Handling

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_parallel_with_error_handling(agents):
    """Run multiple agents with error handling"""
    results = {}
    errors = {}

    with ThreadPoolExecutor(max_workers=len(agents)) as executor:
        futures = {executor.submit(run_agent, agent): agent for agent in agents}

        for future in as_completed(futures, timeout=MAX_AGENT_TIMEOUT_MS/1000):
            agent = futures[future]
            try:
                results[agent["name"]] = future.result()
            except Exception as e:
                errors[agent["name"]] = str(e)
                log(f"Agent {agent['name']} failed: {e}")

    log(f"Parallel execution: {len(results)} success, {len(errors)} errors")
    return {"results": results, "errors": errors, "all_success": len(errors) == 0}
```

---

## Resource Cleanup on Failure

```python
class ResourceCleanup:
    """Cleanup resources when workflow fails"""

    def __init__(self):
        self.odoo_pids = []
        self.temp_files = []
        self.test_db = None

    def register_odoo_pid(self, pid):
        self.odoo_pids.append(pid)

    def register_temp_file(self, path):
        self.temp_files.append(path)

    def register_test_db(self, db_name):
        self.test_db = db_name

    def cleanup_on_failure(self, reason):
        """Clean up all resources"""
        log(f"CLEANUP: Because: {reason}")

        # Stop Odoo processes
        for pid in self.odoo_pids:
            try:
                os.kill(pid, 9)
            except:
                pass

        # Remove temp files
        for f in self.temp_files:
            try:
                os.remove(f)
            except:
                pass

        self.ask_database_deletion()
```

### Enhanced Resource Cleanup

```python
class EnhancedResourceCleanup:
    """Enhanced cleanup with try/finally and graceful degradation"""

    def __init__(self):
        self.odoo_pids = []
        self.temp_files = []
        self.test_db = None
        self.ports = []
        self.backup_dirs = []
        self.custom_resources = {}

    def register_odoo_process(self, pid, port=None):
        self.odoo_pids.append(pid)
        if port:
            self.ports.append(port)

    def cleanup(self, reason="unspecified", ask_db_deletion=True):
        """Complete cleanup of all resources"""
        log(f"CLEANUP STARTED: Reason - {reason}")

        # Cleanup in order
        self.cleanup_odoo_processes()
        self.cleanup_temp_files()
        self.cleanup_ports()

        if ask_db_deletion and self.test_db:
            self.ask_database_deletion()

    def force_cleanup_on_exit(self):
        """Force cleanup that runs even if workflow crashes"""
        try:
            self.cleanup(reason="exit", ask_db_deletion=False)
        except Exception as e:
            log(f"ERROR during force cleanup: {e}")
```

---

## Odoo Crash Detection

```python
import psutil

def check_odoo_health(port):
    """Check if Odoo instance is still healthy"""
    try:
        response = requests.get(f"http://localhost:{port}/web/login", timeout=5)
        if response.status_code == 200:
            return {"healthy": True}
    except requests.exceptions.ConnectionError:
        return {"healthy": False, "reason": "connection_refused"}
    except Exception as e:
        return {"healthy": False, "reason": str(e)}

    return {"healthy": False, "reason": "unknown"}
```

---

## Emergency Stop

```python
EMERGENCY_STOP_FILE = "/tmp/odoo_workflow_stop"

def check_emergency_stop():
    """User can create this file to stop workflow"""
    if os.path.exists(EMERGENCY_STOP_FILE):
        log("EMERGENCY STOP requested!")
        os.remove(EMERGENCY_STOP_FILE)
        return False
    return True

# To stop: touch /tmp/odoo_workflow_stop
```

---

## Usage in Workflow

```python
# Initialize
rollback_mgr = RollbackManager(CUSTOM_ADDONS_PATH)
cleanup = ResourceCleanup()

try:
    # Workflow runs...
    pass
except Exception as e:
    cleanup.cleanup_on_failure(str(e))
    raise
```

---

## Quick Reference

| Feature | Function | When to Use |
|---------|----------|-------------|
| Rollback | `rollback_mgr.rollback()` | Fix made things worse |
| Selective Rollback | `granular_rollback.rollback_file()` | Only one file is bad |
| Cleanup | `cleanup.cleanup_on_failure()` | Workflow failed |
| Emergency Stop | `check_emergency_stop()` | Every iteration |
| Disk Space | `check_disk_space()` | Before duplication |
