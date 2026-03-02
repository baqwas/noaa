#!/usr/bin/env python3
# ==============================================================================
# 📊 QLOG DASHBOARD: SYSTEM HEALTH SUMMARY
# ==============================================================================
# SCRIPT NAME    : show_qlog_summary.py
# VERSION        : 1.0.0
# AUTHOR         : Matha Goram
# DESCRIPTION    : TUI (Terminal User Interface) for the System Harden Audit.
#                  Displays Security, Hygiene, and Spatial status at a glance.
#
# METRICS:
# Drift Value	 Status	Meaning
# 0.00 - 9.99 km GREEN	Optimal Center.
#                       Your data cluster (Wylie, McKinney, Nevada) is
#                       perfectly balanced around Lavon.
# 10.0 - 15.0 km YELLOW	Skew Detected.
#                       Your data is drifting (likely toward McKinney).
#                       Audit your source BBOX.
# > 15.0 km	     RED	Out of Bounds.
#                       The centroid has left the primary North Texas corridor.
#                       Data signals are unreliable.
# ==============================================================================

import json
import os
from datetime import datetime

PROJ_ROOT = "/home/reza/PycharmProjects/noaa"
HEALTH_FILE = os.path.join(PROJ_ROOT, "logs/qlog_system_health.json")

# Styling
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

def render():
    print(f"\n{BLUE}{BOLD}═══ QLOG NASA/NOAA OBS DASHBOARD ═══{NC}")
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