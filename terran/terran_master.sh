#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_master.sh
# 📝 DESCRIPTION   : Master Orchestrator - Ingest, Spatial Audit, & Housekeeping.
# 🔖 VERSION       : 1.2.0
# 📅 UPDATED       : 2026-03-10
# 👤 AUTHOR        : Matha Goram
# ⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
# -------------------------------------------------------------------------------
# [Summary]
# Acts as the primary entry point for the BeUlta Satellite Suite. It wraps the
# ingest engine (terran_watch.sh) and the computer vision quality gate
# (spatial_auditor.py). It also manages filesystem health by pruning old
# debug artifacts and preventing log bloat.
#
# [Workflow]
# 1. Ingest: Calls terran_watch.sh with optional temporal lookback.
# 2. Audit : If ingest is successful, runs HSV-based cloud masking.
# 3. Clean : Prunes .png masks older than 7 days from /vlm_audit/debug.
# 4. Logs  : Truncates master_cron.log if it exceeds 5MB.
#
# [Scripts]
# terran_watch.py: The "Worker" (Downloads)
# terran_watch.sh: The "Supervisor" (Environment wrapper)
# terran_master.sh: The "Director" (Orchestrates everything)
# -------------------------------------------------------------------------------

PROJ_ROOT="/home/reza/PycharmProjects/noaa"
LOG_FILE="/home/reza/Videos/satellite/terran/logs/master_cron.log"
LOOKBACK_VAL=${1:-0}
PURGE_DAYS=7
MAX_LOG_SIZE=5242880  # 5MB in bytes

# --- 🎨 Terminal Aesthetics ---
BLUE='\033[0;34m'; MAGENTA='\033[0;35m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

# --- 🧹 Housekeeping Functions ---
housekeeping() {
    local debug_dir="${PROJ_ROOT}/vlm_audit/debug"
    echo -e "${BLUE}🧹 Housekeeping: Purging debug masks older than ${PURGE_DAYS} days...${NC}"

    if [ -d "$debug_dir" ]; then
        find "$debug_dir" -name "*_mask.png" -type f -mtime +"$PURGE_DAYS" -delete
        echo -e "${GREEN}✅ Mask clean-up complete.${NC}"
    fi
}

log_management() {
    echo -e "${BLUE}📝 Log Management: Checking ${LOG_FILE}...${NC}"
    if [ -f "$LOG_FILE" ]; then
        local current_size=$(stat -c%s "$LOG_FILE")
        if [ "$current_size" -gt "$MAX_LOG_SIZE" ]; then
            echo -e "${BLUE}⚠️  Log exceeds 5MB. Truncating to last 1000 lines...${NC}"
            local temp_log=$(mktemp)
            tail -n 1000 "$LOG_FILE" > "$temp_log"
            cat "$temp_log" > "$LOG_FILE"
            rm "$temp_log"
            echo -e "${GREEN}✅ Log truncated.${NC}"
        else
            echo -e "${GREEN}✅ Log size within limits (${current_size} bytes).${NC}"
        fi
    fi
}

echo -e "${MAGENTA}====================================================${NC}"
echo -e "${MAGENTA}🛰️  TERRAN MASTER: PIPELINE ACTIVE (Lookback: ${LOOKBACK_VAL})${NC}"
echo -e "${MAGENTA}====================================================${NC}"

# 1. Run the Ingest Engine
# Note: Ensure the path to terran_watch.sh is correct relative to PROJ_ROOT
bash "${PROJ_ROOT}/terran/terran_watch.sh" "$LOOKBACK_VAL"

# 2. Run the Spatial Auditor
if [ $? -eq 0 ]; then
    echo -e "\n${BLUE}🔍 Starting Spatial Quality Audit...${NC}"
    "${PROJ_ROOT}/.venv/bin/python3" "${PROJ_ROOT}/vlm_audit/spatial_auditor.py"

    # 3. Trigger Maintenance
    echo -e ""
    housekeeping
    log_management
else
    echo -e "${RED}🔴 Ingest failed. Skipping Audit and Housekeeping.${NC}"
    exit 1
fi

echo -e "${MAGENTA}====================================================${NC}"
echo -e "${MAGENTA}🏁 Master Cycle Complete.${NC}"
