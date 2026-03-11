#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_watch.sh
# 📝 DESCRIPTION   : Unified wrapper for Land Use monitoring with lookback support.
# 🔖 VERSION       : 1.3.0
# 📅 UPDATED       : 2026-03-10
# 👤 AUTHOR        : Matha Goram
# -------------------------------------------------------------------------------

# --- 🎨 Configuration ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
PYTHON_BIN="${PROJ_ROOT}/.venv/bin/python3"
# Note: Ensure this path matches your local structure (terran/ or vlm_audit/ etc)
SCRIPT="${PROJ_ROOT}/terran/terran_watch.py"
CONFIG="${PROJ_ROOT}/config.toml"

# Archive log location for satellite imagery
ACTUAL_LOG="/home/reza/Videos/satellite/terran/logs/terran_watch.log"
LOCKFILE="/tmp/terran_watch.lock"

# --- 🎨 Terminal Aesthetics ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

# --- 🛰️ Argument Handling ---
# If a number is passed (e.g., ./terran_watch.sh 2), use it. Default to 0.
LOOKBACK_VAL=${1:-0}

echo -e "${BLUE}🚀 [$(date +'%Y-%m-%d %H:%M:%S')] Starting Terran Ingest Cycle...${NC}"
echo -e "${BLUE}📅 Temporal Offset: ${LOOKBACK_VAL} days lookback.${NC}"

# --- 🛡️ Guard ---
if [ -e "$LOCKFILE" ]; then
    echo -e "${RED}⚠️  Lockfile detected. Exiting overlapping run.${NC}"
    exit 1
fi
touch "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

# --- ⚙️ Execution ---
# Passing both the config path and the lookback value to the Python engine
"$PYTHON_BIN" "$SCRIPT" --config "$CONFIG" --lookback "$LOOKBACK_VAL"

# --- 🏁 Reporting ---
if [ $? -eq 0 ]; then
    echo -e "${GREEN}🟢 Terran Ingest completed successfully.${NC}"
else
    echo -e "${RED}🔴 Terran Ingest failed. Check SMTP alerts or logs.${NC}"
    exit 1
fi
