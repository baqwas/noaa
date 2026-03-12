#!/usr/bin/env python3
"""
================================================================================
📊 MODULE        : epic_dashboard.py
🚀 DESCRIPTION   : Forensic Audit & Health Reporting for DSCOVR EPIC.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.6.0 (Forensic Analysis Update)
📅 UPDATED       : 2026-03-11
================================================================================
📜 VERSION HISTORY:
    - 1.4.7: SMTP Handshake Protocol Correction.
    - 1.5.0: Added regional image counts and delta tracking.
    - 1.6.0: FORENSIC UPDATE. Added --status argument parsing and substantive
             analysis for "0 new images" scenarios (NASA Idle vs. Failure).
================================================================================
"""

import os
import sys
import json
import logging
import datetime
import argparse
import importlib.util
from pathlib import Path

# --- 📁 Absolute File Import (Conflict Resolution) ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJ_ROOT = SCRIPT_DIR.parent
CORE_PATH = PROJ_ROOT / "utilities" / "core_service.py"
STATE_FILE = SCRIPT_DIR / ".dashboard_state.json"

if not CORE_PATH.exists():
    print(f"❌ [CRITICAL] core_service.py not found at {CORE_PATH}")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("core_service", CORE_PATH)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def get_directory_stats(directory):
    """Calculates file count and total size in GB."""
    if not directory.exists():
        return {'count': 0, 'size_gb': 0.0}

    files = list(directory.glob("*.png"))
    total_size = sum(f.stat().st_size for f in files)
    return {
        'count': len(files),
        'size_gb': total_size / (1024 ** 3)
    }


def main():
    # 1. Forensic Argument Parsing
    parser = argparse.ArgumentParser(description="EPIC Forensic Auditor")
    parser.add_argument("--status", default="UNKNOWN", help="Ingest status from shell wrapper")
    args = parser.parse_args()

    print(f"🚀 [INIT] Starting EPIC Forensic Audit...")

    try:
        config = core.get_config()
        storage_root = Path(config.get('epic', {}).get('storage_dir', '/tmp/epic'))

        # Load previous state
        prev_state = {}
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    prev_state = json.load(f)
            except Exception:
                pass

        # 2. Perform Audit
        current_state = {}
        report_lines = [
            "==========================================",
            "   🛰️ DSCOVR EPIC: SYSTEM HEALTH REPORT   ",
            f"   Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "==========================================",
            f"📡 ORIGIN SCRIPT : epic_dashboard.py",
            f"🔍 INGEST STATUS : {args.status}",
            "------------------------------------------\n"
        ]

        regions = ["Americas", "Africa_Europe", "Asia_Australia"]
        total_delta = 0

        for region in regions:
            stats = get_directory_stats(storage_root / region / "images")
            prev_count = prev_state.get(region, {}).get('count', 0)
            delta = stats['count'] - prev_count
            total_delta += delta

            current_state[region] = stats

            report_lines.append(f"🌍 REGION: {region}")
            report_lines.append(f"   📂 Total Images: {stats['count']} (+{delta} new)")
            report_lines.append(f"   💾 Disk Usage:  {stats['size_gb']:.3f} GB")
            report_lines.append("-" * 30)

        # 3. Substantive Forensic Analysis
        if total_delta == 0:
            report_lines.append("\n💡 FORENSIC ANALYSIS:")
            report_lines.append("   - No new frames were added to the archive during this cycle.")

            if "NASA IDLE" in args.status:
                report_lines.append("   - CAUSE: NASA has not yet released new metadata. This is normal.")
            elif "CRITICAL" in args.status:
                report_lines.append(
                    "   - CAUSE: System Failure. Check /home/reza/Videos/satellite/epic/logs/ for HTTP errors.")
            else:
                report_lines.append("   - CAUSE: Standby. All NASA frames are currently cached locally.")

            report_lines.append("-" * 42)

        report_text = "\n".join(report_lines)
        print(report_text)

        # 4. Dispatch via core_service SMTP
        # Note: send_report logic is handled by core_service in your architecture
        core.send_report(config, report_text,
                         subject=f"🛰️ EPIC Health Report: {datetime.datetime.now().strftime('%Y-%m-%d')}")

        # 5. Commit State
        with open(STATE_FILE, "w") as f:
            json.dump(current_state, f, indent=4)

        print("✅ [SUCCESS] Forensic Audit Dispatched.")

    except Exception as e:
        print(f"❌ [ERROR] Audit Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
