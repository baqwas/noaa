#!/bin/bash
# -----------------------------------------------------------------------------
# 📅 NAME          : compile_all_daily.sh
# 🚀 DESCRIPTION   : Master Rendering Engine for the BeUlta Satellite Suite.
#                   Orchestrates the conversion of daily image sequences into
#                   timelapse videos for GOES, SWPC, and NASA GIBS targets.
#                   Includes an automated SMTP audit via Postfix relay.
#                   Now supports conditional "HAZY DAY" overlays via
#                   visibility_audit.py integration.
# 👤 AUTHOR        : Matha Goram / BeUlta Suite
# 📅 UPDATED       : 2026-03-07
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
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

# --- 🛰️ Standardized Target Registry ---
# Format: "Instrument_Subdir|Target_Name"
TARGETS=(
    "swpc|aurora_north"
    "swpc|aurora_south"
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

# --- 🛡️ Critical Audit List ---
# These targets MUST succeed. Failure triggers an alert via Postfix/Bezaman relay.
CRITICAL_CHECKS=(
    "goes|goes_east"
    "noaa/viirs|true_color"
    "noaa/viirs|aerosols"
    "noaa/viirs|sea_surface_temp"
)

echo -e "${BLUE}>>> 🎬 Starting BeUlta Master Render Sequence [$(date)] <<<${NC}" | tee -a "$SYSTEM_LOG"

# --- 🚀 Processing Loop ---
FAILED_TARGETS=()

for entry in "${TARGETS[@]}"; do
    IFS="|" read -r INST NAME <<< "$entry"

    IMG_DIR="${SATELLITE_ROOT}/${INST}/${NAME}/images"
    VID_DIR="${SATELLITE_ROOT}/${INST}/${NAME}/videos"

    echo -e "${BLUE}🔍 Auditing Target: ${NC}${NAME} (${INST})"

    # 1. Check for Visibility Flags (Atmospheric Interference Audit)
    # If the Python audit detected high AOD, we set the overlay for the render engine.
    OVERLAY_TEXT=""
    if [[ "$INST" == "noaa/viirs" && -f "$VIS_FLAG" ]]; then
        echo -e "${YELLOW}☁️  Low Visibility Detected: Queuing 'HAZY DAY' overlay.${NC}"
        OVERLAY_TEXT="HAZY DAY"
    fi

    # 2. Verify Image Availability
    if [[ -d "$IMG_DIR" && "$(ls -A "$IMG_DIR" 2>/dev/null)" ]]; then
        echo -e "${GREEN}✅ Images found. Initiating render...${NC}"

        # Execute the processing engine
        # Arguments: 1:Source, 2:Destination, 3:Target_Name, 4:Overlay_Text
        if bash "$PROC_SCRIPT" "$IMG_DIR" "$VID_DIR" "$NAME" "$OVERLAY_TEXT" >> "$SYSTEM_LOG" 2>&1; then
            echo -e "${GREEN}✨ Render Complete: ${NAME}${NC}"
        else
            echo -e "${RED}❌ Render Failed: ${NAME}${NC}"
            FAILED_TARGETS+=("$entry")
        fi
    else
        echo -e "${YELLOW}⚠️  No frames found for ${NAME}. Skipping.${NC}"
        # If it was a critical target, log it as a failure
        for crit in "${CRITICAL_CHECKS[@]}"; do
            if [[ "$crit" == "$entry" ]]; then
                FAILED_TARGETS+=("$entry")
            fi
        done
    fi
done

# --- 📧 Post-Processing Audit & Alerts ---
if [ ${#FAILED_TARGETS[@]} -ne 0 ]; then
    # Filter only critical failures for email notification
    CRIT_FAILURES=()
    for fail in "${FAILED_TARGETS[@]}"; do
        for crit in "${CRITICAL_CHECKS[@]}"; do
            if [[ "$fail" == "$crit" ]]; then
                CRIT_FAILURES+=("$fail")
            fi
        done
    done

    if [ ${#CRIT_FAILURES[@]} -ne 0 ]; then
        echo -e "${RED}🚨 CRITICAL FAILURE: Dispatching alert to ${ADMIN_EMAIL}${NC}"

        MSG_BODY="BeUlta Satellite Suite: Critical Render Failure\n\n"
        MSG_BODY+="Timestamp: $(date)\n"
        MSG_BODY+="Host: $HOSTNAME\n\n"
        MSG_BODY+="The following critical targets failed to render or had missing data:\n"
        for f in "${CRIT_FAILURES[@]}"; do MSG_BODY+="- $f\n"; done
        MSG_BODY+="\nPlease check the logs at: $SYSTEM_LOG"

        echo -e "$MSG_BODY" | mail -s "❌ BeUlta Render Alert: Critical Failure on $HOSTNAME" "$ADMIN_EMAIL"
    fi
fi

echo -e "${BLUE}>>> ✅ Master Render Sequence Finished [$(date)] <<<${NC}\n" | tee -a "$SYSTEM_LOG"
