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

def get_dir_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024**3) # Return in GB

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    root = config['epic']['storage_dir']
    stats = []
    total_project_size = 0

    for continent in os.listdir(root):
        cont_path = os.path.join(root, continent)
        if os.path.isdir(cont_path):
            size = get_dir_size(cont_path)
            count = len(os.listdir(cont_path))
            stats.append(f"- {continent}: {count} images ({size:.2f} GB)")
            total_project_size += size

    report = (
        f"EPIC Storage Monthly Report\n"
        f"===========================\n"
        + "\n".join(stats) +
        f"\n\nTotal Storage Used: {total_project_size:.2f} GB\n"
        f"Storage Limit: {config['dashboard']['storage_limit_gb']} GB"
    )

    # Send via Email
    msg = EmailMessage()
    msg.set_content(report)
    msg['Subject'] = "EPIC Project: Monthly Storage Stats"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
        print("Monthly dashboard report sent successfully.")
    except Exception as e:
        print(f"Failed to send dashboard: {e}")

if __name__ == "__main__":
    main()