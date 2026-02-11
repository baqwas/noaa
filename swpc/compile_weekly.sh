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

# --- Paths ---
BASE="/home/reza/Videos/satellite/swpc"
WEEK=$(date +%Y-W%U)

# UI Styling
BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${BLUE}>>> Starting Weekly Archive Compilation ($WEEK) <<<${NC}"

# Find all "videos" directories
find "$BASE" -type d -name "videos" | while read -r VID_DIR; do

    # Validation: Ensure VID_DIR is not empty
    if [[ -z "$VID_DIR" ]]; then continue; fi

    INSTR_ROOT=$(dirname "$VID_DIR")
    # Correctly grab the instrument name (aurora, solar_304, etc.)
    INSTR_NAME=$(basename "$INSTR_ROOT")
    LOG="${INSTR_ROOT}/${INSTR_NAME}.log"

    # Check if there are actually MP4 files to process
    shopt -s nullglob
    VIDEOS=("$VID_DIR"/*.mp4)
    shopt -u nullglob

    if [ ${#VIDEOS[@]} -eq 0 ]; then
        echo -e "${YELLOW}[WARN] No daily videos found in $VID_DIR. Skipping.${NC}"
        continue
    fi

    # Extract unique prefixes (e.g., aurora_north, aurora_south, solar_304)
    # This prevents the "missing operand" error by ensuring we only iterate on existing files
    PREFIXES=$(ls "$VID_DIR"/*.mp4 2>/dev/null | xargs -I {} basename {} | cut -d'_' -f1-2 | sort -u)

    for PREFIX in $PREFIXES; do
        # Final safety check on PREFIX
        if [[ -z "$PREFIX" ]]; then continue; fi

        echo -e "Archiving Weekly: ${GREEN}$PREFIX${NC}"
        echo "[$(date)] Archiving Weekly for $PREFIX" >> "$LOG"

        # Create temporary concat list
        JOIN_FILE="${VID_DIR}/join_${PREFIX}.txt"
        printf "file '%s'\n" "$VID_DIR"/${PREFIX}_*.mp4 > "$JOIN_FILE"

        # -nostdin is critical for running inside a 'while read' loop
        ffmpeg -nostdin -y -f concat -safe 0 -i "$JOIN_FILE" -c copy \
               "${VID_DIR}/WEEKLY_${PREFIX}_${WEEK}.mp4" >> "$LOG" 2>&1

        rm "$JOIN_FILE"
    done
done

echo -e "${GREEN}Weekly processing complete.${NC}"