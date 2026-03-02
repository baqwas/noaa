#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall_trend.py
🚀 DESCRIPTION   : Daily Precipitation Tracker and Trend Analysis.
                   Calculates variance against 7-day rolling averages and
                   visualizes short-term weather shifts.
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
    1. 🛡️  Initialize via CoreService for sanitized DB and MQTT credentials.
    2. 🏗️  Establish SQLAlchemy connectivity for high-performance data frames.
    3. 📊  Query the last 7 days of rainfall records for the target station.
    4. 🧮  Compute 7-day mean and calculate the current day's deviation.
    5. 🎨  Generate a trend sparkline visualization (PNG) in 'Agg' mode.
    6. 📡  Broadcast trend metrics (Avg vs Actual) via MQTT telemetry.
================================================================================
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    sys.path.insert(0, str(project_root / 'utilities'))
    from core_service import CoreService
except ImportError as e:
    print(f"\033[0;31m❌ [CRITICAL] CoreService dependency not found: {e}\033[0m")
    sys.exit(1)


class RainfallTrendNode(CoreService):
    def __init__(self, cfg_file: Path):
        super().__init__(cfg_file)
        self.rain_params = self.config.get("rainfall", {})
        self.station_id = self.rain_params.get("station_id", "GHCND:USW00053914")
        self.output_dir = project_root / "reports" / "trends"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_trend_plot(self):
        print(f"\033[0;34m📈 Initiating 7-Day Variance Analysis: {self.station_id}\033[0m")

        engine = self.get_sqlalchemy_engine()
        query = f"SELECT record_date, value FROM rainfall_records WHERE station_id = '{self.station_id}' ORDER BY record_date DESC LIMIT 7"

        try:
            df = pd.read_sql(query, engine)
            if df.empty:
                print("\033[0;33m⚠️  [IDLE] Insufficient data for 7-day trend analysis.\033[0m")
                return

            avg_rain = df['value'].mean()
            latest_rain = df.iloc[0]['value']
            variance = latest_rain - avg_rain

            print(f"  🔍 Avg: {avg_rain:.2f} | Latest: {latest_rain:.2f} | Var: {variance:+.2f}")

            # 🎨 Short-term Trend Plot
            plt.figure(figsize=(10, 4))
            plt.bar(df['record_date'].dt.strftime('%m-%d'), df['value'], color='#3498db', alpha=0.7)
            plt.axhline(y=avg_rain, color='#e74c3c', linestyle='--', label='7-Day Avg')
            plt.title(f"Weekly Precipitation Variance: {self.station_id}")
            plt.ylabel(f"Value ({self.rain_params.get('units', 'metric')})")
            plt.legend()

            plot_path = self.output_dir / f"trend_{self.station_id.replace(':', '_')}.png"
            plt.savefig(plot_path)
            plt.close()

            print(f"\033[0;32m✅ Trend update published to MQTT.\033[0m")
            self.publish_mqtt("rainfall/trend", f"Latest: {latest_rain} | Var: {variance:+.2f}")

        except Exception as e:
            print(f"\033[0;31m❌ [TREND ERROR]: {e}\033[0m")


if __name__ == "__main__":
    cfg = Path(__file__).parent.parent / "config.toml"
    RainfallTrendNode(cfg).generate_trend_plot()
