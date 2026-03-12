#!/bin/bash
# -----------------------------------------------------------------------------
# 📅 NAME          : compile_all_daily.sh
# 🚀 DESCRIPTION   : Master Rendering Engine for the BeUlta Satellite Suite.
#                   RETAINS FULL MANIFEST with Universal Verified Cleanup.
# 👤 AUTHOR        : Matha Goram / BeUlta Suite
# 🔖 VERSION       : 1.2.0 (Global Storage Optimization)
# 📅 UPDATED       : 2026-03-11
# -----------------------------------------------------------------------------

# --- ⚙️ Global Paths & Environment ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
SATELLITE_ROOT="/home/reza/Videos/satellite"
LOG_DIR="${SATELLITE_ROOT}/logs"
PROC_SCRIPT="${PROJ_ROOT}/swpc/process_timelapse.sh"
VIS_FLAG="${LOG_DIR}/visibility_flag.txt"
SYSTEM_LOG="${LOG_DIR}/daily_render.log"

# --- 📧 Notification Settings ---
ADMIN_EMAIL="reza@parkcircus.org"
HOSTNAME=$(hostname)

# --- 🎨 UI Styling ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

# --- 🛰️ Full Target Registry ---
TARGETS=(
    "swpc|aurora_north"
    "swpc|aurora_south"
    "swpc|lasco_c3"
    "swpc|lasco_c2"
    "goes|goes_east"
    "goes|goes_west"
    "terran|land_use"
    "noaa/viirs|true_color"
    "noaa/viirs|night_lights"
    "noaa/viirs|surface_reflectance"
    "noaa/viirs|aerosols"
    "noaa/viirs|carbon_monoxide"
    "noaa/viirs|sea_surface_temp"
    "noaa/viirs|precipitable_water"
)

# Critical targets for SMTP alerting
CRITICAL_CHECKS=(
    "goes|goes_east"
    "swpc|lasco_c3"
    "noaa/viirs|true_color"
    "noaa/viirs|aerosols"
)

echo -e "${BLUE}>>> 🎬 Starting Universal Render & Purge Cycle [$(date)] <<<${NC}" | tee -a "$SYSTEM_LOG"

FAILED_TARGETS=()

for entry in "${TARGETS[@]}"; do
    IFS="|" read -r INST NAME <<< "$entry"

    IMG_DIR="${SATELLITE_ROOT}/${INST}/${NAME}/images"
    VID_DIR="${SATELLITE_ROOT}/${INST}/${NAME}/videos"

    # 1. Verify Image Availability
    if [[ -d "$IMG_DIR" && "$(ls -A "$IMG_DIR" 2>/dev/null)" ]]; then
        echo -e "${BLUE}🎞️  Processing: ${NAME}...${NC}"

        # 2. Execute rendering engine
        # Overlay logic for VIIRS is handled inside process_timelapse.sh
        if bash "$PROC_SCRIPT" "$IMG_DIR" "$VID_DIR" "$NAME" >> "$SYSTEM_LOG" 2>&1; then

            # --- 🧹 GLOBAL VERIFIED CLEANUP ---
            # Verify the MP4 for today exists before deleting anything
            DATE_STAMP=$(date +%Y-%m-%d)
            EXPECTED_VID="${VID_DIR}/${NAME}_${DATE_STAMP}.mp4"

            if [[ -f "$EXPECTED_VID" ]]; then
                echo -e "${GREEN}✅ Render Verified. Purging source images for ${NAME}...${NC}"
                rm -f "$IMG_DIR"/*.jpg "$IMG_DIR"/*.png
            else
                echo -e "${RED}⚠️  Render Verification Failed: ${EXPECTED_VID} not found. Images retained.${NC}"
                FAILED_TARGETS+=("$entry")
            fi
        else
            echo -e "${RED}❌ Render Engine Error: ${NAME}${NC}"
            FAILED_TARGETS+=("$entry")
        fi
    else
        echo -e "${YELLOW}⚠️  No frames found for ${NAME}. Skipping.${NC}"
    fi
done

# --- 📧 Alerts for Critical Failures ---
if [ ${#FAILED_TARGETS[@]} -ne 0 ]; then
    CRIT_LOG=""
    for fail in "${FAILED_TARGETS[@]}"; do
        for crit in "${CRITICAL_CHECKS[@]}"; do
            [[ "$fail" == "$crit" ]] && CRIT_LOG+="- $fail\n"
        done
    done

    if [[ -n "$CRIT_LOG" ]]; then
        echo -e "Subject: ❌ BeUlta Critical Purge/Render Failure\n\nFailed targets:\n$CRIT_LOG" | mail -s "BeUlta Alert: $HOSTNAME" "$ADMIN_EMAIL"
    fi
fi

echo -e "${BLUE}>>> ✅ Purge Cycle Finished [$(date)] <<<${NC}\n" | tee -a "$SYSTEM_LOG"
