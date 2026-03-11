#!/usr/bin/env python3
"""
===============================================================================
📡 NAME          : gibs_backfill.py
🚀 DESCRIPTION   : Automated backfill utility for NASA GIBS datasets.
                   Retrieves 30 days of historical SST and TPW imagery.
👤 AUTHOR        : Matha Goram / BeUlta Suite
📅 UPDATED       : 2026-03-07
===============================================================================
"""

import os
import requests
import datetime
from pathlib import Path
import time

# --- ⚙️ CONFIGURATION ---
BASE_ROOT = Path("/home/reza/Videos/satellite/noaa/viirs")
DAYS_TO_BACKFILL = 30

# Target Definitions
TARGETS = {
    "sea_surface_temp": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&LAYERS=MODIS_Terra_L3_SST_MidIR_4km_Night_Daily&STYLE=&FORMAT=image/jpeg&BBOX=-100.0,18.0,-80.0,31.0&WIDTH=4096&HEIGHT=4096&TIME={TIME}",
    "precipitable_water": "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&LAYERS=AMSR2_Total_Precipitable_Water_Day&STYLE=&FORMAT=image/jpeg&BBOX=-101.35,28.04,-91.35,38.04&WIDTH=4096&HEIGHT=4096&TIME={TIME}"
}


def backfill():
    # Start from yesterday (since 'Best' data has a 24h lag)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=DAYS_TO_BACKFILL)

    print(f"🚀 Starting backfill from {start_date} to {end_date}...")

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")

        for name, url_template in TARGETS.items():
            # Setup Paths
            dest_dir = BASE_ROOT / name / "images"
            dest_dir.mkdir(parents=True, exist_ok=True)
            file_path = dest_dir / f"{name}_{date_str}.jpg"

            if file_path.exists():
                print(f"⏭️  Skipping {name} for {date_str} (File exists)")
                continue

            # Fetch Data
            url = url_template.format(TIME=date_str)
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Downloaded: {name} | {date_str}")
                else:
                    print(f"⚠️  Unavailable: {name} | {date_str} (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ Error fetching {date_str}: {e}")

            # Politeness delay for NASA servers
            time.sleep(0.5)

        current_date += datetime.timedelta(days=1)

    print("\n✨ Backfill operation complete.")


if __name__ == "__main__":
    backfill()
