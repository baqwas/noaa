#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           retrieve_goes.py
Description:    Unified retrieval utility for GOES-East and GOES-West imagery.
                Fetches high-resolution satellite data based on TOML targets.
Version:        2.0.0
Updated:        2026-02-06
License:        MIT License
Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
-------------------------------------------------------------------------------
Processing Workflow:
1. Load global configuration from absolute path.
2. Iterate through 'goes_targets' defined in config.toml.
3. Fetch imagery via streaming requests to minimize memory footprint.
4. Archive images to satellite-specific /images directories.
-------------------------------------------------------------------------------
"""

import datetime
import logging
import os
import requests
import smtplib
import tomllib
from email.message import EmailMessage

# --- Configuration Constants ---
# Using absolute path to ensure reliability across Cron and Manual execution
CONFIG_PATH = "/home/reza/PycharmProjects/noaa/swpc/config.toml"

try:
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    print(f"Critical Error: Configuration not found at {CONFIG_PATH}")
    exit(1)


def setup_target_logging(target_name):
    """Configures localized logging for each satellite target."""
    # Maps name (goes-east) to its specific log directory
    base_log_dir = f"/home/reza/Videos/satellite/noaa/{target_name}/logs"
    os.makedirs(base_log_dir, exist_ok=True)

    log_file = os.path.join(base_log_dir, f"{target_name}_retrieval.log")

    logger = logging.getLogger(target_name)
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def send_alert(subject, body):
    """Dispatches SMTP alerts for fetch failures."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"GOES SYSTEM ALERT: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception:
        pass  # Logging handled by target logger


def retrieve_satellite_image(target):
    """Fetches imagery and saves to the designated images/ directory."""
    name = target['name']  # e.g., 'goes-east'
    url = target['url']

    # Enforced pathing structure
    save_dir = f"/home/reza/Videos/satellite/noaa/{name}/images"
    os.makedirs(save_dir, exist_ok=True)

    logger = setup_target_logging(name)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    filename = os.path.join(save_dir, f"{name}_{timestamp}.jpg")

    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Successfully archived {name} image: {filename}")
        else:
            raise Exception(f"HTTP Status {response.status_code}")
    except Exception as e:
        error_msg = f"Failed to retrieve {name}. Error: {str(e)}"
        logger.error(error_msg)
        send_alert(f"Fetch Failure - {name}", error_msg)


def main():
    targets = config.get('goes_targets', [])
    for target in targets:
        retrieve_satellite_image(target)


if __name__ == "__main__":
    main()