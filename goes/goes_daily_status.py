#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
📊 NAME          : goes_daily_status.py
📝 DESCRIPTION   : Daily storage and ingest audit for GOES-East/West.
-------------------------------------------------------------------------------
"""

import os
import tomllib
import smtplib
import io
from datetime import datetime
from email.message import EmailMessage

CONFIG_PATH = "/home/reza/PycharmProjects/noaa/swpc/config.toml"


def main():
    with open(CONFIG_PATH, "rb") as f:
        config = tomllib.load(f)

    root = config['goes']['storage_root']
    report = io.StringIO()
    report.write(f"🛰️ GOES SYSTEM STATUS: {datetime.now().strftime('%Y-%m-%d')}\n")
    report.write("=" * 60 + "\n")
    report.write(f"{'Target':<15} | {'Images':<10} | {'Videos':<10}\n")
    report.write("-" * 60 + "\n")

    for sat in ["goes_east", "goes_west"]:
        img_p = os.path.join(root, sat, "images")
        vid_p = os.path.join(root, sat, "videos")

        imgs = len(os.listdir(img_p)) if os.path.exists(img_p) else 0
        vids = len(os.listdir(vid_p)) if os.path.exists(vid_p) else 0
        report.write(f"{sat:<15} | {imgs:<10} | {vids:<10}\n")

    msg = EmailMessage()
    msg.set_content(report.getvalue())
    msg['Subject'] = f"📊 [GOES-STATUS] System Audit"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
        print("✅ Status report dispatched.")
    except Exception as e:
        print(f"❌ Report failed: {e}")


if __name__ == "__main__":
    main()