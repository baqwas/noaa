#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : system_audit.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.9.0 (Video-Centric Audit Logic)
📝 DESCRIPTION   : Forensic Auditor that verifies the presence of daily
                   rendered MP4s across the entire satellite manifest.
===============================================================================
📜 VERSION HISTORY:
    - 1.8.5: Recursive VIIRS scanning and split-sensor tracking.
    - 1.9.0: PIVOT TO EGRESS. Now verifies daily MP4 files instead of raw
             images to confirm the full end-to-end pipeline health.
===============================================================================
"""
import os
import sys
import shutil
import datetime
from pathlib import Path

# Setup pathing for CoreService import
project_root = Path("/home/reza/PycharmProjects/noaa")
sys.path.insert(0, str(project_root / 'utilities'))

from core_service import CoreService


class SystemAuditNode(CoreService):
    def __init__(self):
        super().__init__()
        self.origin_script = Path(__file__).name
        self.stats_log = []
        self.all_humming = True
        self.today_str = datetime.datetime.now().strftime('%Y-%m-%d')

    def check_video_health(self, folder_path, target_name):
        """Verifies if today's rendered MP4 exists in the videos folder."""
        video_dir = folder_path / "videos"
        # Standard naming pattern: target_name_YYYY-MM-DD.mp4
        expected_video = video_dir / f"{target_name}_{self.today_str}.mp4"

        if expected_video.exists() and expected_video.stat().st_size > 1024:
            return True, expected_video.stat().st_size
        return False, 0

    def run_audit(self):
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        print(f"🚀 [INIT] BeUlta Forensic Audit (Video-Centric): {ts}")

        # 1. Manifest definitions matching compile_all_daily.sh
        manifest = {
            'Aurora North': Path("/home/reza/Videos/satellite/swpc/aurora_north"),
            'Aurora South': Path("/home/reza/Videos/satellite/swpc/aurora_south"),
            'LASCO C3': Path("/home/reza/Videos/satellite/swpc/lasco_c3"),
            'LASCO C2': Path("/home/reza/Videos/satellite/swpc/lasco_c2"),
            'GOES-East': Path("/home/reza/Videos/satellite/goes/goes_east"),
            'GOES-West': Path("/home/reza/Videos/satellite/goes/goes_west"),
            'Land Use': Path("/home/reza/Videos/satellite/terran/land_use")
        }

        # 2. Add Dynamic VIIRS Folders
        viirs_root = Path("/home/reza/Videos/satellite/noaa/viirs")
        if viirs_root.exists():
            for sub in viirs_root.iterdir():
                if sub.is_dir():
                    manifest[f"VIIRS:{sub.name}"] = sub

        # 3. Process the Health Checks
        for name, path in manifest.items():
            # Extract internal name for file matching (e.g., VIIRS:true_color -> true_color)
            target_file_name = name.split(':')[-1] if ':' in name else name.lower().replace(' ', '_')

            healthy, size_bytes = self.check_video_health(path, target_file_name)

            if healthy:
                size_mb = size_bytes / (1024 * 1024)
                status_icon, status_text = "🟢", f"Active ({size_mb:.1f} MB Video)"
            else:
                status_icon, status_text = "🔴", "STALLED (No Video Found)"
                self.all_humming = False

            print(f"{status_icon} {name:.<25} {status_text}")
            self.stats_log.append(f"{status_icon} {name:.<18}: {status_text}")

        # 4. Storage Audit
        usage = shutil.disk_usage("/")
        pct = (usage.used / usage.total) * 100

        self.dispatch_formatted_report(ts, pct)

    def dispatch_formatted_report(self, ts, pct):
        subj = "✨ BeUlta: Pipeline Humming" if self.all_humming else "🚨 BeUlta: Pipeline ALERT"

        body = [
            f"BeUlta Health Report [{ts}]",
            f"Source Script: {self.origin_script}",
            "=" * 55,
            "PIPELINE OUTPUT STATUS (MP4 Verification):",
            "\n".join(self.stats_log),
            "",
            f"Storage Usage: {pct:.1f}%",
            "=" * 55,
            "\nRegards,\n\nBeUlta Systems Auditor\nSatellite Archive Division"
        ]
        self.send_report(self.config, "\n".join(body), subject=subj)


if __name__ == "__main__":
    SystemAuditNode().run_audit()
