#!/usr/bin/env python3
"""
================================================================================
📊 MODULE        : goes_daily_status.py
🚀 DESCRIPTION   : Daily storage and ingest audit for GOES-East/West.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.3.0 (Method Alignment & Eye Candy)
📅 UPDATED       : 2026-03-11
================================================================================
"""
import os
import sys
import io
from pathlib import Path
from datetime import datetime

# Path Injection
project_root = Path("/home/reza/PycharmProjects/noaa")
sys.path.insert(0, str(project_root / 'utilities'))

from core_service import CoreService


class GoesStatusNode(CoreService):
    def run_audit(self):
        print(f"🚀 [INIT] Starting GOES Storage Audit...")
        targets = self.config.get('goes_targets', [])

        report = io.StringIO()
        report.write("==========================================\n")
        report.write("   🛰️ GOES SYSTEM: DAILY HEALTH REPORT   \n")
        report.write(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        report.write("==========================================\n\n")
        report.write(f"{'SATELLITE':<15} | {'IMAGES':<10} | {'VIDEOS':<10}\n")
        report.write("-" * 45 + "\n")

        for target in targets:
            name = target.get('name', 'Unknown')
            target_dir = Path(target.get('dir', ''))

            img_count = len(list(target_dir.glob("images/*.jpg"))) if target_dir.exists() else 0
            vid_count = len(list(target_dir.glob("videos/*.mp4"))) if target_dir.exists() else 0

            report.write(f"{name:<15} | {img_count:<10} | {vid_count:<10}\n")

        report.write("\n" + "=" * 45 + "\n")
        report.write("BeUlta Systems Auditor - Satellite Division\n")

        report_text = report.getvalue()
        print(report_text)

        # Standardized method call
        self.send_report(self.config, report_text, subject="📊 GOES Daily Health Report")


if __name__ == "__main__":
    GoesStatusNode().run_audit()
