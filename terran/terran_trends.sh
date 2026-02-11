#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# Name:           terran_trends.sh
# Description:    Monthly trend analysis for Collin County Land Use.
# -------------------------------------------------------------------------------

# --- Configuration ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
REQUIRED_CONFIG="${PROJ_ROOT}/swpc/config.toml"
DATE_STAMP=$(date +%Y-%m)

# ANSI Styling
GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'

# Extract storage_root from config
STORAGE_ROOT=$(grep "instrument_root" "$REQUIRED_CONFIG" | cut -d'"' -f2 | grep "terran")

echo -e "${BLUE}>>> Starting Monthly Land Use Trend Analysis ($DATE_STAMP) <<<${NC}"

# Find all layer directories within the terran root
find "$STORAGE_ROOT" -maxdepth 1 -type d ! -path "$STORAGE_ROOT" ! -name "logs" | while read -r LAYER_PATH; do

    LAYER_NAME=$(basename "$LAYER_PATH")
    IMG_DIR="${LAYER_PATH}/images"
    VID_DIR="${LAYER_PATH}/videos"

    # Check if images exist for processing
    if [[ -d "$IMG_DIR" ]] && [ "$(ls -A "$IMG_DIR"/*.png 2>/dev/null)" ]; then
        mkdir -p "$VID_DIR"
        OUTPUT_FILE="${VID_DIR}/${LAYER_NAME}_${DATE_STAMP}.mp4"

        echo "Processing $LAYER_NAME..."

        # -nostdin prevents ffmpeg from swallowing loop input
        ffmpeg -nostdin -y -framerate 2 -pattern_type glob -i "${IMG_DIR}/*.png" \
               -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
               "$OUTPUT_FILE" &> /dev/null

        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}Success: Created $OUTPUT_FILE${NC}"
            # Clean up source images after successful render
            rm "${IMG_DIR}"/*.png
        fi
    fi
done