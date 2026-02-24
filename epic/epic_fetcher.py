#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
🌍 NAME          : epic_fetcher.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.3.0
📅 UPDATED       : 2026-02-23
📝 DESCRIPTION   : Professional-grade ingest tool for DSCOVR EPIC imagery.
                   Centered on major continents to track global trends.
🛠️ WORKFLOW      :
    1. Initialize argparse with optional config path and default fallback.
    2. Parse TOML configuration for storage and API endpoints.
    3. Query NASA EPIC 'natural' API for latest metadata.
    4. Identify frames closest to target longitudes for specific continents.
    5. Download and archive high-res PNGs to the media partition.
    6. Log all activity and dispatch SMTP alerts on critical failure.

🖥️ INTERFACE     : CLI via argparse (Optional: --config)
⚠️ ERRORS        : Comprehensive exception handling with log-to-file and email alerts.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
📚 REFERENCES    : https://epic.gsfc.nasa.gov/about/api
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

# --- 📍 Constants & Geometries ---
# Centering longitudes to capture "Noon" snapshots for each region
CONTINENT_LONGITUDES = {
    "Americas": -80.0,
    "Africa_Europe": 15.0,
    "Asia_Australia": 120.0
}


def setup_professional_logging(log_dir):
    """Initializes iconified logging in the media partition."""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "epic_fetcher.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s 🛰️ [%(levelname)s] %(message)s'
    )
    # Console handler for real-time terminal feedback
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter('%(asctime)s 🛰️ %(message)s'))
    logging.getLogger('').addHandler(console)


def send_alert(config, subject, body):
    """Dispatches critical failure notifications via SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"🚨 [EPIC-FETCHER] ALERT: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"❌ Critical SMTP Failure: Unable to send alert. Error: {e}")


def main():
    # --- 🛠️ User Interface ---
    # Determine the script directory to build a reliable default path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, "../swpc/config.toml")

    parser = argparse.ArgumentParser(description="NASA EPIC Image Ingest Tool")
    # --config is now optional with a default relative path
    parser.add_argument(
        "--config",
        default=default_config,
        help=f"Path to config.toml (default: {default_config})"
    )
    args = parser.parse_args()

    # --- ⚙️ Config Loading ---
    try:
        with open(args.config, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found at: {args.config}")
        return
    except Exception as e:
        print(f"❌ Failed to parse config: {e}")
        return

    # Initialize logging using the directory specified in the config
    setup_professional_logging(config['epic']['log_dir'])
    storage_root = config['epic']['storage_root']

    logging.info("🚀 [START] Initiating EPIC Ingest Cycle")

    try:
        # --- 📡 API Query ---
        logging.info("🔗 Querying NASA EPIC Metadata...")
        response = requests.get(config['epic']['api_url'], timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data:
            logging.warning("💤 No new EPIC imagery available at this time.")
            return

        # --- 🔄 Processing Workflow ---
        for continent, target_lon in CONTINENT_LONGITUDES.items():
            # Select the frame closest to the continent's center
            best_frame = min(data, key=lambda x: abs(x['centroid_coordinates']['lon'] - target_lon))

            image_name = best_frame['image']
            date_obj = datetime.strptime(best_frame['date'], "%Y-%m-%d %H:%M:%S")
            date_path = date_obj.strftime("%Y/%m/%d")

            # Organize by Continent: /Videos/satellite/epic/Americas/images/
            img_dir = os.path.join(storage_root, continent, "images")
            os.makedirs(img_dir, exist_ok=True)

            save_path = os.path.join(img_dir, f"{continent}_{date_obj.strftime('%Y%m%d')}.png")

            if os.path.exists(save_path):
                logging.info(f"⏭️  [SKIP] {continent}: Snapshot already archived.")
                continue

            # --- ⬇️ Download Logic ---
            download_url = f"{config['epic']['archive_base']}/{date_path}/png/{image_name}.png"
            logging.info(f"📥 Fetching {continent} ({date_obj.strftime('%Y-%m-%d')})...")

            img_res = requests.get(download_url, stream=True, timeout=60)
            img_res.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in img_res.iter_content(8192):  # Efficient chunking for high-res PNGs
                    f.write(chunk)

            logging.info(f"✅ [SUCCESS] Archived {continent} imagery.")

    except requests.exceptions.RequestException as e:
        error_msg = f"Network failure during API communication: {e}"
        logging.error(f"❌ {error_msg}")
        send_alert(config, "Network Error", error_msg)
    except Exception as e:
        error_msg = f"Unexpected runtime exception: {str(e)}"
        logging.error(f"❌ {error_msg}")
        send_alert(config, "System Error", error_msg)
    finally:
        logging.info("🏁 [FINISH] EPIC Ingest cycle complete.")


if __name__ == "__main__":
    main()