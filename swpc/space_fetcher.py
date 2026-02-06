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

Data Type,Description,Static URL (Latest Image)
Solar EUV,SUVI 304Å (Solar Filaments/Prominences),https://services.swpc.noaa.gov/images/animations/suvi/primary/304/latest.png
Solar EUV,SUVI 195Å (Coronal Holes),https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png
CME (Inner),LASCO C2 (2–6 Solar Radii),https://services.swpc.noaa.gov/images/animations/lasco-c2/latest.png
CME (Outer),LASCO C3 (3.7–30 Solar Radii),https://services.swpc.noaa.gov/images/animations/lasco-c3/latest.png
New CME,GOES-19 CCOR-1 (Modern Coronagraph),https://services.swpc.noaa.gov/images/animations/ccor-1/latest.png
"""

import argparse
from datetime import datetime
from email.message import EmailMessage
import hashlib
import os
import logging
import requests
import shutil
import smtplib
import tomllib

# --- Configuration Constants ---
MIN_DISK_GB = 2.0

# Global config placeholder (populated in main)
config = {}


def get_most_recent_file(directory):
    """Returns the path to the newest file in the directory, or None."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def calculate_md5(content):
    """Returns MD5 hex digest of binary content."""
    return hashlib.md5(content).hexdigest()


def calculate_file_md5(file_path):
    """Returns MD5 hex digest of an existing file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def send_alert(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"AURORA-BOT ALERT: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Failed to send SMTP alert: {e}")


def check_disk_space(path):
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (2 ** 30)
    if free_gb < MIN_DISK_GB:
        msg = f"Low Disk Space: {free_gb:.2f} GB remaining."
        logging.warning(msg)
        send_alert("Disk Space Warning", msg)
        return False
    return True


def main():
    global config

    # --- Argparse setup ---
    parser = argparse.ArgumentParser(description="NOAA Space Imagery Fetcher")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the configuration TOML file"
    )
    args = parser.parse_args()

    # --- Load Configuration ---
    try:
        with open(args.config, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"Critical Error: Could not load config at {args.config}. Error: {e}")
        return

    # --- Logging Setup ---
    log_dir = config['paths']['swpc_log_dir']
    log_path = os.path.join(log_dir, "space_fetcher.log")
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(filename=log_path, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not config['targets'] or not check_disk_space(os.path.dirname(config['targets'][0]['dir'])):
        return

    for target in config['targets']:
        name, url, save_dir = target['name'], target['url'], target['dir']
        os.makedirs(save_dir, exist_ok=True)

        # Correctly determine extension from URL
        ext = "png" if url.lower().endswith(".png") else "jpg"
        filename = os.path.join(save_dir, f"{name}_{timestamp}.{ext}")

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            new_content = response.content
            new_hash = calculate_md5(new_content)

            # --- MD5 Hash Check ---
            last_file = get_most_recent_file(save_dir)
            if last_file:
                last_hash = calculate_file_md5(last_file)
                if new_hash == last_hash:
                    logging.info(f"Skipped {name}: Content unchanged.")
                    continue

            with open(filename, 'wb') as fp:
                fp.write(new_content)
            logging.info(f"Successfully saved: {name}")

        except Exception as e:
            msg = f"Failed to download {name}. Error: {e}"
            logging.error(msg)
            send_alert("Fetch Failure", msg)


if __name__ == "__main__":
    main()