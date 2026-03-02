#!/usr/bin/env python3
"""
================================================================================
📊 MODULE        : epic_dashboard.py
🚀 DESCRIPTION   : Storage Audit & Health Reporting for DSCOVR EPIC.
                   Calculates regional storage metrics and dispatches
                   automated reports via authenticated LAN SMTP.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.4.7 (SMTP Handshake Protocol Correction)
📅 UPDATED       : 2026-03-01
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
📜 MIT LICENSE:
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
================================================================================
📋 WORKFLOW PROCESSING:
    1. 🛡️  Inject .env variables into system environment memory.
    2. ⚙️  Parse config.toml using Template for ${VAR} interpolation.
    3. 📂 Audit: Recurse through regional image archives.
    4. 📉 Delta: Calculate regional image counts against '.dashboard_state.json'.
    5. 📊 Compile: Generate report with health status indicators.
    6. 📧 Dispatch: Secure SMTP delivery with implicit hostname propagation.
    7. 💾 Commit: Persist current counts to state file upon successful delivery.
    8. Explicit Connection -> EHLO -> STARTTLS -> EHLO
    By initializing the SMTP object with the host parameter and removing the
    non-standard server_hostname keyword from the starttls() call, the internal
    SSL context had the correct identity to complete the encrypted tunnel
================================================================================
"""

import os
import sys
import json
import smtplib
import tomllib
import datetime
from pathlib import Path
from email.message import EmailMessage
from string import Template
from typing import Dict, Any
from dotenv import load_dotenv

# --- 📁 Path Infrastructure ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJ_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJ_ROOT / "config.toml"
ENV_PATH = PROJ_ROOT / ".env"
STATE_FILE = SCRIPT_DIR / ".dashboard_state.json"

# --- 🛡️ Environment Initialization ---
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def load_secure_config(path: Path) -> Dict[str, Any]:
    """Loads TOML config with environment variable interpolation."""
    if not path.exists():
        print(f"❌ Configuration missing at {path}")
        sys.exit(1)
    with open(path, "r") as f:
        # Interpolate variables like ${SMTP_SERVER} before parsing TOML
        content = Template(f.read()).safe_substitute(os.environ)
        return tomllib.loads(content)


def get_directory_stats(root_path: Path) -> Dict[str, Any]:
    """Calculates file count and total size (GB) for the given directory."""
    stats = {"count": 0, "size_gb": 0.0}
    if not root_path.exists():
        return stats

    total_size = 0
    # Search for all PNG frames in the regional archive
    for f in root_path.glob('*.png'):
        if f.is_file():
            stats["count"] += 1
            total_size += f.stat().st_size

    stats["size_gb"] = total_size / (1024 ** 3)
    return stats


def send_report(config: Dict, report_body: str):
    """Dispatches report via SMTP with corrected TLS handshake."""
    smtp_cfg = config.get('smtp', {})

    # Map variables strictly to config.toml keys
    server_addr = smtp_cfg.get('server')
    server_port = int(smtp_cfg.get('port', 587))
    auth_user = smtp_cfg.get('user')
    auth_pass = smtp_cfg.get('password')
    mail_sender = smtp_cfg.get('sender')
    mail_rcvr = smtp_cfg.get('receiver')

    # Guard against interpolation failures in .env
    if not mail_rcvr or "$" in str(mail_rcvr):
        print(f"⚠️  [ERROR] SMTP Receiver resolution failed: {mail_rcvr}")
        return

    msg = EmailMessage()
    msg.set_content(report_body)
    msg['Subject'] = f"🛰️ EPIC Health Report: {datetime.datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = mail_sender
    msg['To'] = mail_rcvr

    print(f"📧 Dispatching report to {mail_rcvr} via {server_addr}...")

    try:
        # Step 1: Initialize and connect using the constructor.
        # Passing 'host' here ensures starttls() knows the hostname for the SSL context.
        server = smtplib.SMTP(host=server_addr, port=server_port, timeout=30)

        # Step 2: Establish Secure Handshake
        server.ehlo()
        # starttls() uses the hostname provided in the constructor automatically.
        # It does NOT accept 'server_hostname' as a keyword argument.
        server.starttls()
        server.ehlo()

        # Step 3: Authenticate and Transmit
        server.login(auth_user, auth_pass)
        server.send_message(msg)
        server.quit()

        print("✅ Email dispatched successfully.")
    except Exception as e:
        print(f"❌ SMTP Handshake Error: {e}")


def main():
    print(f"🚀 [INIT] Starting EPIC Storage Audit...")

    try:
        config = load_secure_config(CONFIG_PATH)
        epic_cfg = config.get('epic', {})
        storage_root = Path(epic_cfg.get('instrument_root', '/home/reza/Videos/satellite/epic'))

        # 1. Load Previous State
        prev_state = {}
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                prev_state = json.load(f)

        # 2. Perform Audit
        current_state = {}
        report_lines = [
            "==========================================",
            "   🛰️ DSCOVR EPIC: SYSTEM HEALTH REPORT   ",
            f"   Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "==========================================\n"
        ]

        regions = ["Americas", "Africa_Europe", "Asia_Australia"]
        for region in regions:
            stats = get_directory_stats(storage_root / region / "images")
            prev_count = prev_state.get(region, {}).get('count', 0)
            delta = stats['count'] - prev_count

            current_state[region] = stats

            report_lines.append(f"🌍 REGION: {region}")
            report_lines.append(f"   📂 Total Images: {stats['count']} (+{delta} new)")
            report_lines.append(f"   💾 Disk Usage:  {stats['size_gb']:.2f} GB")
            report_lines.append("-" * 30)

        report_text = "\n".join(report_lines)
        print(report_text)

        # 3. Dispatch Report
        send_report(config, report_text)

        # 4. Commit State
        with open(STATE_FILE, "w") as f:
            json.dump(current_state, f, indent=4)

        print(f"💾 State updated in {STATE_FILE.name}")

    except Exception as e:
        print(f"💥 [CRITICAL FAILURE] {e}")


if __name__ == "__main__":
    main()