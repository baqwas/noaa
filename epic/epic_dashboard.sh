#!/usr/bin/env bash
# ==============================================================================
# 📊 NAME          : epic_dashboard.sh
# 🚀 DESCRIPTION   : Orchestration Wrapper for EPIC Health Audit & Archival.
#                   Manages environment, runs Python audit, and performs
#                   monthly time-lapse consolidation.
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.3.0
# 📅 UPDATED       : 2026-03-01
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================

# --- 🎨 ANSI Color Palette ---
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m';
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'

# --- 📁 Path Resolution ---
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJ_ROOT=$(dirname "$SCRIPT_DIR")
VENV="${PROJ_ROOT}/.venv/bin/activate"
PYTHON_AUDIT="${SCRIPT_DIR}/epic_dashboard.py"

# --- 🛰️ Config Extraction (Simple grep for shell speed) ---
# We assume the standard root, but check config.toml if needed
STORAGE_ROOT="/home/reza/Videos/satellite/epic"
DATE_STAMP=$(date +%Y-%m)
DAY_OF_MONTH=$(date +%d)

log_info()    { echo -e "${BLU}📡 [INFO]${NC} $1"; }
log_success() { echo -e "${GRN}✅ [OK]${NC}   $1"; }
log_warn()    { echo -e "${YLW}⚠️  [WARN]${NC} $1"; }
log_error()   { echo -e "${RED}❌ [FAIL]${NC} $1"; }

# --- 🎞️ Monthly Archival Engine ---
# Logic: If it's the 1st of the month, compile the previous month's data.
compile_archives() {
    log_info "Running Monthly Archival Sequence for ${DATE_STAMP}..."
    CONTINENTS=("Americas" "Africa_Europe" "Asia_Australia")

    for region in "${CONTINENTS[@]}"; do
        IMG_DIR="${STORAGE_ROOT}/${region}/images"
        VID_DIR="${STORAGE_ROOT}/${region}/videos"
        OUT_FILE="${VID_DIR}/${region}_Archive_${DATE_STAMP}.mp4"

        if [[ -d "$IMG_DIR" ]] && [ "$(ls -A "$IMG_DIR"/*.png 2>/dev/null)" ]; then
            mkdir -p "$VID_DIR"
            log_info "Compiling permanent archive for $region..."

            # Using 10fps for a smoother long-term review
            ffmpeg -nostdin -y -framerate 10 -pattern_type glob -i "${IMG_DIR}/*.png" \
                   -c:v libx264 -pix_fmt yuv420p -crf 23 \
                   -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
                   "$OUT_FILE" &> /dev/null

            if [[ $? -eq 0 ]]; then
                log_success "Archive Created: $(basename "$OUT_FILE")"
                # Optional: Uncomment to purge images after archival
                # rm "$IMG_DIR"/*.png && log_info "Cleared image cache for $region."
            else
                log_error "Failed to render archive for $region."
            fi
        fi
    done
}

main() {
    echo -e "${CYN}====================================================${NC}"
    echo -e "${CYN}📊  EPIC SYSTEM DASHBOARD & ARCHIVE ENGINE          ${NC}"
    echo -e "${CYN}====================================================${NC}"

    # 1. Environment Guard
    if [[ ! -f "$VENV" ]]; then
        log_error "Virtual Environment missing at $VENV"
        exit 1
    fi
    source "$VENV"

    # 2. Execute Python Health Audit (Dispatches Email)
    if [[ -f "$PYTHON_AUDIT" ]]; then
        python3 "$PYTHON_AUDIT"
    else
        log_error "Audit script not found: $PYTHON_AUDIT"
        exit 1
    fi

    # 3. Monthly Maintenance Trigger
    # Runs on the 1st of every month
    if [[ "$DAY_OF_MONTH" == "01" ]]; then
        compile_archives
    else
        log_info "Skipping monthly archival (Day of month: $DAY_OF_MONTH)."
    fi

    echo -e "${CYN}----------------------------------------------------${NC}"
    log_success "Dashboard sequence complete."
}

main
