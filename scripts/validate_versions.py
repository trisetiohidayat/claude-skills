#!/usr/bin/env python3
"""Validate Odoo version migration path."""

# Minimum and maximum versions supported by odoo-module-migrator
MIN_VERSION = "8.0"
MAX_VERSION = "19.0"

def validate_version(source: str, target: str) -> tuple[bool, str]:
    """Validate if migration path is supported.

    odoo-module-migrator supports direct non-consecutive migrations.
    It runs all intermediate migration steps internally.
    """
    # Parse versions (e.g., "15.0" -> 15, "8.0" -> 8)
    source_clean = int(source.replace(".0", "").replace(".", ""))
    target_clean = int(target.replace(".0", "").replace(".", ""))

    # Check if going backwards
    if target_clean < source_clean:
        return False, f"Cannot migrate backwards from {source} to {target}"

    # Check if within supported range
    min_ver = int(MIN_VERSION.replace(".0", ""))
    max_ver = int(MAX_VERSION.replace(".0", ""))

    if source_clean < min_ver or source_clean > max_ver:
        return False, f"Source version {source} is outside supported range ({MIN_VERSION}-{MAX_VERSION})"

    if target_clean < min_ver or target_clean > max_ver:
        return False, f"Target version {target} is outside supported range ({MIN_VERSION}-{MAX_VERSION})"

    # Non-consecutive migrations ARE supported - tool runs intermediate steps internally
    if target_clean - source_clean > 1:
        return True, f"Migration {source} -> {target} is supported (will run intermediate steps internally)"

    return True, f"Migration {source} -> {target} is supported"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: validate_versions.py <source> <target>")
        print("Example: validate_versions.py 15.0 19.0")
        sys.exit(1)

    source, target = sys.argv[1], sys.argv[2]
    valid, message = validate_version(source, target)
    print(message)
    sys.exit(0 if valid else 1)
