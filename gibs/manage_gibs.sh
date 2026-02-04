#!/bin/bash
# -----------------------------------------------------------------------------
# Name:         manage_gibs.sh
# Description:  Professional Lifecycle Manager for NASA GIBS Image Retrieval.
#               Handles daily execution of Python fetchers, monthly animation
#               compilation with text overlays, and automated housekeeping.
# Location:     ~/noaa/gibs/manage_gibs.sh
# License:      MIT License
# Copyright:    (c) 2026
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -----------------------------------------------------------------------------
# Troubleshooting:
# Check,Command to Verify,Why it matters
# Permissions,ls -l ~/noaa/gibs/manage_gibs.sh,Must have -rwxr-xr-x (executable).
# FFmpeg Path,which ffmpeg,"Cron may need the full path (e.g., /usr/bin/ffmpeg)."
# Environment,"grep ""SHELL"" <(crontab -l)",Ensure SHELL=/bin/bash is at the top of your crontab.

# --- Configuration & Styling ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Absolute Paths
PY_SCRIPT="$HOME/PycharmProjects/noaa/gibs/gibs_fetcher.py"
LOG_DIR="$HOME/Videos/satellite/gibs/logs"
DATA_ROOT="$HOME/Videos/satellite/gibs/data"
LOG_FILE="$LOG_DIR/bash_manager.log"

# Standard Font Path (Adjust for RHEL/CentOS if necessary to /usr/share/fonts/dejavu/...)
FONT_PATH="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --- Initialization ---
mkdir -p "$LOG_DIR"
# Redirect stdout and stderr to both the log file and the terminal
exec > >(tee -a "$LOG_FILE") 2>&1

log_msg() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error_msg() { echo -e "${RED}${BOLD}[ERROR]${NC} $1"; }
success_msg() { echo -e "${GREEN}${BOLD}[SUCCESS]${NC} $1"; }
warn_msg() { echo -e "${YELLOW}${BOLD}[WARN]${NC} $1"; }

log_msg "------------------------------------------------------------"
log_msg "Starting GIBS lifecycle management for Collin County area..."

# --- 1. Python Ingestion Cycle ---
if [[ ! -f "$PY_SCRIPT" ]]; then
    error_msg "Python fetcher not found at $PY_SCRIPT."
    exit 1
fi

log_msg "Executing Python image fetcher..."
python3 "$PY_SCRIPT"
if [[ $? -ne 0 ]]; then
    error_msg "Python fetcher failed. check gibs_fetch.log."
else
    success_msg "Image retrieval cycle finished."
fi

# --- 2. Monthly Housekeeping & Video Compilation ---
if [[ "$(date +%d)" == "01" ]]; then
    log_msg "First of the month: Compiling land-use tracking videos..."
    PREV_MONTH=$(date -d "last month" +%Y-%m)

    for MODE in "day" "night"; do
        INPUT_DIR="${DATA_ROOT}/${MODE}"
        ARCHIVE_DIR="${INPUT_DIR}/archive"
        OUTPUT_FILE="${DATA_ROOT}/gibs_${MODE}_${PREV_MONTH}.mp4"

        if ls "$INPUT_DIR"/*.jpg >/dev/null 2>&1; then
            log_msg "Compiling $MODE timelapse at 2 FPS..."

            # FFmpeg Optimizations:
            # -r 2: Sets output to 2 frames per second (slow motion)
            # -crf 17: Near-lossless quality to preserve pixel edges
            # drawtext: Scaled for 4096px resolution (fontsize 80)
            ffmpeg -f image2 -pattern_type glob -i "$INPUT_DIR/*.jpg" \
                   -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2, \
                        drawtext=fontfile=${FONT_PATH}: \
                        text='North TX Regional - %{metadata\:source_basename}': \
                        fontcolor=white: fontsize=80: box=1: boxcolor=black@0.6: \
                        boxborderw=20: x=w-tw-40: y=h-th-40" \
                   -c:v libx264 -crf 17 -pix_fmt yuv420p -r 2 "$OUTPUT_FILE" -y -loglevel error

            if [[ $? -eq 0 ]]; then
                mkdir -p "$ARCHIVE_DIR"
                mv "$OUTPUT_FILE" "$ARCHIVE_DIR/"
                rm "$INPUT_DIR"/*.jpg
                success_msg "Video Archived: gibs_${MODE}_${PREV_MONTH}.mp4"
            else
                error_msg "FFmpeg failed for $MODE."
            fi
        else
            warn_msg "No $MODE images found."
        fi
    done
fi

log_msg "GIBS lifecycle management complete."
log_msg "------------------------------------------------------------"