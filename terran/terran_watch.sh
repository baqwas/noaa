#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_watch.sh
# 📝 DESCRIPTION   : Wrapper for Land Use monitoring. Handles cron/env/logs.
# 🔖 VERSION       : 1.1.0 (Iconified)
# 📅 UPDATED       : 2026-02-10
# 👤 AUTHOR        : Matha Goram
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -------------------------------------------------------------------------------

# --- 🎨 Configuration & Styling ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV="${PROJ_ROOT}/.venv/bin/activate"
CONFIG="${PROJ_ROOT}/swpc/config.toml"
SCRIPT="${PROJ_ROOT}/terran/terran_watch.py"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

echo -e "${BLUE}🚀 [$(date +'%Y-%m-%d %H:%M:%S')] Starting Terran (GIBS) Ingest...${NC}"

# --- 🛡️ Environment Validation ---
if [[ ! -f "$VENV" ]]; then
    echo -e "${RED}❌ [ERROR] Virtual Environment not found at: $VENV${NC}"
    exit 1
fi

# --- ⚙️ Execution ---
source "$VENV"
python3 "$SCRIPT" --config "$CONFIG"

# --- 🏁 Exit Status & Reporting ---
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ [SUCCESS] Terran update cycle completed successfully.${NC}"
else
    echo -e "${RED}❌ [FAIL] Terran update encountered errors. Check 📜 terran_watch.log${NC}"
    exit 1
fi
