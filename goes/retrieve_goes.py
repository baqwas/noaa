# !/usr/bin/env python3
"""
-------------------------------------------------------------------------------
🛰️ NAME          : retrieve_goes.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 2.3.1
📅 UPDATED       : 2026-02-25
📝 DESCRIPTION   : Retrieval utility for GOES-East and GOES-West.
                   Standardizes nomenclature to goes_east and goes_west.

🛠️ WORKFLOW      :
    1. Load configuration from absolute path.
    2. Initialize centralized logging in /goes/logs/.
    3. Iterate through satellite targets defined in config.toml.
    4. Stream imagery to respective /images subfolders.
    5. Dispatch SMTP alerts on network or disk failures.

🖥️ INTERFACE     : CLI (Automated via cron or retrieve_goes.sh)
⚠️ ERRORS        : SMTP alerts for 4xx/5xx HTTP errors and OS permission issues.
⚖️ LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
                   Permission is hereby granted, free of charge, to any person
                   obtaining a copy of this software and associated documentation...
📋 PREREQUISITES :
    - Python 3.11+
    - Valid 'goes_targets' array in swpc/config.toml
    - Write access to /home/reza/Videos/satellite/goes/
-------------------------------------------------------------------------------
"""

import datetime
import logging
import sys
import requests
import smtplib
import tomllib
from pathlib import Path
from email.message import EmailMessage

# --- Professional Terminal Colors ---
C_BLUE, C_GREEN, C_RED, C_YELLOW, C_NC = "\033[0;34m", "\033[0;32m", "\033[0;31m", "\033[1;33m", "\033[0m"

CONFIG_PATH = Path("/home/reza/PycharmProjects/noaa/swpc/config.toml")

def setup_logging(config):
    """Initializes logging using Path objects."""
    log_dir = Path(config['goes']['log_dir'])
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "goes_operations.log"

    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format='%(asctime)s 🛰️ [%(levelname)s] %(message)s'
    )
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(f'{C_BLUE}%(asctime)s{C_NC} 🛰️ %(message)s'))
    logging.getLogger('').addHandler(console)

def send_alert(config, subject, body):
    """Dispatches SMTP alerts."""
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
        logging.error(f"{C_RED}❌ SMTP Failure: {e}{C_NC}")

def main():
    try:
        with CONFIG_PATH.open("rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"{C_RED}❌ [CRITICAL] Config Load Failure: {e}{C_NC}")
        sys.exit(1)

    setup_logging(config)
    logging.info(f"{C_YELLOW}🚀 Starting Unified GOES Ingest{C_NC}")

    storage_root = Path(config['goes']['storage_root'])

    for target in config.get('goes_targets', []):
        name = target['name']
        save_dir = storage_root / name / "images"
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
        filepath = save_dir / f"{name}_{timestamp}.jpg"

        try:
            r = requests.get(target['url'], timeout=30, stream=True)
            r.raise_for_status()
            with filepath.open('wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            logging.info(f"{C_GREEN}✅ Archived {name} snapshot.{C_NC}")
        except Exception as e:
            logging.error(f"{C_RED}❌ Failed to fetch {name}: {e}{C_NC}")
            send_alert(config, name, str(e))

if __name__ == "__main__":
    main()