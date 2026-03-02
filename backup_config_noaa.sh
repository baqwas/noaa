#!/bin/bash
# -----------------------------------------------------------------------------
# 💾 NAME          : backup_config.sh
# 👤 AUTHOR        : Reza (BeUlta) / Matha Goram
# 🔖 VERSION       : 1.1.0 (NAS Mount-Aware)
# 📅 UPDATED       : 2026-02-10
# 📝 DESCRIPTION   : Backs up project source code and TOML configurations to NAS.
#                    Excludes bulky imagery and video assets.
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- 🎨 Configuration & Styling ---
SOURCE_DIR="/home/reza/PycharmProjects/noaa"
# Local mount point for your Synology NAS
BACKUP_DIR="/mnt/synology_backup/beulta_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="beulta_src_${TIMESTAMP}.tar.gz"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

echo -e "${BLUE}🚀 [START] Initiating Source Code Backup...${NC}"

# --- 🛰️ NAS Mount Check ---
# This command checks the mount table for the BACKUP_DIR.
# It specifically prevents writing to the local folder if the NAS is unmounted.
if ! mountpoint -q "/mnt/synology_backup"; then
    echo -e "${RED}❌ [ERROR] NAS is not mounted at /mnt/synology_backup.${NC}"
    echo -e "${RED}⚠️  Aborting to prevent local disk overflow.${NC}"
    exit 1
fi

# --- 🛡️ Directory Validation ---
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo -e "${RED}❌ [ERROR] Source directory not found: $SOURCE_DIR${NC}"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

# --- ⚙️ Compression Logic ---
echo -e "${BLUE}📦 [PACK] Compressing scripts and configs to NAS...${NC}"

tar --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.mp4' \
    --exclude='*.jpg' \
    --exclude='*.png' \
    -czf "${BACKUP_DIR}/${ARCHIVE_NAME}" -C "$SOURCE_DIR" .

# --- 🏁 Exit Status ---
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ [SUCCESS] Backup archived to NAS: ${BOLD}${ARCHIVE_NAME}${NC}"

    # Keep only the last 5 backups on the NAS to manage storage
    ls -t "${BACKUP_DIR}"/beulta_src_*.tar.gz | tail -n +6 | xargs rm -f 2>/dev/null
    echo -e "${BLUE}🧹 [CLEAN] Pruned old archives on NAS (keeping latest 5).${NC}"
else
    echo -e "${RED}❌ [FAIL] Backup failed. Check NAS permissions or network connection.${NC}"
    exit 1
fi
