#!/bin/bash
# ==============================================================================
# 🛡️ SYSTEM HARDENING & AUDIT WRAPPER (Consolidated Edition)
# ==============================================================================
# SCRIPT NAME    : check_spatial_audit.sh
# VERSION        : 1.5.0
# AUTHOR         : Matha Goram
# LICENSE        : MIT License (c) 2026 ParkCircus Productions
# PROJECT        : NASA NOAA Observation for Consumers
#
# MIT LICENSE:
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
# RUNS:
#   1. Whenever you modify your data ingestion parameters (e.g., changing
#      the Overpass BBOX or swapping data providers) to ensure the new
#      data source is correctly centered.
#   2. When you add new counties to your data cluster, run it to verify
#      that the centroid remains within the acceptable threshold
#      (15km of Lavon).
#   3. If your dashboard (qlog) shows an AUDIT ALERT or "OUT OF BOUNDS" error,
#      run it manually to isolate which specific data points are causing the drift.
# ==============================================================================

# --- Configuration ---
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
VENV_PY="${PROJ_ROOT}/.venv/bin/python3"
AUDIT_SCRIPT="${PROJ_ROOT}/utilities/check_spatial_audit.py"
WATCHDOG_SCRIPT="${PROJ_ROOT}/utilities/alert_secrets_vulnerable.py"
QLOG_HEALTH_FILE="${PROJ_ROOT}/logs/qlog_system_health.json"

# --- UI Styling ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ICON_SEC="🛡️"; ICON_SWEEP="🧹"; ICON_MAP="📍"; ICON_DASH="📊"; ICON_MAIL="📧"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 INITIATING PROFESSIONAL EXECUTION CHECKLIST${NC}"
echo -e "${BLUE}============================================================${NC}"

# --- PHASE 1: 🔐 SECURITY (ggshield) ---
echo -e "\n${YELLOW}${ICON_SEC} PHASE 1: Secret Scanning...${NC}"
SECRET_STATUS="UNKNOWN"
if command -v ggshield &> /dev/null; then
    ggshield secret scan path . --recursive --exit-zero --yes
    if [ $? -eq 0 ]; then
        SECRET_STATUS="CLEAR"
        echo -e "${GREEN}✅ Security Scan Complete: No secrets found.${NC}"
    else
        SECRET_STATUS="VULNERABLE"
        echo -e "${RED}❌ Security Scan: Secrets detected!${NC}"
    fi
else
    echo -e "${RED}❌ ERROR: ggshield not found.${NC}"
fi

# --- PHASE 2: 🧹 HYGIENE (Git Clean) ---
echo -e "\n${YELLOW}${ICON_SWEEP} PHASE 2: Repository Hygiene...${NC}"
HYGIENE_STATUS="CLEAN"
CLEAN_OUTPUT=$(git clean -nd)
if [ -n "$CLEAN_OUTPUT" ]; then
    HYGIENE_STATUS="DIRTY"
    echo -e "${YELLOW}⚠️  Hygiene Check: Untracked files detected.${NC}"
else
    echo -e "${GREEN}✅ Hygiene Check: Repository is clean.${NC}"
fi

# --- PHASE 3: 📍 INTEGRITY (Spatial Audit) ---
echo -e "\n${YELLOW}${ICON_MAP} PHASE 3: Spatial & Pre-flight Integrity...${NC}"
if [[ -f "$AUDIT_SCRIPT" ]]; then
    AUDIT_RAW=$($VENV_PY "$AUDIT_SCRIPT")
    AUDIT_EXIT=$?
    echo "$AUDIT_RAW"
    DRIFT_KM=$(echo "$AUDIT_RAW" | grep "DRIFT_VALUE:" | cut -d':' -f2)
else
    echo -e "${RED}❌ ERROR: Audit script missing.${NC}"
    exit 1
fi

# --- PHASE 4: 📊 DASHBOARD & ALERT INTEGRATION ---
mkdir -p "$(dirname "$QLOG_HEALTH_FILE")"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
STATUS_VAL=$([[ $AUDIT_EXIT -eq 0 ]] && echo "OK" || echo "FAIL")

echo -e "\n${YELLOW}${ICON_DASH} PHASE 4: Finalizing Dashboard & Alerts...${NC}"

# Update JSON
echo "{\"status\": \"$STATUS_VAL\", \"last_audit\": \"$TIMESTAMP\", \"origin\": \"Lavon, TX\", \"drift_km\": \"$DRIFT_KM\", \"secrets\": \"$SECRET_STATUS\", \"hygiene\": \"$HYGIENE_STATUS\"}" > "$QLOG_HEALTH_FILE"

# Run the Alert Watchdog
if [[ -f "$WATCHDOG_SCRIPT" ]]; then
    $VENV_PY "$WATCHDOG_SCRIPT"
else
    echo -e "${RED}⚠️  Watchdog script missing at $WATCHDOG_SCRIPT${NC}"
fi

# Final Output
if [ $AUDIT_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ SYSTEM HARDENING SUCCESSFUL${NC}"
else
    echo -e "${RED}❌ SYSTEM HARDENING FAILED${NC}"
    exit 1
fi
echo -e "${BLUE}============================================================${NC}"