#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           alerts_texas.sh
# Description:    Wrapper for Texas Weather Alerts monitoring.
# -------------------------------------------------------------------------------

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m';
BLUE='\033[0;34m'; NC='\033[0m'

# Absolute Configuration Paths
WORKING_DIR="${HOME}/PycharmProjects/noaa/weather"
SWPC_DIR="${HOME}/PycharmProjects/noaa/swpc"
VENV="${SWPC_DIR}/../.venv/bin/activate"
CONFIG="${SWPC_DIR}/config.toml"
PYTHON_SCRIPT="${WORKING_DIR}/alerts_texas.py"

echo -e "${YELLOW}>>> Checking for Active Texas Weather Alerts... <<<${NC}"

# Check for environment before running
if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}[ERROR] Virtual environment not found at $VENV${NC}"
    exit 1
fi

source "$VENV"

# Execute Python script
python3 "$PYTHON_SCRIPT" --config "$CONFIG"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Check complete. Logs stored in ~/Videos/satellite/weather/logs/${NC}"
else
    echo -e "${RED}[ERROR] Alert check failed with exit code $EXIT_CODE. Check logs.${NC}"
fi