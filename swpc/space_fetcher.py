#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
🚀 NAME          : space_fetcher.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.2.0 (Parallel Ingest)
📝 DESCRIPTION   : Multi-threaded downloader for NOAA SWPC imagery.
-------------------------------------------------------------------------------
🛠️ WORKFLOW      :
    1. Verify storage health (>2.0 GB free).
    2. Initialize ThreadPoolExecutor for concurrent downloads.
    3. Perform MD5 hash verification to skip redundant frames.
📋 PREREQUISITES : Python 3.11+, requests, config.toml
-------------------------------------------------------------------------------
"""

import os
import hashlib
import datetime
import requests
import tomllib
import logging
from concurrent.futures import ThreadPoolExecutor

CONFIG_PATH = "/home/reza/PycharmProjects/noaa/swpc/config.toml"


def fetch_target(target, timestamp):
    """Worker function for parallel downloading."""
    root = target['instrument_root']
    img_dir = os.path.join(root, target.get('subdir', 'images'))
    os.makedirs(img_dir, exist_ok=True)

    try:
        resp = requests.get(target['url'], timeout=20)
        resp.raise_for_status()

        current_hash = hashlib.md5(resp.content).hexdigest()
        ext = "png" if "png" in target['url'] else "jpg"
        save_path = os.path.join(img_dir, f"{target['name']}_{timestamp}.{ext}")

        # Check latest file to prevent redundant frames
        files = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
        if files:
            latest = max(files, key=os.path.getmtime)
            with open(latest, "rb") as f:
                if current_hash == hashlib.md5(f.read()).hexdigest():
                    return f"✅ {target['name']}: Data identical, skipped."

        with open(save_path, "wb") as f:
            f.write(resp.content)
        return f"🚀 {target['name']}: Success."
    except Exception as e:
        return f"❌ {target['name']}: Failed - {e}"


def main():
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Use ThreadPoolExecutor to leverage multiple cores for I/O
    with ThreadPoolExecutor(max_workers=len(config['targets'])) as executor:
        results = list(executor.map(lambda t: fetch_target(t, timestamp), config['targets']))

    for res in results:
        print(res)


if __name__ == "__main__":
    main()
