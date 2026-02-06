#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           terran_watch.sh
# Description:    Wrapper for Land Use monitoring. Handles cron/env/logs.
# -------------------------------------------------------------------------------

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m';
BLUE='\033[0;34m'; NC='\033[0m'

# Paths
TERRAN_DIR="$HOME/PycharmProjects/noaa/terran"
SWPC_DIR="$HOME/PycharmProjects/noaa/swpc"
VENV="${SWPC_DIR}/../.venv/bin/activate"
CONFIG="${SWPC_DIR}/config.toml"

log_msg() { echo -e "${BLUE}[TERRAN]${NC} $1"; }

main() {
    echo -e "${YELLOW}>>> Starting Collin County Land Use Monitor <<<${NC}"

    if [[ ! -f "$VENV" ]]; then
        echo -e "${RED}Error: Venv not found at $VENV${NC}"
        exit 1
    fi

    source "$VENV"

    python3 "${TERRAN_DIR}/terran_watch.py" --config "$CONFIG"
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}Update Successful.${NC}"
    else
        echo -e "${RED}Update Failed. Check logs.${NC}"
    fi
}

main