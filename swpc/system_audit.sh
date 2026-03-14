#!/bin/bash
# ==============================================================================
# 🐕 SCRIPT      : system_audit.sh
# 🚀 DESCRIPTION : Master Forensic Orchestrator for the BeUlta Suite.
# 🔖 VERSION     : 1.9.0 (Watchdog Integration)
# 📅 UPDATED     : 2026-03-14
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
    echo "🛰️  BEULTA MASTER FORENSIC TRACE | $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================================================"
    echo "🏠 HOSTNAME   : $(hostname)"
    echo "📜 SOURCE     : system_audit.sh"
    echo "========================================================================"

    # 1. Video Egress Audit
    echo -e "\n🔍 STEP 1: OUTPUT VALIDATION & PERFORMANCE METRICS"
    $PYTHON_BIN "$SCRIPT_DIR/system_audit.py"

    # 2. Archive Inventory
    echo -e "\n📊 STEP 2: ARCHIVE INVENTORY"
    if [ -f "$PROJECT_ROOT/gibs/space_status.py" ]; then
        $PYTHON_BIN "$PROJECT_ROOT/gibs/space_status.py"
    fi

    # 3. Universal Storage Watchdog (The Cleanup Check)
    echo -e "\n🧹 STEP 3: STORAGE CLEANUP AUDIT (Watchdog)"
    if [ -f "$PROJECT_ROOT/utilities/universal_watchdog.py" ]; then
        $PYTHON_BIN "$PROJECT_ROOT/utilities/universal_watchdog.py"
    else
        echo "⚠️  [NOTICE] universal_watchdog.py not found. Skipping cleanup audit."
    fi

} > "$REPORT_LOG" 2>&1

# --- 📧 TELEMETRY DISPATCH ---
sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" "$REPORT_LOG" > "${REPORT_LOG}.clean"
mail -s "✨ BeUlta: Full System Audit [$(hostname)]" "$EMAIL_RECIPIENT" < "${REPORT_LOG}.clean"
rm "$REPORT_LOG" "${REPORT_LOG}.clean"
