#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
📊 NAME          : goes_daily_status.py
📝 DESCRIPTION   : Daily storage and ingest audit for GOES-East/West.
-------------------------------------------------------------------------------
"""

import tomllib
import smtplib
import io
from pathlib import Path
from datetime import datetime
from email.message import EmailMessage

CONFIG_PATH = Path("/home/reza/PycharmProjects/noaa/swpc/config.toml")

def main():
    with CONFIG_PATH.open("rb") as f:
        config = tomllib.load(f)

    root = Path(config['goes']['storage_root'])
    report = io.StringIO()
    report.write(f"🛰️ GOES SYSTEM STATUS: {datetime.now().strftime('%Y-%m-%d')}\n")
    report.write("=" * 60 + "\n")
    report.write(f"{'Target':<15} | {'Images':<10} | {'Videos':<10}\n")
    report.write("-" * 60 + "\n")

    for sat in ["goes_east", "goes_west"]:
        img_p = root / sat / "images"
        vid_p = root / sat / "videos"

        # Count files using pathlib globbing
        imgs = len(list(img_p.glob("*.jpg"))) if img_p.exists() else 0
        vids = len(list(vid_p.glob("*.mp4"))) if vid_p.exists() else 0
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