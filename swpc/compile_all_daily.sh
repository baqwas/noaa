#!/bin/bash
# -----------------------------------------------------------------------------
# 🎞️ NAME          : compile_all_daily.sh
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.1.0 (Refactored for Path Alignment)
# 📅 UPDATED       : 2026-02-25
# 📝 DESCRIPTION   : Batch processes all satellite timelapses in parallel.
#                   Consolidates Aurora and GOES rendering into one engine.
#
# 🛠️ WORKFLOW      :
#    1. Define array of target directories and labels.
#    2. Pass targets to xargs for parallel execution.
#    3. Invoke process_timelapse.sh for each valid target.
#
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- Configuration & Styling ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

PROJ_DIR="/home/reza/PycharmProjects/noaa"
PROC_SCRIPT="${PROJ_DIR}/swpc/process_timelapse.sh"

# --- 🛰️ Target Registry ---
# Note: Paths now match [goes.storage_root] from config.toml
TARGETS=(
    "swpc/aurora/north/images|aurora_north"
    "swpc/aurora/south/images|aurora_south"
    "noaa/goes/goes_east/images|goes_east"
    "noaa/goes/goes_west/images|goes_west"
)

echo -e "${BLUE}>>> 🚀 Launching Parallel Render Engine <<<${NC}"

# Verify if the processor script exists before launching
if [[ ! -f "$PROC_SCRIPT" ]]; then
    echo -e "${RED}❌ [FATAL] Processor script missing: $PROC_SCRIPT${NC}"
    exit 1
fi

# -P 2 runs two ffmpeg instances at once.
printf "%s\n" "${TARGETS[@]}" | xargs -P 2 -I {} bash -c '
    IFS="|" read -r dir label <<< "{}"
    target_path="/home/reza/Videos/satellite/$dir"

    if [[ -d "$target_path" ]]; then
        bash "'$PROC_SCRIPT'" "$target_path" "$label"
    else
        echo -e "\033[0;31m⚠️  [SKIP] Path not found: $target_path\033[0m"
    fi
'

echo -e "${GREEN}>>> ✅ All daily renders complete. <<<${NC}"