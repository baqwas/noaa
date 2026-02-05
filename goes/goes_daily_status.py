#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           goes_daily_status.py
Description:    Daily status dashboard for GOES-East/West archives.
                Calculates daily burn rates and storage life.
-------------------------------------------------------------------------------
"""

import os
import shutil
import tomllib
import smtplib
import io
from datetime import datetime
from email.message import EmailMessage

with open("../swpc/config.toml", "rb") as f:
    config = tomllib.load(f)

MIN_DISK_GB = 2.0


def get_stats(path):
    """Calculates counts and sizes for images and archived videos."""
    images = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.jpg')]
    img_mb = sum(os.path.getsize(f) for f in images) / (1024 * 1024)

    vid_path = os.path.join(path, "videos")
    vids = []
    vid_mb = 0
    if os.path.exists(vid_path):
        vids = [os.path.join(vid_path, f) for f in os.listdir(vid_path) if f.endswith('.mp4')]
        vid_mb = sum(os.path.getsize(f) for f in vids) / (1024 * 1024)

    return len(images), img_mb, len(vids), vid_mb


def main():
    report_buffer = io.StringIO()

    def report(text):
        print(text)
        report_buffer.write(text + "\n")

    total, used, free = shutil.disk_usage(os.path.expanduser("~/"))
    free_gb = free / (2 ** 30)
    percent = (used / total) * 100

    report(f"🌎 GOES DAILY ARCHIVE REPORT")
    report(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report("-" * 85)
    report(f"System Storage: {percent:.1f}% used ({free_gb:.2f} GB free)")
    report("-" * 85)
    report(f"{'Satellite':<15} | {'Img Cnt':<7} | {'Img Size':<10} | {'Vid Cnt':<7} | {'Vid Size':<10}")
    report("-" * 85)

    total_mb = 0
    # Process only GOES targets from your config
    for target in config.get('goes_targets', []):
        img_c, img_s, vid_c, vid_s = get_stats(target['dir'])
        total_mb += (img_s + vid_s)
        flag = "!" if img_c > 200 else " "  # Flag if daily purge failed
        report(f"{target['name']:<15} | {img_c:<7}{flag} | {img_s:>7.1f} MB | {vid_c:<7} | {vid_s:>7.1f} MB")

    # --- Daily Growth Projection ---
    # 10-minute intervals = 144 images/day per satellite
    daily_burn_mb = (144 * 2 * 0.5)  # Estimate 0.5MB per GOES image
    usable_mb = max(0, free_gb - MIN_DISK_GB) * 1024
    days_left = usable_mb / daily_burn_mb if daily_burn_mb > 0 else 999

    report("-" * 85)
    report(f"DAILY GROWTH FORECAST:")
    report(f" * Est. Daily Ingest: {daily_burn_mb:.1f} MB")
    report(f" * Est. Storage Life: {int(days_left)} days remaining")
    report("-" * 85)

    # Email Logic
    msg = EmailMessage()
    msg.set_content(report_buffer.getvalue())
    msg['Subject'] = f"GOES Daily Status - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        print(f"Email failed: {e}")


if __name__ == "__main__":
    main()