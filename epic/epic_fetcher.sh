#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           epic_fetcher.sh
# Author:         Matha Goram
# Version:        1.0.0
# Updated:        2026-02-06
# Description:    Production wrapper for epic_fetcher.py. Manages environment
#                 activation and passes absolute config paths.
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
# Leveraging your existing variable style for consistency
EPIC_ROOT="$HOME/PycharmProjects/noaa/epic/"
SWPC_ROOT="$HOME/PycharmProjects/noaa/swpc/"
VENV_PATH="${SWPC_ROOT}../.venv/bin/activate" #
PYTHON_SCRIPT="${EPIC_ROOT}epic_fetcher.py"
REQUIRED_CONFIG="${SWPC_ROOT}config.toml"     #

# --- UI Functions ---
log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

header() {
    echo -e "${CYAN}==============================================${NC}"
    echo -e "${CYAN}   NASA EPIC FETCHER - AUTOMATION WRAPPER     ${NC}"
    echo -e "${CYAN}==============================================${NC}"
}

# --- Validation Logic ---
check_environment() {
    log_info "Validating project structure..."

    # Check if Python script exists at defined path
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        log_error "Target script not found: $PYTHON_SCRIPT"
        exit 1
    fi

    # Check if the unified config.toml exists in the swpc folder
    if [[ ! -f "$REQUIRED_CONFIG" ]]; then
        log_error "Global configuration missing: $REQUIRED_CONFIG"
        exit 1
    fi

    # Check if venv exists
    if [[ ! -f "$VENV_PATH" ]]; then
        log_error "Virtual environment activation script missing: $VENV_PATH"
        exit 1
    fi
}

# --- Execution ---
main() {
    header

    check_environment

    # 1. Activate Virtual Environment
    log_info "Sourcing virtual environment..."
    # shellcheck disable=SC1091
    if source "$VENV_PATH"; then #
        log_success "Environment successfully activated."
    else
        log_error "Failed to source the virtual environment."
        exit 1
    fi

    # 2. Dependency Check
    if ! python3 -c "import requests, tomllib" &> /dev/null; then
        log_error "Required libraries (requests/tomllib) not found in venv."
        exit 1
    fi

    # 3. Launch Python Script
    log_info "Executing EPIC ingest process..."
    echo -e "${CYAN}----------------------------------------------${NC}"

    # Passing the REQUIRED_CONFIG as a command line parameter
    python3 "$PYTHON_SCRIPT" --config "$REQUIRED_CONFIG"
    EXIT_CODE=$?

    echo -e "${CYAN}----------------------------------------------${NC}"

    # 4. Final Status Reporting
    if [[ $EXIT_CODE -eq 0 ]]; then
        log_success "EPIC Fetcher completed successfully."
    else
        log_error "EPIC Fetcher failed with exit code: $EXIT_CODE"
        log_warn "Check logs in ~/noaa/epic/logs/ for details."
        exit $EXIT_CODE
    fi
}

# Invoke Main
main