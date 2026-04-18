#!/bin/bash
# Odoo Upgrade Automation Script
# Usage: ./odoo_upgrade.sh <dump_file> <target_version> [contract_file]
#
# This script handles:
# 1. Running upgrade.odoo.com test/production commands
# 2. Monitoring upgrade progress
# 3. Parsing and displaying errors
# 4. Generating ACTUAL SQL fixes for detected errors

set -e

DUMP_FILE=${1:-"dump.sql"}
TARGET_VERSION=${2:-"17.0"}
CONTRACT_FILE=${3:-".odoo_contract"}

# ===========================================
# PATHS — always absolute, relative to script location
# ===========================================
# Use the script's own directory as base so paths are stable
# regardless of where the user runs the script from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# If caller passes a relative DUMP_FILE, resolve it from their CWD
if [[ "$DUMP_FILE" != /* ]]; then
    DUMP_FILE="$(pwd)/$DUMP_FILE"
fi
# Contract file resolved from CWD
if [[ "$CONTRACT_FILE" != /* ]]; then
    CONTRACT_FILE="$(pwd)/$CONTRACT_FILE"
fi

# ===========================================
# PROJECT DIR & WORK DIR
# ===========================================
# Logs go to the PROJECT directory where the dump file lives,
# NOT to the skill directory.
# Structure: PROJECT_DIR/upgrade_YYYYMMDD_HHMMSS/upgrade_logs/run_XXX/

# PROJECT_DIR: where the dump file lives (resolved to absolute path)
PROJECT_DIR="$(dirname "$(realpath "$DUMP_FILE")")"

# WORK_DIR: unique per-run folder in project directory
WORK_DIR="$PROJECT_DIR/upgrade_$(date +%Y%m%d_%H%M%S)"

# ===========================================
# RUN NUMBER LOGIC (auto-increment run_XXX inside WORK_DIR)
# ===========================================
# Finds the highest run_NNN folder in WORK_DIR/upgrade_logs/ and increments by 1.
# Falls back to run_001 if no previous runs exist.

get_next_run_num() {
    local log_dir="${1:-$WORK_DIR/upgrade_logs}"
    local max_run=0

    if [[ -d "$log_dir" ]]; then
        for dir in "$log_dir"/run_[0-9][0-9][0-9]; do
            if [[ -d "$dir" ]]; then
                local run_name
                run_name=$(basename "$dir")
                local run_num
                run_num="${run_name#run_}"
                run_num=$((10#$run_num))
                if [[ "$run_num" -gt "$max_run" ]]; then
                    max_run=$run_num
                fi
            fi
        done
    fi

    local next_run=$((max_run + 1))
    printf "%03d" "$next_run"
}

LOG_DIR="$WORK_DIR/upgrade_logs"
RUN_NUM=$(get_next_run_num "$LOG_DIR")
RUN_DIR="$LOG_DIR/run_$RUN_NUM"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}=== Odoo Upgrade Automation ===${NC}"
echo "Dump: $DUMP_FILE"
echo "Target: $TARGET_VERSION"
echo "Contract file: $CONTRACT_FILE"
echo "Project dir: $PROJECT_DIR"
echo -e "Work dir: ${CYAN}$WORK_DIR${NC}"
echo -e "Run: ${CYAN}run_$RUN_NUM${NC}"
echo ""

# Check contract file
if [ ! -f "$CONTRACT_FILE" ]; then
    echo -e "${RED}Error: Contract file not found: $CONTRACT_FILE${NC}"
    echo "Please create a file with your contract number:"
    echo "  echo 'YOUR_CONTRACT_NUMBER' > $CONTRACT_FILE"
    echo ""
    echo "Usage:"
    echo "  ./odoo_upgrade.sh dump.sql 17.0"
    exit 1
fi

# Read contract number from file
CONTRACT=$(cat "$CONTRACT_FILE" | tr -d '\n\r')

if [ -z "$CONTRACT" ]; then
    echo -e "${RED}Error: Contract file is empty${NC}"
    exit 1
fi

# Check dump file exists
if [ ! -f "$DUMP_FILE" ]; then
    echo -e "${RED}Error: Dump file not found: $DUMP_FILE${NC}"
    exit 1
fi

# Create run-specific log directory
mkdir -p "$RUN_DIR"

LOG_FILE="$RUN_DIR/upgrade.log"
FIX_FILE="$RUN_DIR/fix_run${RUN_NUM}.sql"
CHANGES_FILE="$RUN_DIR/changes.md"
SUMMARY_FILE="$RUN_DIR/summary.txt"

echo -e "Work dir: ${CYAN}$WORK_DIR${NC}"
echo -e "Log dir:  ${CYAN}$LOG_DIR${NC}"
echo -e "Log file: ${CYAN}$LOG_FILE${NC}"
echo ""

# Check if dump is compressed
DUMP_ARG="$DUMP_FILE"
if [[ "$DUMP_FILE" == *.gz ]]; then
    echo -e "${YELLOW}Note: Detected gzipped dump${NC}"
elif [[ "$DUMP_FILE" == *.zip ]]; then
    echo -e "${YELLOW}Note: Detected zip dump${NC}"
fi

# Run upgrade test
echo -e "${YELLOW}Starting upgrade test...${NC}"
echo ""

UPGRADE_CMD="python <(curl -s https://upgrade.odoo.com/upgrade) test \
    -i \"$DUMP_FILE\" \
    -t \"$TARGET_VERSION\" \
    -c \"$CONTRACT\""

echo "Command: $UPGRADE_CMD"
echo ""

# Run upgrade and capture output
eval "$UPGRADE_CMD" 2>&1 | tee "$LOG_FILE"

UPGRADE_STATUS=${PIPESTATUS[0]}

echo ""
echo -e "${YELLOW}Checking for errors in log...${NC}"

# ===========================================
# ERROR PARSING — collect raw error lines
# ===========================================
ERROR_LINES=$(grep -iE "(Error|Error:|FATAL|Exception|Traceback|failed):" "$LOG_FILE" 2>/dev/null | grep -v "^--$" | head -50 || true)

# Categorize errors
declare -a MODULE_ERRORS
declare -a VIEW_ERRORS
declare -a COLUMN_ERRORS
declare -a TABLE_ERRORS
declare -a CONSTRAINT_ERRORS
declare -a L10N_ERRORS
declare -a L10N_ACCT_ERRORS

categorize_errors() {
    # --- l10n (country localization) module failures ---
    # Pattern: ValueError: External ID not found in the system: account.X_l10n_id_XXXXXXX
    #   or: Exception in l10n_XX module migration script
    # Fix: Insert missing account.account.template + ir.model.data record directly.
    #      DO NOT uninstall or set to_upgrade — the migration script will retry.
    local l10n_grep_pattern="External ID not found|l10n_id"
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        # Extract l10n module name: l10n_id, l10n_id_efaktur
        local mod_name
        mod_name=$(echo "$line" | grep -i "l10n_id_efaktur" | head -1 | tr -d '\r' || true)
        if [[ -z "$mod_name" ]]; then
            mod_name=$(echo "$line" | grep -i "l10n_id" | head -1 | tr -d '\r' || true)
            mod_name=$(echo "$mod_name" | sed 's/.*l10n_id.*/l10n_id/' | head -1)
        fi
        [[ -n "$mod_name" && "$mod_name" != "null" ]] && L10N_ERRORS+=("l10n_id")

        # Extract the missing external ID: account.1_l10n_id_21221020
        local missing_xid
        missing_xid=$(echo "$line" | grep -oE "account\.[0-9]+_l10n_id_[0-9]+" | head -1 || true)
        [[ -n "$missing_xid" ]] && L10N_ACCT_ERRORS+=("$missing_xid")
    done < <(grep -i "$l10n_grep_pattern" "$LOG_FILE" 2>/dev/null || true)

    # --- Module / Key already exists errors ---
    # Pattern: Key (name)=(module_name) already exists
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local mod_name
        mod_name=$(echo "$line" | sed -n 's/.*Key (name)=\([^)]*\)[\"].*/\1/p' | tr -d "'" | tr -d '\r' || true)
        if [[ -z "$mod_name" ]]; then
            mod_name=$(echo "$line" | sed 's/.*Key (name)=//' | cut -d')' -f1 | tr -d "'" | tr -d '\r' || true)
        fi
        [[ -n "$mod_name" ]] && MODULE_ERRORS+=("$mod_name")
    done < <(grep -iE "Key \(name\)=.*already exists" "$LOG_FILE" 2>/dev/null || true)

    # --- View dependency errors ---
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local view_info
        view_info=$(echo "$line" | awk '{print $NF}' | tr '\n' ' ' | sed 's/[[:space:]]*$//' | tr -d '\r' || true)
        [[ -n "$view_info" ]] && VIEW_ERRORS+=("$view_info")
    done < <(grep -iE "view.*depends|column.*does not exist|programming error at|invalid.*view" "$LOG_FILE" 2>/dev/null || true)

    # --- Missing column errors ---
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local col_info
        col_info=$(echo "$line" | grep -oE "column [^\"]+|\"[^\"]+\"" | head -3 | tr '\n' ' ' | tr -d '\r' || true)
        [[ -n "$col_info" ]] && COLUMN_ERRORS+=("$col_info")
    done < <(grep -iE "column.*does not exist" "$LOG_FILE" 2>/dev/null || true)

    # --- Missing table errors ---
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local tbl_info
        tbl_info=$(echo "$line" | grep -oP "relation \K[\".a-zA-Z0-9_.]+" | head -3 || true)
        TABLE_ERRORS+=("$tbl_info")
    done < <(grep -iE "relation.*does not exist" "$LOG_FILE" 2>/dev/null || true)

    # --- Constraint errors ---
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        CONSTRAINT_ERRORS+=("$line")
    done < <(grep -iE "constraint.*failed|violates foreign key" "$LOG_FILE" 2>/dev/null || true)
}

categorize_errors

# ===========================================
# GENERATE ACTUAL SQL FIXES
# ===========================================
generate_sql_fixes() {
    echo "-- ============================================================"
    echo "-- SQL FIXES for run_$RUN_NUM"
    echo "-- Generated: $(date)"
    echo "-- Source log: $LOG_FILE"
    echo "-- Target: Odoo $TARGET_VERSION"
    echo "-- ============================================================"
    echo ""
    echo "-- HOW TO USE THIS FILE:"
    echo "-- 1. Review the SQL statements below"
    echo "-- 2. Edit as needed for your database"
    echo "-- 3. Apply with: psql -h localhost -U odoo -d your_database -f $FIX_FILE"
    echo ""
    echo ""

    # ---- 0. L10N MISSING ACCOUNT TEMPLATE FIXES ----
    # Example: ValueError: External ID not found in the system: account.1_l10n_id_21221020
    # The l10n_id migration script end-migrate_update_taxes.py tries to reference an account
    # template (l10n_id_21221020) that was never loaded into the database.
    # Fix: Insert the missing account.account.template record + ir.model.data entry.
    if [[ ${#L10N_ACCT_ERRORS[@]} -gt 0 || ${#L10N_ERRORS[@]} -gt 0 ]]; then
        local -A seen_xid
        local unique_xids=()
        for xid in "${L10N_ACCT_ERRORS[@]}" "${L10N_ERRORS[@]}"; do
            local clean
            clean=$(echo "$xid" | grep -oE "account\.[0-9]+_l10n_id_[0-9]+" | head -1 || true)
            [[ -z "$clean" ]] && continue
            [[ "${seen_xid[$clean]}" == "1" ]] && continue
            seen_xid[$clean]=1
            unique_xids+=("$clean")
        done

        if [[ ${#unique_xids[@]} -gt 0 ]]; then
            echo "-- ============================================================"
            echo "-- FIX 0: Missing account template (l10n) — add directly, do NOT uninstall l10n"
            echo "-- ============================================================"
            echo "--"
            echo "-- Error: ValueError: External ID not found in the system: account.X_l10n_id_XXXXXXX"
            echo "--"
            echo "-- The l10n_id migration script (l10n_id/1.3/end-migrate_update_taxes.py)"
            echo "-- is trying to reference account template l10n_id_XXXXXXX but it was never loaded."
            echo "--"
            echo "-- Fix: Insert missing account.account.template record + ir.model.data entry."
            echo "--      This allows the migration script to proceed without uninstalling l10n_id."
            echo "--"
            echo "-- IMPORTANT: Review and adjust the INSERT values below to match your company setup."
            echo "--      The 'code' field must match an existing code in the chart template."
            echo "--"
            echo ""

            for xid in "${unique_xids[@]}"; do
                # Parse: account.1_l10n_id_21221020 -> module=l10n_id, company_id=1, name=l10n_id_21221020
                local mod_name="${xid#account.[0-9]*_}"
                mod_name="${mod_name%%_*}"  # first segment of name
                local company_id
                company_id=$(echo "$xid" | grep -oE "^account\.[0-9]+" | cut -d. -f2 || echo "1")
                local xid_name
                xid_name=$(echo "$xid" | grep -oE "[^.]+$" || echo "l10n_id_placeholder")

                echo "-- Missing external ID: $xid"
                echo "-- Module: l10n_id  Company: $company_id"
                echo ""
                echo "-- Step 1: Insert the account.account.template record"
                echo "--   (Adjust code, name, user_type_id to match your chart template)"
                echo "--   user_type_id 212 = 'Expenses' (view type), adjust as needed"
                echo ""
                echo "-- Find your chart account code range first:"
                echo "-- SELECT id, code, name FROM account_account WHERE"
                echo "--   name LIKE '%tax%' OR code LIKE '2%' LIMIT 10;"
                echo ""
                echo "-- Then run (adjust values to match your existing accounts):"
                echo "-- INSERT INTO account_account ("
                echo "--     name, code, user_type_id, company_id, reconcile, note,"
                echo "--     create_uid, create_date, write_uid, write_date"
                echo "-- ) VALUES ("
                echo "--     'Tax Adjustment Account',       -- name (adjust)"
                echo "--     '21221020',                     -- code (adjust to match chart)"
                echo "--     (SELECT id FROM account_account_type WHERE name='Expenses' LIMIT 1),"
                echo "--     $company_id,                    -- company_id"
                echo "--     false,                           -- reconcile"
                echo "--     NULL,                           -- note"
                echo "--     1, NOW(), 1, NOW()"
                echo "-- );"
                echo ""
                echo "-- Step 2: Insert the ir.model.data entry so migration can find it"
                echo "--   (Use the actual id from the account_account INSERT above)"
                echo "WITH acct AS ("
                echo "    SELECT id FROM account_account"
                echo "     WHERE company_id = $company_id"
                echo "       AND name = 'Tax Adjustment Account'"
                echo "     LIMIT 1"
                echo ")"
                echo "INSERT INTO ir_model_data ("
                echo "    name, model, module, res_id, noupdate,"
                echo "    create_uid, create_date, write_uid, write_date"
                echo ") VALUES ("
                echo "    '$xid_name', 'account.account.template', 'l10n_id',"
                echo "    (SELECT id FROM acct LIMIT 1), false,"
                echo "    1, NOW(), 1, NOW()"
                echo ")"
                echo "ON CONFLICT (module, name) DO NOTHING;"
                echo ""
            done
        fi
    fi

    # ---- 1. MODULE FIXES ----
    if [[ ${#MODULE_ERRORS[@]} -gt 0 ]]; then
        # Deduplicate module names
        local -A seen_mod
        local unique_mods=()
        for mod in "${MODULE_ERRORS[@]}"; do
            mod=$(echo "$mod" | tr -d "'\" " | tr '[:upper:]' '[:lower:]')
            [[ -z "$mod" ]] && continue
            [[ "${seen_mod[$mod]}" == "1" ]] && continue
            seen_mod[$mod]=1
            unique_mods+=("$mod")
        done

        if [[ ${#unique_mods[@]} -gt 0 ]]; then
            echo "-- ============================================================"
            echo "-- FIX 1: Module 'already exists' — mark as 'to upgrade'"
            echo "-- ============================================================"
            echo "--"
            echo '-- During upgrade, custom modules cause duplicate key errors'
            echo "-- because upgrade.odoo.com tries to CREATE them again."
            echo "-- Fix: Set state='to upgrade' so Odoo UPDATE them instead."
            echo "--"
            echo "UPDATE ir_module_module"
            echo "   SET state = 'to upgrade'"
            echo " WHERE name IN ('${unique_mods[*]}');"
            echo ""
            echo "-- Verify:"
            echo "-- SELECT name, state FROM ir_module_module WHERE name IN ('${unique_mods[*]}');"
            echo ""
        fi
    fi

    # ---- 2. VIEW DISABLE FIXES ----
    if [[ ${#VIEW_ERRORS[@]} -gt 0 ]]; then
        echo "-- ============================================================"
        echo "-- FIX 2: Broken inherited views"
        echo "-- ============================================================"
        echo "--"
        echo "-- Views that depend on removed/renamed columns cause"
        echo "-- 'programming error' during upgrade."
        echo "-- Fix: Disable views that have inheritance conflicts."
        echo ""

        # Auto-extract view IDs from the error log
        # Pattern 1: "View ... id=XXX" or "id: XXX" in error context
        # Pattern 2: from ir_ui_view references in error lines
        local -a detected_view_ids=()
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            # Match patterns like: view id=383, id: 514, id=705, view(383), ID: 741
            local ids
            ids=$(echo "$line" | grep -oE "\bid=?[0-9]{2,}\b" | grep -oE "[0-9]{2,}" || true)
            [[ -n "$ids" ]] && detected_view_ids+=($ids)
        done < <(grep -iE "view|ir_ui_view|inherit|arch|xpath" "$LOG_FILE" 2>/dev/null | grep -iE "id[ =:]+[0-9]{2,}|Error|Exception|failed" | head -50 || true)

        # Also search near error lines for view ID references
        local context_ids
        context_ids=$(grep -n -iE "Error|Exception|Traceback|failed" "$LOG_FILE" 2>/dev/null \
            | cut -d: -f1 \
            | while read -r linenum; do
                # Read 5 lines before and after each error line
                for offset in -5 -4 -3 -2 -1 0 1 2 3 4 5; do
                    sed -n "$((linenum + offset))p" "$LOG_FILE" 2>/dev/null
                done
              done \
            | grep -oE "\b(id=|[Ii]d:? ?)[0-9]{2,}\b" \
            | grep -oE "[0-9]{2,}" \
            | sort -nu | head -30 || true)

        if [[ -n "${detected_view_ids[*]}" || -n "$context_ids" ]]; then
            # Merge and deduplicate all detected IDs
            local all_ids
            all_ids=$(printf '%s\n%s\n' "${detected_view_ids[*]}" "$context_ids" 2>/dev/null \
                | grep -E "^[0-9]{2,}$" | sort -nu | tr '\n' ',' | sed 's/,$//')
            if [[ -n "$all_ids" ]]; then
                echo "-- Auto-detected view IDs from error log:"
                echo "UPDATE ir_ui_view SET active = false WHERE id IN ($all_ids);"
                echo ""
                echo "-- Verify before applying — list the views:"
                echo "-- SELECT id, name, model, type, inherit_id, active"
                echo "--   FROM ir_ui_view WHERE id IN ($all_ids);"
                echo ""
            fi
        fi

        echo "-- Also check for views with inheritance conflicts:"
        echo "-- SELECT id, name, model, type, inherit_id"
        echo "--   FROM ir_ui_view"
        echo "--  WHERE model IN ('res.partner','product.template','sale.order')"
        echo "--    AND active = true;"
        echo ""
    fi

    # ---- 3. MISSING COLUMN FIXES ----
    if [[ ${#COLUMN_ERRORS[@]} -gt 0 ]]; then
        echo "-- ============================================================"
        echo "-- FIX 3: Missing columns"
        echo "-- ============================================================"
        echo "--"
        echo "-- A column referenced by a view/stored function was removed"
        echo "-- or renamed during the upgrade."
        echo "-- Fix: Add the missing column or disable the view."
        echo "--"

        # Deduplicate column refs
        local -A seen_col
        local unique_cols=()
        for col in "${COLUMN_ERRORS[@]}"; do
            col=$(echo "$col" | tr -d '". ' | tr '[:upper:]' '[:lower:]')
            [[ -z "$col" || "$col" == "null" ]] && continue
            [[ "${seen_col[$col]}" == "1" ]] && continue
            seen_col[$col]=1
            unique_cols+=("$col")
        done

        if [[ ${#unique_cols[@]} -gt 0 ]]; then
            echo "-- Detected missing column references (verify from log):"
            for col in "${unique_cols[@]}"; do
                echo "--   - $col"
            done
            echo ""
            echo "-- To find which table/view is missing the column:"
            echo "-- SELECT v.id, v.name, v.model, v.type"
            echo "--   FROM ir_ui_view v"
            echo "--  WHERE v.active = true"
            echo "--    AND v.arch ~ '(${unique_cols[0]}|${unique_cols[1]:-NOMATCH})';"
            echo ""
        fi
        echo "-- Recommendation: Disable the broken view (see FIX 2 above)"
        echo ""
    fi

    # ---- 4. MISSING TABLE FIXES ----
    if [[ ${#TABLE_ERRORS[@]} -gt 0 ]]; then
        echo "-- ============================================================"
        echo "-- FIX 4: Missing tables"
        echo "-- ============================================================"
        echo "--"
        echo "-- A table expected by a module/function does not exist."
        echo "-- Fix: Either create the table or mark the module for upgrade."
        echo "--"

        local -A seen_tbl
        local unique_tbls=()
        for tbl in "${TABLE_ERRORS[@]}"; do
            tbl=$(echo "$tbl" | tr -d '". ' | tr '[:upper:]' '[:lower:]')
            [[ -z "$tbl" || "$tbl" == "null" ]] && continue
            [[ "${seen_tbl[$tbl]}" == "1" ]] && continue
            seen_tbl[$tbl]=1
            unique_tbls+=("$tbl")
        done

        for tbl in "${unique_tbls[@]}"; do
            echo "-- Table missing: $tbl"
            echo "--"
            echo "-- Option A — Create stub table (if it's a tracking/audit table):"
            echo "-- CREATE TABLE IF NOT EXISTS $tbl ("
            echo "--     id SERIAL PRIMARY KEY,"
            echo "--     create_uid INTEGER,"
            echo "--     create_date TIMESTAMP,"
            echo "--     write_uid INTEGER,"
            echo "--     write_date TIMESTAMP"
            echo "-- );"
            echo ""
            echo "-- Option B — Mark module as 'to upgrade' (if table is managed by module):"
            echo "-- UPDATE ir_module_module SET state = 'to upgrade'"
            echo "--  WHERE name = 'module_name';"
            echo ""
        done
    fi

    # ---- 5. CONSTRAINT FIXES ----
    if [[ ${#CONSTRAINT_ERRORS[@]} -gt 0 ]]; then
        echo "-- ============================================================"
        echo "-- FIX 5: Constraint violations"
        echo "-- ============================================================"
        echo "--"
        echo "-- Detected constraint/foreign key errors:"
        for cerr in "${CONSTRAINT_ERRORS[@]}"; do
            echo "--   $cerr"
        done
        echo ""
        echo "-- Recommendation: Disable failing constraints temporarily"
        echo "-- ALTER TABLE table_name DISABLE TRIGGER ALL;  -- use with caution"
        echo ""
    fi

    # ---- 6. GENERAL UPGRADE MODULE MARKER ----
    echo "-- ============================================================"
    echo "-- FIX 6: Mark all custom modules for upgrade (safety net)"
    echo "-- ============================================================"
    echo "--"
    echo "-- Run this as a safety net to ensure all custom modules"
    echo "-- are processed during the next upgrade attempt."
    echo "--"
    echo "-- Identify custom modules (non-community modules):"
    echo "-- SELECT name, state FROM ir_module_module"
    echo "--  WHERE name LIKE 'asb_%'"
    echo "--     OR name LIKE 'custom_%'"
    echo "--     OR name LIKE 'x_%';"
    echo ""
    echo "-- Mark custom modules for upgrade (replace pattern as needed):"
    echo "-- UPDATE ir_module_module"
    echo "--    SET state = 'to upgrade'"
    echo "--  WHERE name LIKE 'asb_%'"
    echo "--    AND state = 'installed';"
    echo ""
    echo "-- ============================================================"
    echo "-- END OF FIX FILE"
    echo "-- ============================================================"
}

# ===========================================
# CATEGORIZE AND DISPLAY ERRORS
# ===========================================

if [[ -n "$ERROR_LINES" ]]; then
    echo -e "${RED}Errors detected!${NC}"
    echo ""
    echo "=== Error Summary ==="
    echo "$ERROR_LINES"
    echo ""

    echo "=== Error Categories ==="

    if [[ ${#MODULE_ERRORS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  - Module 'already exists' errors: ${MODULE_ERRORS[*]}${NC}"
    fi

    if [[ ${#VIEW_ERRORS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  - View dependency errors${NC}"
    fi

    if [[ ${#COLUMN_ERRORS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  - Missing column errors${NC}"
    fi

    if [[ ${#TABLE_ERRORS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  - Missing table errors${NC}"
    fi

    if [[ ${#CONSTRAINT_ERRORS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  - Constraint violations${NC}"
    fi

    if [[ ${#L10N_ERRORS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}  - l10n localization module failures: ${#L10N_ERRORS[@]} module(s)${NC}"
    fi

    if [[ ${#MODULE_ERRORS[@]} -eq 0 && ${#VIEW_ERRORS[@]} -eq 0 && \
          ${#COLUMN_ERRORS[@]} -eq 0 && ${#TABLE_ERRORS[@]} -eq 0 && \
          ${#CONSTRAINT_ERRORS[@]} -eq 0 && ${#L10N_ERRORS[@]} -eq 0 ]]; then
        echo -e "${YELLOW}  - Uncategorized errors (check log for details)${NC}"
    fi

    echo ""
    echo -e "${CYAN}Generating SQL fix file...${NC}"

    # Generate actual SQL fix file
    generate_sql_fixes > "$FIX_FILE"

    echo -e "${GREEN}SQL fix file created: $FIX_FILE${NC}"
    echo ""

    # Create changes log
    {
        echo "# Upgrade Changes Log — run_$RUN_NUM"
        echo ""
        echo "## Metadata"
        echo "- **Run:** run_$RUN_NUM"
        echo "- **Date:** $(date)"
        echo "- **Dump:** $DUMP_FILE"
        echo "- **Target:** Odoo $TARGET_VERSION"
        echo "- **Status:** FAILED — errors detected"
        echo ""
        echo "## Error Summary"
        echo '```'
        echo "$ERROR_LINES"
        echo '```'
        echo ""
        echo "## Categories Detected"
        if [[ ${#MODULE_ERRORS[@]} -gt 0 ]]; then
            echo "- Module 'already exists': ${MODULE_ERRORS[*]}"
        fi
        if [[ ${#VIEW_ERRORS[@]} -gt 0 ]]; then
            echo "- View dependency errors: ${#VIEW_ERRORS[@]} occurrences"
        fi
        if [[ ${#COLUMN_ERRORS[@]} -gt 0 ]]; then
            echo "- Missing columns: ${#COLUMN_ERRORS[@]} occurrences"
        fi
        if [[ ${#TABLE_ERRORS[@]} -gt 0 ]]; then
            echo "- Missing tables: ${#TABLE_ERRORS[@]} occurrences"
        fi
        if [[ ${#CONSTRAINT_ERRORS[@]} -gt 0 ]]; then
            echo "- Constraint violations: ${#CONSTRAINT_ERRORS[@]} occurrences"
        fi
        if [[ ${#L10N_ERRORS[@]} -gt 0 ]]; then
            echo "- l10n localization failures: ${#L10N_ERRORS[@]} module(s)"
        fi
        echo ""
        echo "## Files Generated"
        echo "- Log: $LOG_FILE"
        echo "- SQL Fix: $FIX_FILE"
        echo ""
        echo "## Next Steps"
        echo "1. Review $FIX_FILE — edit SQL as needed for your database"
        echo "2. Apply fixes: psql -h localhost -U odoo -d target_db -f $FIX_FILE"
        echo "3. Export new dump after applying fixes"
        echo "4. Re-run: ./odoo_upgrade.sh fixed_dump.sql $TARGET_VERSION"
        echo "   (Will automatically use run_$(printf "%03d" $((10#$RUN_NUM + 1))))"
    } > "$CHANGES_FILE"

    # Summary
    {
        echo "run_$RUN_NUM | $(date) | FAILED"
        echo "  Errors: ${#MODULE_ERRORS[@]} module, ${#VIEW_ERRORS[@]} view, ${#COLUMN_ERRORS[@]} column, ${#TABLE_ERRORS[@]} table, ${#CONSTRAINT_ERRORS[@]} constraint, ${#L10N_ERRORS[@]} l10n"
        echo "  Fix: $FIX_FILE"
        echo "  Next run: run_$(printf "%03d" $((10#$RUN_NUM + 1)))"
    } > "$SUMMARY_FILE"

    echo ""
    echo -e "${RED}Upgrade failed. Check $LOG_FILE for details${NC}"
    echo -e "${YELLOW}See $FIX_FILE for generated SQL fixes${NC}"
    exit 1

else
    echo -e "${GREEN}No explicit errors found in log!${NC}"

    # Check for success indicators
    if grep -qi "success\|complete\|finished\|ready\|token" "$LOG_FILE" 2>/dev/null; then
        echo -e "${GREEN}Upgrade completed successfully!${NC}"

        {
            echo "# Upgrade Changes Log — run_$RUN_NUM"
            echo ""
            echo "## Metadata"
            echo "- **Run:** run_$RUN_NUM"
            echo "- **Date:** $(date)"
            echo "- **Dump:** $DUMP_FILE"
            echo "- **Target:** Odoo $TARGET_VERSION"
            echo "- **Status:** SUCCESS"
            echo ""
            echo "## Next Steps"
            echo "1. Download upgraded database from upgrade.odoo.com"
            echo "2. Test in staging environment"
            echo "3. Deploy to production"
        } > "$CHANGES_FILE"

        {
            echo "run_$RUN_NUM | $(date) | SUCCESS"
        } > "$SUMMARY_FILE"

        echo -e "${GREEN}Upgrade completed successfully!${NC}"
        exit 0
    else
        if grep -qi "token\|request" "$LOG_FILE" 2>/dev/null; then
            echo -e "${YELLOW}Upgrade may still be in progress. Check upgrade.odoo.com for status.${NC}"
            echo ""
            echo "To check status:"
            echo "  python <(curl -s https://upgrade.odoo.com/upgrade) status -t <TOKEN>"
        fi
    fi
fi

echo ""
echo "Upgrade process completed. Check logs for details."
