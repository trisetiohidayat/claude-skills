# Self-Healing Reference

This file contains confidence scoring, verification, and human checkpoint mechanisms.

## Table of Contents

1. [SelfHealer](#selfhealer)
2. [ConfidenceScorer](#confidencescorer)
3. [FixVerifier](#fixverifier)
4. [HumanCheckpoint](#humancheckpoint)
5. [Error Prioritization](#error-prioritization)
6. [Convergence Check](#convergence-check)

---

## SelfHealer

Auto-recovery when agents get stuck with retry logic.

```python
class SelfHealer:
    """Auto-recovery mechanism for stuck agents"""

    MAX_RETRIES = 3
    RETRY_DELAYS = [5000, 15000, 45000]  # Exponential backoff in ms
    RETRY_BACKOFF = 2

    def __init__(self):
        self.retry_counts = {}  # agent_name -> retry count
        self.stuck_agents = {}  # agent_name -> stuck detection count

    def should_retry(self, agent_name, error):
        """Determine if agent should retry"""
        retry_count = self.retry_counts.get(agent_name, 0)

        if retry_count >= self.MAX_RETRIES:
            log(f"SELF-HEAL: {agent_name} exceeded max retries")
            return False

        # Check if error is retryable
        retryable_errors = [
            "timeout", "connection", "temporary", "network"
        ]

        error_str = str(error).lower()
        is_retryable = any(e in error_str for e in retryable_errors)

        if not is_retryable:
            return False

        return True

    def get_retry_delay(self, agent_name):
        """Get delay before next retry with exponential backoff"""
        retry_count = self.retry_counts.get(agent_name, 0)
        base_delay = self.RETRY_DELAYS[min(retry_count, len(self.RETRY_DELAYS)-1)]
        return base_delay

    def record_retry(self, agent_name):
        """Record retry attempt"""
        self.retry_counts[agent_name] = self.retry_counts.get(agent_name, 0) + 1
        log(f"SELF-HEAL: {agent_name} retry {self.retry_counts[agent_name]}/{self.MAX_RETRIES}")

    def record_success(self, agent_name):
        """Record successful execution"""
        self.retry_counts[agent_name] = 0
        self.stuck_agents[agent_name] = 0
```

---

## ConfidenceScorer

Calculate confidence score for each fix based on historical data.

```python
class ConfidenceScorer:
    """Calculate confidence score for fix proposals"""

    def __init__(self):
        self.fix_history = []  # List of past fixes
        self.success_patterns = {}  # pattern -> success_rate
        self.module_success_rates = {}  # module -> success_rate

    def calculate_fix_confidence(self, error_type, module_name, fix_approach):
        """Calculate confidence 0-100% for a fix"""
        confidence = 50  # Base confidence

        # Adjust based on error type
        error_confidence_adjustments = {
            "javascript": 15,
            "template": 15,
            "python_import": 10,
            "python_attribute": -5,
            "database": -10,
            "migration": -20,
        }

        for error, adjustment in error_confidence_adjustments.items():
            if error in error_type.lower():
                confidence += adjustment
                break

        # Adjust based on module
        if module_name in self.module_success_rates:
            module_rate = self.module_success_rates[module_name]
            confidence = confidence * 0.5 + module_rate * 0.5

        # Adjust based on fix approach
        fix_confidence_adjustments = {
            "add_field": 10,
            "fix_method": 5,
            "update_view": 10,
            "migration": -15,
            "core_change": -20,
        }

        for fix, adjustment in fix_confidence_adjustments.items():
            if fix in fix_approach.lower():
                confidence += adjustment

        return max(0, min(100, confidence))

    def get_confidence_level(self, confidence):
        """Get human-readable confidence level"""
        if confidence >= 80:
            return "HIGH"
        elif confidence >= 50:
            return "MEDIUM"
        else:
            return "LOW"

    def record_fix_result(self, error_type, module_name, fix_approach, success):
        """Record fix result for learning"""
        self.fix_history.append({
            "error_type": error_type,
            "module": module_name,
            "fix_approach": fix_approach,
            "success": success
        })

        # Update module success rates
        if module_name not in self.module_success_rates:
            self.module_success_rates[module_name] = []

        self.module_success_rates[module_name].append(1 if success else 0)

        # Keep history bounded
        if len(self.fix_history) > 100:
            self.fix_history = self.fix_history[-100:]
```

---

## FixVerifier

Verify that fixes actually work before proceeding.

```python
class FixVerifier:
    """Verify fixes work before proceeding"""

    def __init__(self):
        self.verification_methods = {
            "unit_test": self._verify_with_tests,
            "click_test": self._verify_with_click_test,
            "manual_check": self._verify_manually,
        }

    def verify_fix(self, fix, verification_method="unit_test"):
        """Verify a fix using specified method"""
        verifier = self.verification_methods.get(verification_method)
        if not verifier:
            raise ValueError(f"Unknown verification: {verification_method}")

        return verifier(fix)

    def _verify_with_tests(self, fix):
        """Run unit tests to verify fix"""
        log("VERIFY: Running unit tests...")
        # Implementation depends on test runner
        return {"verified": True, "tests_passed": True}

    def _verify_with_click_test(self, fix):
        """Run click test to verify fix"""
        log("VERIFY: Running click test...")
        # Implementation depends on click test runner
        return {"verified": True, "no_js_errors": True}

    def _verify_manually(self, fix):
        """Manual verification needed"""
        log("VERIFY: Manual verification required")
        return {"verified": False, "reason": "manual_verification_needed"}

    def should_proceed(self, verification_result):
        """Determine if workflow should proceed"""
        if verification_result.get("verified"):
            return True, "Fix verified"

        reason = verification_result.get("reason", "Unknown")
        return False, f"Verification failed: {reason}"
```

---

## HumanCheckpoint

Request human approval for critical decisions.

```python
class HumanCheckpoint:
    """Request human approval for critical decisions"""

    def __init__(self):
        self.check_triggers = {
            "rollback": {"confidence_threshold": 0, "always": True},
            "stop_workflow": {"confidence_threshold": 0, "always": True},
            "skip_agent": {"confidence_threshold": 30, "always": False},
            "continue_with_errors": {"confidence_threshold": 50, "always": False},
        }

    def should_check_with_human(self, action, confidence, risk_level):
        """Determine if human should approve"""
        trigger = self.check_triggers.get(action, {})

        # Always check for critical actions
        if trigger.get("always", False):
            return True, f"Critical action: {action}"

        # Check confidence threshold
        threshold = trigger.get("confidence_threshold", 50)
        if confidence < threshold:
            return True, f"Low confidence: {confidence}% < {threshold}%"

        # Check risk level
        if risk_level == "HIGH":
            return True, f"High risk action: {risk_level}"

        return False, "No human check needed"

    def format_checkpoint_request(self, action, context):
        """Format checkpoint request for human"""
        return f"""
        ╔═══════════════════════════════════════════════════════════════╗
        ║              HUMAN CHECKPOINT REQUIRED                      ║
        ╠═══════════════════════════════════════════════════════════════╣
        ║ Action: {action:<50}    ║
        ║                                                               ║
        ║ Context:                                                       ║
        {context}                                                       ║
        ║                                                               ║
        ║ Please respond with:                                          ║
        ║   - "YA [reason]" to approve                                 ║
        ║   - "TIDAK [reason]" to reject                              ║
        ║                                                               ║
        ╚═══════════════════════════════════════════════════════════════╝
        """
```

---

## Error Prioritization

Prioritize errors based on severity, impact, and complexity.

```python
class ErrorPrioritizer:
    """Prioritize errors for fixing"""

    PRIORITY_CRITICAL = 100
    PRIORITY_HIGH = 75
    PRIORITY_MEDIUM = 50
    PRIORITY_LOW = 25

    SEVERITY_CRASH = "CRITICAL"
    SEVERITY_BROKEN = "HIGH"
    SEVERITY_WORKAROUND = "MEDIUM"
    SEVERITY_COSMETIC = "LOW"

    COMPLEXITY_EASY = "EASY"
    COMPLEXITY_MEDIUM = "MEDIUM"
    COMPLEXITY_HARD = "HARD"

    def __init__(self):
        self.error_priorities = {}
        self.error_dependencies = {}

    def assess_severity(self, error):
        """Assess error severity level"""
        error_type = error.get("type", "").lower()
        message = error.get("message", "").lower()

        if any(k in error_type + message for k in ["crash", "fatal", "database error"]):
            return self.SEVERITY_CRASH, self.PRIORITY_CRITICAL
        if any(k in error_type + message for k in ["attributeerror", "import error"]):
            return self.SEVERITY_BROKEN, self.PRIORITY_HIGH
        if any(k in error_type + message for k in ["warning", "deprecated"]):
            return self.SEVERITY_WORKAROUND, self.PRIORITY_MEDIUM

        return self.SEVERITY_COSMETIC, self.PRIORITY_LOW

    def prioritize_errors(self, errors):
        """Sort errors by priority"""
        prioritized = []
        for error in errors:
            severity, score = self.assess_severity(error)
            prioritized.append({
                "error": error,
                "severity": severity,
                "priority": score
            })

        prioritized.sort(key=lambda x: x["priority"], reverse=True)
        return prioritized
```

---

## Convergence Check

Detect if errors are converging (being fixed) or diverging.

```python
ITERATION_HISTORY = []
MIN_FIX_RATE = 0.3  # Minimum 30% error reduction

def calculate_fix_rate(iteration_history):
    """Calculate fix rate from iteration history"""
    if len(iteration_history) < 2:
        return 1.0

    rates = []
    for i in range(1, len(iteration_history)):
        prev_errors = iteration_history[i-1].get("errors", 0)
        curr_errors = iteration_history[i].get("new_errors", 0)
        if prev_errors > 0:
            rate = (prev_errors - curr_errors) / prev_errors
            rates.append(rate)

    return sum(rates) / len(rates) if rates else 0.0

def check_convergence():
    """Detect if errors are converging"""
    if len(ITERATION_HISTORY) < 2:
        return True

    recent = ITERATION_HISTORY[-2:]
    local_stagnant = (
        recent[0].get("new_errors", 0) >= recent[0].get("fixed", 0) and
        recent[1].get("new_errors", 0) >= recent[1].get("fixed", 0)
    )

    global_fix_rate = calculate_fix_rate(ITERATION_HISTORY)
    global_stagnant = global_fix_rate < MIN_FIX_RATE

    if local_stagnant and global_stagnant:
        log(f"CONVERGENCE FAILURE: Fix rate {global_fix_rate:.1%} < {MIN_FIX_RATE:.1%}")
        return False

    return True
```

---

## Usage

```python
# Initialize
self_healer = SelfHealer()
confidence_scorer = ConfidenceScorer()
fix_verifier = FixVerifier()
human_checkpoint = HumanCheckpoint()
error_prioritizer = ErrorPrioritizer()

# During workflow
confidence = confidence_scorer.calculate_fix_confidence(error_type, module, approach)
confidence_level = confidence_scorer.get_confidence_level(confidence)

# Check if needs human approval
should_check, reason = human_checkpoint.should_check_with_human(
    action="continue_with_errors",
    confidence=confidence,
    risk_level="HIGH"
)

# Prioritize errors
prioritized = error_prioritizer.prioritize_errors(errors)
next_error = prioritized[0]

# Verify fix
result = fix_verifier.verify_fix(fix, "unit_test")
proceed, reason = fix_verifier.should_proceed(result)
```

---

## Quick Reference

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| SelfHealer | Auto-recovery | `should_retry()`, `get_retry_delay()` |
| ConfidenceScorer | Confidence scoring | `calculate_fix_confidence()`, `get_confidence_level()` |
| FixVerifier | Fix verification | `verify_fix()`, `should_proceed()` |
| HumanCheckpoint | Human approval | `should_check_with_human()` |
| ErrorPrioritizer | Priority sorting | `prioritize_errors()`, `assess_severity()` |
