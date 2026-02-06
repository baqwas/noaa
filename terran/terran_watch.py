#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           terran_watch.py
Author:         Matha Goram
Version:        1.0.0
Description:    Parallel monitoring for Collin County Land Use & NDVI.
                Independent of EPIC/SWPC fetchers to prevent code burden.
License:        MIT License
-------------------------------------------------------------------------------
"""

import argparse
import os
import logging
import requests
import tomllib
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage


def send_alert(config, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"TERRAN-WATCH ALERT: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"SMTP Error: {e}")


def fetch_gibs_image(config, layer, date_str):
    """Fetches a high-res snapshot for the Collin County BBox."""
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "TIME": date_str,
        "LAYERS": layer,
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "BBOX": config['terran']['bbox'],
        "SRS": "EPSG:4326",
        "WIDTH": "1200",
        "HEIGHT": "800"
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"Layer {layer} fetch failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    os.makedirs(config['terran']['log_dir'], exist_ok=True)
    logging.basicConfig(filename=os.path.join(config['terran']['log_dir'], "terran.log"),
                        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    today = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for layer in config['terran']['layers']:
        save_path = os.path.join(config['terran']['storage_dir'], layer)
        os.makedirs(save_path, exist_ok=True)

        filename = f"{layer}_{today.replace('-', '')}.png"
        full_path = os.path.join(save_path, filename)

        if os.path.exists(full_path):
            continue

        content = fetch_gibs_image(config, layer, today)
        if content:
            with open(full_path, "wb") as f:
                f.write(content)
            logging.info(f"Saved {layer} for {today}")


if __name__ == "__main__":
    main()