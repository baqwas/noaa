#!/usr/bin/env python3
"""
================================================================================
🌍 MODULE        : epic_fetcher.py
🚀 DESCRIPTION   : NASA DSCOVR EPIC Multi-Continental Ingest Engine.
                   Calculates and archives "Solar Noon" snapshots for
                   Americas, EMEA, and APAC regions using CoreService.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.8.0 (CoreService Integration)
📅 UPDATED       : 2026-03-01
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
📋 WORKFLOW PROCESSING:
    1. 🛡️  Load CoreService (Config, SMTP, and Environment).
    2. 📡  Query NASA EPIC 'Natural' Color API for latest metadata.
    3. 📍  Mapping: Match target longitudes to centroid coordinates.
    4. 📥  Idempotent Download: Skip existing frames; archive new imagery.
    5. 📧  Alerting: Dispatch SMTP failure reports via CoreService.
================================================================================
"""

import os
import sys
import logging
import requests
import importlib.util
from datetime import datetime
from pathlib import Path

# --- 📁 Absolute File Import (Conflict Resolution) ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJ_ROOT = SCRIPT_DIR.parent
CORE_PATH = PROJ_ROOT / "utilities" / "core_service.py"

if not CORE_PATH.exists():
    print(f"❌ Critical: core_service.py not found at {CORE_PATH}")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("core_service_local", CORE_PATH)
core_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_mod)

# --- 🛠️ Instantiate Core Service ---
service = core_mod.CoreService(config_path="../config.toml")
config = service.config

# --- 🛰️ Target Coordinates (Longitude for Solar Noon) ---
CONTINENTS = {
    "Americas": -95.0,  # Central US/Mexico
    "Africa_Europe": 15.0,  # Central European Time
    "Asia_Australia": 120.0  # East Asia / Western Australia
}

# --- 🎨 Colors ---
C_YELLOW = '\033[1;33m';
C_RED = '\033[0;31m';
C_GREEN = '\033[0;32m';
C_NC = '\033[0m'


def setup_logging(cfg):
    """Initializes logging based on epic configuration."""
    log_path = cfg.get('epic', {}).get('log_dir', SCRIPT_DIR / "logs")
    log_dir = Path(log_path)
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "epic_fetcher.log",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_best_frame(metadata: list, target_lon: float) -> dict:
    """Calculates the frame with the smallest longitudinal delta to target."""
    return min(metadata, key=lambda x: abs(x['centroid_coordinates']['lon'] - target_lon))


def main():
    setup_logging(config)
    print(f"{C_YELLOW}🚀 [INIT] Starting NASA EPIC Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C_NC}")

    epic_cfg = config.get('epic', {})
    storage_root = Path(epic_cfg.get('instrument_root', '/home/reza/Videos/satellite/epic'))

    try:
        # 1. Fetch Metadata from NASA
        api_url = "https://epic.gsfc.nasa.gov/api/natural"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        metadata = response.json()

        if not metadata:
            print("⚠️ [IDLE] No new metadata returned from NASA API.")
            return

        # 2. Process Geographical Targets
        for continent, lon in CONTINENTS.items():
            frame = get_best_frame(metadata, lon)
            img_id = frame['image']
            # Convert date 2026-03-01 to URL path 2026/03/01
            date_path = frame['date'].split(" ")[0].replace("-", "/")

            img_dir = storage_root / continent / "images"
            img_dir.mkdir(parents=True, exist_ok=True)
            save_path = img_dir / f"{img_id}.png"

            if save_path.exists():
                print(f"⏭️  {continent:.<25} Already cached ({img_id})")
                continue

            # 3. Download Logic
            dl_url = f"https://epic.gsfc.nasa.gov/archive/natural/{date_path}/png/{img_id}.png"
            print(f"📥 {continent:.<25} Fetching frame {img_id}... ", end="", flush=True)

            img_data = requests.get(dl_url, timeout=60)
            img_data.raise_for_status()

            with open(save_path, 'wb') as f:
                f.write(img_data.content)

            print(f"{C_GREEN}[OK]{C_NC}")
            logging.info(f"✅ Archived {continent} frame: {img_id}")

    except Exception as e:
        err_msg = f"❌ [RUNTIME ERROR] EPIC Ingest failed: {e}"
        print(f"{C_RED}{err_msg}{C_NC}")
        logging.error(err_msg)

        # Dispatch alerqt via CoreService SMTP
        service.send_email(
            subject="🛰️ EPIC Engine Alert",
            body=f"Critical failure in EPIC ingest logic.\nTimestamp: {datetime.now()}\nError: {e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()