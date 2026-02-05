#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           space_status.py
Description:    Quick-look dashboard for the Space Weather Archive. Displays
                image counts, archive totals, and disk health.
License:        MIT License
Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
-------------------------------------------------------------------------------
"""

import os
import shutil
import tomllib
import smtplib
import io
from datetime import datetime
from email.message import EmailMessage

# Load configuration
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# Safety threshold from your fetcher logic
MIN_DISK_GB = 2.0


def get_dir_stats(path):
    """Returns counts and total MB for images and mp4s."""
    image_files = [os.path.join(path, f) for f in os.listdir(path)
                   if f.lower().endswith(('.jpg', '.png'))]
    image_size_mb = sum(os.path.getsize(f) for f in image_files) / (1024 * 1024)

    archive_path = os.path.join(path, "archive")
    mp4_size_mb = 0
    mp4_count = 0
    if os.path.exists(archive_path):
        mp4_files = [os.path.join(archive_path, f) for f in os.listdir(archive_path)
                     if f.lower().endswith('.mp4')]
        mp4_count = len(mp4_files)
        mp4_size_mb = sum(os.path.getsize(f) for f in mp4_files) / (1024 * 1024)

    return len(image_files), image_size_mb, mp4_count, mp4_size_mb


def get_disk_info():
    """Returns detailed disk stats."""
    path = os.path.dirname(config['targets'][0]['dir'])
    total, used, free = shutil.disk_usage(path)
    percent = (used / total) * 100
    free_gb = free / (2 ** 30)
    return percent, free_gb


def send_dashboard_email(content):
    """Sends the captured dashboard output via SMTP."""
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = f"Weekly Space Weather Archive Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']

    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send dashboard email: {e}")


def main():
    report_buffer = io.StringIO()

    def report(text):
        print(text)
        report_buffer.write(text + "\n")

    percent_used, free_gb = get_disk_info()
    status = "OK"
    if percent_used > 80: status = "WARNING"
    if percent_used > 95: status = "CRITICAL"

    report(f"🛰️  SPACE WEATHER ARCHIVE DASHBOARD")
    report(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report("-" * 85)
    report(f"System Storage: {percent_used:.1f}% used ({free_gb:.2f} GB free) - Status: {status}")
    report("-" * 85)
    report(f"{'Target Name':<18} | {'Img Cnt':<7} | {'Img Size':<10} | {'Vid Cnt':<7} | {'Vid Size':<10}")
    report("-" * 85)

    total_images_size = 0
    total_videos_size = 0
    total_img_count = 0

    for target in config['targets']:
        name = target['name']
        path = target['dir']

        if os.path.exists(path):
            img_c, img_s, vid_c, vid_s = get_dir_stats(path)
            total_images_size += img_s
            total_videos_size += vid_s
            total_img_count += img_c

            flag = "!" if img_c > 400 else " "
            report(f"{name:<18} | {img_c:<7}{flag} | {img_s:>7.1f} MB | {vid_c:<7} | {vid_s:>7.1f} MB")
        else:
            report(f"{name:<18} | DIR MISSING")

    report("-" * 85)

    # --- Projected Growth Logic ---
    # Calculate average image size (approx 150-300KB usually)
    avg_img_mb = (total_images_size / total_img_count) if total_img_count > 0 else 0.25

    # Assuming your 15-minute cron (96 fetches/day) for each of your 4 targets
    daily_img_count = 96 * len(config['targets'])
    daily_burn_mb = daily_img_count * avg_img_mb

    # Usable space before hitting the 2GB safety floor
    usable_gb = max(0, free_gb - MIN_DISK_GB)
    usable_mb = usable_gb * 1024

    days_remaining = usable_mb / daily_burn_mb if daily_burn_mb > 0 else 999

    report(f"{'TOTALS':<18} | {'Combined Image Size:':<18} {total_images_size:>10.1f} MB")
    report(f"{'':<18} | {'Combined Video Size:':<18} {total_videos_size:>10.1f} MB")
    report("-" * 85)
    report(f"GROWTH FORECAST:")
    report(f" * Avg. Daily Accumulation: {daily_burn_mb:.1f} MB")
    report(f" * Estimated Storage Life:  {int(days_remaining)} days remaining (until {MIN_DISK_GB}GB limit)")
    report("-" * 85)
    report("\nNote: '!' indicates high image count (verify compile_weekly.sh).")

    send_dashboard_email(report_buffer.getvalue())
    report_buffer.close()


if __name__ == "__main__":
    main()
