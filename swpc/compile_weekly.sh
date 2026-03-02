#!/bin/bash
# -----------------------------------------------------------------------------
# 📅 NAME          : compile_weekly.sh
# 🚀 DESCRIPTION   : Recursive Weekly Video Archive Engine.
#                   Consolidates daily MP4s into weekly summaries.
# 👤 AUTHOR        : Matha Goram
# 📅 UPDATED       : 2026-03-01
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- ⚙️ Paths ---
BASE_ROOT="/home/reza/Videos/satellite"
WEEK_LABEL=$(date +%Y_W%U)

# UI Styling
BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${BLUE}>>> 🗓️  Starting Weekly Archive Compilation ($WEEK_LABEL) <<<${NC}"

# 1. Find every 'videos' directory in the satellite archive
find "$BASE_ROOT" -type d -name "videos" | while read -r VID_DIR; do

    # Identify the parent target name (e.g., goes_east)
    TARGET_DIR=$(dirname "$VID_DIR")
    TARGET_NAME=$(basename "$TARGET_DIR")

    # Check for daily MP4s
    shopt -s nullglob
    DAILY_VIDS=("$VID_DIR"/*.mp4)
    shopt -u nullglob

    if [ ${#DAILY_VIDS[@]} -eq 0 ]; then
        continue
    fi

    echo -e "📦 Archiving Weekly: ${GREEN}$TARGET_NAME${NC}"

    JOIN_FILE="${VID_DIR}/join_list.txt"
    OUTPUT_FILE="${VID_DIR}/WEEKLY_${TARGET_NAME}_${WEEK_LABEL}.mp4"

    # Create FFMPEG concat list
    > "$JOIN_FILE"
    for vid in "${DAILY_VIDS[@]}"; do
        # Do not include existing weekly files in the new weekly file
        if [[ $(basename "$vid") != WEEKLY_* ]]; then
            echo "file '$(basename "$vid")'" >> "$JOIN_FILE"
        fi
    done

    # 2. Compile using Concat Demuxer (Fast, no re-encoding)
    if [ -s "$JOIN_FILE" ]; then
        ffmpeg -y -f concat -safe 0 -i "$JOIN_FILE" -c copy "$OUTPUT_FILE" > /dev/null 2>&1
        echo -e "✅ Created: $OUTPUT_FILE"
        rm "$JOIN_FILE"
    fi
done

echo -e "${BLUE}>>> 🏁 Weekly Archive Cycle Complete <<<${NC}"
