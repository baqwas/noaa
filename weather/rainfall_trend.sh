#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_trend.sh
# 🚀 DESCRIPTION   : Production wrapper for Node 22 weekly rainfall trends.
# 👤 AUTHOR        : Matha Goram
# 📅 VERSION       : 1.0.0
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================
# WORKFLOW:
# 1. Resolve absolute script paths for crontab compatibility.
# 2. Source the Python virtual environment (.venv).
# 3. Execute the rainfall_trend.py analysis engine.
# 4. Return status codes and log output for system monitoring.
# ==============================================================================

# --- Color Configuration & UI Icons ---
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
BLU='\033[0;34m'
NC='\033[0m'
CHECK="✅"
ERROR="❌"
INFO="ℹ️"

# --- Path Resolution ---
# Ensures the script functions correctly when called via absolute path in cron
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/rainfall_trend.py"
VENV_PATH="$SCRIPT_DIR/../.venv/bin/activate"

echo -e "${BLU}${INFO} Starting Node 22 Weekly Trend Task...${NC}"

# --- Environment Validation ---
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    echo -e "${RED}${ERROR} CRITICAL: Virtual environment not found at $VENV_PATH.${NC}"
    exit 1
fi

# --- Execution ---
# Standardizes execution to the python3 binary within the activated venv
python3 "$PY_SCRIPT"

# --- Post-Execution Summary ---
if [ $? -eq 0 ]; then
    echo -e "${GRN}${CHECK} Weekly Trend completed successfully.${NC}"
else
    echo -e "${RED}${ERROR} Weekly Trend failed. Check log for details.${NC}"
    exit 1
fi