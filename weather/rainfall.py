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
import logging
from datetime import datetime, timedelta


class RainfallFetcher:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.base_dir, "../swpc/config.toml")

        # Load consolidated section
        with open(self.config_path, "rb") as f:
            config_data = tomllib.load(f)
            self.params = config_data.get('rainfall', {})

        self._setup_logging()

    def _setup_logging(self):
        os.makedirs(self.params['log_dir'], exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(self.params['log_dir'], "rainfall_fetcher.log"),
            level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_daily_rainfall(self):
        lookback = self.params.get('default_lookback', 3)
        target_date = (datetime.now() - timedelta(days=lookback)).strftime('%Y-%m-%d')

        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        headers = {'token': self.params['token']}
        api_params = {
            'datasetid': 'GHCND',
            'stationid': self.params['station_id'],
            'startdate': target_date,
            'enddate': target_date,
            'datatypeid': 'PRCP',
            'units': self.params['units'],
            'limit': 1
        }

        print(f"[*] Node 22 Daily Fetch | Target: {target_date}")
        try:
            res = requests.get(url, headers=headers, params=api_params, timeout=self.params['timeout'])
            res.raise_for_status()
            data = res.json()
            if 'results' in data:
                val = data['results'][0]['value']
                print(f"[SUCCESS] {target_date}: {val} {self.params['units']}")
                logging.info(f"Fetched {val} for {target_date}")
            else:
                print(f"[INFO] No data for {target_date} yet.")
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    RainfallFetcher().get_daily_rainfall()