#!/usr/bin/env python3
"""
===============================================================================
📡 NAME          : visibility_audit.py
🚀 DESCRIPTION   : Compares Aerosol Optical Depth (AOD) vs True Color imagery
                   using OpenCV to quantify atmospheric interference.
                   Generates a visibility flag for the Bash render engine to
                   apply a "HAZY DAY" overlay if particulates are high.
👤 AUTHOR        : Matha Goram / BeUlta Suite
📅 UPDATED       : 2026-03-07
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
===============================================================================
"""

import cv2
import numpy as np
import os
import datetime
import sys
from pathlib import Path

# --- ⚙️ CONFIGURATION ---
# Paths are set to your standardized BeUlta satellite root
SATELLITE_ROOT = Path("/home/reza/Videos/satellite/noaa/viirs")
LOG_DIR = Path("/home/reza/Videos/satellite/logs")
SYSTEM_AUDIT_LOG = LOG_DIR / "system_audit.log"
VISIBILITY_FLAG = LOG_DIR / "visibility_flag.txt"

# THRESHOLD_AOD: 0-255 grayscale intensity.
# Higher values represent thicker aerosol/dust concentration.
# 180 is a baseline for "Significant Haze" in NASA's MODIS AOD layer.
THRESHOLD_AOD = 180


def get_latest_image(subdir):
    """
    Retrieves the most recent JPEG from a specific instrument subdirectory.
    """
    img_path = SATELLITE_ROOT / subdir / "images"
    if not img_path.exists():
        return None

    files = list(img_path.glob("*.jpg"))
    return max(files, key=os.path.getctime) if files else None


def analyze_visibility():
    """
    Performs pixel-intensity analysis on the Aerosol layer and compares it
    to the True Color baseline. Logs result and manages the visibility flag.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Grab latest frames
    true_color_img = get_latest_image("true_color")
    aerosol_img = get_latest_image("aerosols")

    if not true_color_img or not aerosol_img:
        print(f"[{timestamp}] ⚠️ VISIBILITY_AUDIT: Missing image pairs. Analysis skipped.")
        return

    # 2. Process with OpenCV
    try:
        # Load as Grayscale (intensity map)
        tc_gray = cv2.imread(str(true_color_img), cv2.IMREAD_GRAYSCALE)
        ao_gray = cv2.imread(str(aerosol_img), cv2.IMREAD_GRAYSCALE)

        if tc_gray is None or ao_gray is None:
            raise ValueError("OpenCV failed to decode one or more images.")

        # Calculate Mean Brightness (0-255)
        avg_tc = np.mean(tc_gray)
        avg_ao = np.mean(ao_gray)

        # 3. Decision Logic
        status = "CLEAR"
        if avg_ao > THRESHOLD_AOD:
            status = "LOW_VISIBILITY"

        # 4. Flag Management
        # This file is checked by compile_all_daily.sh
        if status == "LOW_VISIBILITY":
            with open(VISIBILITY_FLAG, "w") as f:
                f.write("HAZY")
            print(f"🚩 Visibility Flag Set: {status}")
        else:
            if VISIBILITY_FLAG.exists():
                os.remove(VISIBILITY_FLAG)
            print(f"☀️ Visibility Status: {status}")

        # 5. Persistent Logging
        log_entry = (f"[{timestamp}] [VISIBILITY_AUDIT] Status: {status} | "
                     f"AOD_Intensity: {avg_ao:.2f} | TC_Intensity: {avg_tc:.2f}\n")

        with open(SYSTEM_AUDIT_LOG, "a") as f:
            f.write(log_entry)

    except Exception as e:
        with open(SYSTEM_AUDIT_LOG, "a") as f:
            f.write(f"[{timestamp}] [VISIBILITY_AUDIT_ERROR] {str(e)}\n")
        print(f"❌ Error during analysis: {e}")


if __name__ == "__main__":
    analyze_visibility()
