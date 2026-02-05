#!/bin/bash
# -----------------------------------------------------------------------------
# Name:         process_timelapse.sh
# Author:       Matha Goram
# Version:      1.0.3
# Updated:      2026-02-04
# Description:  Converts weekly aurora images into MP4 via FFmpeg and clears
#               source files upon success.
# License:      MIT License (c) 2026 ParkCircus Productions; All Rights Reserved
# -----------------------------------------------------------------------------

# Load paths from config (simplified for bash)
LOG_FILE="/home/reza/Videos/satellite/space_fetcher/data/aurora/logs/conversion.log"
NORTH_DIR="/home/reza/Videos/satellite/space_fetcher/data/aurora/north"
SOUTH_DIR="/home/reza/Videos/satellite/space_fetcher/data/aurora/south"
DATE_STAMP=$(date +%Y-%m-%W)

exec >> "$LOG_FILE" 2>&1

echo "--- Starting Weekly Conversion: $(date) ---"

process_hemisphere() {
    local DIR=$1
    local HEMI=$2
    local OUTPUT="${DIR}/aurora_${HEMI}_${DATE_STAMP}.mp4"

    if [ "$(ls -A $DIR/*.jpg 2>/dev/null)" ]; then
        # Use ffmpeg to create a 30fps timelapse
        ffmpeg -pattern_type glob -i "$DIR/*.jpg" -c:v libx264 -pix_fmt yuv420p "$OUTPUT" -y

        if [ $? -eq 0 ]; then
            echo "SUCCESS: Created $OUTPUT. Deleting source images..."
            rm "$DIR"/*.jpg
        else
            echo "ERROR: FFmpeg failed for $HEMI"
            # Trigger error email (re-using the logic from config or a simple mail command)
            echo "Weekly timelapse failed for $HEMI" | mail -s "Aurora Conversion Failure" admin@yourdomain.com
        fi
    else
        echo "No images found for $HEMI. Skipping."
    fi
}

process_hemisphere "$NORTH_DIR" "north"
process_hemisphere "$SOUTH_DIR" "south"

echo "--- Conversion Task Finished: $(date) ---"