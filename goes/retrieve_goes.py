#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           retrieve_goes_unified.py
Description:    Unified retrieval utility for GOES-East and GOES-West imagery.
                Consolidates multi-satellite fetching into a single process
                driven by TOML configuration.
Version:        1.0.0
Updated:        2026-02-04
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

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-------------------------------------------------------------------------------
"""

import datetime
from email.message import EmailMessage
import logging
import os
import requests
import smtplib
import tomllib

# --- Initialization & Configuration ---
CONFIG_PATH = os.path.expanduser("../swpc/config.toml")

try:
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    print(f"Error: Configuration file not found at {CONFIG_PATH}")
    exit(1)

# Setup Logging based on config paths
log_dir = config.get('paths', {}).get('swpc_log_dir', '/tmp')
log_path = os.path.join(log_dir, "goes_retrieval.log")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GOES_Unified")


def send_alert(subject, body):
    """Dispatches SMTP alerts for critical failures using config credentials."""
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
    except Exception as e:
        logger.error(f"Failed to send SMTP alert: {e}")


def retrieve_satellite_image(target):
    """Fetches and persists imagery for a specific satellite target."""
    name = target['name']
    url = target['url']
    save_dir = target['dir']

    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    filename = os.path.join(save_dir, f"{name}_{timestamp}.jpg")

    try:
        logger.info(f"Initiating download for {name}...")
        response = requests.get(url, stream=True, timeout=30)

        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    f.write(chunk)
            logger.info(f"Successfully archived {name} to {filename}")

            # Placeholder for MQTT Notification
            # notify_mqtt(name, filename)

        else:
            raise requests.exceptions.HTTPError(f"HTTP Status {response.status_code}")

    except Exception as e:
        error_msg = f"Failed to retrieve {name} imagery. Error: {str(e)}"
        logger.error(error_msg)
        send_alert(f"Fetch Failure - {name}", error_msg)


def main():
    """Main execution loop for all GOES targets defined in config."""
    logger.info("--- Starting GOES Unified Retrieval Cycle ---")

    targets = config.get('goes_targets', [])
    if not targets:
        logger.warning("No GOES targets found in configuration.")
        return

    for target in targets:
        retrieve_satellite_image(target)

    logger.info("--- Retrieval Cycle Complete ---")


if __name__ == "__main__":
    main()