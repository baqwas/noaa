#!/usr/bin/env python3
# ==============================================================================
# 🛡️ AUDIT & COMPLIANCE DOCUMENTATION
# ==============================================================================
# SCRIPT NAME    : check_spatial_audit.py
# VERSION        : 1.1.0
# AUTHOR         : Matha Goram
# LICENSE        : MIT License (c) 2026 ParkCircus Productions
# PROJECT        : NASA NOAA Imagery
# AUDIT CLASS    : GEO-SPATIAL-INTEGRITY-01
#
# DESCRIPTION:
#   Validates geographic telemetry for the North Texas data cluster.
#   Calculates the centroid of ingested data points and measures drift
#   relative to Lavon, TX (Home Base). Includes persistent logging.
#
# MIT LICENSE:
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files... (Standard MIT terms)
#
# REFERENCES:
# 1. Haversine Formula for Geodesic Distance
# 2. ISO 19115: Geographic Information Metadata Standard
#
# RUNS:
# 1. Whenever you modify your data ingestion parameters
#    (e.g., changing the Overpass BBOX or swapping data providers)
#    to ensure the new data source is correctly centered.
# 2. When you add new counties to your data cluster,
#    run it to verify that the centroid remains within the acceptable threshold
#    (15km of Nevada).
# 3. If your dashboard (qlog) shows an AUDIT ALERT or "OUT OF BOUNDS" error,
#    run it manually to isolate which specific data points are causing the drift.
# ==============================================================================

import sys
import logging
import os
from datetime import datetime

# External Dependencies
try:
    import numpy as np
except ImportError:
    print("\033[0;31m❌ ERROR: Dependency 'numpy' missing. Run: pip install numpy\033[0m")
    sys.exit(1)

# 🎨 UI/UX: ANSI Color and Unicode Definitions
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

ICON_HOME = "🏠"
ICON_SCAN = "📡"
ICON_SUCCESS = "✅"
ICON_ALERT = "🚨"
ICON_ERROR = "❌"

# 📍 Spatial Reference: Lavon, TX
REFERENCE_LAT = 33.0232
REFERENCE_LON = -96.4372
DRIFT_THRESHOLD_KM = 15.0

# 📂 Logging Configuration
LOG_DIR = "/home/reza/Videos/quants/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"spatial_audit_{datetime.now().strftime('%Y-%m')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SpatialAudit")

def calculate_centroid(coords):
    """
    Computes the geometric mean of a coordinate set.
    """
    try:
        if not coords:
            raise ValueError("Coordinate dataset is empty.")

        lats = [float(c[0]) for c in coords]
        lons = [float(c[1]) for c in coords]

        return np.mean(lats), np.mean(lons)

    except (ValueError, TypeError) as ee:
        logger.error(f"{RED}{ICON_ERROR} CALCULATION ERROR: {str(ee)}{NC}")
        return None

def run_spatial_audit(current_centroid):
    """
    Workflow Processing: Evaluates drift against reference location.
    """
    if current_centroid is None:
        return False

    # Haversine-lite for North Texas scale
    lat_diff_km = (current_centroid[0] - REFERENCE_LAT) * 111
    lon_diff_km = (current_centroid[1] - REFERENCE_LON) * 96
    drift_distance = np.sqrt(lat_diff_km ** 2 + lon_diff_km ** 2)

    logger.info(f"{BLUE}============================================================{NC}")
    logger.info(f"{BLUE}{ICON_SCAN} SPATIAL INTEGRITY AUDIT INITIATED{NC}")
    logger.info(f"{ICON_HOME} Reference Point : Lavon, TX ({REFERENCE_LAT}, {REFERENCE_LON})")
    logger.info(f"📍 Data Centroid  : {current_centroid[0]:.4f}, {current_centroid[1]:.4f}")

    if drift_distance <= DRIFT_THRESHOLD_KM:
        logger.info(f"{GREEN}{ICON_SUCCESS} AUDIT PASSED: Drift is {drift_distance:.2f} km (Within Bounds){NC}")
        return True
    else:
        logger.warning(f"{RED}{ICON_ALERT} AUDIT ALERT: Drift is {drift_distance:.2f} km (OUT OF BOUNDS){NC}")
        return False

if __name__ == "__main__":
    sample_cluster = [
        (33.0232, -96.4372), (33.0151, -96.5389),
        (33.1972, -96.6398), (32.9312, -96.4597),
        (33.0435, -96.3719)
    ]

    try:
        centroid = calculate_centroid(sample_cluster)
        success = run_spatial_audit(centroid)
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.critical(f"{RED}{ICON_ERROR} CRITICAL SYSTEM EXCEPTION: {str(e)}{NC}")
        sys.exit(2)
