#!/usr/bin/env python3
# ==============================================================================
# 🛡️ AUDIT & COMPLIANCE DOCUMENTATION
# ==============================================================================
# SCRIPT NAME    : check_spatial_audit.py
# VERSION        : 1.4.0 (Consolidated Edition)
# AUTHOR         : Matha Goram
# LICENSE        : MIT License (c) 2026 ParkCircus Productions
# PROJECT        : NASA NOAA Observation Data for Consumers
# AUDIT CLASS    : GEO-SPATIAL-INTEGRITY-01 | SEC-COMPLIANCE-02
#
# DESCRIPTION:
#   1. Pre-flight Security: Ensures no plain-text secrets are in environment.
#   2. Spatial Integrity: Validates North Texas centroid relative to Lavon, TX.
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
# REFERENCES:
#   1. Haversine Formula for Geodesic Distance
#   2. ISO 19115: Geographic Information Metadata Standard
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

import json
import os
from datetime import datetime

PROJ_ROOT = "/home/reza/PycharmProjects/noaa"
HEALTH_FILE = os.path.join(PROJ_ROOT, "logs/qlog_system_health.json")

# Styling
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

def render():
    print(f"\n{BLUE}{BOLD}═══ QLOG QUANT-OPS DASHBOARD ═══{NC}")
    if not os.path.exists(HEALTH_FILE):
        print(f"{RED}❌ No health data. Run check_spatial_audit.sh{NC}"); return

    with open(HEALTH_FILE, 'r') as f:
        data = json.load(f)

    # 1. Global Status
    status = data.get("status", "UNKNOWN")
    print(f"{BOLD}Status     :{NC}  {GREEN if status=='OK' else RED}[ SYSTEM {status} ]{NC}")

    # 2. Security Status
    secrets = data.get("secrets", "UNKNOWN")
    s_col = GREEN if secrets == "CLEAR" else RED
    print(f"{BOLD}Secrets    :{NC}  {s_col}🛡️ {secrets}{NC}")

    # 3. Git Hygiene
    hygiene = data.get("hygiene", "UNKNOWN")
    h_col = GREEN if hygiene == "CLEAN" else YELLOW
    print(f"{BOLD}Git Hygiene:{NC}  {h_col}🧹 {hygiene}{NC}")

    # 4. Spatial Telemetry
    drift = data.get("drift_km", "N/A")
    try:
        d_val = float(drift)
        d_col = GREEN if d_val < 10 else (YELLOW if d_val <= 15 else RED)
        print(f"{BOLD}Spatial    :{NC}  {d_col}{drift} km drift{NC} ({data.get('origin')})")
    except:
        print(f"{BOLD}Spatial    :{NC}  N/A")

    # 5. Timestamp
    print(f"{BOLD}Last Audit :{NC}  {data.get('last_audit')}")
    print(f"{BLUE}════════════════════════════════{NC}\n")

if __name__ == "__main__":
    render()
