#!/bin/bash
# ==============================================================================
# 🎥 SCRIPT      : compile_all_daily.sh
# 🚀 DESCRIPTION : Universal Production Orchestrator for the BeUlta Suite.
#                  Renders T-1 image sequences into MP4 and performs a
#                  precision forensic purge of source frames.
# 👤 AUTHOR      : Matha Goram
# 🔖 VERSION     : 3.0.0 (T-1 Precision Edition)
# 📅 UPDATED     : 2026-03-14
# ==============================================================================
# 📑 VERSION HISTORY:
#     - 1.0.0: Initial monolithic render script.
#     - 2.5.0: Added loop-based processing for GOES/SWPC targets.
#     - 3.0.0: TEMPORAL PRECISION. Introduced strict T-1 date filtering to
#              eliminate multi-day bloat and ensure reliable purging.
#
# ⚙️ WORKFLOW / PROCESSING:
#     1. Temporal Sync: Computes the YESTERDAY (T-1) string (YYYYMMDD).
#     2. Discovery: Iterates through instrument directories (GOES, SWPC, etc.).
#     3. Precision Render: Executes ffmpeg using a date-locked glob pattern.
#     4. Forensic Purge: Deletes source frames ONLY if the render exit is 0.
#     5. Telemetry: Logs operation status for the system_audit watchdog.
#
# ⚠️ ERROR MESSAGES:
#     - [WARN]  No images found for target date: Skipping render.
#     - [ALERT] FFMPEG Failure: Render aborted; source frames preserved.
#     - [ALERT] Path Error: Target imagery directory does not exist.
#
# 📋 PREREQUISITES:
#     - ffmpeg installed and available in PATH.
#     - Standardized directory structure: .../[target]/images/ and .../videos/
#
# 🔗 REFERENCES:
#     - FFmpeg Documentation: Image2 Demuxer / Pattern Type Glob.
#
# ⚖️ LICENSE:
#     MIT License | Copyright (c) 2026 ParkCircus Productions
# ==============================================================================

# --- ⚙️ ENVIRONMENT & PATHING ---
VIDEO_ROOT="/home/reza/Videos/satellite"
LOG_FILE="$VIDEO_ROOT/logs/daily_render.log"
mkdir -p "$(dirname "$LOG_FILE")"

# --- 📅 TEMPORAL ISOLATION (T-1) ---
# This variable ensures we only touch files from the previous calendar day.
YESTERDAY=$(date -d "yesterday" +%Y%m%d)

echo "========================================================================" | tee -a "$LOG_FILE"
echo "🎬 BEULTA PRODUCTION CYCLE | TARGET: $YESTERDAY" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"

# --- 📂 TARGET INVENTORY ---
# Define the instrument paths relative to VIDEO_ROOT
# Logic: [Instrument Name]:[Relative Path]
TARGETS=(
    "GOES-EAST:goes/goes_east"
    "GOES-WEST:goes/goes_west"
    "SWPC-D-RAP:swpc/d_rap"
)

# --- 🏃 PRODUCTION LOOP ---
for ENTRY in "${TARGETS[@]}"; do
    NAME="${ENTRY%%:*}"
    REL_PATH="${ENTRY#*:}"

    IMG_DIR="$VIDEO_ROOT/$REL_PATH/images"
    VID_DIR="$VIDEO_ROOT/$REL_PATH/videos"
    OUT_FILE="$VID_DIR/${REL_PATH##*/}_$YESTERDAY.mp4"

    echo "🔍 Processing $NAME..." | tee -a "$LOG_FILE"

    # 1. Validation: Ensure images for the specific date exist
    if [[ -z $(ls "$IMG_DIR"/*"$YESTERDAY"* 2>/dev/null) ]]; then
        echo "   ⚠️ NOTICE: No frames found for $YESTERDAY. Skipping." | tee -a "$LOG_FILE"
        continue
    fi

    # 2. Precision Render: ffmpeg captures ONLY the T-1 date-stamped files
    echo "   🎥 Rendering to: $(basename "$OUT_FILE")" | tee -a "$LOG_FILE"

    ffmpeg -y -hide_banner -loglevel error \
        -f image2 -pattern_type glob -i "$IMG_DIR/*$YESTERDAY*.jpg" \
        -c:v libx264 -pix_fmt yuv420p -crf 23 -preset fast \
        "$OUT_FILE"

    RENDER_EXIT=$?

    # 3. Forensic Purge: Only delete if the video was successfully created
    if [ $RENDER_EXIT -eq 0 ]; then
        SIZE=$(du -h "$OUT_FILE" | cut -f1)
        echo "   ✅ SUCCESS: Render complete ($SIZE)." | tee -a "$LOG_FILE"
        echo "   🧹 PURGE: Removing $YESTERDAY source frames..." | tee -a "$LOG_FILE"

        # Strict deletion: only files containing the yesterday string
        rm "$IMG_DIR"/*"$YESTERDAY"*.jpg
    else
        echo "   🚨 FAILURE: ffmpeg exited with code $RENDER_EXIT." | tee -a "$LOG_FILE"
        echo "   💾 FORENSIC: Source frames preserved for review." | tee -a "$LOG_FILE"
    fi
    echo "------------------------------------------------------------------------" | tee -a "$LOG_FILE"
done

echo "🏁 PRODUCTION CYCLE COMPLETE: $(date)" | tee -a "$LOG_FILE"
