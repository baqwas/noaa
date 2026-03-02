#!/bin/bash
"""
===============================================================================
🚀 NAME          : universal_watchdog.sh
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 2.1.0 (Enterprise Automation)
📝 DESCRIPTION   : Dynamically audits all satellite imagery directories.
                   Ensures post-render cleanup success across the entire
                   storage tree.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🔍 Recursive discovery of all 'images' subdirectories.
    2. 📊 Granular file count analysis per module.
    3. 🚨 Threshold-based alerting for cleanup failures.
    4. 🧹 (Optional) Auto-recovery via aged-file purging.

📋 PREREQUISITES :
    - Bash 4.4+ (for mapfile support)
    - GNU findutils
    - Write permissions on /home/reza/Videos/satellite/

📜 LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

# --- ANSI Color Registry ---
GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
MAGENTA='\033[0;35m'; CYAN='\033[0;36m'; NC='\033[0m'

# --- Configuration ---
SATELLITE_ROOT="/home/reza/Videos/satellite"
MAX_IMAGE_THRESHOLD=500  # Alert if images exceed this count after render
RETENTION_DAYS=2         # Safety net for auto-purge (if enabled)

# --- Header Visualization ---
echo -e "${BLUE}🛡️  BEULTA STORAGE WATCHDOG v2.1.0${NC}"
echo -e "${CYAN}📅 Audit Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${MAGENTA}📂 Scanning Root: $SATELLITE_ROOT${NC}"
echo "-----------------------------------------------------------------"

# --- Step 1: Dynamic Discovery ---
# mapfile safely handles paths with spaces
if [[ ! -d "$SATELLITE_ROOT" ]]; then
    echo -e "${RED}💀 CRITICAL ERROR: Storage root not mounted or missing.${NC}"
    exit 1
fi

mapfile -t IMAGE_DIRS < <(find "$SATELLITE_ROOT" -type d -name "images" 2>/dev/null)

if [ ${#IMAGE_DIRS[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: No active imagery directories found.${NC}"
    exit 0
fi

# --- Step 2: Granular Audit ---
for DIR in "${IMAGE_DIRS[@]}"; do
    # Remove hidden carriage returns for cross-platform stability
    DIR=$(echo "$DIR" | tr -d '\r')

    # Relative path for cleaner output
    REL_PATH=${DIR#$SATELLITE_ROOT/}

    # Calculate file count, suppressing permission errors
    IMG_COUNT=$(find "$DIR" -maxdepth 1 -type f 2>/dev/null | wc -l)

    # --- Step 3: Exception Handling & Output ---
    if [ "$IMG_COUNT" -gt "$MAX_IMAGE_THRESHOLD" ]; then
        echo -e "${RED}🚨 CLEANUP FAILURE:${NC} ${YELLOW}$REL_PATH${NC}"
        echo -e "   ├─ Status : CRITICAL"
        echo -e "   └─ Detail : Found ${RED}$IMG_COUNT${NC} files (Threshold: $MAX_IMAGE_THRESHOLD)"

        # --- (Optional) Auto-Recovery Action ---
        # Uncomment the lines below to enable automated safety purging
        # echo -e "   └─ Action : ${BLUE}Purging files older than $RETENTION_DAYS days...${NC}"
        # find "$DIR" -type f -mtime +$RETENTION_DAYS -delete
    else
        echo -e "${GREEN}✅ PASS:${NC} ${YELLOW}$REL_PATH${NC} [${CYAN}$IMG_COUNT files${NC}]"
    fi
done

# --- Footer & Disk Telemetry ---
echo "-----------------------------------------------------------------"
echo -ne "${MAGENTA}📊 DISK UTILIZATION: ${NC}"
df -h "$SATELLITE_ROOT" | awk 'NR==2 {print $3 " used of " $2 " (" $5 ")"}'
echo -e "${BLUE}🏁 Audit complete.${NC}\n"