#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           space_fetcher.py
Author:         Matha Goram
Version:        1.0.1
Updated:        2026-02-04
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

import os
import shutil
import requests
import tomllib
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --- Configuration ---
MIN_DISK_GB = 2.0  # Minimum free space required to proceed

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# Setup Logging
log_path = os.path.join(config['paths']['log_dir'], "space_fetcher.log")
os.makedirs(config['paths']['log_dir'], exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
    """Returns True if free space is above MIN_DISK_GB."""
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (2 ** 30)
    if free_gb < MIN_DISK_GB:
        msg = f"Low Disk Space: {free_gb:.2f} GB remaining. Threshold: {MIN_DISK_GB} GB."
        logging.warning(msg)
        send_alert("Disk Space Warning", msg)
        return False
    return True


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Check disk space using the first target directory's parent as a proxy for the volume
    if not config['targets'] or not check_disk_space(os.path.dirname(config['targets'][0]['dir'])):
        return

    for target in config['targets']:
        name = target['name']
        url = target['url']
        save_dir = target['dir']

        os.makedirs(save_dir, exist_ok=True)

        ext = "png" if "png" in url else "jpg"
        filename = os.path.join(save_dir, f"{name}_{timestamp}.{ext}")

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            with open(filename, 'wb') as fp:
                fp.write(response.content)
            logging.info(f"Successfully saved: {name}")
        except Exception as e:
            msg = f"Failed to download {name}. Error: {e}"
            logging.error(msg)
            send_alert("Fetch Failure", msg)


if __name__ == "__main__":
    main()