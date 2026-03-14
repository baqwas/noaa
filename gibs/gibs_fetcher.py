#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gibs_fetcher.py
👤 ROLE         : Core Ingestion Engine (NASA GIBS)
🔖 VERSION       : 2.9.1
📅 LAST UPDATE  : 2026-03-14
===============================================================================

📝 DESCRIPTION:
    Standardized ingestion engine for NASA Global Imagery Browse Services (GIBS).
    Handles time-series retrieval of satellite layers using WMS 1.3.0 protocols.

⚙️ WORKFLOW / PROCESSING:
    1. Loads system configuration via CoreService class.
    2. Determines temporal lookback window based on 'lookback_days'.
    3. Iterates through configured layers (e.g., VIIRS, MODIS).
    4. Constructs WMS GetMap requests with Coordinate Reference System EPSG:4326.
    5. Downloads and archives images to the localized BeUlta filesystem.

🛠️ PREREQUISITES:
    - Active internet connection for NASA Earthdata access.
    - Configuration file (config.toml) with valid 'gibs' section.
    - utilities/core_service.py accessible in PYTHONPATH.

⚠️ ERROR MESSAGES:
    - [CRITICAL] Failed to load core_service: Dependency or pathing failure.
    - [ERROR] WMS Request Failed: Network timeout or invalid BBOX coordinates.

⚖️ LICENSE:
    MIT License | Copyright (c) 2026 ParkCircus Productions

📚 REFERENCES:
    - NASA GIBS API Documentation: https://www.earthdata.nasa.gov/gibs
    - Meeus, J. (1998). Astronomical Algorithms. (Contextual for IoTML Level 2).
===============================================================================
"""
import os
import sys
import requests
import logging
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
util_path = project_root / "utilities"

if str(util_path) not in sys.path:
    sys.path.insert(0, str(util_path))

try:
    from core_service import TerminalColor, init_mqtt, CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Failed to load core_service: {e}")
    sys.exit(1)

class GIBSFetcher:
    def __init__(self):
        self.clr = TerminalColor()
        self.config = CoreService.get_config()
        # ... [Rest of implementation remains unchanged]
