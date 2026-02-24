#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_trends.sh
# 📝 DESCRIPTION   : Monthly trend analysis for Collin County Land Use.
#                   Compiles daily snapshots, handles yearly single-images,
#                   and stores output in the Videos directory.
# 🔖 VERSION       : 1.7.0 (Multi-County Walk)
# 📅 UPDATED       : 2026-02-23
# 👤 AUTHOR        : Matha Goram
# -------------------------------------------------------------------------------

# --- ⚙️ Configuration ---
CODE_ROOT="/home/reza/PycharmProjects/noaa/terran"
REQUIRED_CONFIG="${CODE_ROOT}/config.toml"
DATE_STAMP=$(date +%Y-%m)

# Destination for all media
MEDIA_ROOT="/home/reza/Videos/satellite/terran"
SUMMARY_DIR="${MEDIA_ROOT}/monthly_summaries/${DATE_STAMP}"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

mkdir -p "$SUMMARY_DIR"

if [[ ! -f "$REQUIRED_CONFIG" ]]; then
    echo -e "${RED}❌ [ERROR] Configuration file not found.${NC}"
    exit 1
fi

# Extract instrument_root
STORAGE_ROOT=$(grep "instrument_root" "$REQUIRED_CONFIG" | cut -d'=' -f2 | tr -d '"' | xargs)

echo -e "${BLUE}>>> 📽️  Starting Multi-County Trend Analysis ($DATE_STAMP) <<<${NC}"

# --- 🔄 The Recursive Walk ---
# This finds every "images" directory, regardless of which county folder it's in.
find "$STORAGE_ROOT" -type d -name "images" | while read -r IMG_DIR; do

    # Path breakdown:
    # IMG_DIR    = .../terran/harris/MODIS_Layer/images
    # LAYER_PATH = .../terran/harris/MODIS_Layer
    # LAYER_NAME = MODIS_Layer
    # COUNTY     = harris

    LAYER_PATH=$(dirname "$IMG_DIR")
    LAYER_NAME=$(basename "$LAYER_PATH")
    COUNT_PATH=$(dirname "$LAYER_PATH")
    COUNTY_NAME=$(basename "$COUNT_PATH")

    VID_DIR="${LAYER_PATH}/videos"
    IMG_COUNT=$(ls -1 "$IMG_DIR"/*.png 2>/dev/null | wc -l)

    if [ "$IMG_COUNT" -gt 1 ]; then
        echo -e "${BLUE}🎞️  Processing $COUNTY_NAME | $LAYER_NAME ($IMG_COUNT images)...${NC}"

        mkdir -p "$VID_DIR"
        TEMP_OUTPUT="${VID_DIR}/${COUNTY_NAME}_${LAYER_NAME}_${DATE_STAMP}.mp4"
        SPACE_BEFORE=$(du -sk "$IMG_DIR" | cut -f1)

        ffmpeg -nostdin -y -framerate 2 -pattern_type glob -i "${IMG_DIR}/*.png" \
               -c:v libx264 -pix_fmt yuv420p -crf 23 "$TEMP_OUTPUT" &> /dev/null

        if [ $? -eq 0 ]; then
            # Copy to unified summary folder with county prefix
            cp "$TEMP_OUTPUT" "${SUMMARY_DIR}/${COUNTY_NAME}_${LAYER_NAME}_${DATE_STAMP}.mp4"
            rm "${IMG_DIR}"/*.png

            SPACE_AFTER=$(du -sk "$IMG_DIR" | cut -f1)
            RECLAIMED_MB=$(echo "scale=2; ($SPACE_BEFORE - $SPACE_AFTER) / 1024" | bc)
            echo -e "${GREEN}✅ Created video for $COUNTY_NAME (Saved ${RECLAIMED_MB} MB)${NC}"
        fi

    elif [ "$IMG_COUNT" -eq 1 ]; then
        echo -e "ℹ️  Snapshot found for $COUNTY_NAME | $LAYER_NAME. Moving to summary."
        cp "$IMG_DIR"/*.png "${SUMMARY_DIR}/${COUNTY_NAME}_${LAYER_NAME}_snapshot_${DATE_STAMP}.png"
        rm "${IMG_DIR}"/*.png
        echo -e "${GREEN}✅ Snapshot moved.${NC}"
    fi
done

echo -e "\n${BOLD}=================================================${NC}"
echo -e "${GREEN}🎉 All Counties Processed.${NC}"
echo -e "📂 Media: ${BLUE}$SUMMARY_DIR${NC}"
echo -e "${BOLD}=================================================${NC}"