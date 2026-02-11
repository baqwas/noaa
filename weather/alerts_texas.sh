#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# ⚠️ NAME          : alerts_texas.sh
# 🔖 VERSION       : 1.1.0 (Iconified)
# -------------------------------------------------------------------------------

PROJ_DIR="/home/reza/PycharmProjects/noaa"
VENV_PATH="${PROJ_DIR}/.venv/bin/activate"
PYTHON_SCRIPT="${PROJ_DIR}/weather/alerts_texas.py"
LOG_FILE="/home/reza/Videos/satellite/noaa/logs/weather.log"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}📡 [$(date +'%H:%M:%S')] Syncing Texas Alerts to MQTT Broker...${NC}"

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    echo -e "${RED}❌ [ERROR] Venv not found at $VENV_PATH${NC}" | tee -a "$LOG_FILE"
    exit 1
fi

python3 -u "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ [SUCCESS] Alerts dispatched to raspbari7.${NC}"
else
    echo -e "${RED}❌ [FAIL] Dispatch failed. Check logs.${NC}"
fi

