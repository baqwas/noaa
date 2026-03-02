#!/bin/bash
# ==============================================================================
# 🐕 SCRIPT      : system_audit.sh
# 🚀 DESCRIPTION : Professional Shell Wrapper for the BeUlta Suite Watchdog.
#                  Orchestrates the validation of GOES (goes_east/west) and
#                  SWPC infrastructure health.
# 👤 AUTHOR      : Matha Goram
# 📅 UPDATED     : 2026-03-01
# ⚖️ LICENSE     : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================

# --- ⚙️ ENVIRONMENT & PATHING ---
# Ensure we are operating from the script's own directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"

# --- 🏃 EXECUTION ---
echo "===================================================="
echo "ℹ️  Initiating BeUlta Suite System Audit..."
echo "--- Session Start: $(date) ---"
echo "📂 Standardized Nomenclature: goes_east | goes_west"

# 1. Activate Virtual Environment if present
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "📅 Virtual Environment: Active (.venv)"
else
    echo "⚠️  Virtual Environment not found. Using system environment."
fi

# 2. Execute the Python Audit Engine
# Note: system_audit.py dynamically resolves config.toml from the root.
python3 "$SCRIPT_DIR/system_audit.py"

# 3. Handle Exit States
if [ $? -eq 0 ]; then
    echo "--- Session End: Success ---"
else
    echo "--- Session End: Finished with Errors/Warnings ---"
fi

# 4. Graceful Cleanup
if [[ "$VIRTUAL_ENV" != "" ]]; then
    deactivate
fi
echo "===================================================="
