#!/usr/bin/env python3
"""
================================================================================
📊 MODULE        : goes_daily_status.py
🚀 DESCRIPTION   : Daily storage and ingest audit for GOES-East/West.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.2.5 (Correct Method Signature)
📅 UPDATED       : 2026-03-01
================================================================================
"""

import os
import sys
import io
import importlib.util
from pathlib import Path
from datetime import datetime

# --- 📁 Absolute File Import ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJ_ROOT = SCRIPT_DIR.parent
CORE_PATH = PROJ_ROOT / "utilities" / "core_service.py"

if not CORE_PATH.exists():
    print(f"❌ Critical: core_service.py not found at {CORE_PATH}")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("core_service_local", CORE_PATH)
core_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_mod)

# --- 🛠️ Instantiate Core Service ---
service = core_mod.CoreService(config_path="../config.toml")
config = service.config


def main():
    print(f"🚀 [INIT] Starting GOES Storage Audit...")

    # 1. Compile Audit Report
    report = io.StringIO()
    report.write("==========================================\n")
    report.write("   🛰️ GOES SYSTEM: DAILY HEALTH REPORT   \n")
    report.write(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    report.write("==========================================\n\n")

    report.write(f"{'SATELLITE':<15} | {'IMAGES':<10} | {'VIDEOS':<10}\n")
    report.write("-" * 45 + "\n")

    # 2. Iterate through targets defined in config.toml
    targets = config.get('goes_targets', [])
    for target in targets:
        name = target.get('name', 'Unknown')
        target_dir = Path(target.get('dir', ''))

        if not target_dir.exists():
            report.write(f"{name:<15} | {'DIR MISSING':<10} | {'-':<10}\n")
            continue

        img_p = target_dir / "images"
        vid_p = target_dir / "videos"

        imgs = len(list(img_p.glob("*.jpg"))) if img_p.exists() else 0
        vids = len(list(vid_p.glob("*.mp4"))) if vid_p.exists() else 0

        report.write(f"{name:<15} | {imgs:<10} | {vids:<10}\n")

    report.write("\n" + "=" * 45 + "\n")
    report_text = report.getvalue()
    print(report_text)

    # 3. Corrected Dispatch (Method: send_email, Args: subject, body)
    service.send_email("📊 GOES Daily Health Report", report_text)


if __name__ == "__main__":
    main()
