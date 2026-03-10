#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gen_dashboard.py
👤 AUTHOR       : Matha Goram
🔖 VERSION      : 1.1.0
📅 LAST UPDATE  : 2026-03-07
⚖️ COPYRIGHT    : (c) 2026 ParkCircus Productions
📜 LICENSE      : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.0.0: Initial Montage Script (Basic ImageMagick wrapper).
    - 1.1.0: Refactored to inherit CoreService; integrated central logging
             and dynamic path resolution from config.toml.

📝 DESCRIPTION:
    Generates a 2x2 multi-spectral composite dashboard using ImageMagick.
    Aggregates the most recent captures from the instrument_root.

🛠️ PREREQUISITES:
    - core_service.py in ~/noaa/utilities
    - ImageMagick installed (`sudo apt install imagemagick`)
===============================================================================
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
util_path = os.path.expanduser("~/noaa/utilities")
if util_path not in sys.path:
    sys.path.insert(0, util_path)

try:
    from core_service import CoreService, TerminalColor
except ImportError:
    print(f"❌ [CRITICAL] Could not find core_service.py in: {util_path}")
    sys.exit(1)


class DashboardGenerator(CoreService):
    """
    Service class for generating daily 2x2 satellite composites.
    """

    def __init__(self):
        super().__init__("DASHBOARD_GEN")
        gibs_cfg = self.config.get("gibs", {})
        self.instr_root = Path(gibs_cfg.get("instrument_root", "/tmp"))
        # Dashboard output goes to the root of the instrument folder
        self.output_dir = self.instr_root / "dashboards"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_composite(self, target_date: str = None):
        """
        Creates a 2x2 montage of the specified date's imagery.
        """
        if not target_date:
            target_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        self.logger.info(f"{self.clr.BOLD}🖥️  Generating BeUlta Dashboard for: {target_date}{self.clr.ENDC}")

        # Define the 4 quadrants for the 2x2 layout
        # (Using the standardized subdirs from config.toml)
        tiles = [
            self.instr_root / "true_color" / f"viirs_true_color_{target_date}.jpg",
            self.instr_root / "night_lights" / f"conus_night_lights_{target_date}.jpg",
            self.instr_root / "precipitation" / f"texas_precipitation_{target_date}.jpg",
            self.instr_root / "aerosols" / f"texas_aerosols_{target_date}.jpg"
        ]

        # Filter for existing files only
        valid_tiles = [str(t) for t in tiles if t.exists()]

        if len(valid_tiles) < 4:
            self.logger.warning(f"⚠️  Incomplete tile set ({len(valid_tiles)}/4). Creating partial dashboard.")

        if not valid_tiles:
            self.logger.error("❌ No valid images found for dashboard. Aborting.")
            return

        output_file = self.output_dir / f"BeUlta_Dashboard_{target_date}.jpg"

        # ImageMagick Montage Command
        cmd = [
            "montage",
            "-background", "#1a1a1a",
            "-fill", "white",
            "-font", "Liberation-Sans",
            "-pointsize", "40",
            "-geometry", "1024x1024+5+5",
            "-tile", "2x2",
            "-title", f"BeUlta Satellite Suite | {target_date}"
        ]
        cmd.extend(valid_tiles)
        cmd.append(str(output_file))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"{self.clr.OKGREEN}✅ Dashboard Created: {output_file.name}{self.clr.ENDC}")
                self.mqtt_publish(f"beulta/dashboard/status", "UPDATED")
            else:
                self.logger.error(f"ImageMagick Error: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Execution Error: {e}")


if __name__ == "__main__":
    gen = DashboardGenerator()
    # If no argument is passed, it defaults to yesterday (T-1)
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    gen.generate_daily_composite(date_arg)
