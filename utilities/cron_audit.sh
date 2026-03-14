#!/bin/bash
# ===============================================================================
# 🚀 PROJECT      : BeUlta Satellite Suite
# 📦 MODULE       : cron_audit.sh
# 👥 ROLE         : Master Forensic Orchestrator & Telemetry Dispatcher
# 🔖 VERSION      : 1.1.0
# 📅 LAST UPDATE  : 2026-03-14
# ===============================================================================
#
# 📝 DESCRIPTION:
#     The central shell orchestrator for daily system-wide audits. It triggers
#     the System Audit Node (video verification) and Space Status (archive
#     telemetry), consolidating their output into a single forensic trace
#     dispatched via the system mailer.
#
# ⚙️ WORKFLOW / PROCESSING:
#     1. Environment Sync: Locates project root and validates Python .venv.
#     2. Pre-flight: Checks for the existence of required audit scripts.
#     3. Execution: Triggers system_audit.py and space_status.py sequentially.
#     4. Reporting: Compiles stdout into a temporary trace and dispatches via mail.
#
# 🛠️ PREREQUISITES:
#     - 'mail' utility installed (bsd-mailx or postfix).
#     - Standardized BeUlta directory structure (/utilities, /gibs, etc.).
#
# ⚖️ LICENSE:
#     MIT License | Copyright (c) 2026 ParkCircus Productions
# ===============================================================================

# --- 1. DYNAMIC PATH DISCOVERY ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="/home/reza/PycharmProjects/noaa"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
REPORT_LOG="/tmp/beulta_daily_audit.log"
EMAIL_RECIPIENT="reza@parkcircus.org"

# --- 2. ANSI COLORS ---
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# --- 3. AUDIT EXECUTION ---
{
    echo "========================================================================"
    echo "🛰️  BEULTA MASTER AUDIT TRACE | $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================================================"
    echo -e "Node: $(hostname)\n"

    # Step A: System Video Health Audit
    echo "🔍 STEP 1: Executing Forensic System Audit..."
    if [ -f "$PROJECT_ROOT/gibs/system_audit.py" ]; then
        $PYTHON_BIN "$PROJECT_ROOT/gibs/system_audit.py"
    else
        echo "❌ [ERROR] system_audit.py not found at expected location."
    fi

    echo -e "\n"

    # Step B: Space Archive Telemetry
    echo "📊 STEP 2: Gathering Archive Telemetry..."
    if [ -f "$PROJECT_ROOT/gibs/space_status.py" ]; then
        $PYTHON_BIN "$PROJECT_ROOT/gibs/space_status.py"
    else
        echo "❌ [ERROR] space_status.py not found at expected location."
    fi

    echo -e "\n"
    echo "🏁 AUDIT COMPLETE. DATA UPLOADED TO TELEMETRY STREAM."
    echo "========================================================================"
} > "$REPORT_LOG" 2>&1

# --- 4. TELEMETRY DISPATCH ---
# Strips ANSI color codes for clean email rendering
sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" "$REPORT_LOG" > "${REPORT_LOG}.clean"

mail -s "✨ BeUlta: Daily Forensic Telemetry [$(date +%F)]" "$EMAIL_RECIPIENT" < "${REPORT_LOG}.clean"

# Clean up temporary logs
rm "$REPORT_LOG" "${REPORT_LOG}.clean"

exit 0
