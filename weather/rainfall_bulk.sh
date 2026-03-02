#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_bulk.sh
# 🚀 DESCRIPTION   : Production wrapper for Regional Rainfall Data Sync.
#                   Synchronizes multiple stations with exponential backoff.
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
#    1. Python 3.10+ installed in project root .venv.
#    2. MariaDB instance with 'rainfall_records' table schema.
#    3. NOAA_TOKEN exported in environment or .env file.
#
# 📋 WORKFLOW:
#    1. 📂 Resolve absolute paths for Crontab/Systemd compatibility.
#    2. 🔌 Activate Virtual Environment (.venv).
#    3. 🐍 Execute 'rainfall_bulk.py' regional sync engine.
#    4. 📡 Broadcast sync telemetry via MQTT.
#    5. 📝 Archive session results to 'rainfall_sync.log'.
# ==============================================================================

# --- 🎨 ANSI Color Palette & Icons ---
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m';
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

CHECK="✅"; ERROR="❌"; INFO="📡"; GEAR="⚙️"; SYNC="🔄"

# --- 📁 Path Resolution ---
# Locates resources relative to the script location to ensure portability
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_bulk.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"
LOG_FILE="$SCRIPT_DIR/rainfall_sync.log"

# --- 🚀 User Interface Header ---
echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${GEAR}  BEULTA SUITE: Regional Bulk Rainfall Sync  ${NC}"
echo -e "${CYN}====================================================${NC}"

# Open a dual-stream logging block (Console + File)
{
    echo -e "\n--- [ SESSION START: $(date) ] ---"

    # --- 🛡️ Validation: Virtual Environment ---
    if [[ -f "$VENV_PATH" ]]; then
        source "$VENV_PATH"
        echo -e "${GRN}${CHECK} Environment:${NC} Virtual Environment (.venv) Activated."
    else
        echo -e "${RED}${ERROR} CRITICAL:${NC} .venv not found at $VENV_PATH"
        echo -e "${YLW}${SYNC} Action:${NC} Execute 'pip install -r requirements.txt' in project root."
        exit 1
    fi

    # --- 🛡️ Validation: Python Engine ---
    if [[ ! -f "$PY_SCRIPT" ]]; then
        echo -e "${RED}${ERROR} CRITICAL:${NC} Logic engine missing: $PY_SCRIPT"
        exit 1
    fi

    # --- ⚡ Execution Gate ---
    echo -e "${BLU}${INFO} Syncing:${NC} Executing Regional Data Engine..."

    python3 "$PY_SCRIPT"
    EXIT_CODE=$?

    # --- 🏁 Post-Execution Summary ---
    echo -e "${CYN}----------------------------------------------------${NC}"
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GRN}${CHECK} SUCCESS:${NC} Regional Bulk Sync finished. Data archived to MariaDB."
        echo -e "--- [ SESSION END: SUCCESS ] ---"
    else
        echo -e "${RED}${ERROR} FAILURE:${NC} Sync engine exited with error code: $EXIT_CODE"
        echo -e "${YLW}${SYNC} Retrying via Crontab in next scheduled window.${NC}"
        echo -e "--- [ SESSION END: CRASHED ] ---"
        exit $EXIT_CODE
    fi

} 2>&1 | tee -a "$LOG_FILE"

echo -e "${CYN}====================================================${NC}"