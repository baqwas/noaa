#!/bin/bash
# -----------------------------------------------------------------------------
# 🛡️ NAME         : goes_watchdog.sh
# 📝 DESCRIPTION  : Verifies existence of today's GOES MP4 files.
#                  Sends email alert via msmtp if files are missing.
# -----------------------------------------------------------------------------

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
DATE_STAMP=$(date +%Y-%m-%d)
BASE_ROOT="/home/reza/Videos/satellite/goes"
RECIPIENT="reza@parkcircus.org"
SATELLITES=("goes_east" "goes_west")
MISSING_SATS=()

for SAT in "${SATELLITES[@]}"; do
    VID_FILE="${BASE_ROOT}/${SAT}/videos/${SAT}_${DATE_STAMP}.mp4"
    if [[ ! -f "$VID_FILE" ]]; then
        MISSING_SATS+=("$SAT")
    fi
done

if [[ ${#MISSING_SATS[@]} -gt 0 ]]; then
    # Directly evaluate the success of the alert transmission
    if echo -e "Subject: ⚠️ GOES Watchdog Alert: Missing Videos\n\nThe following daily time-lapses were NOT found for $DATE_STAMP:\n\n${MISSING_SATS[*]}" | msmtp $RECIPIENT; then
        echo -e "${GREEN}[$(date)] Alert sent for missing videos: ${MISSING_SATS[*]}${NC}"
    else
        echo -e "${RED}[$(date)] Failed to send alert via msmtp${NC}"
    fi
else
    echo -e "${GREEN}[$(date)] All GOES videos verified for $DATE_STAMP.${NC}"
fi