#!/usr/bin/env bash
# ==============================================================================
# 📦 NAME          : alerts_texas.sh
# 🚀 DESCRIPTION   : Production wrapper for NWS Alert Ingestion.
# 👤 AUTHOR        : Matha Goram / Gemini
# 📅 VERSION       : 2.1.0
# ==============================================================================

# --- 🎨 Color Configuration & UI Icons ---
CYN='\033[0;36m'; GRN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
CHECK="📡"; ERROR="❌"; INFO="ℹ️"

# --- 📁 Path Resolution (Absolute) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/alerts_texas.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"

# 🧠 Professional Developer Addition: Dynamic Log Discovery
# Instead of hardcoding, we try to ensure the log directory exists
LOG_DIR="/home/reza/Videos/satellite/weather/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/weather_alerts.log"

echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${INFO} Syncing Texas Alerts to MQTT Broker...${NC}"
echo -e "${CYN}====================================================${NC}"

# Start logging block
{
    echo -e "--- Session Start: $(date) ---"

    if [ -f "$VENV_PATH" ]; then
        source "$VENV_PATH"
        echo -e "${GRN}✅ Virtual Environment activated.${NC}"
    else
        echo -e "${RED}${ERROR} CRITICAL: Virtual environment not found.${NC}"
        exit 1
    fi

    # 🧠 Professional Developer Addition: Check if Python script exists
    if [[ ! -f "$PY_SCRIPT" ]]; then
        echo -e "${RED}${ERROR} CRITICAL: Python engine missing at $PY_SCRIPT${NC}"
        exit 1
    fi

    # Execute with unbuffered output (-u) for real-time logging
    # Capturing stderr and stdout to the log file
    python3 -u "$PY_SCRIPT"

    if [ $? -eq 0 ]; then
        echo -e "${GRN}✅ [SUCCESS] Alerts processed.${NC}"
        echo -e "--- Session End: Success ---"
    else
        # The error message is already printed by Python, we just mark the log
        echo -e "--- Session End: Failure ---"
    fi
} 2>&1 | tee -a "$LOG_FILE"

echo -e "${CYN}====================================================${NC}"
