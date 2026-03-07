#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_bulk.sh
# 🚀 DESCRIPTION   : Production wrapper for Regional Rainfall Data Sync.
#                   Synchronizes multiple stations with exponential backoff.
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.2.1
# 📅 UPDATED       : 2026-03-07
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

# --- 🎨 Color Configuration & UI Icons ---
CYN='\033[0;36m'; GRN='\033[0;32m'; RED='\033[0;31m'; YLW='\033[0;33m'; BLU='\033[0;34m'; NC='\033[0m'
CHECK="✅"; ERROR="❌"; INFO="ℹ️"; SYNC="🔄"

# --- 📁 Path Resolution (Absolute) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_bulk.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"

# Centralized Logging Redirection
LOG_DIR="/home/reza/Videos/satellite/weather/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/rainfall_sync.log"

echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${INFO} Initiating Regional Rainfall Sync...${NC}"
echo -e "${CYN}====================================================${NC}"

# Start execution block for dual logging
{
    echo -e "\n--- [ SESSION START: $(date) ] ---"

    # --- 🛡️ Validation: Virtual Environment ---
    if [[ -f "$VENV_PATH" ]]; then
        source "$VENV_PATH"
        echo -e "${GRN}${CHECK} Environment:${NC} Virtual Environment (.venv) Activated."
    else
        echo -e "${RED}${ERROR} CRITICAL:${NC} .venv not found at $VENV_PATH"
        exit 1
    fi

    # --- 🛡️ Validation: Python Engine ---
    if [[ ! -f "$PY_SCRIPT" ]]; then
        echo -e "${RED}${ERROR} CRITICAL:${NC} Logic engine missing: $PY_SCRIPT"
        exit 1
    fi

    # --- ⚡ Execution Gate ---
    echo -e "${BLU}${INFO} Syncing:${NC} Executing Regional Data Engine..."

    python3 -u "$PY_SCRIPT"
    EXIT_CODE=$?

    # --- 🏁 Post-Execution Summary ---
    echo -e "${CYN}----------------------------------------------------${NC}"
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GRN}${CHECK} SUCCESS:${NC} Regional Bulk Sync finished."
        echo -e "--- [ SESSION END: SUCCESS ] ---"
    else
        echo -e "${RED}${ERROR} FAILURE:${NC} Sync engine exited with error code: $EXIT_CODE"
        echo -e "--- [ SESSION END: FAILURE ] ---"
    fi
} 2>&1 | tee -a "$LOG_FILE"
