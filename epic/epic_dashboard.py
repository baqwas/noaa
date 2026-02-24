#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
📊 NAME          : epic_dashboard.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.3.1 (Enhanced SMTP Validation)
📅 UPDATED       : 2026-02-24
📝 DESCRIPTION   : Professional monitoring tool for the DSCOVR EPIC project.
                   Audits storage health, tracks daily ingest deltas, and
                   dispatches status reports via SMTP with response verification.

🛠️ WORKFLOW      :
    1. Load configuration from TOML and retrieve previous ingest counts.
    2. Recurse through continental directories to calculate disk usage.
    3. Compare current image counts against stored state to identify deltas.
    4. Compile a standardized text report with health status indicators.
    5. Dispatch the report via SMTP, verifying server acceptance before
       reporting success and updating the persistent state file.

📋 PREREQUISITES :
    - Python 3.11+ (for tomllib support)
    - Valid SMTP credentials in config.toml
    - Write access to the local directory for state tracking (.dashboard_state.json)

🖥️ INTERFACE     : CLI via argparse (Optional: --config)
⚠️ ERRORS        : Detailed console reporting for IO, JSON, and SMTP failures.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
📚 REFERENCES    : https://docs.python.org/3/library/email.message.html
-------------------------------------------------------------------------------
"""

import argparse
import os
import tomllib
import smtplib
import json
from datetime import datetime
from email.message import EmailMessage


def get_dir_size_gb(path):
    """Calculates total directory size in Gigabytes via recursive walk."""
    total_size = 0
    if not os.path.exists(path):
        return 0.0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            try:
                total_size += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                continue  # Ignore files that may have been moved/deleted during scan
    return total_size / (1024 ** 3)


def main():
    # --- 🛠️ Interface & Config Initialization ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, "../swpc/config.toml")
    state_file = os.path.join(script_dir, ".dashboard_state.json")

    parser = argparse.ArgumentParser(description="EPIC Storage & Ingest Dashboard")
    parser.add_argument(
        "--config",
        default=default_config,
        help=f"Path to configuration TOML (default: {default_config})"
    )
    args = parser.parse_args()

    # --- ⚙️ Load Configuration ---
    try:
        with open(args.config, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found at {args.config}")
        return
    except Exception as e:
        print(f"❌ Error: Failed to parse configuration: {e}")
        return

    # --- 💾 State Management ---
    prev_counts = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                prev_counts = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Warning: State file corrupted. Resetting deltas.")

    # --- 🔄 Processing Workflow ---
    root = config['epic']['storage_root']
    stats = []
    total_project_size = 0
    current_counts = {}
    continents = ["Americas", "Africa_Europe", "Asia_Australia"]

    print("🛰️ Auditing EPIC storage directories...")

    for continent in continents:
        cont_path = os.path.join(root, continent)
        img_dir = os.path.join(cont_path, "images")

        size = get_dir_size_gb(cont_path)
        count = len(os.listdir(img_dir)) if os.path.exists(img_dir) else 0

        delta = count - prev_counts.get(continent, count)
        delta_str = f"(+{delta} new)" if delta > 0 else "(no change)"

        current_counts[continent] = count
        stats.append(f"📍 {continent.ljust(15)}: {count:3} images {delta_str.ljust(12)} | {size:.4f} GB")
        total_project_size += size

    # --- 📝 Report Construction ---
    limit_gb = config['dashboard']['storage_limit_gb']
    health_status = 'NORMAL' if total_project_size < limit_gb else 'OVER LIMIT'

    report_body = (
            f"🌎 EPIC Project: Storage & Ingest Report\n"
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"🖥️ Host: {os.uname()[1]}\n"
            f"{'=' * 60}\n"
            + "\n".join(stats) +
            f"\n{'=' * 60}\n"
            f"📊 Total Usage:  {total_project_size:.4f} GB\n"
            f"⚠️ Disk Limit:   {limit_gb} GB\n"
            f"✅ Status:       {health_status}\n"
            f"{'=' * 60}\n"
            f"End of automated report."
    )

    # --- 📧 Dispatch & Verification ---
    msg = EmailMessage()
    msg.set_content(report_body)
    msg['Subject'] = f"🛰️ [EPIC-DASHBOARD] Storage Summary: {total_project_size:.2f} GB used"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])

            # send_message returns a dict of any rejected recipients
            refused = server.send_message(msg)

            if refused:
                print(f"⚠️ Warning: Message was rejected by these recipients: {refused}")
            else:
                # Only update state and report success if the server accepted the delivery
                with open(state_file, "w") as f:
                    json.dump(current_counts, f)
                print(f"✅ Success: Report accepted by SMTP server for {config['smtp']['receiver']}.")

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Error: Authentication failed. Please check your username/password.")
    except smtplib.SMTPConnectError:
        print(f"❌ SMTP Error: Could not connect to {config['smtp']['server']}.")
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: The server rejected the request: {e}")
    except Exception as e:
        print(f"❌ System Error: An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()