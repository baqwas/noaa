#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Name:         run_goes_retrieval.sh
# Description:  Professional wrapper for the Unified GOES Retrieval System.
#               Manages environment checks, execution, and granular logging.
# Author:       Matha Goram
# Version:      1.0.0
# Updated:      2026-02-04
# License:      MIT License
# Copyright:    (c) 2026 ParkCircus Productions; All Rights Reserved
# -----------------------------------------------------------------------------

# --- Configuration & Styling ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- Paths ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
PYTHON_SCRIPT="${PROJ_ROOT}/goes/retrieve_goes.py"

# Standard UI Styling
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}[$(date)] Starting GOES Retrieval Cycle...${NC}"

if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}[ERROR] Virtual environment not found at $VENV${NC}"
    exit 1
fi

source "$VENV"
python3 "$PYTHON_SCRIPT"

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}[SUCCESS] Images retrieved. Check ${PROJ_ROOT}/goes/${NC}"
else
    echo -e "${RED}[FAILURE] Check logs for specific error details.${NC}"
    exit 1
fi