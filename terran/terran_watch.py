#!/usr/bin/env python3
"""
🌱 NAME          : terran_watch.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.1.0 (Unified & Iconified)
📅 UPDATED       : 2026-02-10
📝 DESCRIPTION   : Parallel monitoring for Collin County Land Use & NDVI trends.
                   Uses NASA GIBS WMS for high-res terrestrial snapshots.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
"""

import argparse
import os
import logging
import requests
import tomllib
from datetime import datetime, timedelta

# --- 🎨 Standardized Logging with Icons ---
def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "terran_watch.log")
    
    # Using specific icons for log levels to assist in rapid auditing
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s 🛰️ [%(levelname)s] %(message)s'
    )
    # Console output for manual execution
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

def fetch_gibs_image(config, layer, date_str):
    """Fetches a high-res snapshot for the defined BBox via WMS."""
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": layer,
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "BBOX": config['terran']['bbox'],
        "SRS": "EPSG:4326",
        "WIDTH": "1200",
        "HEIGHT": "800",
        "TIME": date_str
    }
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"❌ Layer {layer} fetch failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    # Load configuration using the standardized TOML parser
    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    setup_logging(config['terran']['log_dir'])

    # GIBS data usually has a 1-day latency; targeting 'yesterday'
    target_date = (datetime.now() - timedelta(days=1))
    date_str = target_date.strftime("%Y-%m-%d")
    file_tag = target_date.strftime("%Y%m%d")

    root = config['terran']['instrument_root']
    
    logging.info(f"🚀 [START] Initiating Terran Ingest for {date_str}")

    for layer in config['terran']['layers']:
        # Hierarchical Path: .../terran/LAYER_NAME/images/
        img_dir = os.path.join(root, layer, "images")
        os.makedirs(img_dir, exist_ok=True)

        filename = f"{layer}_{file_tag}.png"
        full_path = os.path.join(img_dir, filename)

        if os.path.exists(full_path):
            logging.info(f"💤 [SKIP] {layer}: Frame already exists for {date_str}")
            continue

        content = fetch_gibs_image(config, layer, date_str)
        if content:
            with open(full_path, "wb") as f:
                f.write(content)
            logging.info(f"✅ [SUCCESS] Archived {layer} image.")

    logging.info(f"🏁 [FINISH] Terran cycle complete.")

if __name__ == "__main__":
    main()

