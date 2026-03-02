#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_review.sh
# 🚀 DESCRIPTION   : Production wrapper for 10-Year historical review.
#                   Analyzes rainfall patterns and generates visual reports.
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
#    1. Python 3.10+ with Matplotlib and Pandas.
#    2. Configured MariaDB with historical rainfall_records.
#    3. CoreService utility accessible in project root.
#
# 📋 WORKFLOW:
#    1. 📂 Resolve absolute script paths for reliable Crontab execution.
#    2. 🔌 Activate Python Virtual Environment (.venv).
#    3. 🐍 Execute 'rainfall_review.py' analysis engine.
#    4. 📧 Dispatch generated PNG reports via secure SMTP.
#    5. 📝 Log session telemetry for audit trails.
# ==============================================================================

# --- 🎨 ANSI Color Palette & Icons ---
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m';
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

CHECK="📅"; ERROR="⚠️"; INFO="ℹ️"; GEAR="⚙️"; MAIL="📧"

# --- 📁 Path Resolution ---
# Locates resources relative to the script's physical location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_review.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"
LOG_FILE="$SCRIPT_DIR/rainfall_review.log"

# --- 🚀 User Interface Header ---
echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${INFO}  BEULTA SUITE: 10-Year Historical Review Engine  ${NC}"
echo -e "${CYN}====================================================${NC}"

# Start execution block for dual logging (Tee outputs to terminal and log file)
{
    echo -e "\n--- [ SESSION START: $(date) ] ---"

    # --- 🛡️ Validation: Virtual Environment ---
    if [[ -f "$VENV_PATH" ]]; then
        source "$VENV_PATH"
        echo -e "${GRN}${CHECK} Environment:${NC} Virtual Environment (.venv) Activated."
    else
        echo -e "${RED}${ERROR} CRITICAL:${NC} Missing .venv at $VENV_PATH"
        exit 1
    fi

    # --- 🛡️ Validation: Python Engine ---
    if [[ ! -f "$PY_SCRIPT" ]]; then
        echo -e "${RED}${ERROR} CRITICAL:${NC} Analysis engine missing: $PY_SCRIPT"
        exit 1
    fi

    # --- ⚡ Execution Gate ---
    echo -e "${BLU}${GEAR} Processing:${NC} Compiling historical data via $(basename "$PY_SCRIPT")..."

    python3 "$PY_SCRIPT"
    EXIT_CODE=$?

    # --- 🏁 Post-Execution Summary ---
    echo -e "${CYN}----------------------------------------------------${NC}"
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GRN}${CHECK} SUCCESS:${NC} Historical report generated and ${MAIL} dispatched."
        echo -e "--- [ SESSION END: SUCCESS ] ---"
    else
        echo -e "${RED}${ERROR} FAILURE:${NC} Review engine exited with error code: $EXIT_CODE"
        echo -e "${YLW}🔍 Check 'rainfall_review.log' for stack trace details.${NC}"
        echo -e "--- [ SESSION END: CRASHED ] ---"
        exit $EXIT_CODE
    fi

} 2>&1 | tee -a "$LOG_FILE"

echo -e "${CYN}====================================================${NC}"
