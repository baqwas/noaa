#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_review.sh
# 🚀 DESCRIPTION   : Production wrapper for 10-Year historical review.
#                   Designed for manual execution and Crontab compatibility.
# 👤 AUTHOR        : Matha Goram / Gemini
# 📅 VERSION       : 1.1.0
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================
# WORKFLOW:
# 1. Resolve absolute script paths to prevent directory context errors.
# 2. Source the Python virtual environment.
# 3. Execute the rainfall_review.py engine and log results.
# ==============================================================================

# --- 🎨 Color Configuration & UI Icons ---
RED='\033[0;31m'
GRN='\033[0;32m'
CYN='\033[0;36m'
YLW='\033[1;33m'
NC='\033[0m' # No Color

CHECK="📅"
ERROR="⚠️"
INFO="ℹ️"

# --- 📁 Path Resolution (Absolute) ---
# This ensures the script works regardless of where it is called from (Home or Cron)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_review.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"
LOG_FILE="$SCRIPT_DIR/rainfall_review.log"

# --- 🚀 Execution Header ---
echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${INFO} Initiating Monthly Historical Review...${NC}"
echo -e "${CYN}====================================================${NC}"

# Start logging to file while simultaneously printing to terminal
{
    echo -e "--- Session Start: $(date) ---"

    # --- 🛠️ Environment Validation ---
    if [ -f "$VENV_PATH" ]; then
        source "$VENV_PATH"
        echo -e "${GRN}${CHECK} Virtual Environment activated.${NC}"
    else
        echo -e "${RED}${ERROR} CRITICAL: Virtual environment not found at $VENV_PATH${NC}"
        exit 1
    fi

    # --- 🐍 Python Engine Execution ---
    echo -e "${CYN}${INFO} Running Analysis Engine: $(basename "$PY_SCRIPT")${NC}"

    # We use 'python3' from the activated venv
    python3 "$PY_SCRIPT"

    # --- 🏁 Post-Execution Summary ---
    if [ $? -eq 0 ]; then
        echo -e "${GRN}${CHECK} Monthly Review Dispatched Successfully.${NC}"
        echo -e "--- Session End: Success ---"
    else
        echo -e "${RED}${ERROR} Monthly Review encountered an exception. See logs above.${NC}"
        echo -e "--- Session End: Failure ---"
        exit 1
    fi
} | tee -a "$LOG_FILE"

echo -e "${CYN}====================================================${NC}"