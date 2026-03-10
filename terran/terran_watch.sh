#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_watch.sh
# 📝 DESCRIPTION   : Unified wrapper for Land Use monitoring.
# 🔖 VERSION       : 1.2.5
# 📅 UPDATED       : 2026-03-09
# 👤 AUTHOR        : Matha Goram
# -------------------------------------------------------------------------------

# --- 🎨 Configuration ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
PYTHON_BIN="${PROJ_ROOT}/.venv/bin/python3"
SCRIPT="${PROJ_ROOT}/terran/terran_watch.py"
CONFIG="${PROJ_ROOT}/config.toml"

# Archive log location for satellite imagery
ACTUAL_LOG="/home/reza/Videos/satellite/terran/logs/terran_watch.log"
LOCKFILE="/tmp/terran_watch.lock"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}🚀 [$(date +'%Y-%m-%d %H:%M:%S')] Starting Terran Ingest...${NC}"

# --- 🛡️ Guard ---
if [ -e "$LOCKFILE" ]; then
    echo -e "${RED}⚠️  Lockfile detected. Exiting overlapping run.${NC}"; exit 1
fi
touch "$LOCKFILE"; trap 'rm -f "$LOCKFILE"' EXIT

# --- ⚙️ Execution ---
"$PYTHON_BIN" "$SCRIPT" --config "$CONFIG"

# --- 🏁 Reporting ---
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ [SUCCESS] Terran update completed.${NC}"
else
    # Improved log capture for Collin County alerts
    LOG_TAIL=$(tail -n 20 "$ACTUAL_LOG" 2>/dev/null || echo "Log missing at $ACTUAL_LOG")
    echo -e "Subject: ❌ Terran Failure\n\nAlert: Collin County monitor failed.\n\n$LOG_TAIL" | msmtp reza@parkcircus.org
    exit 1
fi
