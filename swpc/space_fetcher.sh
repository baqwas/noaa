#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           space_fetcher.sh
# Author:         Matha Goram
# Version:        1.2.2
# Updated:        2026-02-27
# Description:    Production wrapper for space_fetcher.py. Handles virtual
#                 environment activation, dependency validation, and logging.
#                 Located in /swpc to prevent root directory decay.
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
# 🛠️  WORKFLOW      :
#    1. 🛠️  Dynamically resolve Project Root from script location.
#    2. 🔍  Validate Virtual Environment and Config at root level.
#    3. 🧪  Source Python Virtual Environment.
#    4. 🛰️  Execute space_fetcher.py using relative pathing.
# ==============================================================================

# --- ANSI Color Codes ---
# Restored per your requested version
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m';
BLUE='\033[0;34m'; NC='\033[0m'

# --- Dynamic Path Resolution ---
# Determines the root by looking one level up from the script's directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJ_ROOT=$(dirname "$SCRIPT_DIR")

VENV="${PROJ_ROOT}/.venv/bin/activate"
CONFIG="${PROJ_ROOT}/config.toml"
SCRIPT="${SCRIPT_DIR}/space_fetcher.py"

# --- 1. STRICT EXTERNAL LOGGING ---
# --- Production Logging Registry ---
# Redirects all telemetry to the requested video storage path
LOG_ROOT="/home/reza/Videos/satellite/swpc/logs"
LOG_FILE="${LOG_ROOT}/space_fetcher.log"

# --- 2. PRE-EMPTIVE DIRECTORY CREATION ---
# This MUST run before any redirection happens
# Ensure the log directory exists in the satellite storage path
mkdir -p "$LOG_ROOT"

# --- 3. DYNAMIC PATH RESOLUTION ---
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJ_ROOT=$(dirname "$SCRIPT_DIR")
VENV="${PROJ_ROOT}/.venv/bin/activate"
SCRIPT="${SCRIPT_DIR}/space_fetcher.py"



echo -e "${BLUE}📡 [$(date '+%Y-%m-%d %H:%M:%S')] Initializing NOAA Ingest Cycle...${NC}"

# 1. Environment Validation
if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}💀 CRITICAL: Virtual Environment not found at $VENV${NC}"
    exit 1
fi

if [[ ! -f "$CONFIG" ]]; then
    echo -e "${RED}💀 CRITICAL: Config manifest missing at $CONFIG${NC}"
    exit 1
fi

if [[ ! -d "$LOG_ROOT" ]]; then
    mkdir -p "$LOG_ROOT"
fi

# --- 4. EXECUTION ---
if [[ -f "$VENV" ]]; then
    source "$VENV"
    # Redirection is now safe because $LOG_ROOT is guaranteed to exist
    python3 "$SCRIPT" >> "$LOG_FILE" 2>&1
else
    echo "💀 Virtual environment missing at $VENV"
fi

# 3. Telemetry Output
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Cycle successful.${NC}"
else
    echo -e "${RED}❌ Cycle failed. Check $LOG_FILE${NC}"
    exit $EXIT_CODE
fi
