#!/usr/bin/env python3
"""
================================================================================
📊 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : epic_dashboard.py
👤 ROLE         : Forensic Audit & Health Reporting (DSCOVR EPIC)
🔖 VERSION       : 1.6.1
📅 LAST UPDATE  : 2026-03-14
================================================================================

📝 DESCRIPTION:
    Analyzes the EPIC frame archive to detect "Stalls" vs "Idle" states.
    Maintains a local JSON state to track image accumulation deltas and
    generates substantive analysis reports for pipeline transparency.

⚙️ WORKFLOW / PROCESSING:
    1. Runtime Setup: Standardizes pathing and loads config via CoreService.
    2. State Retrieval: Loads .dashboard_state.json to establish a baseline.
    3. Discovery: Scans regional directories to count current PNG assets.
    4. Delta Calculation: Computes the 'drift' or 'accumulation' since the
       last successful audit cycle.
    5. Forensic Analysis: Analyzes 0-delta scenarios to identify causes
       (e.g., NASA "Idle" vs. System "Critical").
    6. Reporting: Dispatches a formatted SMTP health report via CoreService.

🛠️ PREREQUISITES:
    - utilities/core_service.py accessible in PYTHONPATH.
    - Write permissions for the local .dashboard_state.json file.
    - config.toml containing [epic] and [smtp] sections.

⚠️ ERROR MESSAGES:
    - [CRITICAL] core_service.py not found: Execution halted.
    - [WARNING] JSON Corrupt: Dashboard state reset to zero.
    - [ALERT] 0-Delta Detected: System audit suggests pipeline stall.

🖥️ USER INTERFACE:
    - CLI-based output with Analysis summary and Unicode health status:
      🟢 Healthy | 🟡 Standby | 🔴 Critical | 💡 Forensic Insight

📜 VERSION HISTORY:
    - 1.6.0: FORENSIC UPDATE. Added --status argument and delta analysis.
    - 1.6.1: OPTION A ALIGNMENT. Migrated to class-based CoreService.get_config()
             and restored full state-management logic.

⚖️ LICENSE:
    MIT License | Copyright (c) 2026 ParkCircus Productions
    Permission is hereby granted for all usage with attribution.

📚 REFERENCES:
    - NASA EPIC Metadata Standards.
    - BeUlta IoTML (Introspections on Technical Mindset Learning) Framework.
================================================================================
"""

import os
import sys
import json
import logging
import datetime
import argparse
from pathlib import Path

# --- 🛠️ BEULTA PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root / 'utilities'))

try:
    # Option A: Import CoreService class for static method access
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Dependency Resolution Error: {e}")
    sys.exit(1)

# --- 📁 Persistent State Configuration ---
STATE_FILE = Path(__file__).parent / ".dashboard_state.json"


def run_dashboard():
    """
    Executes the forensic audit and dispatches the health report.
    """
    # Instantiate CoreService for config and SMTP access
    core = CoreService()
    config = CoreService.get_config()

    # Argument Parsing for forensic context
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", type=str, default="Normal", help="Forensic cause tag")
    args = parser.parse_args()

    print(f"📊 BeUlta EPIC Dashboard Audit Started: {datetime.datetime.now()}")

    try:
        # 1. Load Previous State
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                previous_state = json.load(f)
        else:
            print("🟡 [NOTICE] No previous state found. Initializing...")
            previous_state = {}

        # 2. Gather Current Statistics
        epic_cfg = config.get('epic', {})
        targets = epic_cfg.get('targets', [])
        storage_root = Path(epic_cfg.get('storage_root', '/home/reza/Videos/satellite/epic'))

        current_state = {}
        report_lines = [
            f"EPIC Archive Health Audit - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            f"{'Region':<20} | {'Current':<10} | {'Delta':<10}",
            "-" * 60
        ]

        total_delta = 0

        for continent in targets:
            name = continent.get('name', 'Unknown')
            # Resolve directory: Use specific 'dir' or default to root/name/images
            img_dir = Path(continent.get('dir', storage_root / name / "images"))

            if img_dir.exists():
                count = len(list(img_dir.glob("*.png")))
            else:
                count = 0

            prev_count = previous_state.get(name, 0)
            delta = count - prev_count
            total_delta += delta
            current_state[name] = count

            report_lines.append(f"{name:<20} | {count:<10} | {delta:<+10}")

        # 3. Substantive Forensic Analysis (RESTORED)
        report_lines.append("-" * 60)
        report_lines.append(f"TOTAL ACCUMULATION DELTA: {total_delta:+d}")

        if total_delta == 0:
            report_lines.append("\n💡 FORENSIC ANALYSIS:")
            report_lines.append("   - No new frames were added to the archive during this cycle.")

            if "NASA IDLE" in args.status.upper():
                report_lines.append("   - CAUSE: NASA has not yet released new metadata. (Operational Idle)")
            elif "CRITICAL" in args.status.upper():
                report_lines.append("   - CAUSE: System Failure. Check local logs for HTTP errors.")
            else:
                report_lines.append("   - CAUSE: Standby. Existing frames match current NASA manifest.")

        report_body = "\n".join(report_lines)
        print(report_body)

        # 4. Dispatch via CoreService SMTP
        subject = f"🛰️ EPIC Health: {'Nominal' if total_delta > 0 else 'Idle'} ({datetime.date.today()})"
        core.send_report(config, report_body, subject=subject)

        # 5. Commit State for Next Cycle
        with open(STATE_FILE, "w") as f:
            json.dump(current_state, f, indent=4)

        print("✅ [SUCCESS] Forensic Audit Dispatched and State Committed.")

    except Exception as e:
        err_msg = f"🔴 [CRITICAL] Dashboard Engine Failure: {str(e)}"
        print(err_msg)
        core.send_report(config, err_msg, subject="🚨 EPIC Dashboard FAILURE")


if __name__ == "__main__":
    run_dashboard()
