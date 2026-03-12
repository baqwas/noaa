#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Name:         retrieve_goes.sh
# Version:      1.1.0 (Standardized Wrapper)
# -----------------------------------------------------------------------------
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
PYTHON_SCRIPT="${PROJ_ROOT}/goes/retrieve_goes.py"
LOG_FILE="/home/reza/Videos/satellite/goes/logs/retrieval_shell.log"

echo -e "${BLUE}[$(date)] Initializing GOES Retrieval Cycle...${NC}"

if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}[ERROR] Virtual environment missing at $VENV${NC}"
    exit 1
fi

source "$VENV"
# Redirect output to log file for forensic history
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ GOES Retrieval Successful.${NC}"
else
    echo -e "${RED}❌ GOES Retrieval Failed. Check logs.${NC}"
    exit 1
fi
