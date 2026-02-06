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
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m';
BLUE='\033[0;34m'; NC='\033[0m'

# Absolute Configuration Paths
WORKING_DIR="${HOME}/PycharmProjects/noaa/weather"
SWPC_DIR="${HOME}/PycharmProjects/noaa/swpc"
# Updated to use absolute path for standard NOAA environment consistency
VENV="${HOME}/PycharmProjects/noaa/.venv/bin/activate"
CONFIG="${SWPC_DIR}/config.toml"
PYTHON_SCRIPT="${WORKING_DIR}/alerts_texas.py"

echo -e "${YELLOW}>>> Checking for Active Texas Weather Alerts... <<<${NC}"

# Check for environment before running
if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}[ERROR] Virtual environment not found at $VENV${NC}"
    exit 1
fi

# Activate Virtual Environment
source "$VENV"

# Execute Python script
python3 "$PYTHON_SCRIPT" --config "$CONFIG"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Check complete. Logs stored in ~/Videos/satellite/weather/logs/${NC}"
else
    echo -e "${RED}[ERROR] Alert check failed with exit code $EXIT_CODE. Check logs.${NC}"
fi