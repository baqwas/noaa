#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : satellite_health_check.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 1.3.1 (Production Grade - Centralized Logging)
📝 DESCRIPTION   : Monitors NASA GIBS layer status via WMTS metadata.
                   Identifies data processing lags and generates alerts.
                   Includes automated logging and SMTP notification.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🛡️  Perform pre-flight sanity check on local SMTP relay.
    2. 🔍  Retrieve WMTS GetCapabilities XML from NASA GIBS.
    3. 🏗️  Parse XML tree to locate specific Instrument/Layer identifiers.
    4. ⏱️  Extract '<TimeSpan>' metadata to determine the latest data date.
    5. 🧪  Calculate drift between current system time and satellite data.
    6. 📄  Record status telemetry to central log file with severity levels.
    7. 📬  Dispatch SMTP alert if any layer lags exceed the 3-day threshold.

📋 PREREQUISITES :
    - Python 3.10+
    - Packages: `requests`
    - Network: Port 25 access to LAN SMTP relay (192.168.1.5)

📂 FOLDERS       :
    - Log File: /home/reza/Videos/satellite/noaa/viirs/logs/satellite_health.log

📜 LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import smtplib
from email.message import EmailMessage
import socket
import argparse
from pathlib import Path

# --- 🛰️ NASA GIBS CONFIGURATION ---
WMTS_URL = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml"
LAYERS = [
    "VIIRS_SNPP_CorrectedReflectance_TrueColor",
    "VIIRS_SNPP_DayNightBand_ENCC",
    "VIIRS_SNPP_Precipitable_Water"
]
DRIFT_THRESHOLD_DAYS = 3

# --- 📧 SMTP CONFIGURATION ---
SMTP_SERVER = "bezaman.parkcircus.org"
SMTP_PORT = 25
EMAIL_FROM = "beulta-bot@parkcircus.org"
EMAIL_TO = "reza@parkcircus.org"

# --- 🛠️ CENTRALIZED LOGGING ALIGNMENT ---
LOG_DIR = Path("/home/reza/Videos/satellite/noaa/viirs/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "satellite_health.log"

# Define shared logger
logger = logging.getLogger("HEALTH_CHECK")
logger.setLevel(logging.INFO)

# File Handler (Appends to the suite's main log)
file_handler = logging.FileHandler(LOG_FILE)
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console Handler (For verbose output in the bash wrapper)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('\033[0;36m%(levelname)s:\033[0m %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def check_smtp_server(host, port, timeout=3):
    """Verifies the local SMTP relay is reachable."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False


def get_layer_metadata():
    """Fetches and parses the NASA WMTS Capabilities XML."""
    try:
        response = requests.get(WMTS_URL, timeout=30)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except Exception as e:
        logger.error("Failed to retrieve NASA WMTS Metadata: %s", e)
        return None


def parse_drift(root):
    """Calculates the time difference between current date and NASA's last update."""
    if root is None:
        return "Critical Error: XML Metadata Unavailable", []

    ns = {'wmts': 'http://www.opengis.net/wmts/1.0', 'ows': 'http://www.opengis.net/ows/1.1'}
    report = []
    outages = []
    current_time = datetime.utcnow()

    for layer_name in LAYERS:
        # XPath to find the specific layer block
        xpath_query = f".//wmts:Layer[ows:Identifier='{layer_name}']"
        layer = root.find(xpath_query, ns)

        if layer is not None:
            # Extract Timespan (last value is usually the latest)
            timespan = layer.find(".//wmts:Dimension[ows:Identifier='Time']/wmts:Value[last()]", ns)
            if timespan is not None:
                latest_date_str = timespan.text.split('/')[0] if '/' in timespan.text else timespan.text
                latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
                drift = (current_time - latest_date).days

                status_icon = "✅" if drift <= DRIFT_THRESHOLD_DAYS else "⚠️"
                report.append(f"{status_icon} Layer: {layer_name}\n   Latest: {latest_date_str} (Drift: {drift} days)")

                if drift > DRIFT_THRESHOLD_DAYS:
                    logger.warning("Data drift detected for %s: %d days", layer_name, drift)
                    outages.append(layer_name)
                else:
                    logger.info("Health Check OK for %s", layer_name)
            else:
                report.append(f"❓ Layer: {layer_name}\n   Status: NO TIMESPAN METADATA")
        else:
            report.append(f"❌ Layer: {layer_name}\n   Status: NOT FOUND IN METADATA")
            outages.append(layer_name)

    return "\n".join(report), outages


def send_alert(body, outage_list):
    """Dispatches the status report via local SMTP relay."""
    msg = EmailMessage()
    subject = "🛰️ Satellite Health: OK" if not outage_list else f"⚠️ Satellite Alert: {len(outage_list)} Layers Lagging"
    msg.set_content(f"NASA GIBS Health Check Report:\n\n{body}\n\nGenerated by BeUlta Satellite Suite.")
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
        logger.info("📧 Email alert sent successfully to %s", EMAIL_TO)
    except Exception as e:
        logger.error("📧 Failed to send email alert: %s", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor NASA GIBS layer health.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console output.")
    args = parser.parse_args()

    # Adjust console logging based on verbose flag
    if not args.verbose:
        console_handler.setLevel(logging.WARNING)

    # 1. Sanity Check
    if not check_smtp_server(SMTP_SERVER, SMTP_PORT):
        logger.critical("Aborting health check: SMTP relay %s is unreachable.", SMTP_SERVER)
        exit(1)

    # 2. Process Metadata
    xml_root = get_layer_metadata()
    health_report, lag_list = parse_drift(xml_root)

    # 3. Output results
    if args.verbose:
        print("\n" + health_report + "\n")

    # 4. Dispatch Alert
    send_alert(health_report, lag_list)
