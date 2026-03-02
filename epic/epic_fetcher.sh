#!/usr/bin/env bash
# ==============================================================================
# 🚀 NAME          : epic_fetcher.sh
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.5.0
# 📝 DESCRIPTION   : Orchestration wrapper for the EPIC DSCOVR ingest engine.
#                    Manages environment sourcing and error-trapping.
# ------------------------------------------------------------------------------
# 🛠️  WORKFLOW      :
#    1. 🛠️  Resolve Project Root from script location.
#    2. 🔍  Validate Python Virtual Environment & script existence.
#    3. 🧪  Source VENV to ensure dependencies (requests, dotenv) are met.
#    4. 📥  Execute epic_fetcher.py and log output to the archive root.
#
# 📋 PREREQUISITES :
#    - Python 3.11+ Virtual Environment at ../.venv
#    - Valid config.toml at project root.
#
# 📜 LICENSE       : MIT License
# ==============================================================================

# --- 🖥️ DESKTOP NOTIFICATION SUPPORT (CRON COMPATIBILITY) ---
# Cron doesn't know about your desktop. We must point it to your session.
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

# --- ANSI Color Palette ---
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'

# --- Dynamic Path Resolution ---
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJ_ROOT=$(dirname "$SCRIPT_DIR")
VENV="${PROJ_ROOT}/.venv/bin/activate"
PYTHON_SCRIPT="${SCRIPT_DIR}/epic_fetcher.py"
LOG_DIR="/home/reza/Videos/satellite/epic/logs"

# Ensure log directory exists
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/fetch_$(date +%Y%m).log"

echo -e "${BLUE}🌍 [$(date '+%Y-%m-%d %H:%M:%S')] Initializing EPIC Ingest Cycle...${NC}"

# 1. Validation Logic
if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}💀 CRITICAL: Virtual Environment missing at $VENV${NC}"
    # Fallback alert if python can't run
    notify-send "🛰️ EPIC Error" "VENV Missing. Check log: $LOG_FILE" --urgency=critical
    exit 1
fi

# 2. Execution logic
source "$VENV"
# Note: we use ${PIPESTATUS[0]} later to check the Python exit code specifically
python3 "$PYTHON_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

# 3. Final Status Handling
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ EPIC Ingest cycle finished successfully.${NC}"
else
    echo -e "${RED}❌ EPIC Ingest cycle failed. Check $LOG_FILE${NC}"
    exit 1
fi
