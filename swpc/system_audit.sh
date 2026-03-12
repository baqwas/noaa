#!/bin/bash
# ==============================================================================
# 🐕 SCRIPT      : system_audit.sh
# 🚀 DESCRIPTION : Professional Shell Wrapper for the BeUlta Suite Watchdog.
#                  Orchestrates validation of SWPC, Terran, and GOES health.
#                  Now features Forensic Logging to support "Good News" tracking.
# 👤 AUTHOR      : Matha Goram
# 🔖 VERSION     : 1.6.0
# 📅 UPDATED     : 2026-03-11
# ⚖️ LICENSE     : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================
# 📑 VERSION HISTORY:
#     - 1.5.1: Initial Production Grade release.
#     - 1.6.0: FORENSIC UPDATE. Added centralized logging for audit results
#              and "Heartbeat" output capture for SWPC/Terran visibility.
# ==============================================================================

# --- ⚙️ ENVIRONMENT & PATHING ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"

# --- 📁 LOGGING CONFIGURATION ---
# We store the audit history in the SWPC root for easy admin access
LOG_DIR="/home/reza/Videos/satellite/swpc/logs"
LOG_FILE="$LOG_DIR/system_audit.log"
mkdir -p "$LOG_DIR"

# --- 🏃 EXECUTION ---
{
    echo "===================================================="
    echo "ℹ️  Initiating BeUlta Suite Forensic Audit..."
    echo "--- Session Start: $(date) ---"

    # 1. Activate Virtual Environment
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
        echo "📅 Environment: .venv Active"
    else
        echo "⚠️  Environment: System Default (VENV NOT FOUND)"
    fi

    # 2. Execute the Python Audit Engine
    # We pass the root to ensure it finds the master config.toml
    python3 "$SCRIPT_DIR/system_audit.py"

    AUDIT_EXIT=$?

    # 3. Handle Exit States
    if [ $AUDIT_EXIT -eq 0 ]; then
        echo "--- Session End: All Systems Humming ---"
    else
        echo "--- Session End: Finished with Critical Alerts ---"
    fi
    echo -e "====================================================\n"

} | tee -a "$LOG_FILE"

# The 'tee -a' command ensures the output goes to BOTH your terminal
# (if running manually) and the persistent log file for the suite.
