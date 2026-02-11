#!/bin/bash
# -----------------------------------------------------------------------------
# 🌌 NAME          : process_timelapse.sh
# 👤 AUTHOR        : Matha Goram / BeUlta Suite
# 🔖 VERSION       : 1.1.0 (Unified & Iconified)
# 📅 UPDATED       : 2026-02-10
# 📝 DESCRIPTION   : Converts raw imagery into MP4 videos using FFmpeg.
#                    Supports daily/weekly cycles with "yesterday" datestamping.
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- 🎨 ANSI Color Palette ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m';
BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m';

# --- 📥 Input Arguments ---
IMG_DIR="$1"
LABEL="$2"
# 🕒 Set DATE to yesterday to accurately reflect the data capture period
DATE=$(date -d "yesterday" +%Y-%m-%d)

# --- 🛡️ Validation Gate ---
if [[ -z "$IMG_DIR" || ! -d "$IMG_DIR" ]]; then
    echo -e "${RED}❌ [ERROR]${NC} Invalid or missing image directory: $IMG_DIR"
    exit 1
fi

# --- 📂 Path Orchestration ---
INSTR_ROOT=$(dirname "$IMG_DIR")
VID_DIR="${INSTR_ROOT}/videos"     # 🎥 Final MP4 destination
LOG="${INSTR_ROOT}/processing.log" # 📜 Internal audit log
mkdir -p "$VID_DIR"

# --- 🔍 Image Discovery ---
shopt -s nullglob
FILES=("$IMG_DIR"/*.{jpg,png,jpeg})

echo -e "${BLUE}🚀 [START]${NC} Processing ${BOLD}${LABEL}${NC} for ${YELLOW}${DATE}${NC}..."

if [ ${#FILES[@]} -gt 0 ]; then
    OUT_FILE="${VID_DIR}/${LABEL}_${DATE}.mp4"

    # --- 🎞️ FFmpeg Engine ---
    # ⚙️ -framerate 24 : Fluid movement
    # ⚙️ -vf scale     : Prevents odd-pixel dimension failures
    ffmpeg -nostdin -y -framerate 24 -pattern_type glob -i "$IMG_DIR/*.{jpg,png,jpeg}" \
           -c:v libx264 -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
           "$OUT_FILE" >> "$LOG" 2>&1

    if [ $? -eq 0 ]; then
        # 🧹 SUCCESS: Purge source images to reclaim disk space
        rm "$IMG_DIR"/*.{jpg,png,jpeg}
        echo "[$(date)] ✅ SUCCESS: Created $OUT_FILE" >> "$LOG"
        echo -e "${GREEN}✅ [SUCCESS]${NC} Video archived: ${BOLD}$(basename "$OUT_FILE")${NC}"
        echo -e "${BLUE}🧹 [CLEAN]${NC} Source frames purged from ${IMG_DIR}"
    else
        # ⚠️ FAIL: Retain images for troubleshooting
        echo "[$(date)] ❌ ERROR: FFmpeg failed for $LABEL" >> "$LOG"
        echo -e "${RED}❌ [FAIL]${NC} Encoding failed. Check 📜 ${LOG}"
    fi
else
    # 💤 IDLE: No data found for processing
    echo -e "${YELLOW}💤 [IDLE]${NC} No images found in directory. Skipping."
fi

echo -e "${BLUE}🏁 [FINISH]${NC} Processing cycle complete.\n"

