#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           gibs_fetcher.py
Author:         Matha Goram
Version:        1.0.2
Updated:        2026-02-04
Description:    Retrieves NASA GIBS imagery for Nevada, TX at specific times.
                Saves Day (MODIS) and Night (VIIRS) layers to local folders.
License:        MIT License
Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
-------------------------------------------------------------------------------
Considerations:
Component | Status/Value
--- | ---
Execution Times | 01:05 and 13:05 (Daily)
Resolution | 4096 x 4096 (High Fidelity)
BBOX Strategy | "Regional Native (1,024km span)"
Video Playback,2 FPS (Land-use optimized)
Visual Quality,CRF 17 (Near-lossless)
Safety,SMTP Alerts & Log Rotation

Crontab entries:
# NASA GIBS: Night Layer (Run at 1:05 AM to avoid the top-of-the-hour rush)
5 1 * * * /bin/bash /home/reza/PycharmProjects/noaa/gibs/manage_gibs.sh 2>&1

# NASA GIBS: Day Layer (Run at 1:05 PM)
5 13 * * * /bin/bash /home/reza/PycharmProjects/noaa/gibs/manage_gibs.sh 2>&1
"""

import os
import requests
import tomllib
import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage

# Load configuration
CONFIG_PATH = os.path.expanduser("~/PycharmProjects/noaa/swpc/config.toml")
with open(CONFIG_PATH, "rb") as f:
    config = tomllib.load(f)

# Setup Logging
log_file = os.path.join(config['paths']['gibs_log_dir'], "gibs_fetch.log")
os.makedirs(config['paths']['gibs_log_dir'], exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def send_error(error_msg):
    msg = EmailMessage()
    msg.set_content(f"GIBS Fetch Failure:\n\n{error_msg}")
    msg['Subject'] = "ALERT: NASA GIBS Download Error"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def fetch_gibs(is_night=False):
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    layer = config['gibs']['night_layer'] if is_night else config['gibs']['day_layer']
    time_now = datetime.now()
    time_str = time_now.strftime("%Y-%m-%d")

    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": layer,
        "FORMAT": "image/jpeg",
        "TRANSPARENT": "false",
        "BBOX": config['gibs']['bbox'],
        "WIDTH": config['gibs']['width'],
        "HEIGHT": config['gibs']['height'],
        "SRS": "EPSG:4326",
        "TIME": time_str
    }

    mode = "night" if is_night else "day"
    dest_dir = os.path.join(config['paths']['gibs_data_dir'], mode)
    os.makedirs(dest_dir, exist_ok=True)

    filename = f"gibs_{mode}_{time_now.strftime('%Y%m%d_%H%M%S')}.jpg"
    save_path = os.path.join(dest_dir, filename)

    try:
        logging.info(f"Requesting GIBS {mode} image for {time_str}...")
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        with open(save_path, 'wb') as fb:
            fb.write(response.content)
        logging.info(f"Successfully saved {mode} image to {save_path}")
    except Exception as e:
        err = f"Error fetching {mode} image: {e}"
        logging.error(err)
        send_error(err)


if __name__ == "__main__":
    # Determine if this is the Noon or Midnight run based on current hour
    current_hour = datetime.now().hour
    is_night_run = (current_hour < 6 or current_hour > 18)
    fetch_gibs(is_night=is_night_run)