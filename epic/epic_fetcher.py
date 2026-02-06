#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           epic_fetcher.py
Author:         Matha Goram
Version:        1.0.0
Updated:        2026-02-06
Description:    Downloads DSCOVR EPIC full-disk Earth imagery at specific
                intervals to track seasonal and continental trends.
License:        MIT License
Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
-------------------------------------------------------------------------------
"""

import argparse
import os
import logging
import requests
import tomllib
import smtplib
from datetime import datetime
from email.message import EmailMessage

# Mapping of continents to approximate "Noon" longitudes for EPIC centering
CONTINENT_LONGITUDES = {
    "Americas": -80.0,
    "Africa_Europe": 15.0,
    "Asia_Australia": 120.0
}


def send_alert(config, subject, body):
    """Sends error notifications via LAN SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"EPIC-FETCHER ALERT: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Critical SMTP Failure: {e}")


def main():
    parser = argparse.ArgumentParser(description="NASA EPIC Image Fetcher")
    parser.add_argument("--config", required=True, help="Path to config.toml")
    args = parser.parse_args()

    # Load Config
    try:
        with open(args.config, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"Failed to load config: {e}")
        return

    # Setup Logging
    log_file = os.path.join(config['epic']['log_dir'], "epic_fetcher.log")
    os.makedirs(config['epic']['log_dir'], exist_ok=True)
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        logging.info("Querying NASA EPIC API...")
        response = requests.get(config['epic']['api_url'], timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data:
            logging.warning("No new EPIC imagery available in API response.")
            return

        storage_root = config['epic']['storage_dir']

        # Iterate through target longitudes to find the best matching frame
        for continent, target_lon in CONTINENT_LONGITUDES.items():
            # Find the frame where the Earth's centroid is closest to target longitude
            best_frame = min(data, key=lambda x: abs(x['centroid_coordinates']['lon'] - target_lon))

            image_name = best_frame['image']
            # EPIC dates are in format YYYY-MM-DD HH:MM:SS
            date_obj = datetime.strptime(best_frame['date'], "%Y-%m-%d %H:%M:%S")
            date_path = date_obj.strftime("%Y/%m/%d")

            # Construct download URL: archive/natural/YYYY/MM/DD/png/image_name.png
            download_url = f"{config['epic']['archive_base']}/{date_path}/png/{image_name}.png"

            cont_dir = os.path.join(storage_root, continent)
            os.makedirs(cont_dir, exist_ok=True)
            save_path = os.path.join(cont_dir, f"{continent}_{date_obj.strftime('%Y%m%d')}.png")

            if os.path.exists(save_path):
                logging.info(f"Skipping {continent}: File already exists for today.")
                continue

            # Download Image
            img_res = requests.get(download_url, stream=True, timeout=60)
            img_res.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in img_res.iter_content(1024):
                    f.write(chunk)

            logging.info(f"Successfully archived {continent} imagery to {save_path}")

    except Exception as e:
        error_msg = f"EPIC Fetcher encountered a runtime error: {str(e)}"
        logging.error(error_msg)
        send_alert(config, "Runtime Failure", error_msg)


if __name__ == "__main__":
    main()