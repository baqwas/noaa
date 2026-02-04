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
from datetime import datetime

# Load configuration
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# ANSI Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_dir_stats(path):
    """Returns counts of images and mp4s in the directory and sub-archives."""
    images = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png'))]

    archive_path = os.path.join(path, "archive")
    mp4s = []
    if os.path.exists(archive_path):
        mp4s = [f for f in os.listdir(archive_path) if f.lower().endswith('.mp4')]

    return len(images), len(mp4s)


def check_disk():
    """Returns disk usage percentage and status."""
    path = os.path.dirname(config['targets'][0]['dir'])
    total, used, free = shutil.disk_usage(path)
    percent = (used / total) * 100
    free_gb = free / (2 ** 30)

    color = GREEN
    if percent > 80: color = YELLOW
    if percent > 95: color = RED

    return f"{color}{percent:.1f}% used ({free_gb:.2f} GB free){RESET}"


def main():
    print(f"\n{BOLD}🛰️  SPACE WEATHER ARCHIVE DASHBOARD{RESET}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    print(f"System Storage: {check_disk()}")
    print("-" * 50)
    print(f"{'Target Name':<20} | {'Images':<8} | {'Archived Videos':<15}")
    print("-" * 50)

    for target in config['targets']:
        name = target['name']
        path = target['dir']

        if os.path.exists(path):
            img_count, vid_count = get_dir_stats(path)

            # Highlight if images are building up (meaning weekly script hasn't run)
            img_str = f"{YELLOW}{img_count:<8}{RESET}" if img_count > 400 else f"{img_count:<8}"

            print(f"{name:<20} | {img_str} | {vid_count:<15}")
        else:
            print(f"{name:<20} | {RED}{'DIR MISSING':<25}{RESET}")

    print("-" * 50 + "\n")


if __name__ == "__main__":
    main()