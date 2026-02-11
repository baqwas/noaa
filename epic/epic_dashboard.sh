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

# --- Configuration ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV_PATH="${PROJ_ROOT}/.venv/bin/activate"
REQUIRED_CONFIG="${PROJ_ROOT}/swpc/config.toml"
PYTHON_SCRIPT="${PROJ_ROOT}/epic/epic_dashboard.py"

# ANSI Styling for terminal output
GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

create_timelapses() {
    # Extract storage_root from config.toml (Standardized key)
    local STORAGE_ROOT=$(grep "storage_root" "$REQUIRED_CONFIG" | cut -d'"' -f2 | head -n 1)
    local DATE_STAMP=$(date +%Y-%m)

    # Continent sub-folders to process
    local CONTINENTS=("Americas" "Africa_Europe" "Asia_Australia")

    for continent in "${CONTINENTS[@]}"; do
        local IMG_DIR="${STORAGE_ROOT}/${continent}/images"
        local VID_DIR="${STORAGE_ROOT}/${continent}/videos"
        local OUTPUT_FILE="${VID_DIR}/${continent}_${DATE_STAMP}.mp4"

        # Check if source directory exists and contains PNG images
        if [[ -d "$IMG_DIR" ]] && [ "$(ls -A "$IMG_DIR"/*.png 2>/dev/null)" ]; then
            mkdir -p "$VID_DIR"
            log_info "Compiling monthly video for $continent..."

            # -nostdin prevents ffmpeg from breaking the bash loop
            ffmpeg -nostdin -y -framerate 10 -pattern_type glob -i "${IMG_DIR}/*.png" \
                   -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
                   "$OUTPUT_FILE" &> /dev/null

            if [[ $? -eq 0 ]]; then
                log_success "Created: $OUTPUT_FILE"
                # Purge source images after successful render to reclaim space
                rm "${IMG_DIR}"/*.png
            else
                log_error "Failed to compile video for $continent"
            fi
        else
            log_info "No images found for $continent. Skipping."
        fi
    done
}

main() {
    # Ensure VENV is available
    if [[ -f "$VENV_PATH" ]]; then
        source "$VENV_PATH"
    fi

    # 1. Run stats reporting and email dispatch (Python)
    if [[ -f "$PYTHON_SCRIPT" ]]; then
        python3 "$PYTHON_SCRIPT" --config "$REQUIRED_CONFIG"
    fi

    # 2. Compile monthly continent videos and purge source files
    create_timelapses
}

main
