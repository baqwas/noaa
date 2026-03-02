#!/usr/bin/env python3
"""
================================================================================
🌱 MODULE        : terran_watch.py
🚀 DESCRIPTION   : NASA GIBS (Global Imagery Browse Services) Ingest Engine.
                   Monitors land use and NDVI trends across Texas counties.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.3.2 (Emulated Root Pathing)
📅 UPDATED       : 2026-03-01
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
📋 WORKFLOW PROCESSING:
    1. 🛡️  Path Resolution: Emulates EPIC fetcher logic to reach project root.
    2. ⚙️  Core Service: Bootstraps shared infrastructure from /utilities.
    3. 📍  Spatial Iteration: Processes BBoxes for Harris, Collin, & Kaufman.
    4. 📥  Standardized Archive: Idempotent image storage and naming.
    5. 📧  Failure Alerting: Dispatches SMTP reports via CoreService.
================================================================================
"""

import os
import sys
import logging
import requests
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path

# --- 📁 Standardized Path Discovery (EPIC Fetcher Emulation) ---
# SCRIPT_DIR = /noaa/terran
SCRIPT_DIR = Path(__file__).parent.resolve()
# PROJ_ROOT = /noaa
PROJ_ROOT = SCRIPT_DIR.parent
# CORE_PATH = /noaa/utilities/core_service.py
CORE_PATH = PROJ_ROOT / "utilities" / "core_service.py"

if not CORE_PATH.exists():
    print(f"❌ Critical: core_service.py not found at {CORE_PATH}")
    sys.exit(1)

# Import CoreService from absolute path to prevent .venv/site-packages conflicts
spec = importlib.util.spec_from_file_location("core_service_local", CORE_PATH)
core_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_mod)

# --- 🛠️ Instantiate Core Service ---
# Logic: Service is in /utilities, it looks UP one level for config.toml
service = core_mod.CoreService(config_path="../config.toml")
config = service.config

# --- 🎨 Professional Terminal Colors ---
C_YELLOW = '\033[1;33m';
C_RED = '\033[0;31m';
C_GREEN = '\033[0;32m';
C_NC = '\033[0m'


def setup_logging(cfg):
    """Initializes logging based on paths defined in config.toml."""
    log_dir = Path(cfg.get('terran', {}).get('log_dir', SCRIPT_DIR / "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / "terran_watch.log"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s 🛰️ [%(levelname)s] %(message)s'
    )
    # Stream to console for interactive debugging
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)


def fetch_gibs_image(bbox, layer, date_str):
    """Queries NASA GIBS WMS API for a specific coordinate bounding box."""
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "TIME": date_str,
        "LAYERS": layer,
        "BBOX": bbox,
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "WIDTH": "1600",
        "HEIGHT": "1200",
        "SRS": "EPSG:4326",
        "STYLES": ""
    }

    try:
        response = requests.get(base_url, params=params, timeout=45)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"📡 [GIBS ERROR] Failed to fetch {layer}: {e}")
        return None


def main():
    setup_logging(config)
    print(f"{C_YELLOW}🚀 Starting Terran (GIBS) Ingest: {datetime.now().date()}{C_NC}")

    terran_cfg = config.get('terran', {})
    root_storage = Path(terran_cfg.get('instrument_root', '/home/reza/Videos/satellite/terran'))

    # Process data for "Yesterday" to ensure GIBS tiles are fully processed
    target_date = (datetime.now() - timedelta(days=1))
    date_str = target_date.strftime("%Y-%m-%d")
    file_tag = target_date.strftime("%Y%m%d")

    try:
        for loc in terran_cfg.get('locations', []):
            loc_name = loc['name']
            bbox = loc['bbox']

            for layer in terran_cfg.get('layers', []):
                # Path Pattern: storage_root / county / instrument / images /
                img_dir = root_storage / loc_name / layer / "images"
                img_dir.mkdir(parents=True, exist_ok=True)

                filename = f"{loc_name}_{layer}_{file_tag}.png"
                full_path = img_dir / filename

                if full_path.exists():
                    logging.info(f"💤 [SKIP] {loc_name} | {layer} already exists.")
                    continue

                print(f"📡 Fetching {loc_name:.<12} | {layer:.<15} ", end="", flush=True)

                content = fetch_gibs_image(bbox, layer, date_str)
                if content:
                    with open(full_path, 'wb') as f:
                        f.write(content)
                    print(f"{C_GREEN}[OK]{C_NC}")
                    logging.info(f"✅ Saved: {filename}")
                else:
                    print(f"{C_RED}[FAILED]{C_NC}")

    except Exception as e:
        err_msg = f"❌ [FATAL] Terran Engine Failure: {e}"
        logging.critical(err_msg)
        # Dispatch SMTP alert via the CoreService dispatcher
        service.send_email(
            subject="🌱 TERRAN WATCH ALERT",
            body=f"Critical failure in GIBS ingest sequence.\nDate: {date_str}\nError: {e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()