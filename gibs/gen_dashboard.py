#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gen_dashboard.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.1.1
📅 LAST UPDATE  : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.0.0: Initial Montage Script (Basic ImageMagick wrapper).
    - 1.1.0: Refactored to inherit CoreService class (Deprecated).
    - 1.1.1: Handshake 2.4.0 Migration. Switched to functional initialization
             and standardized PycharmProjects path resolution.

📝 DESCRIPTION:
    Generates a 2x2 multi-spectral composite dashboard using ImageMagick.
    Aggregates the most recent captures from the instrument_root defined
    in the global configuration.

🛠️ PREREQUISITES:
    - core_service.py v2.4.0 in ~/PycharmProjects/noaa/utilities
    - ImageMagick installed (`sudo apt install imagemagick`)

[Workflow Pipeline Description]
1. Path Injection: Forces local utilities path to the front of sys.path.
2. Configuration: Hydrates settings via core_service.get_config().
3. Tile Discovery: Scans instrument subdirectories for the latest T-1 JPEGs.
4. Composition: Executes 'montage' to create a labeled 2048x2048 grid.
5. Telemetry: Updates MQTT topic 'beulta/dashboard/status'.

[Error Messages Summary]
- "ERR_PATH_001": Critical failure locating the utilities directory.
- "ERR_IMG_002" : ImageMagick 'montage' execution failure.
===============================================================================
"""

import os
import sys
import subprocess
import logging
import datetime
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
project_root = "/home/reza/PycharmProjects/noaa"
util_path = os.path.join(project_root, "utilities")

if util_path not in sys.path:
    sys.path.insert(0, util_path)

try:
    from core_service import get_config, init_mqtt, TerminalColor
except ImportError:
    print(f"❌ [CRITICAL] ERR_PATH_001: Could not find core_service.py in: {util_path}")
    sys.exit(1)

# --- ⚙️ INITIALIZATION ---
TC = TerminalColor()
config = get_config()


class DashboardGenerator:
    def __init__(self):
        self.gibs_cfg = config.get('gibs', {})
        self.instr_root = Path(self.gibs_cfg.get('images_dir', '/home/reza/Videos/satellite/gibs'))
        self.output_dir = self.instr_root / "dashboards"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.mqtt_client = init_mqtt()
        self.clr = TerminalColor()

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("BeUlta.Dashboard")

    def mqtt_publish(self, topic, payload):
        if self.mqtt_client:
            self.mqtt_client.publish(topic, payload, retain=True)

    def generate_composite(self):
        """Finds latest tiles and stitches them into a 2x2 grid."""
        target_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        valid_tiles = []

        # Subdirectories to pull from for the 2x2 grid
        subdirs = ["viirs_true_color", "night_lights", "aerosol_optical_depth", "precipitable_water"]

        for sd in subdirs:
            img_path = self.instr_root / sd / "images"
            # Search for the specific T-1 file
            matches = list(img_path.glob(f"*{target_date}.jpg"))
            if matches:
                valid_tiles.append(str(matches[0]))

        if not valid_tiles:
            self.logger.error("❌ ERR_IMG_001: No valid images found for T-1 dashboard.")
            return

        output_file = self.output_dir / f"BeUlta_Dashboard_{target_date}.jpg"

        cmd = [
            "montage",
            "-background", "#1a1a1a",
            "-fill", "white",
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
                self.mqtt_publish("beulta/dashboard/status", "UPDATED")
            else:
                self.logger.error(f"🚨 ERR_IMG_002: ImageMagick Error: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Execution Error: {e}")


if __name__ == "__main__":
    gen = DashboardGenerator()
    gen.generate_composite()
