#!/bin/bash
# ===============================================================================
# 🚀 PROJECT      : BeUlta Satellite Suite
# 📦 MODULE       : gibs_ingest.sh
# 👥 ROLE         : Path-Agnostic Orchestrator & Forensic Auditor
# 🔖 VERSION      : 1.7.0
# 📅 LAST UPDATE  : 2026-03-12
# ⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
# 📜 LICENSE       : MIT License
# ===============================================================================
#
# 📑 VERSION HISTORY (2026-03-12 Audit Trail):
#     - 1.5.1: Initial path-agnostic resolution and basic step execution.
#     - 1.6.0: FORENSIC UPDATE. Implemented stdout capture with error payloads.
#     - 1.7.0: AUTO-AUDIT INTEGRATION.
#              - Replaced system python3 calls with standardized $PYTHON_BIN.
#              - Integrated sync_audit.py (v1.1.0) as the final forensic gate.
#              - Standardized TerminalColor output across all steps.
#
# 📝 DESCRIPTION:
#     The master shell orchestrator for the NASA GIBS pipeline. It manages
#     pre-flight health checks, asset pruning, data ingestion, and forensic
#     auditing. Designed to run seamlessly in both Cron and Manual TTY modes.
#
# 🛠️ PREREQUISITES:
#     - .venv/bin/python within the project root.
#     - utilities/core_service.py for path-agnostic environment checks.
# ===============================================================================

# --- 1. DYNAMIC PATH DISCOVERY ---
# Locates the project root regardless of whether run from home or the gibs/ dir.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [[ "$SCRIPT_DIR" == *"gibs"* ]]; then
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

# Define standardized binary and utility paths
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python3"
UTILITIES_PATH="$PROJECT_ROOT/utilities"

# --- 2. THE TERMINAL COLOR SUITE ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- 3. PRE-FLIGHT INTEGRITY CHECK ---
echo -e "${CYAN}🔍 [INTEGRITY] Validating BeUlta Environment...${NC}"

if [ ! -f "$UTILITIES_PATH/core_service.py" ]; then
    echo -e "${RED}❌ [CRITICAL] ERR_PATH_001: core_service.py not found at: $UTILITIES_PATH${NC}"
    exit 1
fi

if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}❌ [CRITICAL] Virtual Environment binary not found at: $PYTHON_BIN${NC}"
    exit 1
fi

# Move to root to ensure all relative imports in Python scripts resolve correctly
cd "$PROJECT_ROOT" || { echo -e "${RED}❌ Failed to enter Project Root.${NC}"; exit 1; }

# --- 4. EXECUTION PIPELINE ---

# Step 1: NASA Health Check (Metadata Audit)
echo -e "\n${CYAN}🩺 ${GREEN}NASA GIBS Health Check${NC} | Auditor (v1.4.1)"
echo -e "${CYAN}----------------------------------------------------${NC}"
$PYTHON_BIN gibs/satellite_health_check.py
HEALTH_EXIT=$?

if [ $HEALTH_EXIT -eq 1 ]; then
    echo -e "${RED}❌ [ABORT] Critical Health Failure. Ingest suspended to prevent drift corruption.${NC}"
    exit 1
elif [ $HEALTH_EXIT -eq 2 ]; then
    echo -e "${YELLOW}⚠️  [NOTICE] Data drift detected, but proceeding with ingest.${NC}"
fi

# Step 2: Maintenance (Disk Space Optimization)
echo -e "\n${CYAN}🧹 ${GREEN}Maintenance${NC} | Pruning assets older than 30 days..."
$PYTHON_BIN gibs/gibs_cleanup.py

# Step 3: Ingest Data (Core Fetcher)
echo -e "\n${CYAN}----------------------------------------------------${NC}"
echo -e "🛰️  ${GREEN}BeUlta Ingest Started${NC} | Root: $PROJECT_ROOT"
echo -e "${CYAN}----------------------------------------------------${NC}"
$PYTHON_BIN gibs/gibs_fetcher.py

# Step 4: Integrity Inspection (Content Validation)
echo -e "\n${CYAN}🔍 ${GREEN}Image Inspector${NC} | v1.2.1"
echo -e "${CYAN}----------------------------------------------------${NC}"
$PYTHON_BIN gibs/image_inspector.py

# Step 5: Forensic Sync Audit (Precision & Density Check)
# This confirms T-1 alignment and detects low-density (error) files.
echo -e "\n${CYAN}📊 ${GREEN}Forensic Sync Audit${NC} | v1.1.0"
echo -e "${CYAN}----------------------------------------------------${NC}"
$PYTHON_BIN utilities/sync_audit.py

# --- 5. SIGNATURE & COMPLETION ---
echo -e "\n${GREEN}✅ BeUlta Ingest Pipeline Complete.${NC}"
echo "Timestamp: $(date)"
