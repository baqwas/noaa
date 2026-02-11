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

PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
CONFIG="${PROJ_ROOT}/swpc/config.toml"
SCRIPT="${PROJ_ROOT}/swpc/space_fetcher.py"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; NC='\033[0m'

echo -e "${BLUE}[$(date)] Starting Space Fetcher Cycle...${NC}"

if [[ ! -f "$VENV" ]]; then
    echo -e "Error: Virtual Environment not found."
    exit 1
fi

source "$VENV"
python3 "$SCRIPT" --config "$CONFIG"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Cycle successful.${NC}"
else
    echo -e "${RED}Cycle failed. Check instrument logs.${NC}"
fi