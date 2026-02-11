#!/usr/bin/env python3
"""
📦 NAME          : rainfall.py
👤 AUTHOR        : Matha Goram
📅 VERSION       : 1.5.0
🚀 UPDATED       : 2026-02-10
📝 DESCRIPTION   : Fetches daily precipitation data from NOAA CDO Web Services.
                   Updated to use a 72-hour lookback for production stability.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
"""

import os
import tomllib
import requests
from datetime import datetime, timedelta


def find_latest_data(config_path="../swpc/config.toml", max_search=14):
    # 1. Load Config
    with open(config_path, "rb") as f:
        conf = tomllib.load(f)

    api_key = conf['noaa_api']['token']
    station = conf['noaa_api']['station_id']
    url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"

    print(f"--- Node 22: Searching for Latest Data for {station} ---")

    # 2. Loop backwards from today
    for i in range(1, max_search + 1):
        target_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')

        params = {
            'datasetid': 'GHCND',
            'stationid': station,
            'startdate': target_date,
            'enddate': target_date,
            'datatypeid': 'PRCP',
            'units': 'standard',
            'limit': 1
        }

        try:
            response = requests.get(url, headers={'token': api_key}, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    val = data['results'][0]['value']
                    print(f"✅ FOUND! Date: {target_date} | Value: {val} inches")
                    print(f"📈 Current Lag for this station: {i} days.")
                    return i, target_date
                else:
                    print(f"[-] No data for {target_date}...")
        except Exception as e:
            print(f"[!] Error on {target_date}: {e}")

    print(f"❌ No data found in the last {max_search} days. Station might be inactive.")
    return None


if __name__ == "__main__":
    find_latest_data()