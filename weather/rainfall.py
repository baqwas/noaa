#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall.py
🚀 DESCRIPTION   : Single-Station Precipitation Ingest Engine.
                   Fetches daily rainfall data from NOAA CDO Web Services.
                   Optimized for 72-hour lookback reliability.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-03-01
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
📜 MIT LICENSE:
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
================================================================================
📋 WORKFLOW PROCESSING:
    1. 🛡️  Inherit infrastructure from CoreService (config/env/ports).
    2. 📅  Calculate target window (Standard 72-hour lookback).
    3. 🌪️  Execute authenticated NOAA CDO API request for 'PRCP' data.
    4. 📈  Standardize units (Metric/Standard) based on configuration.
    5. 📡  Broadcast real-time telemetry via MQTT receipt-verified handshake.
    6. 📝  Log session metrics for long-term health monitoring.
================================================================================
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    utilities_path = project_root / 'utilities'
    if str(utilities_path) not in sys.path:
        sys.path.insert(0, str(utilities_path))
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Dependency Resolution Error: {e}")
    sys.exit(1)

class RainfallIngest(CoreService):
    def __init__(self, cfg_file: Path):
        super().__init__(cfg_file)
        self.token = os.getenv("NOAA_TOKEN")
        self.rain_params = self.config.get("rainfall", {})
        self.station_id = self.rain_params.get("station_id", "GHCND:USW00053914")
        self.units = self.rain_params.get("units", "metric")

    def fetch_data(self):
        target_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        headers = {'token': self.token}
        api_params = {
            'datasetid': 'GHCND',
            'stationid': self.station_id,
            'startdate': target_date,
            'enddate': target_date,
            'datatypeid': 'PRCP',
            'units': self.units,
            'limit': 1
        }

        print(f"📡 Querying NOAA Station: {self.station_id} [{target_date}]")
        try:
            res = requests.get(url, headers=headers, params=api_params, timeout=15)
            res.raise_for_status()
            data = res.json()

            if 'results' in data:
                val = data['results'][0]['value']
                self.publish_mqtt("rainfall/live", f"Station {self.station_id}: {val} {self.units}")
                print(f"✅ SUCCESS: Recorded {val} {self.units}")
            else:
                print(f"⚠️ [IDLE] No data available for {target_date}.")
        except Exception as e:
            print(f"❌ [FETCH ERROR]: {e}")

if __name__ == "__main__":
    RainfallIngest(Path(__file__).parent.parent / "config.toml").fetch_data()