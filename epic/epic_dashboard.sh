#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           epic_dashboard.sh
# Author:         Matha Goram
# Version:        1.1.0
# Updated:        2026-02-06
# Description:    Enhanced wrapper for storage_dashboard.py. Adds logic to
#                 compile daily images into monthly continental time-lapses
#                 using ffmpeg and purges source images upon success.
# License:        MIT License
# Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
# -------------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -------------------------------------------------------------------------------

# --- ANSI Color Codes ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Configuration ---
EPIC_ROOT="$HOME/PycharmProjects/noaa/epic/"
SWPC_ROOT="$HOME/PycharmProjects/noaa/swpc/"
VENV_PATH="${SWPC_ROOT}../.venv/bin/activate"
PYTHON_SCRIPT="${EPIC_ROOT}epic_dashboard.py"
REQUIRED_CONFIG="${SWPC_ROOT}config.toml"

# Paths for video processing
DATA_DIR="${EPIC_ROOT}data"
VIDEO_DIR="${EPIC_ROOT}videos"
LAST_MONTH=$(date -d "last month" +%Y-%m)

# --- UI Functions ---
log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1" >&2; }

header() {
    echo -e "${MAGENTA}==============================================${NC}"
    echo -e "${MAGENTA}   EPIC STORAGE DASHBOARD & VIDEO BUILDER     ${NC}"
    echo -e "${MAGENTA}==============================================${NC}"
}

# --- Validation Logic ---
check_environment() {
    log_info "Validating environment and tools..."

    [[ ! -f "$PYTHON_SCRIPT" ]] && { log_error "Python script not found: $PYTHON_SCRIPT"; exit 1; }
    [[ ! -f "$REQUIRED_CONFIG" ]] && { log_error "Config missing: $REQUIRED_CONFIG"; exit 1; }
    [[ ! -f "$VENV_PATH" ]] && { log_error "Venv missing: $VENV_PATH"; exit 1; }

    if ! command -v ffmpeg &> /dev/null; then
        log_error "ffmpeg is not installed. Required for video conversion."
        exit 1
    fi
}

# --- Video Processing Logic ---
create_timelapses() {
    log_info "Starting video conversion for period: $LAST_MONTH"
    mkdir -p "$VIDEO_DIR"

    # Iterate through each continent directory
    for continent_dir in "$DATA_DIR"/*/; do
        continent=$(basename "$continent_dir")
        video_filename="${VIDEO_DIR}/EPIC_${continent}_${LAST_MONTH}.mp4"

        log_info "Processing $continent..."

        # Check if there are images to process
        if [ -z "$(ls -A "$continent_dir"/*.png 2>/dev/null)" ]; then
            log_warn "No imagery found for $continent. Skipping."
            continue
        fi

        # Use ffmpeg to create a 10fps video from the sequence of images
        # -pattern_type glob handles the timestamped filenames
        # -pix_fmt yuv420p ensures compatibility with most players
        ffmpeg -y -f image2 -pattern_type glob -i "${continent_dir}*.png" \
               -vcodec libx264 -crf 25 -pix_fmt yuv420p \
               -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
               "$video_filename" &> /dev/null

        if [[ $? -eq 0 ]]; then
            log_success "Created: $(basename "$video_filename")"

            # Retention Policy: Delete processed images upon successful video creation
            log_info "Reclaiming space: Deleting source images for $continent..."
            rm "${continent_dir}"*.png
        else
            log_error "Failed to create video for $continent. Images retained."
        fi
    done
}

# --- Execution ---
main() {
    header
    check_environment

    # 1. Source Virtual Environment
    log_info "Sourcing virtual environment..."
    # shellcheck disable=SC1091
    if source "$VENV_PATH"; then
        log_success "Environment active."
    else
        log_error "Failed to source virtual environment."
        exit 1
    fi

    # 2. Run Monthly Storage Dashboard (Stats collection first)
    log_info "Collecting storage statistics..."
    python3 "$PYTHON_SCRIPT" --config "$REQUIRED_CONFIG"

    # 3. Compile Videos and Purge Images
    echo -e "${CYAN}----------------------------------------------${NC}"
    create_timelapses
    echo -e "${CYAN}----------------------------------------------${NC}"

    log_success "Monthly operations complete."
}

# Invoke Main
main