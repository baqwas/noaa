#!/bin/bash
# -----------------------------------------------------------------------------
# 🌌 NAME          : process_timelapse.sh
# 👤 AUTHOR        : Matha Goram / BeUlta Suite
# 🔖 VERSION       : 1.2.4 (Enhanced for Consolidated Workflow)
# 📅 UPDATED       : 2026-03-07
# 📝 DESCRIPTION   : Converts raw satellite imagery into MP4 videos.
#                    Now includes image archival to prevent directory bloat.
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- 🎨 ANSI Color Palette ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m';
BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m';

# --- 📥 Input Arguments ---
IMG_DIR="$1"
VID_DIR="$2"
LABEL="$3"
# Use yesterday's date for the filename as we compile at 00:30
DATE=$(date -d "yesterday" +%Y-%m-%d)

# --- 🛡️ Validation Gate ---
if [[ -z "$IMG_DIR" || ! -d "$IMG_DIR" ]]; then
    echo -e "${RED}❌ [ERROR]${NC} Invalid image directory: $IMG_DIR"
    exit 1
fi

TARGET_ROOT=$(dirname "$IMG_DIR")
LOG="${TARGET_ROOT}/processing.log"
ARCHIVE_DIR="${TARGET_ROOT}/archive/${DATE}"
mkdir -p "$VID_DIR"

# --- 🔍 Image Discovery ---
shopt -s nullglob
FILES=("$IMG_DIR"/*.[jJ][pP][gG] "$IMG_DIR"/*.[pP][nN][gG])
TOTAL_FRAMES=${#FILES[@]}

if [ "$TOTAL_FRAMES" -lt 24 ]; then
    echo -e "${YELLOW}⚠️  [SKIP]${NC} Only ${TOTAL_FRAMES} images found for $LABEL. Minimum 24 required."
    exit 0
fi

OUT_FILE="${VID_DIR}/${LABEL}_${DATE}.mp4"
echo -e "${BLUE}🚀 [START]${NC} Rendering ${BOLD}${LABEL}${NC} (${TOTAL_FRAMES} frames)..."

# --- 🎞️ FFmpeg Execution ---
# Generate temp file list for the concat demuxer
printf "file '%s'\n" "${FILES[@]}" > "${TARGET_ROOT}/files.txt"

ffmpeg -nostdin -y -r 24 -f concat -safe 0 -i "${TARGET_ROOT}/files.txt" \
       -c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.2 \
       -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1" \
       -preset medium -crf 23 \
       "$OUT_FILE" >> "$LOG" 2>&1

RENDER_STATUS=$?

# Cleanup temp file
rm -f "${TARGET_ROOT}/files.txt"

# --- 🏁 Exit Logic & Housekeeping ---
if [ $RENDER_STATUS -eq 0 ]; then
    echo "[$(date)] ✅ SUCCESS: $OUT_FILE" >> "$LOG"
    echo -e "${GREEN}✅ [SUCCESS]${NC} Video archived: ${BOLD}$(basename "$OUT_FILE")${NC}"

    # --- 🧹 Housekeeping: Move processed images to archive ---
    mkdir -p "$ARCHIVE_DIR"
    mv "$IMG_DIR"/* "$ARCHIVE_DIR/"
    echo "[$(date)] 🧹 Cleanup: Images moved to $ARCHIVE_DIR" >> "$LOG"

    exit 0
else
    echo "[$(date)] ❌ FAILED: Render error for $LABEL" >> "$LOG"
    echo -e "${RED}❌ [FAILED]${NC} Check $LOG for FFmpeg errors."
    exit 1
fi
