#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_bulk.sh
# 🚀 DESCRIPTION   : Production wrapper for Regional Rainfall Data Sync.
#                   Handles environment activation, logging, and error traps.
# 👤 AUTHOR        : Matha Goram
# 📅 VERSION       : 1.1.0
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================
# WORKFLOW:
# 1. Resolve absolute script paths to prevent directory context errors.
# 2. Verify and source the Python virtual environment (.venv).
# 3. Execute the rainfall_bulk.py engine with real-time log redirection.
# 4. Exit with appropriate status codes for automation system hooks.
# ==============================================================================

# --- 🎨 Color Configuration & UI Icons ---
RED='\033[0;31m'
GRN='\033[0;32m'
CYN='\033[0;36m'
YLW='\033[1;33m'
NC='\033[0m' # No Color

CHECK="✅"
ERROR="❌"
INFO="📡"
GEAR="⚙️"

# --- 📁 Path Resolution (Absolute) ---
# Resolves paths relative to the script location for crontab compatibility
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_bulk.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"

# Log file is directed to the path specified in your solution standards
LOG_FILE="/home/reza/Videos/satellite/weather/logs/rainfall_bulk.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# --- 🚀 Execution Header ---
echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${GEAR} Initiating Regional Bulk Rainfall Sync...${NC}"
echo -e "${CYN}====================================================${NC}"

# Open a block for logging to both file and stdout
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
    if [ -f "$PY_SCRIPT" ]; then
        echo -e "${CYN}${INFO} Executing Data Engine: $(basename "$PY_SCRIPT")${NC}"

        # Execute the python script
        python3 "$PY_SCRIPT"

        # Capture the exit code of the python process
        PY_EXIT_CODE=$?
    else
        echo -e "${RED}${ERROR} CRITICAL: Python engine not found at $PY_SCRIPT${NC}"
        exit 1
    fi

    # --- 🏁 Post-Execution Summary ---
    if [ $PY_EXIT_CODE -eq 0 ]; then
        echo -e "${GRN}${CHECK} Bulk Synchronization completed successfully.${NC}"
        echo -e "--- Session End: Success ---"
    else
        echo -e "${RED}${ERROR} Sync Engine encountered an exception (Code: $PY_EXIT_CODE).${NC}"
        echo -e "--- Session End: Failure ---"
        exit $PY_EXIT_CODE
    fi
} | tee -a "$LOG_FILE"

echo -e "${CYN}====================================================${NC}"