#!/bin/bash
# Odoo Reusable Database Upgrade Script
# Usage: ./odoo_reusable_upgrade.sh <database_dump> <target_version> [options]
#
# This script:
# 1. Takes any database dump (.sql, .zip, .dump)
# 2. Applies proven fixes from a fix pattern file
# 3. Runs upgrade.odoo.com
# 4. Outputs upgraded database
#
# Examples:
#   ./odoo_reusable_upgrade.sh newdb.sql 19.0
#   ./odoo_reusable_upgrade.sh olddb.zip 19.0 --fix-pattern ./fix_pattern.sql
#   ./odoo_reusable_upgrade.sh backup.dump 19.0 --contract .odoo_contract

set -e

# ===========================================
# CONFIGURATION
# ===========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
DUMP_FILE=""
TARGET_VERSION="19.0"
CONTRACT_FILE=".odoo_contract"
FIX_PATTERN=""
BACKUP_DIR="./backup"
DRY_RUN=false
SKIP_FIX=false
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"
DB_PREFIX=""
WORK_DIR="./upgrade_$(date +%Y%m%d_%H%M%S)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ===========================================
# USAGE
# ===========================================

usage() {
    cat << EOF
Odoo Reusable Database Upgrade Script

USAGE:
    $0 <database_dump> <target_version> [OPTIONS]

ARGUMENTS:
    database_dump      Path to database dump (.sql, .zip, .dump, .dump.gz)
    target_version    Target Odoo version (e.g., 17.0, 18.0, 19.0)

OPTIONS:
    -c, --contract FILE      Contract file for upgrade.odoo.com (default: .odoo_contract)
    -f, --fix-pattern FILE   SQL file with fixes to apply BEFORE upgrade
    -b, --backup-dir DIR      Backup directory (default: ./backup)
    -h, --db-host HOST        PostgreSQL host (default: localhost)
    -p, --db-port PORT        PostgreSQL port (default: 5432)
    -u, --db-user USER        PostgreSQL user (default: odoo)
    -w, --db-password PASS    PostgreSQL password (default: odoo)
    --db-prefix PREFIX        Database name prefix
    -n, --dry-run             Show what would be done without executing
    -s, --skip-fix            Skip applying fixes
    --work-dir DIR            Working directory (default: ./upgrade_YYYYMMDD_HHMMSS)
    --help                    Show this help

EXAMPLES:
    # Basic usage
    $0 mydatabase.sql 19.0

    # With contract file
    $0 mydatabase.zip 19.0 --contract my_contract.txt

    # With proven fix pattern
    $0 newdb.sql 19.0 --fix-pattern ./proven_fixes.sql

    # Dry run
    $0 mydatabase.zip 19.0 --dry-run --fix-pattern ./fixes.sql

EOF
    exit 0
}

# ===========================================
# PARSE ARGUMENTS
# ===========================================

parse_args() {
    if [[ $# -lt 2 ]]; then
        usage
    fi

    DUMP_FILE="$1"
    TARGET_VERSION="$2"
    shift 2

    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--contract) CONTRACT_FILE="$2"; shift 2 ;;
            -f|--fix-pattern) FIX_PATTERN="$2"; shift 2 ;;
            -b|--backup-dir) BACKUP_DIR="$2"; shift 2 ;;
            -h|--db-host) DB_HOST="$2"; shift 2 ;;
            -p|--db-port) DB_PORT="$2"; shift 2 ;;
            -u|--db-user) DB_USER="$2"; shift 2 ;;
            -w|--db-password) DB_PASSWORD="$2"; shift 2 ;;
            --db-prefix) DB_PREFIX="$2"; shift 2 ;;
            -n|--dry-run) DRY_RUN=true; shift ;;
            -s|--skip-fix) SKIP_FIX=true; shift ;;
            --work-dir) WORK_DIR="$2"; shift 2 ;;
            --help) usage ;;
            *) echo "Unknown option: $1"; usage ;;
        esac
    done
}

# ===========================================
# PRINT FUNCTIONS
# ===========================================

