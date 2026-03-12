#!/bin/bash
# ===============================================================================
# 🚀 PROJECT      : BeUlta Satellite Suite
# 📦 MODULE       : gibs_ingest.sh
# 👥 ROLE         : Forensic Orchestrator & Error Auditor
# 🔖 VERSION      : 1.6.0
# 📅 LAST UPDATE  : 2026-03-11
# ===============================================================================
# 📑 VERSION HISTORY:
#     - 1.5.1: Path-agnostic resolution and basic step execution.
#     - 1.5.2: Added gibs_cleanup.py integration.
#     - 1.6.0: FORENSIC UPDATE. Implemented stdout/stderr capture with
#              automated substantive email reporting (URL, HTTP Codes, Payloads).
# ===============================================================================

# --- 1. DYNAMIC PATH DISCOVERY ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [[ "$SCRIPT_DIR" == *"gibs"* ]]; then
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
REPORT_LOG="/tmp/beulta_forensics.log"
EMAIL_RECIPIENT="reza@parkcircus.org"

# --- 2. THE FORENSIC REPORTER ---
# Captures script name, step, and the actual error payload from the log.
send_forensic_report() {
    local STEP_NAME=$1
    local SCRIPT_NAME=$2
    local EXIT_CODE=$3

    {
        echo "🚨 BeUlta CRITICAL FAILURE REPORT"
        echo "================================="
        echo "TIMESTAMP    : $(date)"
        echo "SCRIPT       : $SCRIPT_NAME"
        echo "STEP         : $STEP_NAME"
        echo "EXIT CODE    : $EXIT_CODE"
        echo "ACTION TAKEN : Pipeline Aborted / Admin Notified"
        echo -e "\n--- SUBSTANTIVE DIAGNOSTIC TRACE ---"
        echo "---------------------------------------"
        # Grabs the last 25 lines of the log (where the URL and HTTP errors live)
        cat "$REPORT_LOG" | tail -n 25
        echo "---------------------------------------"
        echo -e "\n[End of Forensic Trace]"
    } > /tmp/beulta_mail_body.txt

    mail -s "🚀 BeUlta: CRITICAL ($STEP_NAME Failure)" "$EMAIL_RECIPIENT" < /tmp/beulta_mail_body.txt
}

# --- 3. EXECUTION PIPELINE ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

cd "$PROJECT_ROOT" || exit 1

# --- Step 1: NASA Health Check ---
echo -e "${CYAN}🩺 Step 1: NASA GIBS Health Check${NC}"
$PYTHON_BIN gibs/satellite_health_check.py > "$REPORT_LOG" 2>&1
HEALTH_EXIT=$?

if [ $HEALTH_EXIT -eq 1 ]; then
    send_forensic_report "Metadata Audit" "satellite_health_check.py" $HEALTH_EXIT
    exit 1
fi

# --- Step 2: Maintenance ---
echo -e "🧹 Step 2: Pruning assets older than 30 days..."
$PYTHON_BIN gibs/gibs_cleanup.py >> "$REPORT_LOG" 2>&1

# --- Step 3: Ingest Data ---
echo -e "${CYAN}🛰️  Step 3: GIBS Ingest Started${NC}"
$PYTHON_BIN gibs/gibs_fetcher.py > "$REPORT_LOG" 2>&1
INGEST_EXIT=$?

if [ $INGEST_EXIT -ne 0 ]; then
    # This will now include the "FAILED_URL" and "HTTP_CODE" printed by fetcher.py
    send_forensic_report "Data Ingest" "gibs_fetcher.py" $INGEST_EXIT
    exit 1
fi

# --- Step 4: Dashboard Generation ---
echo -e "${CYAN}🖥️  Step 4: Dashboard Generation${NC}"
$PYTHON_BIN gibs/gen_dashboard.py > "$REPORT_LOG" 2>&1
DASH_EXIT=$?

if [ $DASH_EXIT -ne 0 ]; then
    send_forensic_report "Dashboard Assembly" "gen_dashboard.py" $DASH_EXIT
fi

echo -e "\n${GREEN}🏁 BeUlta Pipeline Complete.${NC}"
