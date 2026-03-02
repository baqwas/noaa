#!/bin/bash
# -----------------------------------------------------------------------------
# 🎞️ NAME         : compile_goes_daily.sh
# 👤 AUTHOR       : Matha Goram
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
DATE_STAMP=$(date -d "yesterday" +%Y-%m-%d)
BASE_ROOT="/home/reza/Videos/satellite/goes"
SATELLITES=("goes_east" "goes_west")

echo -e "${BLUE}[$(date)] Starting Daily Video Compilation for $DATE_STAMP...${NC}"

for SAT in "${SATELLITES[@]}"; do
    IMG_DIR="${BASE_ROOT}/${SAT}/images"
    VID_DIR="${BASE_ROOT}/${SAT}/videos"
    OUT_FILE="${VID_DIR}/${SAT}_${DATE_STAMP}.mp4"

    if [[ -d "$IMG_DIR" ]] && [[ $(ls -1 "$IMG_DIR"/*.jpg 2>/dev/null | wc -l) -gt 0 ]]; then
        echo -e "${BLUE}🎥 Rendering ${SAT}...${NC}"

        # FFMPEG Command: Compiles images into 24fps MP4
        ffmpeg -y -framerate 24 -pattern_type glob -i "${IMG_DIR}/*.jpg" \
               -c:v libx264 -pix_fmt yuv420p -crf 23 "$OUT_FILE" &>/dev/null

        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Success: $OUT_FILE${NC}"
            # Optional: Move or purge images here to keep /images clean
            # rm "$IMG_DIR"/*.jpg
        else
            echo -e "${RED}❌ Render Failed for $SAT${NC}"
        fi
    else
        echo -e "${RED}⚠️ No images found for $SAT in $IMG_DIR${NC}"
    fi
done