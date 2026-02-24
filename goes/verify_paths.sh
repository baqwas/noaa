#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# 🔍 NAME         : verify_paths.sh
# 👤 AUTHOR       : Matha Goram
# 🔖 VERSION      : 1.3.0 (Repair Mode Enabled)
# 📅 UPDATED      : 2026-02-24
# 📝 DESCRIPTION  : Diagnostic and self-healing tool for the GOES project.
#                  Verifies file existence and repairs missing directory trees.
#
# 🛠️ WORKFLOW      :
#    1. Parse arguments for --repair flag.
#    2. Validate core system files (Config, Venv, Scripts).
#    3. Parse config.toml for dynamic satellite storage targets.
#    4. Audit/Repair subfolder structures (images/videos/logs).
#
# 📋 PREREQUISITES :
#    - sudo/write permissions for /home/reza/Videos/satellite/goes/
#    - Valid config.toml at the defined project root.
#
# 🖥️ INTERFACE     : CLI (Use --repair to trigger auto-creation)
# ⚠️ ERRORS        : Permission Denied or Missing Config File.
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

# --- UI Styling ---
GREEN='\033[0;32m'; RED='\033[0;31m'; BLUE='\033[0;34m';
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

# --- Arguments ---
REPAIR_MODE=false
[[ "$1" == "--repair" ]] && REPAIR_MODE=true

# --- Path Definitions ---
CONFIG_FILE="${HOME}/PycharmProjects/noaa/swpc/config.toml"
VENV_PATH="${HOME}/PycharmProjects/noaa/.venv/bin/activate"
LOG_DIR="/home/reza/Videos/satellite/goes/logs"

# Core Script Inventory
CORE_FILES=(
    "$CONFIG_FILE"
    "$VENV_PATH"
    "${HOME}/PycharmProjects/noaa/goes/retrieve_goes.py"
    "${HOME}/PycharmProjects/noaa/goes/compile_goes_daily.sh"
)

echo -e "${BLUE}${BOLD}>>> GOES System Path Audit <<<${NC}"
[[ "$REPAIR_MODE" == true ]] && echo -e "${YELLOW}🔧 REPAIR MODE ACTIVE${NC}\n" || echo -e "${BLUE}🔎 READ-ONLY MODE${NC}\n"

# 1. Verify Core Project Infrastructure
echo -e "${BOLD}Checking System Files:${NC}"
for path in "${CORE_FILES[@]}"; do
    if [ -e "$path" ]; then
        echo -e "  [${GREEN} FOUND ${NC}] $path"
    else
        echo -e "  [${RED} MISSING ${NC}] $path"
    fi
done

# 2. Centralized Log Directory Check/Repair
if [ ! -d "$LOG_DIR" ]; then
    if [ "$REPAIR_MODE" == true ]; then
        mkdir -p "$LOG_DIR"
        echo -e "  [${YELLOW} FIXED ${NC}] Created missing Log Dir: $LOG_DIR"
    else
        echo -e "  [${RED} MISSING ${NC}] Log Dir: $LOG_DIR"
    fi
else
    echo -e "  [${GREEN} FOUND ${NC}] Log Dir: $LOG_DIR"
fi

# 3. Dynamic GOES Target Audit
echo -e "\n${BOLD}Checking Satellite Storage (from config.toml):${NC}"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "  [${RED} ERROR ${NC}] config.toml not found. Cannot audit targets."
else
    # Extract directory paths from config using goes_east/goes_west nomenclature
    grep "dir =" "$CONFIG_FILE" | cut -d'"' -f2 | while read -r target_dir; do
        if [ -d "$target_dir" ]; then
            echo -e "  [${GREEN} OK ${NC}] Target: $target_dir"
        else
            if [ "$REPAIR_MODE" == true ]; then
                mkdir -p "$target_dir"
                echo -e "  [${YELLOW} FIXED ${NC}] Created Target: $target_dir"
            else
                echo -e "  [${RED} MISSING ${NC}] Target: $target_dir"
            fi
        fi

        # Audit/Repair Sub-folders
        for sub in "images" "videos"; do
            SUBPATH="${target_dir}/${sub}"
            if [ -d "$SUBPATH" ]; then
                echo -e "      └─ [${GREEN}OK${NC}] /$sub"
            else
                if [ "$REPAIR_MODE" == true ]; then
                    mkdir -p "$SUBPATH"
                    echo -e "      └─ [${YELLOW}FIXED${NC}] Created /$sub"
                else
                    echo -e "      └─ [${RED}!!${NC}] /$sub is missing"
                fi
            fi
        done
    done
fi

echo -e "\n${BLUE}${BOLD}Audit Complete.${NC}"