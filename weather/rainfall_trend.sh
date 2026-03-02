#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_trend.sh
# 🚀 DESCRIPTION   : Production wrapper for Node 22 weekly rainfall trends.
#                   Calculates variance against 7-day rolling averages.
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.2.0
# 📅 UPDATED       : 2026-03-01
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================
# 📜 MIT LICENSE:
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
# ==============================================================================
# 🛠️ PREREQUISITES:
#    1. Python 3.10+ installed in project root .venv
#    2. Valid 'config.toml' in the parent directory.
#    3. MariaDB service accessible for trend querying.
#
# 📋 WORKFLOW:
#    1. 📂 Resolve absolute paths for Crontab compatibility.
#    2. 🔌 Verify and source the Python Virtual Environment.
#    3. 🐍 Execute 'rainfall_trend.py' with error trapping.
#    4. 📊 Dispatch summary to terminal and local session logs.
# ==============================================================================

# --- 🎨 ANSI Color Palette & Icons ---
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m';
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

CHECK="✅"; ERROR="❌"; INFO="📈"; GEAR="⚙️"; WARN="⚠️"

# --- 📁 Path Resolution ---
# Ensures the script functions regardless of the calling working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_trend.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"
LOG_FILE="$SCRIPT_DIR/rainfall_trend.log"

# --- 🚀 User Interface Header ---
echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${INFO}  BEULTA SUITE: Weekly Rainfall Trend Engine${NC}"
echo -e "${CYN}====================================================${NC}"

# Open a execution block for dual-stream logging (Console + File)
{
    echo -e "\n--- [ SESSION START: $(date) ] ---"

    # --- 🛡️ Dependency Check: Virtual Env ---
    if [[ -f "$VENV_PATH" ]]; then
        source "$VENV_PATH"
        echo -e "${GRN}${CHECK} Environment:${NC} Virtual Environment (.venv) Activated."
    else
        echo -e "${RED}${ERROR} CRITICAL:${NC} Missing .venv at $VENV_PATH"
        echo -e "${YLW}${WARN} Action:${NC} Run 'python3 -m venv .venv && pip install -r requirements.txt'"
        exit 1
    fi

    # --- 🛡️ Dependency Check: Python Logic ---
    if [[ ! -f "$PY_SCRIPT" ]]; then
        echo -e "${RED}${ERROR} CRITICAL:${NC} Python engine missing: $PY_SCRIPT"
        exit 1
    fi

    # --- ⚡ Execution Gate ---
    echo -e "${BLU}${GEAR} Processing:${NC} Analyzing variance data via $(basename "$PY_SCRIPT")..."

    # Execute the python script and capture the exit status
    python3 "$PY_SCRIPT"
    EXIT_CODE=$?

    # --- 🏁 Error Message Summary & Exit Logic ---
    echo -e "${CYN}----------------------------------------------------${NC}"
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GRN}${CHECK} SUCCESS:${NC} Weekly Trend Analysis completed and published."
        echo -e "--- [ SESSION END: SUCCESS ] ---"
    else
        echo -e "${RED}${ERROR} FAILURE:${NC} Analysis engine exited with error code: $EXIT_CODE"
        echo -e "${YLW}${WARN} Note:${NC} Check database connectivity or NOAA API token status."
        echo -e "--- [ SESSION END: CRASHED ] ---"
        exit $EXIT_CODE
    fi

} 2>&1 | tee -a "$LOG_FILE"

echo -e "${CYN}====================================================${NC}"
