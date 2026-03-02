#!/bin/bash
# -----------------------------------------------------------------------------
# 🎞️ NAME          : compile_all_daily.sh
# 🚀 DESCRIPTION   : Standardized Parallel Render Engine for Satellite Imagery.
#                   Ensures output aligns with System Audit nomenclature.
# 👤 AUTHOR        : Matha Goram
# 📅 UPDATED       : 2026-03-01
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- ⚙️ Configuration ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

PROJ_DIR="/home/reza/PycharmProjects/noaa"
PROC_SCRIPT="${PROJ_DIR}/swpc/process_timelapse.sh"
SATELLITE_ROOT="/home/reza/Videos/satellite"

# --- 🛰️ Standardized Target Registry ---
# Format: "Relative_Path_to_Instrument|Target_Name"
# Logic: Audit expects videos in $SATELLITE_ROOT/$Relative_Path/$Target_Name/videos/
TARGETS=(
    "swpc|aurora_north"
    "swpc|aurora_south"
    "swpc|solar_suvi_304"
    "swpc|cme_lasco_c3"
    "noaa|goes_east"
    "noaa|goes_west"
)

echo -e "${BLUE}>>> 🚀 Launching Standardized Render Engine <<<${NC}"

if [[ ! -f "$PROC_SCRIPT" ]]; then
    echo -e "${RED}❌ [FATAL] Processor script missing: $PROC_SCRIPT${NC}"
    exit 1
fi

# Process targets
for entry in "${TARGETS[@]}"; do
    IFS="|" read -r REL_PATH TARGET_NAME <<< "$entry"

    IMG_DIR="${SATELLITE_ROOT}/${REL_PATH}/${TARGET_NAME}/images"
    VID_DIR="${SATELLITE_ROOT}/${REL_PATH}/${TARGET_NAME}/videos"

    # Ensure the auditor's expected directory exists
    mkdir -p "$VID_DIR"

    if [ -d "$IMG_DIR" ] && [ "$(ls -A "$IMG_DIR")" ]; then
        echo -e "${GREEN}🎥 Processing: ${TARGET_NAME}${NC}"
        # Execute processor (Assuming process_timelapse.sh handles individual frames)
        bash "$PROC_SCRIPT" "$IMG_DIR" "$VID_DIR" "$TARGET_NAME"
    else
        echo -e "${RED}⚠️  Skipping ${TARGET_NAME}: No source images in $IMG_DIR${NC}"
    fi
done

echo -e "${BLUE}>>> 🏁 Daily Compilation Cycle Complete <<<${NC}"