#!/bin/bash
# -----------------------------------------------------------------------------
# Name:         compile_goes_daily.sh
# Description:  Daily video compiler for GOES-East and GOES-West imagery.
#               Targets imagery from the previous day, creates a timestamped
#               MP4, and purges source images upon success.
# Author:       Matha Goram
# Version:      1.0.0
# Updated:      2026-02-04
# License:      MIT License
# Copyright:    (c) 2026 ParkCircus Productions; All Rights Reserved
# -----------------------------------------------------------------------------

# --- UI Styling (Consistency with NOAA Project Standards) ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- Paths ---
DATE_STAMP=$(date +%Y-%m-%d)
BASE_PATH="/home/reza/Videos/satellite/noaa"

# --- Helper Functions ---
log_event() {
    local TYPE=$1
    local MSG=$2
    case "$TYPE" in
        "INFO") echo -e "${BLUE}[INFO]${NC} $MSG" ;;
        "SUCCESS") echo -e "${GREEN}${BOLD}[SUCCESS]${NC} $MSG" ;;
        "WARN") echo -e "${YELLOW}[WARN]${NC} $MSG" ;;
        "ERROR") echo -e "${RED}${BOLD}[ERROR]${NC} $MSG" ;;
    esac
}

echo -e "${BLUE}${BOLD}>>> Starting Daily GOES Video Compilation Cycle ($DATE_STAMP) <<<${NC}\n"

# --- Processing Loop ---
for SAT in "goes-east" "goes-west"; do
    IMG_DIR="${BASE_PATH}/${SAT}/images"
    VID_DIR="${BASE_PATH}/${SAT}/videos"
    LOG_FILE="${BASE_PATH}/${SAT}/logs/video_compile.log"

    mkdir -p "$VID_DIR"

    log_event "INFO" "Processing ${SAT}..."

    # 1. Check if images exist
    if [ -d "$IMG_DIR" ] && [ "$(ls -A "$IMG_DIR")" ]; then
        OUTPUT_FILE="${VID_DIR}/${SAT}_${DATE_STAMP}.mp4"

        # 2. Execute FFMPEG
        # Using -y to overwrite if a run failed earlier today
        ffmpeg -y -framerate 10 -pattern_type glob -i "${IMG_DIR}/*.jpg" \
               -c:v libx264 -pix_fmt yuv420p "$OUTPUT_FILE" >> "$LOG_FILE" 2>&1

        if [[ $? -eq 0 ]]; then
            log_event "SUCCESS" "Video created: $(basename "$OUTPUT_FILE")"

            # 3. Purge daily images upon success
            rm "${IMG_DIR}"/*.jpg
            log_event "INFO" "Cleaned ${SAT}/images directory."
        else
            log_event "ERROR" "FFMPEG failed for ${SAT}. Check logs: $LOG_FILE"
        fi
    else
        log_event "WARN" "No source images found in $IMG_DIR. Skipping."
    fi
    echo "------------------------------------------------------------"
done

echo -e "\n${GREEN}${BOLD}Compilation cycle finished.${NC}"
