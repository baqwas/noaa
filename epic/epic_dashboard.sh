#!/usr/bin/env bash
# ==============================================================================
# 📊 NAME          : epic_dashboard.sh
# 🚀 DESCRIPTION   : Orchestration Wrapper for EPIC Health Audit & Archival.
#                   Now featuring Forensic Status Tracking to differentiate
#                   between idle NASA days and ingest failures.
# 👤 AUTHOR        : Matha Goram
# 🔖 VERSION       : 1.6.0
# 📅 UPDATED       : 2026-03-11
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# ==============================================================================
# 📑 VERSION HISTORY:
#     - 1.3.0: Initial release with monthly archival logic.
#     - 1.5.0: Environment guard and VENV path resolution updates.
#     - 1.6.0: FORENSIC UPDATE. Implemented fetch-log scraping to provide
#              substantive context (IDLE vs FAILED) to the email report.
# ==============================================================================

# --- 🎨 ANSI Color Palette ---
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m';
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'

# --- 📁 Path Resolution ---
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJ_ROOT=$(dirname "$SCRIPT_DIR")
VENV="${PROJ_ROOT}/.venv/bin/activate"
PYTHON_AUDIT="${SCRIPT_DIR}/epic_dashboard.py"

# --- 🛰️ Config & Log Extraction ---
STORAGE_ROOT="/home/reza/Videos/satellite/epic"
DATE_STAMP=$(date +%Y-%m)
DAY_OF_MONTH=$(date +%d)
FETCH_LOG="${STORAGE_ROOT}/logs/fetch_$(date +%Y%m).log"

log_info()    { echo -e "${BLU}📡 [INFO]${NC} $1"; }
log_success() { echo -e "${GRN}✅ [SUCCESS]${NC} $1"; }
log_error()   { echo -e "${RED}🚨 [ERROR]${NC} $1"; }

compile_archives() {
    log_info "Initializing Monthly Archive Sequence..."
    # (Existing ffmpeg logic remains unchanged)
    regions=("Americas" "Africa_Europe" "Asia_Australia")
    for region in "${regions[@]}"; do
        IMG_DIR="${STORAGE_ROOT}/${region}/images"
        OUT_FILE="${STORAGE_ROOT}/${region}/archives/EPIC_${region}_${DATE_STAMP}.mp4"
        mkdir -p "$(dirname "$OUT_FILE")"

        if [[ -d "$IMG_DIR" ]]; then
            ffmpeg -y -framerate 5 -pattern_type glob -i "${IMG_DIR}/*.png" \
                   -c:v libx264 -pix_fmt yuv420p -crf 23 \
                   -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
                   "$OUT_FILE" &> /dev/null

            if [[ $? -eq 0 ]]; then
                log_success "Archive Created: $(basename "$OUT_FILE")"
            else
                log_error "Failed to render archive for $region."
            fi
        fi
    done
}

main() {
    echo -e "${CYN}====================================================${NC}"
    echo -e "${CYN}📊  EPIC SYSTEM DASHBOARD & FORENSIC AUDITOR        ${NC}"
    echo -e "${CYN}====================================================${NC}"

    # 1. Environment Guard
    if [[ ! -f "$VENV" ]]; then
        log_error "Virtual Environment missing at $VENV"
        exit 1
    fi
    source "$VENV"

    # 2. Forensic Analysis of the Fetcher Log
    # We determine if the ingest was successful, idle, or crashed.
    INGEST_STATUS="UNKNOWN (No Log Found)"

    if [[ -f "$FETCH_LOG" ]]; then
        if grep -q "❌ \[RUNTIME ERROR\]" "$FETCH_LOG"; then
            INGEST_STATUS="CRITICAL FAILURE (Check logs for HTTP/JSON errors)"
        elif grep -q "⚠️  \[IDLE\]" "$FETCH_LOG"; then
            INGEST_STATUS="NASA IDLE (No new imagery released yet)"
        elif grep -q "✅ Archived" "$FETCH_LOG"; then
            INGEST_STATUS="ACTIVE (New imagery successfully archived)"
        else
            INGEST_STATUS="STANDBY (No changes detected since last cycle)"
        fi
    fi

    log_info "Forensic Status: $INGEST_STATUS"

    # 3. Execute Python Health Audit (Dispatches Email with Context)
    if [[ -f "$PYTHON_AUDIT" ]]; then
        # We pass the forensic status as a command line argument
        python3 "$PYTHON_AUDIT" --status "$INGEST_STATUS"
    else
        log_error "Audit script not found: $PYTHON_AUDIT"
        exit 1
    fi

    # 4. Monthly Maintenance Trigger
    if [[ "$DAY_OF_MONTH" == "01" ]]; then
        compile_archives
    fi
}

main
