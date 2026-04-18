#!/bin/bash
# Apply SQL fix to dump, then retry upgrade
# Usage: ./apply_fix_and_retry.sh <dump.zip> <target_version> <fix.sql> [contract_file]
#
# Workflow:
# 1. Extract dump.sql from zip
# 2. Restore to localhost (creates temp DB)
# 3. Apply SQL fix
# 4. Dump fixed DB back to SQL
# 5. Re-run upgrade with fixed dump
#
set -e

DUMP_FILE="${1:-dump.zip}"
TARGET_VERSION="${2:-19.0}"
FIX_FILE="${3:-fix.sql}"
CONTRACT_FILE="${4:-.odoo_contract}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"

# ===========================================
# COLORS
# ===========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ===========================================
# RESOLVE PATHS (always absolute)
# ===========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [[ "$DUMP_FILE" != /* ]]; then
    DUMP_FILE="$(pwd)/$DUMP_FILE"
fi
if [[ "$FIX_FILE" != /* ]]; then
    FIX_FILE="$(pwd)/$FIX_FILE"
fi
if [[ "$CONTRACT_FILE" != /* ]]; then
    CONTRACT_FILE="$(pwd)/$CONTRACT_FILE"
fi

# Work directory: where dump lives
PROJECT_DIR="$(dirname "$(realpath "$DUMP_FILE")")"
WORK_DIR="$PROJECT_DIR/upgrade_$(date +%Y%m%d_%H%M%S)"
EXTRACT_DIR="$WORK_DIR/extracted"
FIXED_DIR="$WORK_DIR/fixed"

# Temp database name
TEMP_DB="migration_fix_$(date +%Y%m%d_%H%M%S)"

# ===========================================
# PRINT FUNCTIONS
# ===========================================
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
print_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_err()  { echo -e "${RED}[ERROR]${NC} $1"; }
print_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# ===========================================
# PREFLIGHT
# ===========================================
preflight() {
    print_step "Running preflight checks..."

    if [[ ! -f "$DUMP_FILE" ]]; then
        print_err "Dump file not found: $DUMP_FILE"
        exit 1
    fi

    if [[ ! -f "$FIX_FILE" ]]; then
        print_err "Fix file not found: $FIX_FILE"
        exit 1
    fi

    if [[ ! -f "$CONTRACT_FILE" ]]; then
        print_err "Contract file not found: $CONTRACT_FILE"
        echo "Create it with: echo 'YOUR_CONTRACT' > $CONTRACT_FILE"
        exit 1
    fi

    if ! command -v psql &> /dev/null; then
        print_err "psql not found - cannot proceed"
        exit 1
    fi

    export PGPASSWORD="$DB_PASSWORD"

    print_ok "Preflight passed"
    echo "  Dump: $DUMP_FILE"
    echo "  Fix:  $FIX_FILE"
    echo "  Temp DB: $TEMP_DB"
    echo "  Work dir: $WORK_DIR"
}

# ===========================================
# EXTRACT DUMP
# ===========================================
extract_dump() {
    print_step "Extracting dump from archive..."

    mkdir -p "$EXTRACT_DIR"

    local ext="${DUMP_FILE##*.}"
    case "$ext" in
        zip)
            unzip -o "$DUMP_FILE" dump.sql -d "$EXTRACT_DIR" > /dev/null 2>&1
            print_ok "Extracted dump.sql from zip"
            ;;
        sql)
            cp "$DUMP_FILE" "$EXTRACT_DIR/dump.sql"
            print_ok "Copied dump.sql"
            ;;
        *)
            print_err "Unsupported format: $ext"
            exit 1
            ;;
    esac

    if [[ ! -f "$EXTRACT_DIR/dump.sql" ]]; then
        print_err "dump.sql not found after extraction"
        exit 1
    fi

    echo "  Size: $(du -h "$EXTRACT_DIR/dump.sql" | cut -f1)"
}

# ===========================================
# RESTORE TO LOCALHOST
# ===========================================
restore_db() {
    print_step "Restoring dump to localhost PostgreSQL..."

    export PGPASSWORD="$DB_PASSWORD"

    # Use 'postgres' database for DDL commands (CREATE/DROP DATABASE)
    local admin_db="${ADMIN_DB:-postgres}"

    # Drop temp DB if exists (connect to postgres admin db)
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$admin_db" \
        -c "DROP DATABASE IF EXISTS $TEMP_DB" 2>/dev/null || true

    # Create fresh DB (connect to postgres admin db)
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$admin_db" \
        -c "CREATE DATABASE $TEMP_DB" 2>/dev/null

    print_info "Restoring... (this may take a while)"
    # Restore dump to temp DB
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEMP_DB" \
        -f "$EXTRACT_DIR/dump.sql" > /dev/null 2>&1

    print_ok "Database restored: $TEMP_DB"

    # Verify tables exist
    local table_count
    table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEMP_DB" \
        -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'" 2>/dev/null | xargs)
    echo "  Tables restored: $table_count"
}

# ===========================================
# APPLY FIX
# ===========================================
apply_fix() {
    print_step "Applying SQL fix..."

    export PGPASSWORD="$DB_PASSWORD"

    local fix_count
    fix_count=$(grep -cE "^(UPDATE|INSERT|DELETE|CREATE|ALTER|DROP|DO)" "$FIX_FILE" 2>/dev/null || echo "0")
    print_info "Found $fix_count SQL statements"

    # Apply with continue on error
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEMP_DB" \
        -v ON_ERROR_STOP=0 \
        -f "$FIX_FILE" 2>&1 | tee "$WORK_DIR/fix_apply.log"

    print_ok "Fix applied to $TEMP_DB"
    echo "  Log: $WORK_DIR/fix_apply.log"
}

# ===========================================
# VERIFY FIX
# ===========================================
verify_fix() {
    print_step "Verifying fix..."

    export PGPASSWORD="$DB_PASSWORD"

    # Generic verification - check accounts exist
    if grep -q "21221020\|21221010" "$FIX_FILE"; then
        echo "  Checking l10n_id accounts..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEMP_DB" \
            -c "SELECT code, name FROM account_account WHERE code IN ('21221010','21221020');" 2>/dev/null
    fi

    print_ok "Verification complete"
}

# ===========================================
# DUMP FIXED DB
# ===========================================
dump_fixed() {
    print_step "Dumping fixed database..."

    mkdir -p "$FIXED_DIR"

    local fixed_dump="$FIXED_DIR/dump_fixed.sql"
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEMP_DB" \
        --no-owner --no-acl -f "$fixed_dump" 2>/dev/null

    print_ok "Fixed dump created: $fixed_dump"
    echo "  Size: $(du -h "$fixed_dump" | cut -f1)"

    # Store path for next step
    echo "$fixed_dump" > "$WORK_DIR/.fixed_dump_path"
}

# ===========================================
# CLEANUP TEMP DB
# ===========================================
cleanup_temp_db() {
    print_step "Cleaning up temp database..."

    export PGPASSWORD="$DB_PASSWORD"
    local admin_db="${ADMIN_DB:-postgres}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$admin_db" \
        -c "DROP DATABASE IF EXISTS $TEMP_DB" 2>/dev/null || true

    print_ok "Temp DB cleaned up"
}

# ===========================================
# RETRY UPGRADE
# ===========================================
retry_upgrade() {
    print_step "Running upgrade with fixed dump..."

    local fixed_dump
    fixed_dump=$(cat "$WORK_DIR/.fixed_dump_path")

    print_info "Using fixed dump: $fixed_dump"

    # Update contract file path
    if [[ "$CONTRACT_FILE" != /* ]]; then
        CONTRACT_FILE="$(pwd)/$CONTRACT_FILE"
    fi

    # Run upgrade
    "$SKILL_DIR/scripts/odoo_upgrade.sh" \
        "$fixed_dump" \
        "$TARGET_VERSION" \
        "$CONTRACT_FILE"
}

# ===========================================
# GENERATE SUMMARY
# ===========================================
generate_summary() {
    print_step "Generating summary..."

    cat > "$WORK_DIR/FIX_RETRY_SUMMARY.md" << EOF
# Fix & Retry Summary

## Run Info
- **Date:** $(date)
- **Original Dump:** $DUMP_FILE
- **Fix Applied:** $FIX_FILE
- **Target Version:** $TARGET_VERSION
- **Work Dir:** $WORK_DIR

## Workflow Steps
1. ✅ Extract dump.sql from $DUMP_FILE
2. ✅ Restore to temp DB: $TEMP_DB
3. ✅ Apply SQL fix from $FIX_FILE
4. ✅ Dump fixed DB to $FIXED_DIR/dump_fixed.sql
5. ✅ Cleanup temp DB
6. → Retry upgrade (see upgrade_YYYYMMDD_HHMMSS/)

## Next Steps
1. Monitor upgrade at upgrade.odoo.com
2. If fails again, analyze new errors
3. Apply additional fixes if needed
4. Repeat until SUCCESS

## Files Generated
- $WORK_DIR/extracted/dump.sql
- $WORK_DIR/fixed/dump_fixed.sql
- $WORK_DIR/fix_apply.log
- $WORK_DIR/FIX_RETRY_SUMMARY.md
EOF

    print_ok "Summary: $WORK_DIR/FIX_RETRY_SUMMARY.md"
}

# ===========================================
# MAIN
# ===========================================
main() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  FIX BEFORE RETRY WORKFLOW${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
    echo "Usage: $0 <dump.zip> <target_version> <fix.sql> [contract_file]"
    echo ""
    echo "Configuration:"
    echo "  DB Host:     $DB_HOST:$DB_PORT"
    echo "  DB User:     $DB_USER"
    echo "  Temp DB:     $TEMP_DB"
    echo "  Dump:        $DUMP_FILE"
    echo "  Fix:         $FIX_FILE"
    echo "  Contract:    $CONTRACT_FILE"
    echo ""

    preflight
    extract_dump
    restore_db
    apply_fix
    verify_fix
    dump_fixed
    cleanup_temp_db
    retry_upgrade
    generate_summary

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  FIX & RETRY COMPLETED${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo "Work directory: $WORK_DIR"
    echo ""
}

main "$@"
