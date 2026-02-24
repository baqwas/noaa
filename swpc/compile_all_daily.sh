#!/bin/bash
# -----------------------------------------------------------------------------
# 🎞️ NAME         : compile_all_daily.sh
# 🔖 VERSION      : 1.0.0 (Multi-Core Optimized)
# 📝 DESCRIPTION  : Batch processes all satellite timelapses in parallel.
# -----------------------------------------------------------------------------

PROJ_DIR="/home/reza/PycharmProjects/noaa"
PROC_SCRIPT="${PROJ_DIR}/swpc/process_timelapse.sh"

# Define targets: [Folder Name]|[Label]
TARGETS=(
    "swpc/aurora/north/images|aurora_north"
    "swpc/aurora/south/images|aurora_south"
    "noaa/goes_east/images|goes_east"
    "noaa/goes_west/images|goes_west"
)

echo -e "\033[0;34m>>> Launching Parallel Render Engine <<<\033[0m"

# -P 2 runs two ffmpeg instances at once. Adjust based on your CPU heat/load.
printf "%s\n" "${TARGETS[@]}" | xargs -P 2 -I {} bash -c '
    IFS="|" read -r dir label <<< "{}"
    bash "'$PROC_SCRIPT'" "/home/reza/Videos/satellite/$dir" "$label"
'

echo -e "\033[0;32m>>> All daily renders complete. <<<\033[0m"