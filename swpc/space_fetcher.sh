#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           space_fetcher.sh
# Author:         Matha Goram
# Version:        1.1.0
# Updated:        2026-02-06
# Description:    Production wrapper for space_fetcher.py. Handles virtual
#                 environment activation, dependency validation, and logging.
# License:        MIT License
# Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
# -------------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -------------------------------------------------------------------------------

# --- ANSI Color Codes ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Configuration ---
SWPC="$HOME/PycharmProjects/noaa/swpc/"
VENV_PATH="${SWPC}../.venv/bin/activate"
PYTHON_SCRIPT="${SWPC}space_fetcher.py"
REQUIRED_CONFIG="${SWPC}config.toml"

# --- UI Functions ---
log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

header() {
    echo -e "${CYAN}==============================================${NC}"
    echo -e "${CYAN}   NOAA SPACE FETCHER - AUTOMATION WRAPPER    ${NC}"
    echo -e "${CYAN}==============================================${NC}"
}

# --- Validation Logic ---
check_environment() {
    log_info "Validating environment..."

    # Check if Python script exists
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        log_error "Target script '$PYTHON_SCRIPT' not found."
        exit 1
    fi

    # Check if config.toml exists
    if [[ ! -f "$REQUIRED_CONFIG" ]]; then
        log_error "Configuration file '$REQUIRED_CONFIG' is missing."
        exit 1
    fi

    # Check if venv exists
    if [[ ! -f "$VENV_PATH" ]]; then
        log_error "Virtual environment not found at: $VENV_PATH"
        exit 1
    fi
}

# --- Execution ---
main() {
    header

    check_environment

    # 1. Activate Virtual Environment
    log_info "Activating virtual environment..."
    # shellcheck disable=SC1091
    if source "$VENV_PATH"; then
        log_success "Environment active."
    else
        log_error "Critical failure during venv activation."
        exit 1
    fi

    # 2. Dependency Verification (Fast Check)
    if ! python3 -c "import requests, tomllib" &> /dev/null; then
        log_error "Missing Python dependencies. Please run 'pip install requests' in venv."
        exit 1
    fi

    # 3. Launch Python Script with Config Path Argument
    log_info "Initializing space_fetcher.py..."
    echo -e "${CYAN}----------------------------------------------${NC}"

    # Passing the config path as a command line parameter
    python3 "$PYTHON_SCRIPT" --config "$REQUIRED_CONFIG"
    EXIT_CODE=$?

    echo -e "${CYAN}----------------------------------------------${NC}"

    # 4. Final Status Reporting
    if [[ $EXIT_CODE -eq 0 ]]; then
        log_success "Space Fetcher completed successfully."
    else
        log_error "Space Fetcher exited with error code: $EXIT_CODE"
        log_warn "Check 'space_fetcher.log' for detailed stack traces."
        exit $EXIT_CODE
    fi
}

# Trigger Main
main