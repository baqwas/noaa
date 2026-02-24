#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall_trend.py
🚀 DESCRIPTION   : Daily Rainfall Tracker and Trend Analysis.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-02-24
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Any

# --- 🛠️ PRIORITY PATH INJECTION ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    utilities_path = os.path.abspath(os.path.join(current_dir, '..', 'utilities'))
    if utilities_path not in sys.path:
        sys.path.insert(0, utilities_path)
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Dependency Resolution Error: {e}")
    sys.exit(1)

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


class RainfallTrendNode(CoreService):
    def __init__(self, config_path: str = "../swpc/config.toml"):
        super().__init__(config_path=config_path)
        self.rain_params: dict[str, Any] = self.config.get('rainfall', {})
        self.station_id = self.rain_params.get('station_id', 'UNKNOWN')

        # Path extraction from config.toml
        self.output_dir = self.rain_params.get('output_dir', './data')
        self.log_dir = self.rain_params.get('log_dir', './logs')

        # Ensure specific sub-folders exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def fetch_recent_data(self):
        """Retrieves recent data for trend plotting."""
        days = self.rain_params.get('trend_window', 30)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        conn = self.get_db_connection()
        df = pd.DataFrame()

        if conn:
            query = """
                SELECT record_date as date, value_in as value 
                FROM rainfall_records 
                WHERE station_id = %s AND record_date BETWEEN %s AND %s
                ORDER BY record_date ASC
            """
            df = pd.read_sql(query, conn, params=(self.station_id, start_date.date(), end_date.date()))
            conn.close()
        return df

    def generate_trend_plot(self):
        """Creates the daily trend visualization."""
        df = self.fetch_recent_data()
        if df.empty:
            print("⚠️ No data found for trend analysis.")
            return

        plt.style.use(self.rain_params.get('theme', 'dark_background'))
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot bars for daily totals
        ax.bar(df['date'], df['value'], color=self.rain_params.get('bar_color', '#3498db'), label='Daily Rain')

        # Overlay trend line if configured
        if self.rain_params.get('show_trend_line', True):
            df['trend'] = df['value'].rolling(window=7).mean()
            ax.plot(df['date'], df['trend'], color=self.rain_params.get('trend_color', '#e74c3c'),
                    linewidth=2, label='7-Day Moving Avg')

        ax.set_title(f"Precipitation Trend: {self.station_id}", fontsize=14)
        ax.set_ylabel(f"Value ({self.rain_params.get('units', 'standard')})")
        ax.legend()

        plt.tight_layout()

        # Output to /home/reza/Videos/satellite/weather/data/
        out_path = os.path.join(self.output_dir, "rainfall_trend_latest.png")
        plt.savefig(out_path, dpi=self.rain_params.get('dpi', 150))
        plt.close()
        print(f"✅ Trend visual saved to: {out_path}")


if __name__ == "__main__":
    node = RainfallTrendNode()
    node.generate_trend_plot()