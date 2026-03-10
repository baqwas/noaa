#!/bin/bash
# -----------------------------------------------------------------------------
# 📅 NAME          : compile_weekly.sh
# 🚀 DESCRIPTION   : Recursive Weekly Video Archive Engine.
#                   Consolidates daily MP4s into weekly summaries.
#                   v1.1: Added file-size validation to skip "ghost" videos.
# 👤 AUTHOR        : Matha Goram
# 📅 UPDATED       : 2026-03-07
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

    TARGET_DIR=$(dirname "$VID_DIR")
    TARGET_NAME=$(basename "$TARGET_DIR")

    shopt -s nullglob
    DAILY_VIDS=("$VID_DIR"/*.mp4)
    shopt -u nullglob

    if [ ${#DAILY_VIDS[@]} -eq 0 ]; then
        continue
    fi

    JOIN_FILE="${VID_DIR}/join_list.txt"
    OUTPUT_FILE="${VID_DIR}/WEEKLY_${TARGET_NAME}_${WEEK_LABEL}.mp4"

    # Create FFMPEG concat list
    > "$JOIN_FILE"
    VALID_COUNT=0

    for vid in "${DAILY_VIDS[@]}"; do
        # Logic: Skip weekly files, and ensure the video is > 100KB
        # (Anything smaller is likely a failed render from missing GIBS data)
        if [[ $(basename "$vid") != WEEKLY_* ]]; then
            FILESIZE=$(stat -c%s "$vid")
            if [ "$FILESIZE" -gt 102400 ]; then
                echo "file '$(basename "$vid")'" >> "$JOIN_FILE"
                ((VALID_COUNT++))
            fi
        fi
    done

    # 2. Compile using Concat Demuxer
    if [ "$VALID_COUNT" -gt 0 ]; then
        echo -e "📦 Archiving Weekly: ${GREEN}$TARGET_NAME${NC} ($VALID_COUNT days)"
        ffmpeg -y -f concat -safe 0 -i "$JOIN_FILE" -c copy "$OUTPUT_FILE" > /dev/null 2>&1
        echo -e "✅ Created: $OUTPUT_FILE"
    fi

    [ -f "$JOIN_FILE" ] && rm "$JOIN_FILE"
done

echo -e "${BLUE}>>> 🏁 Weekly Archive Cycle Complete <<<${NC}"
