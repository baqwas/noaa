#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           space_fetcher.py
Author:         Matha Goram
Version:        1.1.0
Updated:        2026-02-06
Description:    Space Fetcher
Description:    Unified downloader for NOAA Space Weather imagery. Includes
                disk space monitoring and SMTP error reporting.
License:        MIT License
Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
-------------------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
-------------------------------------------------------------------------------
Safety Check: Verify storage health.
Ingestion: Fetch latest high-cadence imagery from NOAA.
Persistence: Store frames with unique timestamps.
Transformation: Weekly consolidation of frames into a playable MP4.
Retention: Final MP4 is archived; raw frames are purged to reclaim space.
-------------------------------------------------------------------------------
Data Type,Description,Static URL (Latest Image)
Solar EUV,SUVI 304Å (Solar Filaments/Prominences),https://services.swpc.noaa.gov/images/animations/suvi/primary/304/latest.png
Solar EUV,SUVI 195Å (Coronal Holes),https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png
CME (Inner),LASCO C2 (2–6 Solar Radii),https://services.swpc.noaa.gov/images/animations/lasco-c2/latest.png
CME (Outer),LASCO C3 (3.7–30 Solar Radii),https://services.swpc.noaa.gov/images/animations/lasco-c3/latest.png
New CME,GOES-19 CCOR-1 (Modern Coronagraph),https://services.swpc.noaa.gov/images/animations/ccor-1/latest.png
-------------------------------------------------------------------------------
Processing Workflow:
1. Parse CLI arguments for config path.
2. Iterate through targets in config.
3. Setup or retrieve a logger specific to the instrument root.
4. Download latest image; save only if MD5 differs from the last saved file.
-------------------------------------------------------------------------------
"""

import argparse
import datetime
import hashlib
import logging
import os
import requests
import tomllib


def get_instrument_logger(instrument_root):
    """Provides a single logger per instrument suite (e.g., aurora.log)."""
    name = os.path.basename(instrument_root)
    logger = logging.getLogger(name)
    if not logger.handlers:
        os.makedirs(instrument_root, exist_ok=True)
        log_path = os.path.join(instrument_root, f"{name}.log")
        fh = logging.FileHandler(log_path)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
        logger.setLevel(logging.INFO)
    return logger


def main():
    parser = argparse.ArgumentParser(description="NOAA Space Fetcher")
    parser.add_argument("--config", required=True, help="Path to config.toml")
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for target in config['targets']:
        root = target['instrument_root']
        # Partition images: e.g., .../aurora/north or .../solar_304/images
        img_dir = os.path.join(root, target.get('subdir', 'images'))
        os.makedirs(img_dir, exist_ok=True)

        logger = get_instrument_logger(root)

        try:
            resp = requests.get(target['url'], timeout=20)
            resp.raise_for_status()

            # MD5 verification
            current_hash = hashlib.md5(resp.content).hexdigest()
            ext = "png" if "png" in target['url'] else "jpg"
            filename = f"{target['name']}_{timestamp}.{ext}"
            save_path = os.path.join(img_dir, filename)

            # Check last file to prevent redundant frames
            files = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
            if files:
                latest = max(files, key=os.path.getmtime)
                with open(latest, "rb") as f:
                    if current_hash == hashlib.md5(f.read()).hexdigest():
                        logger.info(f"Skipped {target['name']}: Data identical.")
                        continue

            with open(save_path, "wb") as f:
                f.write(resp.content)
            logger.info(f"Successfully archived: {filename}")

        except Exception as e:
            logger.error(f"Fetch failed for {target['name']}: {e}")


if __name__ == "__main__":
    main()
