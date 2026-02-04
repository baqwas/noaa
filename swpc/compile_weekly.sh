#!/bin/bash
# -----------------------------------------------------------------------------
# Name:         compile_weekly.sh
# Author:       Matha Goram
# Version:      1.0.2
# Updated:      2026-02-04
# Description:  Iterates through image directories, converts files to MP4,
#               cleans up source images, and archives the final video.
# License:      MIT License
# Copyright:    (c) 2026 ParkCircus Productions; All Rights Reserved
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -----------------------------------------------------------------------------

# Configuration
DATA_ROOT="/path/to/data"
LOG_DIR="/path/to/logs"
LOG_FILE="$LOG_DIR/weekly_conversion.log"
DATE_STAMP=$(date +%Y-%W)
EMAIL_RECEIVER="admin@yourdomain.com"

mkdir -p "$LOG_DIR"
exec >> "$LOG_FILE" 2>&1

echo "--- Weekly Processing Started: $(date) ---"

# Use 'find' to locate directories containing images, excluding existing archive folders
find "$DATA_ROOT" -type d -not -path "*/archive*" | while read -r DIR; do

    # Check if directory contains images
    if ls "$DIR"/*.{jpg,png} >/dev/null 2>&1; then

        # Create a clean log name by removing DATA_ROOT from the path
        # Example: /path/to/data/aurora/north -> aurora/north
        LOG_NAME=${DIR#$DATA_ROOT/}
        LOG_NAME=${LOG_NAME%/} # Remove trailing slash

        # Define output file name (replace slashes with underscores for the filename)
        FILE_SAFE_NAME=$(echo "$LOG_NAME" | tr '/' '_')
        ARCHIVE_DIR="${DIR}/archive"
        OUTPUT_FILE="${DIR}/${FILE_SAFE_NAME}_${DATE_STAMP}.mp4"

        echo "Processing Instrument: [$LOG_NAME]..."

        # FFmpeg: Convert images to MP4
        ffmpeg -f image2 -pattern_type glob -i "$DIR/*.{jpg,png}" \
               -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
               -c:v libx264 -pix_fmt yuv420p -r 10 "$OUTPUT_FILE" -y -loglevel error

        if [ $? -eq 0 ]; then
            mkdir -p "$ARCHIVE_DIR"
            mv "$OUTPUT_FILE" "$ARCHIVE_DIR/"

            # Delete only images in current directory (not subdirs)
            find "$DIR" -maxdepth 1 -type f \( -name "*.jpg" -o -name "*.png" \) -delete

            echo "Success: [$LOG_NAME] archived and purged."
        else
            echo "ERROR: FFmpeg failed for [$LOG_NAME]"
            echo "Weekly timelapse failed for $LOG_NAME on $(date)" | mail -s "Space Video Failure: $LOG_NAME" "$EMAIL_RECEIVER"
        fi
    fi
done

echo "--- Weekly Processing Finished: $(date) ---"