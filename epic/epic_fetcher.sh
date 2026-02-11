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

PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
CONFIG="${PROJ_ROOT}/swpc/config.toml"
SCRIPT="${PROJ_ROOT}/epic/epic_fetcher.py"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; NC='\033[0m'

echo -e "${BLUE}[$(date)] Starting EPIC Ingest...${NC}"

if [[ ! -f "$VENV" ]]; then
    echo "Error: Virtual Environment missing."
    exit 1
fi

source "$VENV"
python3 "$SCRIPT" --config "$CONFIG"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}EPIC images updated successfully.${NC}"
else
    echo -e "\033[0;31mEPIC Fetch failed. Check /Videos/satellite/epic/logs/epic_fetcher.log${NC}"
fi