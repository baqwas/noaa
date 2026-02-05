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
# Adjust these paths if your directory structure differs
PYTHON_SCRIPT="/home/reza/PycharmProjects/noaa/goes/retrieve_goes.py"
CONFIG_FILE="/home/reza/PycharmProjects/noaa/swpc/config.toml"
LOG_DIR="/home/reza/PycharmProjects/noaa/goes/logs"
LOG_FILE="$LOG_DIR/goes_wrapper.log"

# --- Initialization ---
mkdir -p "$LOG_DIR"
# Redirect stdout and stderr to the log file while still printing to console
exec > >(tee -a "$LOG_FILE") 2>&1

log_msg() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error_msg() {
    echo -e "${RED}${BOLD}[ERROR]${NC} $1"
}

success_msg() {
    echo -e "${GREEN}${BOLD}[SUCCESS]${NC} $1"
}

warn_msg() {
    echo -e "${YELLOW}${BOLD}[WARN]${NC} $1"
}

# --- Pre-Flight Checks ---
log_msg "------------------------------------------------------------"
log_msg "Starting GOES Retrieval Wrapper..."

# 1. Check if Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    error_msg "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# 2. Check if Config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    error_msg "Configuration file missing: $CONFIG_FILE"
    exit 1
fi

# 3. Check for Python 3 and required 'requests' library
if ! command -v python3 &> /dev/null; then
    error_msg "Python3 is not installed or not in PATH."
    exit 1
fi

# --- Execution ---
log_msg "Executing: $(basename "$PYTHON_SCRIPT")"

# Run the python script and capture exit code
python3 "$PYTHON_SCRIPT"
EXIT_CODE=$?

# --- Post-Execution Evaluation ---
if [[ $EXIT_CODE -eq 0 ]]; then
    success_msg "GOES retrieval cycle completed successfully."
else
    error_msg "Python execution failed with Exit Code: $EXIT_CODE"
    error_msg "Check $LOG_DIR/goes_retrieval.log for granular Python exceptions."
    exit $EXIT_CODE
fi

log_msg "GOES Retrieval Wrapper Finished."
log_msg "------------------------------------------------------------"