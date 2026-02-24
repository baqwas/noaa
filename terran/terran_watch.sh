#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_watch.sh
# 📝 DESCRIPTION   : Optimized wrapper for Land Use monitoring.
#                   Handles Cron-safe paths, environment locking, and logging.
# 🔖 VERSION       : 1.2.0 (Direct Exec & Lock)
# 📅 UPDATED       : 2026-02-23
# 👤 AUTHOR        : Matha Goram
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -------------------------------------------------------------------------------

# --- 🎨 Configuration & Styling ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
# Direct path to the python executable within the virtual environment
PYTHON_BIN="${PROJ_ROOT}/.venv/bin/python3"
# Ensure this path matches your actual config location (updated from swpc/ to terran/)
CONFIG="${PROJ_ROOT}/terran/config.toml"
SCRIPT="${PROJ_ROOT}/terran/terran_watch.py"
LOG_DIR="/home/reza/Videos/satellite/terran/logs"
LOCKFILE="/tmp/terran_watch.lock"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

echo -e "${BLUE}🚀 [$(date +'%Y-%m-%d %H:%M:%S')] Starting Terran (GIBS) Ingest...${NC}"

# --- 🛡️ Guard: Prevent Overlapping Runs ---
if [ -e "$LOCKFILE" ]; then
    echo -e "${RED}⚠️  [NOTICE] Script is already running or lockfile exists at $LOCKFILE. Exiting.${NC}"
    exit 1
fi

# Create lockfile and ensure it's removed on exit (even if the script crashes)
touch "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# --- 🛡️ Environment Validation ---
if [[ ! -f "$PYTHON_BIN" ]]; then
    echo -e "${RED}❌ [ERROR] Python binary not found at: $PYTHON_BIN${NC}"
    exit 1
fi

if [[ ! -f "$CONFIG" ]]; then
    echo -e "${RED}❌ [ERROR] Configuration file not found at: $CONFIG${NC}"
    exit 1
fi

# --- ⚙️ Execution ---
# Running directly via the venv python binary is more efficient for non-interactive scripts
"$PYTHON_BIN" "$SCRIPT" --config "$CONFIG"

# --- 🏁 Exit Status & Reporting ---
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ [SUCCESS] Terran update completed.${NC}"
else
    # Capture the last few lines of the log to send via email
    LOG_TAIL=$(tail -n 20 "${PROJ_ROOT}/logs/terran_watch.log")

    echo -e "Subject: ❌ Terran Watch Failure\n\nAlert: Collin County monitor failed.\n\nRecent Logs:\n$LOG_TAIL" | msmtp reza@parkcircus.org

    exit 1
fi