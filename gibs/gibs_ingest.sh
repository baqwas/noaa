#!/bin/bash
# ===============================================================================
# 🚀 PROJECT      : BeUlta Satellite Suite
# 📦 MODULE       : gibs_ingest.sh
# 👥 ROLE         : Path-Agnostic Orchestrator Bash Wrapper
# 🔖 VERSION      : 1.5.1
# 📅 LAST UPDATE  : 2026-03-10
# ===============================================================================

# --- 1. DYNAMIC PATH DISCOVERY ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Resolve PROJECT_ROOT
if [[ "$SCRIPT_DIR" == *"gibs"* ]]; then
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

UTILITIES_PATH="$PROJECT_ROOT/utilities"

# --- 2. PRE-FLIGHT INTEGRITY CHECK ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🔍 [INTEGRITY] Validating BeUlta Environment...${NC}"

if [ ! -f "$UTILITIES_PATH/core_service.py" ]; then
    echo -e "${RED}❌ [CRITICAL] core_service.py not found at: $UTILITIES_PATH${NC}"
    exit 1
fi

# --- 3. ENVIRONMENT BOOTSTRAP ---
cd "$PROJECT_ROOT" || { echo -e "${RED}❌ Failed to enter $PROJECT_ROOT${NC}"; exit 1; }

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No .venv found. Running with system python3.${NC}"
fi

export PYTHONPATH="$UTILITIES_PATH:$PROJECT_ROOT:$PYTHONPATH"

# --- 4. EXECUTION PIPELINE ---

# Step 1: NASA GIBS Metadata Health Check (v1.4.0)
echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🩺 ${GREEN}NASA GIBS Health Check${NC} | Auditor (v1.4.0)"
echo -e "${CYAN}----------------------------------------------------${NC}"
python3 gibs/satellite_health_check.py
HEALTH_EXIT=$?

if [ $HEALTH_EXIT -eq 1 ]; then
    echo -e "${RED}❌ [ABORT] Critical Health Failure. Check SMTP/Network.${NC}"
    exit 1
elif [ $HEALTH_EXIT -eq 2 ]; then
    echo -e "${YELLOW}⚠️  [NOTICE] Data drift detected, but proceeding with ingest.${NC}"
fi

echo "🧹 [MAINTENANCE] Pruning assets older than 30 days..."
/home/reza/PycharmProjects/noaa/.venv/bin/python /home/reza/PycharmProjects/noaa/gibs/gibs_cleanup.py

# Step 2: Ingest Data
echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🛰️  ${GREEN}BeUlta Ingest Started${NC} | Root: $PROJECT_ROOT"
echo -e "${CYAN}----------------------------------------------------${NC}"
python3 gibs/gibs_fetcher.py

# Step 3: Integrity Inspection
echo -e "\n${CYAN}🔍 ${GREEN}Inspector${NC} | v1.1.2"
echo -e "${CYAN}----------------------------------------------------${NC}"
python3 gibs/image_inspector.py

# Step 4: Dashboard Generation
echo -e "\n${CYAN}🖥️  ${GREEN}Dashboard Generation${NC}"
echo -e "${CYAN}----------------------------------------------------${NC}"
python3 gibs/gen_dashboard.py

# Step 5: Video Sequence Generation
echo -e "\n${CYAN}🎞️  ${GREEN}Video Generation${NC}"
echo -e "${CYAN}----------------------------------------------------${NC}"
python3 gibs/gen_video.py

echo -e "\n${GREEN}🏁 BeUlta Pipeline Complete.${NC}"
