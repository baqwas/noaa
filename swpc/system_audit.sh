#!/bin/bash
# ==============================================================================
# 🐕 SCRIPT      : system_audit.sh
# 🚀 DESCRIPTION : Master Forensic Orchestrator for the BeUlta Suite.
# 🔖 VERSION     : 2.0.0
# 📅 UPDATED     : 2026-03-14
# ==============================================================================
# 📑 VERSION HISTORY:
#     - 1.6.0: Added centralized logging for audit results.
#     - 1.8.0: PKM Metrics Edition; added hostname/script origin reporting.
#     - 2.0.0: HARD-GATE Edition; integrated test_core_contract.py prelude.
#
# ⚠️ ERROR MESSAGES SUMMARY:
#     - [EXIT 1] Contract Break: core_service.py failed validation.
#     - [EXIT 2] Path Error: VENV or Script directory not found.
#     - [WARN]  Telemetry Failure: mail utility not found or SMTP timeout.
#
# ⚖️ LICENSE     : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================

# --- ⚙️ ENVIRONMENT & PATHING ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_PATH/bin/python"
REPORT_LOG="/tmp/beulta_full_audit.log"
EMAIL_RECIPIENT="reza@parkcircus.org"

{
    echo "========================================================================"
    echo "🛰️  BEULTA MASTER FORENSIC TRACE"
    echo "========================================================================"
    echo "🏠 HOSTNAME   : $(hostname)"
    echo "📜 SOURCE     : system_audit.sh"
    echo "========================================================================"

    # 1. Activate Virtual Environment
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
    fi

    # --- 🧪 STEP 0: THE CONTRACT AUDIT (Hard Gate) ---
    echo -e "\n🧪 STEP 0: CORE SERVICE CONTRACT VALIDATION"
    echo "------------------------------------------------------------------------"
    $PYTHON_BIN "$PROJECT_ROOT/utilities/test_core_contract.py"
    CONTRACT_EXIT=$?

    if [ $CONTRACT_EXIT -ne 0 ]; then
        echo -e "\n🚨 [CRITICAL FAILURE] Core Service Contract is BROKEN."
        echo "Aborting audit to prevent production regression."
        echo "Please troubleshoot core_service.py before continuing."
        # We still send the report so you know WHY it stopped.
    else
        echo -e "✅ Contract Verified. Proceeding with Production Audit..."

        # 2. Video Egress Audit & PKM
        echo -e "\n🔍 STEP 1: OUTPUT VALIDATION & PERFORMANCE METRICS"
        $PYTHON_BIN "$SCRIPT_DIR/system_audit.py"

        # 3. Archive Inventory
        echo -e "\n📊 STEP 2: ARCHIVE INVENTORY"
        if [ -f "$PROJECT_ROOT/gibs/space_status.py" ]; then
            $PYTHON_BIN "$PROJECT_ROOT/gibs/space_status.py"
        fi

        # 4. Storage Watchdog (The Cleanup Check)
        echo -e "\n🧹 STEP 3: STORAGE CLEANUP AUDIT (Watchdog)"
        if [ -f "$PROJECT_ROOT/utilities/universal_watchdog.py" ]; then
            $PYTHON_BIN "$PROJECT_ROOT/utilities/universal_watchdog.py"
        fi
    fi

} > "$REPORT_LOG" 2>&1

# --- 📧 TELEMETRY DISPATCH ---
# Strip ANSI codes and send the combined result
sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" "$REPORT_LOG" > "${REPORT_LOG}.clean"

# Determine subject based on the contract exit code
if [ $CONTRACT_EXIT -ne 0 ]; then
    SUBJ="🚨 BeUlta: CONTRACT BREAK DETECTED [$(hostname)]"
else
    SUBJ="✨ BeUlta: Full System Audit [$(hostname)]"
fi

mail -s "$SUBJ" "$EMAIL_RECIPIENT" < "${REPORT_LOG}.clean"
rm "$REPORT_LOG" "${REPORT_LOG}.clean"
