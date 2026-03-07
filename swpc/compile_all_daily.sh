#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# 🎞️ NAME          : compile_all_daily.sh
# 🚀 DESCRIPTION   : Standardized Parallel Render Engine for Satellite Imagery.
#                   Ensures output aligns with System Audit nomenclature.
#                   Consolidated: Handles Aurora, GOES, and Terran Land-Use.
#                   Includes email alerts and persistent failure logging.
# 👤 AUTHOR        : Matha Goram
# 📅 UPDATED       : 2026-03-07
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- ⚙️ Configuration ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

PROJ_DIR="/home/reza/PycharmProjects/noaa"
PROC_SCRIPT="${PROJ_DIR}/swpc/process_timelapse.sh"
SATELLITE_ROOT="/home/reza/Videos/satellite"
SYSTEM_AUDIT_LOG="${SATELLITE_ROOT}/logs/system_audit.log"
EMAIL_RECIPIENT="reza@parkcircus.org"

# --- 🛰️ Standardized Target Registry ---
# Format: "Relative_Path_to_Instrument|Target_Name"
# Logic: Audit expects videos in $SATELLITE_ROOT/$Relative_Path/$Target_Name/videos/
TARGETS=(
    "swpc|aurora_north"
    "swpc|aurora_south"
    "swpc|solar_suvi_304"
    "swpc|cme_lasco_c3"
    "goes|goes_east"
    "goes|goes_west"
    "terran|land_use"
)

echo -e "${BLUE}>>> 🚀 Launching Standardized Render Engine <<<${NC}"

# Ensure log directory exists for the failure summary
mkdir -p "$(dirname "$SYSTEM_AUDIT_LOG")"

if [[ ! -f "$PROC_SCRIPT" ]]; then
    echo -e "${RED}❌ [FATAL] Processor script missing: $PROC_SCRIPT${NC}"
    exit 1
fi

# --- 🎥 Processing Loop ---
for entry in "${TARGETS[@]}"; do
    IFS="|" read -r REL_PATH TARGET_NAME <<< "$entry"

    IMG_DIR="${SATELLITE_ROOT}/${REL_PATH}/${TARGET_NAME}/images"
    VID_DIR="${SATELLITE_ROOT}/${REL_PATH}/${TARGET_NAME}/videos"

    # Ensure the auditor's expected directory exists
    mkdir -p "$VID_DIR"

    if [ -d "$IMG_DIR" ] && [ "$(ls -A "$IMG_DIR")" ]; then
        echo -e "${GREEN}🎥 Processing: ${TARGET_NAME}${NC}"
        # Execute processor (process_timelapse.sh handles individual frames and archival)
        bash "$PROC_SCRIPT" "$IMG_DIR" "$VID_DIR" "$TARGET_NAME"
    else
        echo -e "${RED}⚠️  Skipping ${TARGET_NAME}: No source images in $IMG_DIR${NC}"
    fi
done

# --- 📧 Post-Render Audit & Persistent Failure Logging ---
# Validates production of critical imagery videos
MISSING_TARGETS=""
CRITICAL_CHECKS=("goes|goes_east" "goes|goes_west" "terran|land_use")
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

for item in "${CRITICAL_CHECKS[@]}"; do
    IFS="|" read -r INST NAME <<< "$item"
    VID_PATH="${SATELLITE_ROOT}/${INST}/${NAME}/videos"

    # Check if an mp4 was created/modified in the last 90 minutes
    if ! find "$VID_PATH" -name "*.mp4" -mmin -90 | grep -q "."; then
        MISSING_TARGETS="${MISSING_TARGETS}\n- ${NAME}"
        # Log to the persistent system_audit.log for historical tracking
        echo "[${TIMESTAMP}] [RENDER_FAILURE] Target: ${NAME} | Path: ${INST}/${NAME}" >> "$SYSTEM_AUDIT_LOG"
    fi
done

# Send email alert if any critical renders failed
if [[ -n "$MISSING_TARGETS" ]]; then
    echo -e "Alert: Satellite Render Failure\n\nThe following critical videos were not generated today:${MISSING_TARGETS}\n\nThis event has been logged to system_audit.log." | \
    mail -s "⚠️ SATELLITE ALERT: Missing Daily Renders" "$EMAIL_RECIPIENT"
else
    # Log a successful health check to the audit log
    echo "[${TIMESTAMP}] [RENDER_HEALTH] All critical targets compiled successfully." >> "$SYSTEM_AUDIT_LOG"
fi

echo -e "${BLUE}>>> 🏁 Daily Compilation Cycle Complete <<<${NC}"
