#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           epic_dashboard.py
Author:         Matha Goram
Version:        1.0.0
Description:    Generates monthly statistics on image storage for the EPIC
                project and sends a summary report.
-------------------------------------------------------------------------------
"""

import argparse
import os
import tomllib
import smtplib
from email.message import EmailMessage


def get_dir_size_gb(path):
    total_size = 0
    if not os.path.exists(path):
        return 0.0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            total_size += os.path.getsize(os.path.join(dirpath, f))
    return total_size / (1024 ** 3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    # Use 'storage_root' as refactored in config.toml
    root = config['epic']['storage_root']
    stats = []
    total_project_size = 0

    # Continents: Americas, Africa_Europe, Asia_Australia
    for continent in ["Americas", "Africa_Europe", "Asia_Australia"]:
        cont_path = os.path.join(root, continent)
        if os.path.isdir(cont_path):
            size = get_dir_size_gb(cont_path)
            # Count images specifically in the /images subfolder
            img_dir = os.path.join(cont_path, "images")
            count = len(os.listdir(img_dir)) if os.path.exists(img_dir) else 0

            stats.append(f"- {continent}: {count} images ({size:.4f} GB total)")
            total_project_size += size

    report = (
            f"EPIC Storage Health Report\n"
            f"Generated: {os.uname()[1]} @ {os.popen('date').read()}\n"
            f"===========================\n"
            + "\n".join(stats) +
            f"\n\nTotal Project Storage: {total_project_size:.4f} GB\n"
            f"Threshold Limit: {config['dashboard']['storage_limit_gb']} GB"
    )

    # Dispatch via SMTP
    msg = EmailMessage()
    msg.set_content(report)
    msg['Subject'] = "EPIC Project: Storage Summary"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        print(f"Reporting Error: {e}")


if __name__ == "__main__":
    main()
