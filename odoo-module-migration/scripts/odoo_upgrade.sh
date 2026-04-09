#!/bin/bash
# Odoo Upgrade Automation Script
# Usage: ./odoo_upgrade.sh <dump_file> <target_version> [contract_file]
#
# This script handles:
# 1. Running upgrade.odoo.com test/production commands
# 2. Monitoring upgrade progress
# 3. Parsing and displaying errors
# 4. Generating SQL fixes for common errors

set -e

DUMP_FILE=${1:-"dump.sql"}
TARGET_VERSION=${2:-"17.0"}
CONTRACT_FILE=${3:-".odoo_contract"}

# Check if there's already a upgrade_logs folder - use existing one instead of creating new
if [[ -d "upgrade_logs" ]]; then
    LOG_DIR="upgrade_logs"
    RUN_NUM=$(date +%Y%m%d_%H%M%S)
    echo "Using existing upgrade_logs folder"
else
    LOG_DIR="upgrade_logs"
    RUN_NUM=$(date +%Y%m%d_%H%M%S)
    echo "Creating new upgrade_logs folder"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Odoo Upgrade Automation ===${NC}"
echo "Dump: $DUMP_FILE"
echo "Target: $TARGET_VERSION"
echo "Contract file: $CONTRACT_FILE"
echo "Run: $RUN_NUM"
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

# Create log directory
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/upgrade_${RUN_NUM}.log"
FIX_FILE="$LOG_DIR/fix_${RUN_NUM}.sql"
CHANGES_FILE="$LOG_DIR/changes_${RUN_NUM}.md"

echo "Log file: $LOG_FILE"
echo ""

# Check if dump is compressed and handle it
DUMP_ARG="$DUMP_FILE"
if [[ "$DUMP_FILE" == *.gz ]]; then
    echo -e "${YELLOW}Note: Detected gzipped dump${NC}"
    # upgrade.odoo.com handles .gz files directly
elif [[ "$DUMP_FILE" == *.zip ]]; then
    echo -e "${YELLOW}Note: Detected zip dump${NC}"
fi

# Run upgrade test first
echo -e "${YELLOW}Starting upgrade test...${NC}"
echo ""

# Build the command - using test upgrade
# Note: upgrade.odoo.com uses -i for input dump file
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

# Analyze log for errors using multiple patterns
ERRORS_FOUND=false
ERROR_LINES=""

# Check for various error patterns
if grep -qi "error\|fatal\|exception\|traceback\|failed" "$LOG_FILE" 2>/dev/null; then
    ERRORS_FOUND=true

    echo -e "${RED}Errors detected!${NC}"

    # Extract relevant error lines
    ERROR_LINES=$(grep -iE "(error|fatal|exception|traceback|failed):" "$LOG_FILE" | head -30 || true)

    if [ -n "$ERROR_LINES" ]; then
        echo ""
        echo "=== Error Summary ==="
        echo "$ERROR_LINES"
    fi

    # Categorize errors
    echo ""
    echo "=== Error Categories ==="

    # Check for specific error types
    if grep -qi "relation.*does not exist" "$LOG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}  - Missing tables (relation does not exist)${NC}"
    fi

    if grep -qi "column.*does not exist" "$LOG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}  - Missing columns${NC}"
    fi

    if grep -qi "duplicate key" "$LOG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}  - Duplicate key errors${NC}"
    fi

    if grep -qi "constraint.*failed" "$LOG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}  - Constraint violations${NC}"
    fi

    if grep -qi "view.*depends" "$LOG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}  - Broken view dependencies${NC}"
    fi

    if grep -qi "module.*not found\|missing module" "$LOG_FILE" 2>/dev/null; then
        echo -e "${YELLOW}  - Missing modules${NC}"
    fi

    # Generate SQL fix suggestion
    {
        echo "-- SQL Fix for Odoo Upgrade Errors"
        echo "-- Run: $RUN_NUM"
        echo "-- Dump: $DUMP_FILE"
        echo "-- Target: Odoo $TARGET_VERSION"
        echo "-- Generated: $(date)"
        echo ""
        echo "-- ==========================================="
        echo "-- ERROR ANALYSIS"
        echo "-- ==========================================="
        echo "$ERROR_LINES"
        echo ""
        echo "-- ==========================================="
        echo "-- SQL FIXES"
        echo "-- ==========================================="
        echo ""
        echo "-- Add your SQL fixes below this line:"
        echo "--"
        echo "-- Example fixes:"
        echo "--"
        echo "-- -- Missing column fix"
        echo "-- ALTER TABLE table_name ADD COLUMN column_name TYPE;"
        echo "--"
        echo "-- -- Missing table fix"
        echo "-- CREATE TABLE table_name (id SERIAL PRIMARY KEY);"
        echo "--"
        echo "-- -- Disable broken view"
        echo "-- UPDATE ir_ui_view SET active = false WHERE name = 'view_name';"
        echo ""
    } > "$FIX_FILE"

    echo ""
    echo -e "${YELLOW}Fix file created: $FIX_FILE${NC}"

    # Create changes log
    {
        echo "# Upgrade Changes Log"
        echo ""
        echo "## Run: $RUN_NUM"
        echo "**Date:** $(date)"
        echo "**Dump:** $DUMP_FILE"
        echo "**Target:** Odoo $TARGET_VERSION"
        echo "**Status:** FAILED - Errors found"
        echo ""
        echo "## Errors Found"
        echo '```'
        echo "$ERROR_LINES"
        echo '```'
        echo ""
        echo "## Next Steps"
        echo "1. Analyze errors in $FIX_FILE"
        echo "2. Apply SQL fixes to database"
        echo "3. Export new database dump"
        echo "4. Re-run: ./odoo_upgrade.sh fixed_dump.sql $TARGET_VERSION"
    } > "$CHANGES_FILE"

    echo ""
    echo -e "${RED}Upgrade failed. Check $LOG_FILE for details${NC}"
    echo -e "${YELLOW}See $FIX_FILE for suggested fixes${NC}"
    exit 1

else
    echo -e "${GREEN}No errors found in log!${NC}"

    # Check for success indicators
    if grep -qi "success\|complete\|finished\|ready" "$LOG_FILE" 2>/dev/null; then
        echo -e "${GREEN}Upgrade completed successfully!${NC}"

        # Create success changes log
        {
            echo "# Upgrade Changes Log"
            echo ""
            echo "## Run: $RUN_NUM"
            echo "**Date:** $(date)"
            echo "**Dump:** $DUMP_FILE"
            echo "**Target:** Odoo $TARGET_VERSION"
            echo "**Status:** SUCCESS"
            echo ""
            echo "## Next Steps"
            echo "1. Download upgraded database"
            echo "2. Test in staging environment"
            echo "3. Deploy to production"
        } > "$CHANGES_FILE"

        echo -e "${GREEN}Upgrade completed successfully!${NC}"
        exit 0
    else
        # Check if upgrade is still in progress
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
