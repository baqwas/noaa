#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# 🌱 NAME          : terran_deploy.sh
# 📝 DESCRIPTION   : Map Code and Data paths across different volumes/folders.
# 🔖 VERSION       : 1.2.0 (Split-Path Mapping)
# 📅 UPDATED       : 2026-02-23
# -------------------------------------------------------------------------------

# --- 📂 Path Mapping ---
CODE_ROOT="/home/reza/PycharmProjects/noaa/terran"
DATA_ROOT="/home/reza/Videos/satellite/terran"
LOG_DIR="/home/reza/Videos/satellite/terran/logs"
CONFIG_FILE="${CODE_ROOT}/config.toml"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

echo -e "${BLUE}${BOLD}🚀 Starting Terran Split-Path Deployment...${NC}\n"

# --- 1. Infrastructure Setup ---
echo -e "${BLUE}[1/5] Creating Directory Structure...${NC}"
# Create Code, Log, and Video directories
mkdir -p "$CODE_ROOT" "$LOG_DIR" "$DATA_ROOT"
echo -e "📁 Code Root: $CODE_ROOT"
echo -e "📁 Data Root: $DATA_ROOT"
echo -e "📁 Log Root:  $LOG_DIR"
echo -e "${GREEN}✅ Directories verified.${NC}"

# --- 2. Dependency Check ---
echo -e "\n${BLUE}[2/5] Checking System Dependencies...${NC}"
DEPS=("ffmpeg" "bc" "msmtp")
for dep in "${DEPS[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        echo -e "${RED}⚠️  Missing: $dep. Please install via: sudo apt install $dep${NC}"
    else
        echo -e "💎 Found: $dep"
    fi
done

# --- 3. Configuration Generation ---
echo -e "\n${BLUE}[3/5] Syncing config.toml...${NC}"
# We write the DATA_ROOT directly into the config so the Python script knows where to go
cat <<EOF > "$CONFIG_FILE"
[terran]
log_dir = "$LOG_DIR"
instrument_root = "$DATA_ROOT"
bbox = "-96.86,32.86,-96.28,33.45"
layers = [
    "MODIS_Terra_NDVI_8Day",
    "MODIS_Terra_Land_Cover_Type_Yearly"
]
EOF
echo -e "${GREEN}✅ Config generated with instrument_root pointing to Videos folder.${NC}"

# --- 4. SMTP Handshake ---
echo -e "\n${BLUE}[4/5] Testing SMTP Relay...${NC}"
if [[ -f "$HOME/.msmtprc" ]]; then
    echo -e "Subject: Terran Path-Mapping Test\n\nDeployment successful on $(hostname)." | msmtp reza@parkcircus.org
    echo -e "${GREEN}✅ Test email dispatched to reza@parkcircus.org${NC}"
else
    echo -e "${RED}⚠️  ~/.msmtprc not found. Alerts will be disabled.${NC}"
fi

# --- 5. Permissions ---
echo -e "\n${BLUE}[5/5] Finalizing Script Permissions...${NC}"
chmod +x "${CODE_ROOT}"/*.sh
echo -e "${GREEN}✅ Done. All scripts in $CODE_ROOT are now executable.${NC}"

echo -e "\n${GREEN}${BOLD}🎉 Deployment successful!${NC}"