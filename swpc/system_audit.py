#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : system_audit.py
👤 ROLE         : Forensic Output Auditor & PKM Reporter
🔖 VERSION       : 2.0.0 (PKM Integration)
📅 LAST UPDATE  : 2026-03-14
===============================================================================
"""

import os
import sys
import socket
import datetime
from pathlib import Path

# --- 🛠️ BEULTA PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root / 'utilities'))

try:
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Failed to load core_service: {e}")
    sys.exit(1)


class SystemAuditNode:
    def __init__(self):
        self.core = CoreService()
        self.config = self.core.get_config()
        self.hostname = socket.gethostname()
        self.origin = Path(__file__).name
        self.today_str = datetime.datetime.now().strftime('%Y-%m-%d')

        # Performance Tracking
        self.metrics = {
            "goals_met": 0,
            "goals_total": 0,
            "total_size_mb": 0.0,
            "alerts": []
        }

    def evaluate_pkm(self):
        """
        Calculates Performance Key Metrics against operational goals.
        Goal: 1 Healthy MP4 (>100KB) per defined satellite target.
        """
        egress_cfg = self.config.get('egress', {})
        egress_dir = Path(egress_cfg.get('storage_root', '/home/reza/Videos/satellite/mp4'))

        # Determine total targets from config (across all modules)
        targets = []
        for key in ['goes_east', 'goes_west', 'gibs', 'epic']:
            section = self.config.get(key, {})
            targets.extend(section.get('targets', []))

        self.metrics["goals_total"] = len(targets)

        if not egress_dir.exists():
            return

        videos = list(egress_dir.glob(f"*{self.today_str}*.mp4"))

        for video in videos:
            size_mb = video.stat().st_size / (1024 * 1024)
            self.metrics["total_size_mb"] += size_mb

            if size_mb > 0.1:  # 100KB Threshold
                self.metrics["goals_met"] += 1
            else:
                self.metrics["alerts"].append(f"Low Density: {video.name}")

    def render_report(self):
        """Prints the substantive PKM trace."""
        self.evaluate_pkm()

        met = self.metrics["goals_met"]
        total = self.metrics["goals_total"]
        pct = (met / total * 100) if total > 0 else 0

        print(f"--- PERFORMANCE KEY METRICS (PKM) ---")
        print(f"ORIGIN HOST   : {self.hostname}")
        print(f"ORIGIN SCRIPT : {self.origin}")
        print(f"GOAL TARGET   : {met}/{total} Daily Renders ({pct:.1f}%)")
        print(f"EGRESS VOLUME : {self.metrics['total_size_mb']:.2f} MB")
        print(f"STATUS        : {'✅ ACHIEVED' if pct >= 100 else '⚠️  SUB-OPTIMAL'}")
        print("-" * 38)

        if self.metrics["alerts"]:
            print("BLOCKING ISSUES:")
            for alert in self.metrics["alerts"]:
                print(f"  - {alert}")

    def run(self):
        self.render_report()


if __name__ == "__main__":
    SystemAuditNode().run()
