#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gen_dashboard.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.1.4
📅 LAST UPDATE  : 2026-03-11
===============================================================================
📑 VERSION HISTORY:
    - 1.1.2: Added .png support and flattened directory logic.
    - 1.1.3: Fixed init_mqtt() TypeError (removed positional arg).
    - 1.1.4: DYNAMIC SYNC. Replaced hardcoded subdirs with dynamic discovery
             from config.toml [[gibs.layers]]. Improved missing tile logging.
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
config = get_config()


class DashboardGenerator:
    def __init__(self):
        self.gibs_cfg = config.get('gibs', {})
        # Aligned with gibs_fetcher.py v2.8.3
        self.instr_root = Path(self.gibs_cfg.get('images_dir', '/tmp/satellite'))
        self.output_dir = self.instr_root / "dashboards"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # FIXED: v1.1.3 fix for init_mqtt() taking 0 arguments
        self.mqtt_client = init_mqtt()
        self.clr = TerminalColor()

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("BeUlta.Dashboard")

    def generate_composite(self):
        """Dynamically identifies layers from config and stitches tiles."""
        # Dashboard always targets T-1
        target_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        valid_tiles = []

        # 🚀 DYNAMIC DISCOVERY: Pulling names directly from the [gibs.layers] table
        layers_config = self.gibs_cfg.get('layers', [])
        subdirs = [layer.get('name') for layer in layers_config if layer.get('name')]

        if not subdirs:
            self.logger.error("❌ ERR_CFG_002: No layers defined in config.toml [[gibs.layers]]")
            return

        self.logger.info(f"🔍 Scanning {len(subdirs)} layers for date: {target_date}")

        for sd in subdirs:
            layer_path = self.instr_root / sd

            # Search for both JPG and PNG (matching new NASA GIBS requirements)
            matches = list(layer_path.glob(f"*{target_date}.*"))
            image_matches = [m for m in matches if m.suffix.lower() in ['.jpg', '.png']]

            if image_matches:
                valid_tiles.append(str(image_matches[0]))
                self.logger.info(f"📍 Found tile: {sd} -> {image_matches[0].name}")
            else:
                self.logger.warning(f"⚠️ Missing tile: {sd} (Check fetcher logs for NASA_REJECTED)")

        if not valid_tiles:
            self.logger.error(f"❌ ERR_IMG_001: No images found for {target_date} in {self.instr_root}")
            return

        output_file = self.output_dir / f"BeUlta_Dashboard_{target_date}.jpg"

        # ImageMagick montage command
        # Note: -tile 2x2 will wrap if you have more than 4 layers.
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
                if self.mqtt_client:
                    self.mqtt_client.publish("beulta/dashboard/status", f"CREATED_{target_date}")
            else:
                self.logger.error(f"🚨 ERR_IMG_002: ImageMagick Error: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Execution Error: {e}")


if __name__ == "__main__":
    gen = DashboardGenerator()
    gen.generate_composite()
