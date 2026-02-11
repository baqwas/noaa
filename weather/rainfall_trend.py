#!/usr/bin/env python3
"""
📦 NAME          : rainfall_trend_v2.py
🚀 DESCRIPTION   : Robust 30-day trend analyzer using KF46 (Rockwall Airport).
                   Automatically adjusts for database lag.
"""

import os
import tomllib
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


class RobustTrendAnalyzer:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.base_dir, "../swpc/config.toml")
        with open(self.config_path, "rb") as f:
            self.config = tomllib.load(f)

    def get_valid_date_range(self, max_lag=7):
        """Finds the most recent date with data to avoid empty plots."""
        api_conf = self.config['noaa_api']
        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"

        for i in range(1, max_lag + 1):
            test_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            params = {
                'datasetid': 'GHCND', 'stationid': api_conf['station_id'],
                'startdate': test_date, 'enddate': test_date,
                'datatypeid': 'PRCP', 'units': 'standard', 'limit': 1
            }
            res = requests.get(url, headers={'token': api_conf['token']}, params=params)
            if res.status_code == 200 and 'results' in res.json():
                print(f"[*] Found latest reliable data on: {test_date}")
                return test_date
        return None

    def build_trend(self):
        end_date = self.get_valid_date_range()
        if not end_date:
            print("[ERROR] No data found in last 7 days. Check Token/Station ID.")
            return

        # Calculate 30-day start from the valid end date
        start_dt = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)
        start_date = start_dt.strftime('%Y-%m-%d')

        # Fetch the block
        params = {
            'datasetid': 'GHCND',
            'stationid': self.config['noaa_api']['station_id'],
            'startdate': start_date,
            'enddate': end_date,
            'datatypeid': 'PRCP',
            'units': 'standard',
            'limit': 100
        }

        res = requests.get("https://www.ncdc.noaa.gov/cdo-web/api/v2/data",
                           headers={'token': self.config['noaa_api']['token']}, params=params)

        data = res.json().get('results', [])
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        # Plotly "Bells & Whistles"
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['date'], y=df['value'], name='Daily Precip', marker_color='#00CC96'))
        fig.update_layout(title=f"30-Day Trend (Ending {end_date})", template='plotly_dark')

        out_file = os.path.join(self.config['paths']['rainfall_dir'], "rainfall_30d.png")
        fig.write_image(out_file)
        print(f"[SUCCESS] Chart saved to: {out_file}")


if __name__ == "__main__":
    analyzer = RobustTrendAnalyzer()
    analyzer.build_trend()