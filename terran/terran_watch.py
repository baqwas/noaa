#!/usr/bin/env python3
"""
🌱 NAME          : terran_watch.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.2.0 (Multi-Location Support)
📅 UPDATED       : 2026-02-23
📝 DESCRIPTION   : Parallel monitoring for TX County Land Use & NDVI trends.
                   Supports Collin, Kaufman, and Harris County mapping.
"""

import argparse
import os
import logging
import requests
import tomllib
from datetime import datetime, timedelta
from pathlib import Path


def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "terran_watch.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s 🛰️ [%(levelname)s] %(message)s'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)


def fetch_gibs_image(bbox, layer, date_str):
    """Fetches a high-res snapshot for the defined BBox via WMS."""
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

    # 📏 Resolution increased to 1600x1200 for Harris County detail
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": layer,
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "BBOX": bbox,
        "SRS": "EPSG:4326",
        "WIDTH": "1600",
        "HEIGHT": "1200",
        "TIME": date_str
    }
    try:
        # Increased timeout to 60s for the larger HD payload
        response = requests.get(base_url, params=params, timeout=60)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"❌ Layer {layer} fetch failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="../swpc/config.toml", help="Path to config file")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Error: Configuration file '{args.config}' not found.")
        return

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    setup_logging(config['terran']['log_dir'])
    root = Path(config['terran']['instrument_root'])

    target_date = (datetime.now() - timedelta(days=1))
    date_str = target_date.strftime("%Y-%m-%d")
    file_tag = target_date.strftime("%Y%m%d")

    logging.info(f"🚀 [START] HD Multi-Layer Ingest for {date_str}")

    for loc in config['terran']['locations']:
        loc_name = loc['name']
        bbox = loc['bbox']

        logging.info(f"📍 Location: {loc_name.upper()}")

        for layer in config['terran']['layers']:
            img_dir = root / loc_name / layer / "images"
            img_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{loc_name}_{layer}_{file_tag}.png"
            full_path = img_dir / filename

            if full_path.exists():
                logging.info(f"💤 [SKIP] {loc_name} | {layer} exists.")
                continue

            content = fetch_gibs_image(bbox, layer, date_str)
            if content:
                with open(full_path, "wb") as f:
                    f.write(content)
                logging.info(f"✅ [SUCCESS] Archived {loc_name} {layer} (HD).")

    logging.info(f"🏁 [FINISH] All HD layers processed.")


if __name__ == "__main__":
    main()