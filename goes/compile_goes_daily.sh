#!/bin/bash
# -----------------------------------------------------------------------------
# 🎞️ NAME         : compile_goes_daily.sh
# 👤 AUTHOR       : Matha Goram
# 📝 DESCRIPTION  : Processes daily GOES imagery into MP4 time-lapses.
#                  Enforces underscore nomenclature and unified logging.
#
# 🛠️ WORKFLOW     :
#    1. Navigate to goes_east and goes_west /images/ directories.
#    2. Check for existence of JPG assets.
#    3. Invoke FFMPEG to render daily MP4 in /videos/ subfolder.
#    4. Upon successful render, purge source imagery.
#    5. Log all output to centralized goes_operations.log.
# -----------------------------------------------------------------------------

# --- Configuration & Styling ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

# --- Paths ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
PYTHON_SCRIPT="${PROJ_ROOT}/goes/retrieve_goes.py"

echo -e "${BLUE}[$(date)] Starting GOES Retrieval Cycle...${NC}"

# Direct check for virtual environment existence
if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}[ERROR] Virtual environment not found at $VENV${NC}"
    exit 1
fi

source "$VENV"

# Direct execution check
if python3 "$PYTHON_SCRIPT"; then
    echo -e "${GREEN}[SUCCESS] Images retrieved. Check /home/reza/Videos/satellite/goes/${NC}"
else
    echo -e "${RED}[FAILURE] Check logs for specific error details.${NC}"
    exit 1
fi