print_header() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  ODOO REUSABLE DATABASE UPGRADE${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# ===========================================
# PREFLIGHT CHECKS
# ===========================================

preflight_checks() {
    print_step "Running preflight checks..."

    # Check dump file
    if [[ ! -f "$DUMP_FILE" ]]; then
        print_error "Dump file not found: $DUMP_FILE"
        exit 1
    fi

    # Check contract file
    if [[ ! -f "$CONTRACT_FILE" ]]; then
        print_error "Contract file not found: $CONTRACT_FILE"
        echo "Please create contract file with your upgrade.odoo.com contract number:"
        echo "  echo 'YOUR_CONTRACT_NUMBER' > $CONTRACT_FILE"
        exit 1
    fi

    # Check fix pattern if specified
    if [[ -n "$FIX_PATTERN" && ! -f "$FIX_PATTERN" ]]; then
        print_error "Fix pattern file not found: $FIX_PATTERN"
        exit 1
    fi

    # Check PostgreSQL connection
    if ! command -v psql &> /dev/null; then
        print_warning "psql not found - cannot verify database connection"
    fi

    print_success "Preflight checks passed"
}

# ===========================================
# EXTRACT DUMP
# ===========================================

extract_dump() {
    print_step "Extracting dump file..."

    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"

    local dump_ext="${DUMP_FILE##*.}"
    local dump_name=$(basename "$DUMP_FILE" .$dump_ext)

    case "$dump_ext" in
        sql)
            print_info "SQL dump detected - using directly"
            ln -sf "$(realpath "$DUMP_FILE")" "./dump.sql"
            ;;
        zip)
            print_info "ZIP dump detected - extracting..."
            unzip -o "$DUMP_FILE" -d ./extracted/ > /dev/null 2>&1
            if [[ -f "./extracted/dump.sql" ]]; then
                ln -sf "$(realpath ./extracted/dump.sql)" "./dump.sql"
                print_success "Extracted dump.sql from zip"
            else
                # Find any .sql file
                local sql_file=$(find ./extracted -name "*.sql" | head -1)
                if [[ -n "$sql_file" ]]; then
                    ln -sf "$(realpath "$sql_file")" "./dump.sql"
                    print_success "Found: $sql_file"
                else
                    print_error "No .sql file found in zip"
                    exit 1
                fi
            fi
            ;;
        dump|gz)
            print_info "PostgreSQL dump detected - will use pg_restore approach"
            # For .dump files, we need to work differently
            if [[ "$dump_ext" == "gz" ]]; then
                gunzip -k "$DUMP_FILE" 2>/dev/null || cp "$DUMP_FILE" "./dump_original.dump"
            else
                cp "$DUMP_FILE" "./dump_original.dump"
            fi
            ;;
        *)
            print_error "Unsupported dump format: $dump_ext"
            exit 1
            ;;
    esac

    if [[ -f "./dump.sql" ]]; then
        print_success "Dump ready: $(realpath ./dump.sql)"
    fi
}

# ===========================================
# PREPARE DATABASE
# ===========================================

prepare_database() {
    print_step "Preparing database for upgrade..."

    # Extract database name from dump
    local db_name=$(grep -oP "(?<=CREATE DATABASE )[a-zA-Z0-9_]+" ./dump.sql 2>/dev/null | head -1 || echo "database")

    # Sanitize for Odoo upgrade
    db_name="${db_name//-/_}"

    # Create temporary database for upgrade
    if command -v psql &> /dev/null; then
        print_info "Checking PostgreSQL connection..."
        export PGPASSWORD="$DB_PASSWORD"

        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
            print_warning "Database $db_name already exists - will drop and recreate"
            if [[ "$DRY_RUN" == false ]]; then
                psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS ${DB_PREFIX}${db_name}_upgrade" 2>/dev/null || true
                psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE ${DB_PREFIX}${db_name}_upgrade" 2>/dev/null || true
            fi
        fi
    fi

    print_success "Database preparation complete"
}

# ===========================================
# APPLY FIXES
# ===========================================

apply_fixes() {
    if [[ "$SKIP_FIX" == true ]]; then
        print_warning "Skipping fix application (--skip-fix specified)"
        return
    fi

    if [[ -z "$FIX_PATTERN" ]]; then
        print_warning "No fix pattern specified - skipping fixes"
        print_info "Use --fix-pattern to apply fixes before upgrade"
        return
    fi

    print_step "Applying fixes from: $FIX_PATTERN"

    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would apply fixes from $FIX_PATTERN"
        print_info "Fixes that would be applied:"
        grep -E "^(UPDATE|CREATE|INSERT|DELETE|ALTER)" "$FIX_PATTERN" | head -20
        return
    fi

    # Apply fixes using psql
    if command -v psql &> /dev/null; then
        export PGPASSWORD="$DB_PASSWORD"

        # Get database name
        local db_name=$(grep -oP "(?<=CREATE DATABASE )[a-zA-Z0-9_]+" ./dump.sql 2>/dev/null | head -1 || echo "database")
        db_name="${db_name//-/_}"

        print_info "Applying fixes to ${DB_PREFIX}${db_name}..."

        # Count fixes
        local fix_count=$(grep -cE "^(UPDATE|CREATE|INSERT|DELETE|ALTER)" "$FIX_PATTERN" || echo "0")
        print_info "Found $fix_count SQL statements to apply"

        # Apply fixes
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "${DB_PREFIX}${db_name}" -f "$FIX_PATTERN" 2>/dev/null && \
            print_success "Fixes applied successfully" || \
            print_warning "Some fixes may have failed - check output above"
    else
        print_warning "psql not available - cannot apply fixes"
        print_info "Fixes were NOT applied"
    fi
}

