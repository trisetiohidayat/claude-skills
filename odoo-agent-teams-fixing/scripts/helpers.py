#!/usr/bin/env python3
"""
Shared utilities for odoo-agent-teams-fixing skill.

This module contains common helper functions used across the skill.
"""

import os
import json
import logging
from datetime import datetime

# Configure logging
def setup_logging(log_file=None):
    """Setup logging configuration"""
    if log_file:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    return logging.getLogger(__name__)

def log(message, level="INFO"):
    """Simple logging helper"""
    logger = logging.getLogger(__name__)
    getattr(logger, level.lower())(message)

# Database helpers
def validate_database_name(db_name):
    """Validate database name follows safety rules"""
    valid_patterns = ['test_', '_test', 'backup_', '_backup', '_dev', '_staging']

    for pattern in valid_patterns:
        if pattern in db_name.lower():
            return True, "Valid test database name"

    return False, f"Invalid: must contain one of {valid_patterns}"

# File helpers
def ensure_directory(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
    return path

# JSON helpers
def save_json(data, file_path):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(file_path):
    """Load data from JSON file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

# Time helpers
def format_duration(seconds):
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m"
    else:
        hours = int(seconds/3600)
        minutes = int((seconds%3600)/60)
        return f"{hours}h {minutes}m"

def get_timestamp():
    """Get current timestamp"""
    return datetime.now().isoformat()

# Error helpers
def classify_error(error):
    """Classify error type"""
    error_str = str(error).lower()

    if any(k in error_str for k in ['crash', 'fatal', 'assertionerror']):
        return "CRITICAL"
    elif any(k in error_str for k in ['attributeerror', 'importerror', 'keyerror']):
        return "HIGH"
    elif any(k in error_str for k in ['warning', 'deprecation']):
        return "MEDIUM"
    else:
        return "LOW"

# Progress helpers
def create_progress_bar(percent, width=50):
    """Create text-based progress bar"""
    filled = int(width * percent / 100)
    return f"[{'█' * filled + '░' * (width - filled)}]"

# Cleanup helpers
def safe_kill_process(pid):
    """Safely kill a process"""
    import signal
    try:
        os.kill(pid, signal.SIGTERM)
        return True, "Process terminated"
    except ProcessLookupError:
        return True, "Process already dead"
    except Exception as e:
        return False, str(e)

def cleanup_temp_files(paths):
    """Clean up temporary files"""
    import shutil
    cleaned = []
    for path in paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            cleaned.append(path)
        except Exception:
            pass
    return cleaned
