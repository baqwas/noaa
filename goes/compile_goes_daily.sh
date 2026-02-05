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

# --- Configuration & Styling ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# --- Paths & Variables ---
# Targets images from "yesterday" (e.g., 2026-02-03)
TARGET_DATE=$(date -d "yesterday" +%Y-%m-%d)
BASE_DATA_DIR="/home/reza/Videos/satellite/noaa"
LOG_DIR="/home/reza/Videos/satellite/noaa/logs"
LOG_FILE="$LOG_DIR/goes_daily_compile.log"
EMAIL_RECEIVER="reza@parkcircus.org"

# List of satellite subdirectories to process
SATELLITES=("goes-east" "goes-west")

# --- Initialization ---
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

log_msg() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error_msg() { echo -e "${RED}${BOLD}[ERROR]${NC} $1"; }
success_msg() { echo -e "${GREEN}${BOLD}[SUCCESS]${NC} $1"; }

log_msg "------------------------------------------------------------"
log_msg "Starting Daily GOES Compilation for Date: $TARGET_DATE"

for SAT in "${SATELLITES[@]}"; do
    DIR="$BASE_DATA_DIR/$SAT"
    VIDEO_DIR="$DIR/videos"
    OUTPUT_FILE="$VIDEO_DIR/${SAT}_${TARGET_DATE}.mp4"

    log_msg "Processing: $SAT"

    # Verify directory exists
    if [[ ! -d "$DIR" ]]; then
        error_msg "Directory not found: $DIR. Skipping."
        continue
    fi

    mkdir -p "$VIDEO_DIR"

    # Identify files from the target date.
    # Assumes filename format from retrieve_goes_unified.py: SATNAME_YYYY-MM-DDTHH:MM:SS.jpg
    FILES=$(find "$DIR" -maxdepth 1 -name "*${TARGET_DATE}*.jpg" | sort)

    if [[ -z "$FILES" ]]; then
        log_msg "No images found for $SAT on $TARGET_DATE. Skipping."
        continue
    fi

    log_msg "Compiling video for $SAT..."

    # FFmpeg: Compile images for the specific date
    # Uses 'scale' filter for compatibility and 'yuv420p' for standard playback
    ffmpeg -f image2 -pattern_type glob -i "$DIR/*${TARGET_DATE}*.jpg" \
           -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
           -c:v libx264 -pix_fmt yuv420p -r 15 "$OUTPUT_FILE" -y -loglevel error

    if [[ $? -eq 0 ]]; then
        success_msg "Video created: $OUTPUT_FILE"

        # Granular Cleanup: Delete only the files that were just processed
        log_msg "Purging source images for $TARGET_DATE..."
        find "$DIR" -maxdepth 1 -name "*${TARGET_DATE}*.jpg" -delete
        success_msg "Cleanup complete for $SAT."
    else
        error_msg "FFmpeg failed for $SAT."
        echo "Daily GOES compilation failed for $SAT on $(date)" | mail -s "GOES Video Failure: $SAT" "$EMAIL_RECEIVER"
    fi
done

log_msg "Daily GOES Compilation Finished."
log_msg "------------------------------------------------------------"