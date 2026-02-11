#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           space_status.sh
# Description:    Envelope wrapper for space_status.py. Ensures VENV activation
#                 for cron execution and passes the master configuration path.
# -------------------------------------------------------------------------------

# --- Absolute Paths ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
CONFIG="${PROJ_ROOT}/swpc/config.toml"
SCRIPT="${PROJ_ROOT}/swpc/space_status.py"

# --- UI Colors ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}[ERROR] Virtual environment not found at $VENV${NC}"
    exit 1
fi

# Activate environment and run dashboard
source "$VENV"
python3 "$SCRIPT" --config "$CONFIG"