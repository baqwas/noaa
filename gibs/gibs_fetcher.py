#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gibs_fetcher.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 2.8.3
📅 LAST UPDATE  : 2026-03-11
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY (2026-03-11 Audit Trail):
    - 2.8.0: Formalized WMS 1.3.0 as the permanent standard.
    - 2.8.1: Added RAW_DEBUG logging and BBOX space-stripping.
    - 2.8.2: Added URL Debugger for manual 400-error inspection.
    - 2.8.3: ALIGNMENT UPDATE. Synchronized 'images_dir' key with dashboard
             generator and reset lookback to T-1 (range starting at 1).
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

        # Aligned with gen_dashboard.py v1.1.3 (Removed config argument)
        self.mqtt = init_mqtt() if self.config.get('mqtt', {}).get('enabled') else None

        # Logging Setup
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("GIBSFetcher")

        # Load GIBS specific config
        gibs_cfg = self.config.get('gibs', {})

        # ALIGNMENT: Standardized on 'images_dir' key
        self.bbox = str(gibs_cfg.get('bbox', '25.8,-106.6,36.5,-93.5')).replace(" ", "")
        self.lookback_days = gibs_cfg.get('lookback_days', 5)
        self.output_base = Path(gibs_cfg.get('images_dir', '/tmp/satellite'))
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
        """
        Executes the GET request. Logs URL on failure for browser debugging.
        """
        try:
            response = requests.get(url, timeout=15)

            if response.status_code == 200:
                if b"ServiceExceptionReport" in response.content:
                    err = self.parse_nasa_error(response.content)
                    return False, f"NASA_REJECTED: {err}"

                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True, "SUCCESS"

            # 🛑 DEBUGGER: Prints clickable link for browser inspection
            self.logger.error(f"❌ HTTP {response.status_code} | Link: {url}")
            return False, f"HTTP_{response.status_code}"

        except Exception as e:
            return False, f"CONN_ERROR: {str(e)}"

    def run(self):
        """Main pipeline loop using strict WMS 1.3.0 logic."""
        self.logger.info(f"🎯 Standard: WMS 1.3.0 | BBOX: {self.bbox}")

        if not isinstance(self.layers, list):
            self.logger.error("❌ Config Error: 'layers' block missing or invalid in config.toml")
            return

        for layer_def in self.layers:
            name = layer_def.get('name')
            raw_url = layer_def.get('url')

            if not name or not raw_url:
                continue

            # ALIGNMENT: Removed '/images' sub-directory to match dashboard globbing
            output_dir = self.output_base / name
            output_dir.mkdir(parents=True, exist_ok=True)

            success = False
            # ALIGNMENT: range(1, ...) ensures T-1 is processed for the dashboard
            for days_back in range(1, self.lookback_days + 1):
                date_obj = datetime.now() - timedelta(days=days_back)
                date_str = date_obj.strftime('%Y-%m-%d')

                final_url = raw_url.strip().replace("{TIME}", date_str).replace("{BBOX}", self.bbox)

                # Dynamic extension based on config (PNG for overlays, JPG for base)
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
