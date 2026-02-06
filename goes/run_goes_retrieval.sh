#!/bin/bash
# -----------------------------------------------------------------------------
# Name:         run_goes_retrieval.sh
# Description:  Wrapper for retrieve_goes.py. Manages 10-minute fetch cycles
#               with system-level pre-flight checks and logging.
# Version:      1.0.0
# License:      MIT License
# Copyright:    (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -----------------------------------------------------------------------------

# --- Styling & Configuration ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
PYTHON_EXEC="/usr/bin/python3"
SCRIPT_DIR="/home/reza/PycharmProjects/noaa/goes/"
PY_SCRIPT="$SCRIPT_DIR/retrieve_goes.py"
LOG_FILE="$SCRIPT_DIR/logs/goes_wrapper.log"

# --- Initialization ---
mkdir -p "$(dirname "$LOG_FILE")"
exec > >(tee -a "$LOG_FILE") 2>&1

log() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

log "Starting GOES Retrieval Cycle..."

# --- Pre-Flight Checks ---
[[ -f "$PY_SCRIPT" ]] || err "Python script not found at $PY_SCRIPT"
command -v "$PYTHON_EXEC" >/dev/null 2>&1 || err "Python interpreter not found."

# --- Execution ---
cd "$SCRIPT_DIR" || err "Could not change to directory $SCRIPT_DIR"
"$PYTHON_EXEC" "$PY_SCRIPT"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "${GREEN}Success:${NC} Retrieval cycle finished."
else
    log "${RED}Failure:${NC} Python exited with code $EXIT_CODE"
    exit $EXIT_CODE
fi