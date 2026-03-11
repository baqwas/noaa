#!/usr/bin/env python3
"""
===============================================================================
📡 NAME          : hydrology_audit.py
🚀 DESCRIPTION   : Analyzes NASA SMAP Soil Moisture imagery to quantify
                   ground wetness levels for the BeUlta Suite.
                   Detects drought or saturation trends in the Texas BBOX.
👤 AUTHOR        : Matha Goram / BeUlta Suite
📅 UPDATED       : 2026-03-07
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
===============================================================================
"""

import cv2
import numpy as np
import os
import datetime
from pathlib import Path

# --- ⚙️ CONFIGURATION ---
SATELLITE_ROOT = Path("/home/reza/Videos/satellite/noaa/viirs")
LOG_DIR = Path("/home/reza/Videos/satellite/logs")
SYSTEM_AUDIT_LOG = LOG_DIR / "system_audit.log"

# SMAP Wetness Logic:
# NASA SMAP Root Zone Wetness is typically a color-coded map.
# 0-255 scale (Grayscale intensity as a proxy for saturation density).
THRESHOLD_DROUGHT = 80  # Lower intensity in blue-mapped pixels = drier
THRESHOLD_SATURATION = 200  # Higher intensity = flood risk/saturated


def get_latest_image(subdir):
    """Retrieves the most recent JPEG from the soil_moisture directory."""
    img_path = SATELLITE_ROOT / subdir / "images"
    if not img_path.exists():
        return None
    files = list(img_path.glob("*.jpg"))
    return max(files, key=os.path.getctime) if files else None


def analyze_hydrology():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Grab latest SMAP frame
    smap_img = get_latest_image("soil_moisture")

    if not smap_img:
        print(f"[{timestamp}] ⚠️ HYDROLOGY_AUDIT: Missing SMAP imagery. Skipping.")
        return

    # 2. Process with OpenCV
    try:
        # Load image
        img = cv2.imread(str(smap_img))
        if img is None:
            raise ValueError("Failed to decode SMAP image.")

        # In SMAP 'Wetness' maps, blue channels correspond to moisture.
        # We'll calculate the mean of the Blue channel (Index 0 in BGR)
        blue_channel = img[:, :, 0]
        avg_wetness = np.mean(blue_channel)

        # 3. Categorization Logic
        if avg_wetness < THRESHOLD_DROUGHT:
            status = "ARID/DROUGHT"
        elif avg_wetness > THRESHOLD_SATURATION:
            status = "SATURATED/FLOOD_RISK"
        else:
            status = "NOMINAL"

        # 4. Persistent Logging
        log_entry = (f"[{timestamp}] [HYDRO_AUDIT] Status: {status} | "
                     f"Wetness_Index: {avg_wetness:.2f}\n")

        with open(SYSTEM_AUDIT_LOG, "a") as f:
            f.write(log_entry)

        print(f"💧 Hydrology Analysis: {status} (Index: {avg_wetness:.2f})")

    except Exception as e:
        with open(SYSTEM_AUDIT_LOG, "a") as f:
            f.write(f"[{timestamp}] [HYDRO_AUDIT_ERROR] {str(e)}\n")
        print(f"❌ Error during hydrology analysis: {e}")


if __name__ == "__main__":
    analyze_hydrology()
