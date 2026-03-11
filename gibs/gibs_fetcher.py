#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gibs_fetcher.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 2.4.2
📅 LAST UPDATE  : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 2.4.0: Migrated to WMS protocol to bypass tile-mapping complexities.
    - 2.4.1: Added centralized BBOX injection and corrected error logging.
    - 2.4.2: Parameterized lookback_days via config.toml (Variable Search Depth).

📝 DESCRIPTION:
    Ingests satellite imagery from NASA GIBS. This version utilizes a
    parametric look-back variable to determine search depth dynamically.
===============================================================================
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
util_path = project_root / "utilities"

if str(util_path) not in sys.path:
    sys.path.insert(0, str(util_path))

try:
    from core_service import TerminalColor, init_mqtt, get_config
except ImportError as e:
    print(f"❌ [CRITICAL] Failed to load core_service: {e}")
    sys.exit(1)


class GIBSFetcher:
    """
    Main ingestion engine for NASA GIBS products.
    Supports dynamic search depth via lookback_days parameter.
    """

    def __init__(self):
        self.clr = TerminalColor()
        self.config = get_config()
        self.mqtt = init_mqtt()

        self.base_output = Path("/home/reza/Videos/satellite/gibs")

        # Load parameters from config.toml
        gibs_cfg = self.config.get('gibs', {})
        self.bbox = gibs_cfg.get('settings', {}).get('texas_bbox', "25.8,-106.6,36.5,-93.5")

        # PARAMETRIC TWEAK: Define the depth of the search window
        self.lookback_days = gibs_cfg.get('lookback_days', 5)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def download_image(self, url, filepath):
        """Downloads image and performs a preliminary XML check."""
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'xml' in content_type or 'text' in content_type:
                return False, "ERR_XML_001: Data not ready (NASA XML Exception)"

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, "Success"

        except Exception as e:
            return False, f"Download Error: {str(e)}"

    def fetch_all_layers(self):
        """Iterates through layers using a dynamic lookback window."""
        self.logger.info(f"{self.clr.HEADER}🛰️  BeUlta Ingest Started | Depth: T-{self.lookback_days}{self.clr.ENDC}")

        layers = self.config.get('gibs', {}).get('layers', [])
        today = datetime.now()

        for layer in layers:
            name = layer['name']
            subdir = layer['subdir']
            raw_url = layer['url']

            output_dir = self.base_output / subdir
            output_dir.mkdir(parents=True, exist_ok=True)

            success = False

            # Line 109 (Approx): Loop limit now uses the variable
            for days_back in range(1, self.lookback_days + 1):
                target_dt = today - timedelta(days=days_back)
                date_str = target_dt.strftime("%Y-%m-%d")

                final_url = raw_url.replace("{TIME}", date_str).replace("{BBOX}", self.bbox)

                filename = f"{name}_{date_str}.jpg"
                save_path = output_dir / filename

                self.logger.info(f"🔄 Processing {name} for {date_str} (T-{days_back})")

                downloaded, msg = self.download_image(final_url, save_path)

                if downloaded:
                    self.logger.info(f"✅ Successfully saved: {filename}")
                    success = True
                    break
                else:
                    self.logger.warning(f"⚠️ {msg}")

            if not success:
                # Line 133 (Approx): Error statement now reflects the dynamic variable
                self.logger.error(
                    f"{self.clr.FAIL}❌ Critical Failure: {name} unavailable after T-{self.lookback_days} attempt.{self.clr.ENDC}")
                if self.mqtt:
                    self.mqtt.publish(f"beulta/ingest/failure", name)


if __name__ == "__main__":
    fetcher = GIBSFetcher()
    fetcher.fetch_all_layers()
