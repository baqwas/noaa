#!/bin/bash
# -----------------------------------------------------------------------------
# 📅 NAME          : process_timelapse.sh
# 🚀 DESCRIPTION   : Core FFmpeg Rendering Engine for BeUlta Satellite Suite.
#                   Converts image sequences to H.264 MP4.
#                   Supports conditional text overlays (e.g., "HAZY DAY").
# 👤 AUTHOR        : Matha Goram / BeUlta Suite
# 📅 UPDATED       : 2026-03-07
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- 📥 Arguments ---
IMG_DIR="$1"      # Source directory of daily JPEGs
VID_DIR="$2"      # Destination for the MP4
TARGET_NAME="$3"  # e.g., "true_color" or "goes_east"
OVERLAY_TEXT="$4" # Optional: "HAZY DAY" or empty

# --- ⚙️ Internal Config ---
DATE_STAMP=$(date +%Y-%m-%d)
OUTPUT_FILE="${VID_DIR}/${TARGET_NAME}_${DATE_STAMP}.mp4"
mkdir -p "$VID_DIR"

# UI Styling
BLUE='\033[0;34m'; YELLOW='\033[1;33m'; NC='\033[0m'

# --- 🎨 FFmpeg Filter Logic ---
# Base filter: scale to 4k width, ensure height is divisible by 2 for H.264
FILTER="scale=4096:-2"

if [[ -n "$OVERLAY_TEXT" ]]; then
    echo -e "${YELLOW}🖌️  Applying Filter: [${OVERLAY_TEXT}]${NC}"
    # drawtext parameters:
    # x,y: Top Right (w-tw-100, 100)
    # box: Creates a semi-transparent black background for the yellow text
    TEXT_FILTER="drawtext=text='${OVERLAY_TEXT}':fontcolor=yellow:fontsize=120:box=1:boxcolor=black@0.6:boxborderw=20:x=w-tw-100:y=100"
    FILTER="${FILTER},${TEXT_FILTER}"
fi

# --- 🎬 Rendering Execution ---
echo -e "${BLUE}🎞️  Rendering ${TARGET_NAME}...${NC}"

# FFmpeg Command Breakdown:
# -y: Overwrite output
# -framerate 12: Smooth 12fps for 24-frame daily sequences
# -pattern_type glob: Handles non-sequential filenames
# -pix_fmt yuv420p: Maximum compatibility for your Thunderbird/Mobile clients
ffmpeg -y -hide_banner -loglevel error \
    -framerate 12 \
    -pattern_type glob -i "${IMG_DIR}/*.jpg" \
    -vf "${FILTER}" \
    -c:v libx264 \
    -preset medium \
    -crf 23 \
    -pix_fmt yuv420p \
    "$OUTPUT_FILE"

# --- 🏁 Exit Status ---
if [ $? -eq 0 ]; then
    # Optional: Log the success for the Visibility Audit to see
    exit 0
else
    exit 1
fi
