#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : rainfall_review.sh
# 🚀 DESCRIPTION   : Production wrapper for 10-Year historical review.
#                   Analyzes rainfall patterns and generates visual reports.
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.2.1
# 📅 UPDATED       : 2026-03-07
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================

# --- 🎨 Color Configuration & UI Icons ---
CYN='\033[0;36m'; GRN='\033[0;32m'; RED='\033[0;31m'; YLW='\033[0;33m'; BLU='\033[0;34m'; NC='\033[0m'
CHECK="✅"; ERROR="❌"; GEAR="⚙️"; MAIL="📧"

# --- 📁 Path Resolution ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/rainfall_review.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"

# Centralized Logging Redirection
LOG_DIR="/home/reza/Videos/satellite/weather/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/rainfall_review.log"

echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${GEAR} Initiating Rainfall Historical Review...${NC}"
echo -e "${CYN}====================================================${NC}"

{
    echo -e "\n--- [ SESSION START: $(date) ] ---"

    if [[ -f "$VENV_PATH" ]]; then
        source "$VENV_PATH"
        echo -e "${GRN}${CHECK} Environment:${NC} Virtual Environment (.venv) Activated."
    else
        echo -e "${RED}${ERROR} CRITICAL:${NC} Missing .venv at $VENV_PATH"
        exit 1
    fi

    if [[ ! -f "$PY_SCRIPT" ]]; then
        echo -e "${RED}${ERROR} CRITICAL:${NC} Analysis engine missing: $PY_SCRIPT"
        exit 1
    fi

    echo -e "${BLU}${GEAR} Processing:${NC} Compiling historical data..."

    python3 -u "$PY_SCRIPT"
    EXIT_CODE=$?

    echo -e "${CYN}----------------------------------------------------${NC}"
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GRN}${CHECK} SUCCESS:${NC} Historical report generated and ${MAIL} dispatched."
        echo -e "--- [ SESSION END: SUCCESS ] ---"
    else
        echo -e "${RED}${ERROR} FAILURE:${NC} Review engine exited with error code: $EXIT_CODE"
        echo -e "--- [ SESSION END: FAILURE ] ---"
    fi
} 2>&1 | tee -a "$LOG_FILE"
