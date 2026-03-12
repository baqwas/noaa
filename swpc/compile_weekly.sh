#!/bin/bash
# -----------------------------------------------------------------------------
# 📅 NAME          : compile_weekly.sh
# 🚀 DESCRIPTION   : Recursive Weekly Video Archive & Image-to-Video Engine.
#                   - v1.1: Added file-size validation to skip "ghost" videos.
#                   - v1.2: Added image-to-video compilation for El Niño
#                           and success-based source purging.
# 👤 AUTHOR        : Matha Goram / Reza
# 📅 UPDATED       : 2026-03-12
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- ⚙️ Paths ---
BASE_ROOT="/home/reza/Videos/satellite"
WEEK_LABEL=$(date +%Y_W%U)

# UI Styling
BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}>>> 🗓️  Starting Weekly Archive & Image Consolidation ($WEEK_LABEL) <<<${NC}"

# --- 🌊 TASK 1: EL NIÑO / IMAGE CONSOLIDATION ---
# Specifically targets directories containing raw imagery like 'elnino_sst'
find "$BASE_ROOT/gibs" -type d -name "elnino_sst" | while read -r IMG_DIR; do

    TARGET_NAME=$(basename "$IMG_DIR")
    OUTPUT_FILE="${IMG_DIR}/WEEKLY_${TARGET_NAME}_${WEEK_LABEL}.mp4"

    # Check for images (.png or .jpg)
    shopt -s nullglob
    IMAGES=("$IMG_DIR"/*.{png,jpg})
    shopt -u nullglob

    if [ ${#IMAGES[@]} -gt 0 ]; then
        echo -e "🎞️  Consolidating Images: ${GREEN}$TARGET_NAME${NC} (${#IMAGES[@]} frames)"

        # Compile images at 2fps to allow visual analysis of thermal drift
        ffmpeg -y -framerate 2 -pattern_type glob -i "$IMG_DIR/*.png" \
               -c:v libx264 -pix_fmt yuv420p "$OUTPUT_FILE" > /dev/null 2>&1

        if [ $? -eq 0 ]; then
            echo -e "✅ Created: $OUTPUT_FILE"
            # SUCCESS-BASED PURGE: Delete images only if the video rendered correctly
            rm "${IMAGES[@]}"
            echo -e "🧹 Source images purged."
        else
            echo -e "🚨 ${RED}ERROR: Image compilation failed for $TARGET_NAME. Assets retained.${NC}"
        fi
    fi
done

# --- 📼 TASK 2: STANDARD VIDEO ARCHIVE (Existing Logic) ---
find "$BASE_ROOT" -type d -name "videos" | while read -r VID_DIR; do

    TARGET_DIR=$(dirname "$VID_DIR")
    TARGET_NAME=$(basename "$TARGET_DIR")

    shopt -s nullglob
    DAILY_VIDS=("$VID_DIR"/*.mp4)
    shopt -u nullglob

    if [ ${#DAILY_VIDS[@]} -eq 0 ]; then continue; fi

    JOIN_FILE="${VID_DIR}/join_list.txt"
    OUTPUT_FILE="${VID_DIR}/WEEKLY_${TARGET_NAME}_${WEEK_LABEL}.mp4"

    > "$JOIN_FILE"
    VALID_COUNT=0

    for vid in "${DAILY_VIDS[@]}"; do
        if [[ $(basename "$vid") != WEEKLY_* ]]; then
            FILESIZE=$(stat -c%s "$vid")
            if [ "$FILESIZE" -gt 102400 ]; then
                echo "file '$(basename "$vid")'" >> "$JOIN_FILE"
                ((VALID_COUNT++))
            fi
        fi
    done

    if [ "$VALID_COUNT" -gt 0 ]; then
        echo -e "📦 Archiving Weekly: ${GREEN}$TARGET_NAME${NC} ($VALID_COUNT days)"
        ffmpeg -y -f concat -safe 0 -i "$JOIN_FILE" -c copy "$OUTPUT_FILE" > /dev/null 2>&1
        echo -e "✅ Created: $OUTPUT_FILE"
    fi

    [ -f "$JOIN_FILE" ] && rm "$JOIN_FILE"
done

echo -e "${BLUE}>>> 🏁 Weekly Archive Cycle Complete <<<${NC}"
