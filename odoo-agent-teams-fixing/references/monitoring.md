# Monitoring Reference

This file contains progress reporting, time estimation, and state persistence.

## Table of Contents

1. [Time Estimation](#time-estimation)
2. [Progress Reporting](#progress-reporting)
3. [State Persistence](#state-persistence)
4. [Tokens Budget Limit](#tokens-budget-limit)
5. [Safety Limits](#safety-limits)

---

## Time Estimation

Estimate time and cost for workflow based on error count, complexity, and historical data.

```python
class TimeEstimator:
    """Estimate time and cost for workflow"""

    FIX_TIME_ESTIMATES = {
        "CRITICAL": 600,   # 10 minutes
        "HIGH": 300,       # 5 minutes
        "MEDIUM": 180,     # 3 minutes
        "LOW": 60,         # 1 minute
    }

    COMPLEXITY_MULTIPLIERS = {
        "custom_addons": 1.0,
        "odoo_core": 1.5,
        "enterprise": 1.8,
        "third_party": 1.3,
    }

    def __init__(self):
        self.start_time = None
        self.error_history = []
        self.module_complexity = "custom_addons"

    def start(self):
        import time
        self.start_time = time.time()

    def record_iteration(self, iteration, errors_fixed, time_taken):
        """Record iteration data for better estimates"""
        self.error_history.append({
            "iteration": iteration,
            "errors_fixed": errors_fixed,
            "time_taken": time_taken
        })

    def calculate_average_fix_time(self):
        """Calculate average time to fix an error"""
        if not self.error_history:
            return 180  # Default: 3 minutes

        total_time = sum(h["time_taken"] for h in self.error_history)
        total_fixed = sum(h["errors_fixed"] for h in self.error_history)

        if total_fixed > 0:
            return total_time / total_fixed
        return 180

    def get_eta(self, remaining_errors, current_iteration, max_iterations):
        """Get Estimated Time of Arrival"""
        if remaining_errors == 0:
            return "Complete!"

        import time
        base_time = self.calculate_average_fix_time()
        complexity_mult = self.COMPLEXITY_MULTIPLIERS.get(self.module_complexity, 1.0)
        adjusted_time = base_time * complexity_mult

        iterations_left = max_iterations - current_iteration
        if iterations_left <= 0:
            return f"~{adjusted_time * remaining_errors / 60:.0f} min"

        errors_per_iteration = min(3, remaining_errors / iterations_left)
        estimated_time = (remaining_errors / errors_per_iteration) * adjusted_time

        if estimated_time < 60:
            return f"{int(estimated_time)} seconds"
        elif estimated_time < 3600:
            return f"~{int(estimated_time / 60)} minutes"
        else:
            hours = int(estimated_time / 3600)
            minutes = int((estimated_time % 3600) / 60)
            return f"~{hours}h {minutes}m"

    def calculate_progress(self, initial_errors, remaining_errors, current_iteration, max_iterations):
        """Calculate progress percentage"""
        if initial_errors == 0:
            return 100

        errors_fixed = initial_errors - remaining_errors
        progress = (errors_fixed / initial_errors) * 100

        iteration_progress = (current_iteration / max_iterations) * 100

        return min(100, (progress * 0.7 + iteration_progress * 0.3))

    def format_progress_report(self, summary):
        """Format a progress report"""
        progress_bar = self._create_progress_bar(summary["progress_percent"])

        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    WORKFLOW PROGRESS                         ║
╠═══════════════════════════════════════════════════════════════╣
║ {progress_bar}  {summary['progress_percent']:.1f}%                  ║
║                                                               ║
║  Elapsed:    {summary['elapsed_seconds']/60:>6.1f} minutes                           ║
║  ETA:       {summary['eta']:<10}                                  ║
║                                                               ║
║  Errors:     {summary['errors_remaining']:<3} remaining                           ║
║  Iterations: {summary['iterations_used']:<2}/{summary['iterations_used'] + summary['iterations_left']:<2} used                               ║
║                                                               ║
║  Est. Tokens: ~{summary['estimated_tokens_remaining']:,}                             ║
║  Avg Fix:    {summary['average_fix_time']:.0f}s per error                         ║
╚═══════════════════════════════════════════════════════════════╝
"""
        return report

    def _create_progress_bar(self, percent, width=50):
        """Create a text-based progress bar"""
        filled = int(width * percent / 100)
        return f"[{'█' * filled + '░' * (width - filled)}]"
```

---

## Progress Reporting

Enhanced progress reporting with real-time progress bar, phase indicator, and visual timeline.

```python
class ProgressReporter:
    """Enhanced progress reporting"""

    PHASE_SETUP = "SETUP"
    PHASE_TESTING = "TESTING"
    PHASE_FIXING = "FIXING"
    PHASE_VERIFICATION = "VERIFICATION"
    PHASE_DONE = "DONE"

    PHASE_ICONS = {
        PHASE_SETUP: "⚙️",
        PHASE_TESTING: "🧪",
        PHASE_FIXING: "🔧",
        PHASE_VERIFICATION: "✅",
        PHASE_DONE: "🎉"
    }

    def __init__(self):
        self.current_phase = self.PHASE_SETUP
        self.iteration_history = []
        self.start_time = None
        self.phase_start_time = None

    def start(self):
        import time
        self.start_time = time.time()
        self.phase_start_time = time.time()

    def set_phase(self, phase):
        """Set current workflow phase"""
        if phase != self.current_phase:
            self.current_phase = phase
            log(f"PHASE: {self.PHASE_ICONS.get(phase, '•')} {phase}")

    def record_iteration(self, iteration, errors_before, errors_after, errors_fixed):
        """Record iteration results"""
        import time

        self.iteration_history.append({
            "iteration": iteration,
            "errors_before": errors_before,
            "errors_after": errors_after,
            "errors_fixed": errors_fixed,
            "timestamp": time.time()
        })

    def generate_timeline(self):
        """Generate visual timeline of iterations"""
        if not self.iteration_history:
            return "No iterations yet"

        lines = ["", "ITERATION TIMELINE:", "-" * 50]
        for record in self.iteration_history:
            iter_num = record["iteration"]
            fixed = record["errors_fixed"]
            before = record["errors_before"]

            bar_width = 20
            filled = int(bar_width * fixed / max(1, before)) if before > 0 else 0
            bar = "█" * filled + "░" * (bar_width - filled)

            lines.append(f"  Iter {iter_num}: [{bar}] -{fixed}")

        return "\n".join(lines)

    def log_progress(self):
        """Log current progress"""
        report = self.generate_detailed_report()
        log(report)
```

---

## State Persistence

Save and resume workflow state to/from JSON files.

```python
import uuid
import hashlib

class WorkflowStateManager:
    """Enhanced state persistence with checkpoints"""

    def __init__(self, workflow_id=None):
        self.workflow_id = workflow_id or self._generate_workflow_id()
        self.state_dir = f"/tmp/odoo_workflow_{self.workflow_id}"
        self.state_file = f"{self.state_dir}/state.json"
        self.checkpoint_dir = f"{self.state_dir}/checkpoints"

    def _generate_workflow_id(self):
        import time
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def save_state(self, iteration, errors, agents_status, phase="unknown", metadata=None):
        """Save current workflow state"""
        state = {
            "workflow_id": self.workflow_id,
            "iteration": iteration,
            "phase": phase,
            "errors": errors,
            "agents": agents_status,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

        log(f"STATE: Saved iteration {iteration}, phase: {phase}")
        return state

    def save_checkpoint(self, iteration, checkpoint_data):
        """Save named checkpoint"""
        checkpoint_file = f"{self.checkpoint_dir}/iter{iteration}.json"
        checkpoint = {
            "iteration": iteration,
            "data": checkpoint_data,
            "timestamp": datetime.now().isoformat()
        }
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def load_state(self):
        """Load most recent state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return None

    def can_resume(self):
        """Check if there's a state to resume from"""
        return os.path.exists(self.state_file)

    def get_resume_info(self):
        """Get info about resumable state"""
        state = self.load_state()
        if state:
            return {
                "can_resume": True,
                "workflow_id": self.workflow_id,
                "iteration": state.get("iteration", 0),
                "phase": state.get("phase", "unknown"),
                "timestamp": state.get("timestamp")
            }
        return {"can_resume": False}

    def clear_state(self):
        """Clear saved state"""
        import shutil
        if os.path.exists(self.state_dir):
            shutil.rmtree(self.state_dir)
```

---

## Tokens Budget Limit

```python
TOTAL_TOKENS_USED = 0
MAX_TOKENS = 1000000  # 1M tokens

def track_tokens(agent_name, tokens_used):
    """Track token usage"""
    global TOTAL_TOKENS_USED
    TOTAL_TOKENS_USED += tokens_used

    log(f"Token usage: {agent_name} used {tokens_used}, total: {TOTAL_TOKENS_USED}/{MAX_TOKENS}")

    if TOTAL_TOKENS_USED >= MAX_TOKENS:
        log("MAX TOKENS REACHED!")
        return False
    return True

def can_continue_with_budget(estimated_tokens):
    """Check if still has budget"""
    return (TOTAL_TOKENS_USED + estimated_tokens) < MAX_TOKENS
```

---

## Safety Limits

```python
# Max Workflow Iterations
MAX_WORKFLOW_ITERATIONS = 5

def check_iteration_limit(iteration_count):
    if iteration_count >= MAX_WORKFLOW_ITERATIONS:
        log("MAX ITERATIONS REACHED - Stopping workflow")
        return False
    return True

# Max Agent Timeout
MAX_AGENT_TIMEOUT_MS = 300000  # 5 minutes per agent

# Adaptive Timeout
class AdaptiveTimeout:
    BASE_TIMEOUTS = {
        "qa_test": 300000,
        "click_test": 180000,
        "devops": 600000,
        "architect": 120000,
        "developer": 300000,
    }

    def get_timeout(self, task_type):
        return self.BASE_TIMEOUTS.get(task_type, 300000)

# Max Total Duration
MAX_TOTAL_DURATION_MS = 7200000  # 2 hours

WORKFLOW_START_TIME = None

def check_duration_limit():
    global WORKFLOW_START_TIME
    if WORKFLOW_START_TIME is None:
        WORKFLOW_START_TIME = time.time()

    elapsed = (time.time() - WORKFLOW_START_TIME) * 1000
    if elapsed >= MAX_TOTAL_DURATION_MS:
        log(f"MAX DURATION REACHED ({elapsed/60000:.1f} minutes)")
        return False
    return True
```

---

## Usage

```python
# Initialize
time_estimator = TimeEstimator()
progress_reporter = ProgressReporter()
state_manager = WorkflowStateManager()

# Start workflow
time_estimator.start()
progress_reporter.start()
progress_reporter.set_phase(ProgressReporter.PHASE_TESTING)

# During iteration
time_estimator.record_iteration(iteration, errors_fixed, time_taken)
progress_reporter.record_iteration(iteration, before, after, fixed)

# Report progress
summary = time_estimator.get_estimate_summary(initial, remaining, iter_num, max_iter)
report = time_estimator.format_progress_report(summary)
log(report)

# Save state
state_manager.save_state(iteration, errors, agents, phase, metadata)
```

---

## Quick Reference

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| TimeEstimator | ETA calculation | `get_eta()`, `calculate_progress()` |
| ProgressReporter | Phase tracking | `set_phase()`, `record_iteration()` |
| WorkflowStateManager | Resume support | `save_state()`, `load_state()`, `can_resume()` |
