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
# Resolves paths relative to script location for Crontab compatibility
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PY_SCRIPT="$SCRIPT_DIR/alerts_texas.py"
VENV_PATH="$PROJECT_ROOT/.venv/bin/activate"

# Leverage log path from config.toml
LOG_FILE="/home/reza/Videos/satellite/weather/logs/weather_alerts.log"

echo -e "${CYN}====================================================${NC}"
echo -e "${CYN}${INFO} Syncing Texas Alerts to MQTT Broker...${NC}"
echo -e "${CYN}====================================================${NC}"

{
    echo -e "--- Session Start: $(date) ---"

    if [ -f "$VENV_PATH" ]; then
        source "$VENV_PATH"
        echo -e "${GRN}✅ Virtual Environment activated.${NC}"
    else
        echo -e "${RED}${ERROR} CRITICAL: Virtual environment not found.${NC}"
        exit 1
    fi

    # Execute with unbuffered output for real-time logging
    python3 -u "$PY_SCRIPT"

    if [ $? -eq 0 ]; then
        echo -e "${GRN}✅ [SUCCESS] Alerts processed.${NC}"
        echo -e "--- Session End: Success ---"
    else
        echo -e "${RED}${ERROR} [FAIL] Dispatch encountered errors.${NC}"
        echo -e "--- Session End: Failure ---"
        exit 1
    fi
} | tee -a "$LOG_FILE"
echo -e "${CYN}====================================================${NC}"

