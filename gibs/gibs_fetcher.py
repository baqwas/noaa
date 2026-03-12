#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gibs_fetcher.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 2.9.0
📅 LAST UPDATE  : 2026-03-12
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY (2026-03-12 Audit Trail):
    - 2.8.3: ALIGNMENT UPDATE. Synchronized 'images_dir' and T-1 lookback.
    - 2.9.0: EL NIÑO INTEGRATION. Added conditional BBOX override for
             equatorial monitoring without disrupting Texas-centric defaults.
===============================================================================
"""

import os
import sys
import requests
import logging
import time
import xml.etree.ElementTree as ET
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
    Standardized ingestion engine for NASA GIBS.
    Strictly adheres to WMS 1.3.0 (Latitude-First EPSG:4326).
    """

    def __init__(self):
        self.clr = TerminalColor()
        self.config = get_config()

        self.mqtt = init_mqtt() if self.config.get('mqtt', {}).get('enabled') else None

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("GIBSFetcher")

        gibs_cfg = self.config.get('gibs', {})

        self.bbox = str(gibs_cfg.get('bbox', '25.8,-106.6,36.5,-93.5')).replace(" ", "")
        self.lookback_days = gibs_cfg.get('lookback_days', 5)
        self.output_base = Path(gibs_cfg.get('images_dir', '/home/reza/Videos/satellite/gibs'))
        self.layers = gibs_cfg.get('layers', [])

    def parse_nasa_error(self, response_content):
        """Parses NASA's ServiceException XML for WMS error strings."""
        try:
            root = ET.fromstring(response_content)
            for child in root.iter():
                if 'ServiceException' in child.tag:
                    return child.text.strip() if child.text else "Empty NASA Exception"
        except Exception:
            return "Malformed XML Response"
        return "Unknown Error"

    def download_image(self, url, save_path):
        """Executes the GET request. Logs URL on failure for browser debugging."""
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                if b"ServiceExceptionReport" in response.content:
                    err = self.parse_nasa_error(response.content)
                    return False, f"NASA_REJECTED: {err}"
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True, "SUCCESS"
            self.logger.error(f"❌ HTTP {response.status_code} | Link: {url}")
            return False, f"HTTP_{response.status_code}"
        except Exception as e:
            return False, f"CONN_ERROR: {str(e)}"

    def run(self):
        """Main pipeline loop using strict WMS 1.3.0 logic."""
        self.logger.info(f"🎯 Standard: WMS 1.3.0 | Default BBOX: {self.bbox}")

        if not isinstance(self.layers, list):
            self.logger.error("❌ Config Error: 'layers' block invalid in config.toml")
            return

        for layer_def in self.layers:
            name = layer_def.get('name')
            raw_url = layer_def.get('url')

            if not name or not raw_url:
                continue

            # --- 🌊 BBOX OVERRIDE LOGIC ---
            # Pivot from Texas to Equatorial Pacific for El Niño monitoring.
            # Normal layers use self.bbox; elnino_sst uses the equatorial strip.
            current_bbox = "-15,-170,15,-90" if name == "elnino_sst" else self.bbox

            output_dir = self.output_base / name
            output_dir.mkdir(parents=True, exist_ok=True)

            success = False
            for days_back in range(1, self.lookback_days + 1):
                date_obj = datetime.now() - timedelta(days=days_back)
                date_str = date_obj.strftime('%Y-%m-%d')

                # Apply the current_bbox (either default or overridden)
                final_url = raw_url.strip().replace("{TIME}", date_str).replace("{BBOX}", current_bbox)

                ext = ".png" if "FORMAT=image/png" in final_url else ".jpg"
                filename = f"{name}_{date_str}{ext}"
                save_path = output_dir / filename

                self.logger.info(f"🔄 Processing {name} for {date_str}")
                downloaded, msg = self.download_image(final_url, save_path)

                if downloaded:
                    self.logger.info(f"✅ Saved: {filename}")
                    success = True
                    break
                else:
                    self.logger.warning(f"⚠️ {msg}")

            if not success:
                self.logger.error(f"{self.clr.FAIL}❌ Final Failure: {name} unavailable.{self.clr.ENDC}")
                if self.mqtt:
                    self.mqtt.publish(f"beulta/ingest/failure", name)

if __name__ == "__main__":
    fetcher = GIBSFetcher()
    fetcher.run()