# ===========================================
# RUN UPGRADE
# ===========================================

run_upgrade() {
    print_step "Running upgrade to Odoo $TARGET_VERSION..."

    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would run upgrade.odoo.com"
        print_info "Command would be:"
        echo "  python <(curl -s https://upgrade.odoo.com/upgrade) test \\"
        echo "    -i $WORK_DIR/dump.sql \\"
        echo "    -t $TARGET_VERSION \\"
        echo "    -c $(cat $CONTRACT_FILE)"
        return
    fi

    # Check if dump exists
    if [[ ! -f "./dump.sql" ]]; then
        print_error "dump.sql not found - cannot run upgrade"
        exit 1
    fi

    # Read contract
    local contract=$(cat "$CONTRACT_FILE" | tr -d ' \n\r')

    # Create upgrade log directory
    mkdir -p "$WORK_DIR/upgrade_logs/run_001"

    print_info "Starting upgrade... (this may take a while)"
    print_info "Check upgrade.odoo.com for status"

    # Run upgrade
    python <(curl -s https://upgrade.odoo.com/upgrade) test \
        -i "$(realpath ./dump.sql)" \
        -t "$TARGET_VERSION" \
        -c "$contract" \
        2>&1 | tee "$WORK_DIR/upgrade_logs/run_001/upgrade.log"

    local upgrade_status=${PIPESTATUS[0]}

    if [[ $upgrade_status -eq 0 ]]; then
        print_success "Upgrade command completed"
        print_info "Check upgrade.odoo.com to download the upgraded database"
    else
        print_error "Upgrade command failed with status: $upgrade_status"
        print_info "Check log: $WORK_DIR/upgrade_logs/run_001/upgrade.log"
    fi
}

# ===========================================
# GENERATE SUMMARY
# ===========================================

generate_summary() {
    print_step "Generating summary..."

    cat > "$WORK_DIR/UPGRADE_SUMMARY.md" << EOF
# Odoo Database Upgrade Summary

## Upgrade Information
- **Date:** $(date)
- **Source Dump:** $DUMP_FILE
- **Target Version:** $TARGET_VERSION
- **Contract:** $(cat $CONTRACT_FILE)
- **Work Directory:** $WORK_DIR

## Fix Pattern Applied
$(if [[ -n "$FIX_PATTERN" ]]; then
    echo "- **Fix File:** $FIX_PATTERN"
    echo "- **Fix Count:** $(grep -cE "^(UPDATE|CREATE|INSERT|DELETE|ALTER)" "$FIX_PATTERN" || echo "0") statements"
else
    echo "- No fix pattern applied"
fi)

## Upgrade Status
$(if [[ "$DRY_RUN" == true ]]; then
    echo "- **Mode:** DRY RUN (no actual upgrade performed)"
else
    echo "- **Mode:** LIVE"
fi)

## Next Steps
1. Check upgrade.odoo.com for upgrade status
2. Download upgraded database when ready
3. Test in staging environment
4. Deploy to production

## Files Generated
- dump.sql (extracted from source)
- upgrade_logs/ (upgrade logs)
- UPGRADE_SUMMARY.md (this file)
EOF

    print_success "Summary saved to: $WORK_DIR/UPGRADE_SUMMARY.md"
}

# ===========================================
# MAIN
# ===========================================

main() {
    parse_args "$@"
    print_header

    echo "Configuration:"
    echo "  Dump File:     $DUMP_FILE"
    echo "  Target Version: $TARGET_VERSION"
    echo "  Contract:      $CONTRACT_FILE"
    echo "  Fix Pattern:   ${FIX_PATTERN:-none}"
    echo "  Work Directory: $WORK_DIR"
    echo "  Dry Run:       $DRY_RUN"
    echo ""

    preflight_checks
    extract_dump
    prepare_database
    apply_fixes
    run_upgrade
    generate_summary

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  UPGRADE WORKFLOW COMPLETED${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo "Work directory: $WORK_DIR"
    echo ""
}

main "$@"
