#!/bin/bash
# ==============================================================================
# 🛡️ SYSTEM HARDENING & AUDIT WRAPPER (Consolidated Edition)
# ==============================================================================
# VERSION        : 1.6.0
# AUTHOR         : Matha Goram
# PROJECT        : NASA NOAA Observation for Consumers
# DESCRIPTION    : Orchestrates secret scans, git hygiene, and spatial audits.
#                  Now features color-coded status icons for terminal display.

# --- CONFIGURATION ---
PROJ_ROOT=$(git rev-parse --show-toplevel)
VENV_PY="$PROJ_ROOT/.venv/bin/python3"
AUDIT_SCRIPT="$PROJ_ROOT/utilities/check_spatial_audit.py"
QLOG_HEALTH_FILE="$PROJ_ROOT/logs/qlog_system_health.json"
THRESHOLD=15

# --- STYLING ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# --- ICONS ---
ICON_SCAN="🔍"
ICON_MAP="📍"
ICON_DASH="📊"

echo -e "${BLUE}${BOLD}🚀 Starting Integrated Security & Spatial Audit...${NC}"

# --- PHASE 1: 🛡️ SECRET SCAN (GitGuardian) ---
echo -e "\n${YELLOW}${ICON_SCAN} PHASE 1: Scanning for leaked secrets...${NC}"
if command -v ggshield &> /dev/null; then
    ggshield secret scan pre-commit
    SECRET_STATUS=$([[ $? -eq 0 ]] && echo "CLEAR" || echo "ALERT")
else
    echo -e "${YELLOW}⚠️ ggshield not found. Skipping local scan.${NC}"
    SECRET_STATUS="UNKNOWN"
fi

# --- PHASE 2: 🧹 GIT HYGIENE ---
echo -e "\n${YELLOW}🧹 PHASE 2: Checking repository hygiene...${NC}"
if [[ -n $(git status --porcelain) ]]; then
    HYGIENE_STATUS="DIRTY"
    echo -e "${YELLOW}⚠️ Hygiene Check: Untracked or modified files detected.${NC}"
else
    HYGIENE_STATUS="CLEAN"
    echo -e "${GREEN}✅ Hygiene Check: Repository is clean.${NC}"
fi

# --- PHASE 3: 📍 INTEGRITY (Spatial Audit) ---
echo -e "\n${YELLOW}${ICON_MAP} PHASE 3: Spatial & Pre-flight Integrity...${NC}"
if [[ -f "$AUDIT_SCRIPT" ]]; then
    # Capture the output from the Python script
    AUDIT_RAW=$($VENV_PY "$AUDIT_SCRIPT")
    AUDIT_EXIT=$?

    # Extract numerical drift value
    DRIFT_KM=$(echo "$AUDIT_RAW" | grep "DRIFT_VALUE:" | cut -d':' -f2 | xargs)

    # If DRIFT_KM is empty (e.g. script crashed), default to 0 for logic
    [[ -z "$DRIFT_KM" ]] && DRIFT_KM="0.00"
else
    echo -e "${RED}❌ ERROR: Audit script missing at $AUDIT_SCRIPT${NC}"
    exit 1
fi

# --- PHASE 4: 📊 DASHBOARD & ALERT INTEGRATION ---
mkdir -p "$(dirname "$QLOG_HEALTH_FILE")"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
STATUS_VAL=$([[ $AUDIT_EXIT -eq 0 ]] && echo "OK" || echo "FAIL")

# Floating point comparison using 'bc'
if (( $(echo "$DRIFT_KM <= $THRESHOLD" | bc -l) )); then
    DRIFT_ICON="🟢"
else
    DRIFT_ICON="🔴"
fi

# Update JSON Log
echo "{\"status\": \"$STATUS_VAL\", \"last_audit\": \"$TIMESTAMP\", \"origin\": \"Lavon, TX\", \"drift_km\": \"$DRIFT_KM\", \"secrets\": \"$SECRET_STATUS\", \"hygiene\": \"$HYGIENE_STATUS\"}" > "$QLOG_HEALTH_FILE"

# --- FINAL TERMINAL OUTPUT ---
echo -e "\n${YELLOW}${ICON_DASH} PHASE 4: Finalizing Dashboard...${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BOLD}FINAL STATUS  :${NC} $STATUS_VAL"
echo -e "${BOLD}SPATIAL DRIFT :${NC} $DRIFT_ICON $DRIFT_KM km"
echo -e "${BOLD}SECRETS       :${NC} $SECRET_STATUS"
echo -e "${BOLD}LAST AUDIT    :${NC} $TIMESTAMP"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# Exit with the status of the audit script
exit $AUDIT_EXIT
