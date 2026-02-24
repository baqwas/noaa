#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
🛰️ NAME          : retrieve_goes.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 2.2.0
📅 UPDATED       : 2026-02-24
📝 DESCRIPTION   : Unified retrieval utility for GOES-East and GOES-West.
                   Standardizes nomenclature to goes_east and goes_west.

🛠️ WORKFLOW      :
    1. Load configuration from absolute path.
    2. Initialize centralized logging in /goes/logs/.
    3. Iterate through satellite targets defined in config.toml.
    4. Stream imagery to respective /images subfolders.
    5. Dispatch SMTP alerts on network or disk failures.

📋 PREREQUISITES :
    - Python 3.11+
    - Valid 'goes_targets' array in swpc/config.toml
    - Write access to /home/reza/Videos/satellite/goes/

🖥️ INTERFACE     : CLI (Automated via cron or retrieve_goes.sh)
⚠️ ERRORS        : SMTP alerts for 4xx/5xx HTTP errors and OS permission issues.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
📚 REFERENCES    : https://cdn.star.nesdis.noaa.gov/
-------------------------------------------------------------------------------
"""

import datetime
import logging
import os
import requests
import smtplib
import tomllib
from email.message import EmailMessage

CONFIG_PATH = "/home/reza/PycharmProjects/noaa/swpc/config.toml"


def setup_logging(config):
    log_dir = config['goes']['log_dir']
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "goes_operations.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s 🛰️ [%(levelname)s] %(message)s'
    )
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(asctime)s 🛰️ %(message)s'))
    logging.getLogger('').addHandler(console)


def send_alert(config, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"🛰️ [GOES-FETCH] Alert: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"❌ SMTP Failure: {e}")


def main():
    try:
        with open(CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"❌ Config Load Failure: {e}")
        return

    setup_logging(config)
    logging.info("🚀 Starting Unified GOES Ingest")

    for target in config.get('goes_targets', []):
        name = target['name']  # Expected: goes_east / goes_west
        url = target['url']
        save_dir = os.path.join(config['goes']['storage_root'], name, "images")
        os.makedirs(save_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
        filename = os.path.join(save_dir, f"{name}_{timestamp}.jpg")

        try:
            r = requests.get(url, timeout=30, stream=True)
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            logging.info(f"✅ Archived {name} snapshot.")
        except Exception as e:
            msg = f"Failed to fetch {name}: {e}"
            logging.error(f"❌ {msg}")
            send_alert(config, name, msg)


if __name__ == "__main__":
    main()