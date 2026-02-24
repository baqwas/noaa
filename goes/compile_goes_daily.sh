#!/bin/bash
# -----------------------------------------------------------------------------
# 🎞️ NAME         : compile_goes_daily.sh
# 👤 AUTHOR       : Matha Goram / BeUlta Suite
# 📝 DESCRIPTION  : Processes daily GOES imagery into MP4 time-lapses.
#                  Enforces underscore nomenclature and unified logging.
#
# 🛠️ WORKFLOW     :
#    1. Navigate to goes_east and goes_west /images/ directories.
#    2. Check for existence of JPG assets.
#    3. Invoke FFMPEG to render daily MP4 in /videos/ subfolder.
#    4. Upon successful render, purge source imagery.
#    5. Log all output to centralized goes_operations.log.
# -----------------------------------------------------------------------------

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
DATE_STAMP=$(date +%Y-%m-%d)

# Path Mapping
BASE_ROOT="/home/reza/Videos/satellite/goes"
LOG_FILE="${BASE_ROOT}/logs/goes_operations.log"
SATELLITES=("goes_east" "goes_west")

echo -e "${BLUE}>>> Starting GOES Video Compilation Cycle ($DATE_STAMP) <<<${NC}"

for SAT in "${SATELLITES[@]}"; do
    IMG_DIR="${BASE_ROOT}/${SAT}/images"
    VID_DIR="${BASE_ROOT}/${SAT}/videos"

    if [ -d "$IMG_DIR" ] && [ "$(ls -A "$IMG_DIR"/*.jpg 2>/dev/null)" ]; then
        mkdir -p "$VID_DIR"
        OUTPUT_FILE="${VID_DIR}/${SAT}_${DATE_STAMP}.mp4"

        echo -e "${BLUE}[INFO]${NC} Encoding $SAT..."
        ffmpeg -y -framerate 12 -pattern_type glob -i "${IMG_DIR}/*.jpg" \
               -c:v libx264 -pix_fmt yuv420p "$OUTPUT_FILE" >> "$LOG_FILE" 2>&1

        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}[SUCCESS]${NC} Rendered $(basename "$OUTPUT_FILE")"
            rm "${IMG_DIR}"/*.jpg
            echo "[$(date)] ✅ Video Success: $SAT" >> "$LOG_FILE"
        else
            echo -e "${RED}[ERROR]${NC} FFMPEG failed for $SAT. See log."
            echo "[$(date)] ❌ Video Failure: $SAT" >> "$LOG_FILE"
        fi
    else
        echo -e "${BLUE}[INFO]${NC} $SAT: No images found. Skipping."
    fi
done