#!/bin/bash
# ===============================================================================
# 🚀 PROJECT      : BeUlta Satellite Suite
# 📦 MODULE       : gibs_ingest.sh
# 👥 ROLE         : Orchestrator Bash Wrapper (Finalized Suite)
# 🔖 VERSION      : 1.2.0
# 📅 LAST UPDATE  : 2026-03-07
# ===============================================================================

# --- 1. Environment & Path Setup ---
PROJECT_ROOT="/home/reza/PycharmProjects/noaa"
UTILITIES_PATH="$HOME/noaa/utilities"

# Standardizing output color for the bash wrapper
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

cd "$PROJECT_ROOT" || { echo "❌ Failed to enter $PROJECT_ROOT"; exit 1; }
source .venv/bin/activate || { echo "❌ Failed to activate .venv"; exit 1; }

# Ensure Python looks in the utilities folder for core_service.py
export PYTHONPATH="$UTILITIES_PATH:$PROJECT_ROOT:$PYTHONPATH"

echo -e "${CYAN}----------------------------------------------------${NC}"
echo -e "🛰️  ${GREEN}BeUlta Ingest Started${NC} | Ingest (v1.3.0)"
echo -e "${CYAN}----------------------------------------------------${NC}"
# Ingest T-1 with T-2 Fallback
python3 gibs/gibs_fetcher.py

echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🔍 ${GREEN}BeUlta Integrity Inspection${NC} | Inspector (v1.1.0)"
echo -e "${CYAN}----------------------------------------------------${NC}"
# Audit JPEGs for corruption or NASA XML errors
python3 gibs/image_inspector.py

echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🖥️  ${GREEN}BeUlta Dashboard Generation${NC} | Dashboard (v1.1.0)"
echo -e "${CYAN}----------------------------------------------------${NC}"
# Generate 2x2 multi-spectral composite
python3 gibs/gen_dashboard.py

echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🎞️  ${GREEN}BeUlta Video Sequence Generation${NC} | Video (v1.2.0)"
echo -e "${CYAN}----------------------------------------------------${NC}"
# Stitch weekly captures into time-lapse MP4s
python3 gibs/gen_video.py

echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🩺 ${GREEN}NASA GIBS Metadata Health Check${NC} | Auditor (v1.3.0)"
echo -e "${CYAN}----------------------------------------------------${NC}"
# Runs the metadata check. -v provides console output alongside the email alert.
python3 gibs/satellite_health_check.py -v

echo -e "\n${GREEN}🏁 BeUlta Pipeline Complete.${NC}\n"
