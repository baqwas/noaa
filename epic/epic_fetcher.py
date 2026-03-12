#!/usr/bin/env python3
"""
================================================================================
🌍 MODULE        : epic_fetcher.py
🚀 DESCRIPTION   : NASA DSCOVR EPIC Multi-Continental Ingest Engine.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.9.0 (Forensic HTTP Auditing)
📅 UPDATED       : 2026-03-11
================================================================================
📜 VERSION HISTORY:
    - 1.8.0: CoreService Integration and continental mapping.
    - 1.9.0: FORENSIC UPDATE. Added deep HTTP error auditing. Captures URLs,
             Status Codes, and Response Payloads for substantive reporting.
             Introduced [IDLE] and [RUNTIME ERROR] tags for shell-scrapers.
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
    print(f"❌ [CRITICAL] core_service.py not found at {CORE_PATH}")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("core_service", CORE_PATH)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

# --- 🎨 Terminal Styling ---
C_RED = "\033[0;31m"
C_GREEN = "\033[0;32m"
C_YELLOW = "\033[1;33m"
C_NC = "\033[0m"

# --- 🛰️ Target Continents & Longitudes ---
CONTINENTS = {
    "Americas": -95.0,
    "Africa_Europe": 15.0,
    "Asia_Australia": 120.0
}


def get_best_frame(metadata, target_lon):
    """Finds the frame whose centroid is closest to the target longitude."""
    return min(metadata, key=lambda x: abs(x['centroid_coordinates']['lon'] - target_lon))


def run_ingest():
    try:
        config = core.get_config()
        storage_root = Path(config.get('epic', {}).get('storage_dir', '/tmp/epic'))

        # 1. Query NASA API
        api_url = "https://epic.gsfc.nasa.gov/api/natural"
        print(f"📡 Querying NASA EPIC API... ", end="", flush=True)

        response = requests.get(api_url, timeout=30)

        if response.status_code != 200:
            print(f"{C_RED}[FAILED]{C_NC}")
            print(f"FAILED_URL : {api_url}")
            print(f"HTTP_CODE  : {response.status_code}")
            print(f"RESPONSE   : {response.text[:500]}")
            logging.error(f"❌ [RUNTIME ERROR] API Access Failed: {response.status_code}")
            sys.exit(1)

        metadata = response.json()

        if not metadata:
            print(f"{C_YELLOW}[IDLE]{C_NC}")
            print("💡 NOTICE: NASA has no new natural color metadata for this cycle.")
            logging.info("⚠️  [IDLE] No new metadata from NASA.")
            return

        print(f"{C_GREEN}[OK]{C_NC}")

        # 2. Process Regional Frames
        for continent, lon in CONTINENTS.items():
            frame = get_best_frame(metadata, lon)
            img_id = frame['image']
            date_path = frame['date'].split(" ")[0].replace("-", "/")

            img_dir = storage_root / continent / "images"
            img_dir.mkdir(parents=True, exist_ok=True)
            save_path = img_dir / f"{img_id}.png"

            if save_path.exists():
                print(f"⏭️  {continent:.<25} Already cached ({img_id})")
                continue

            # 3. Forensic Download Logic
            dl_url = f"https://epic.gsfc.nasa.gov/archive/natural/{date_path}/png/{img_id}.png"
            print(f"📥 {continent:.<25} Fetching frame {img_id}... ", end="", flush=True)

            try:
                img_data = requests.get(dl_url, timeout=60)

                if img_data.status_code != 200:
                    print(f"{C_RED}[FAILED]{C_NC}")
                    print(f"\n   - FAILED_URL: {dl_url}")
                    print(f"   - HTTP_CODE : {img_data.status_code}")
                    logging.error(f"❌ [RUNTIME ERROR] Download failed for {continent}: {img_data.status_code}")
                    continue

                with open(save_path, 'wb') as f:
                    f.write(img_data.content)

                print(f"{C_GREEN}[OK]{C_NC}")
                logging.info(f"✅ Archived {continent} frame: {img_id}")

            except requests.exceptions.RequestException as e:
                print(f"{C_RED}[ERROR]{C_NC}")
                print(f"   - MSG: {str(e)}")

    except Exception as e:
        err_msg = f"❌ [RUNTIME ERROR] EPIC Ingest failed: {e}"
        print(f"{C_RED}{err_msg}{C_NC}")
        logging.error(err_msg)
        sys.exit(1)


if __name__ == "__main__":
    run_ingest()
