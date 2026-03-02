#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall_review.py
🚀 DESCRIPTION   : 10-Year Historical Seasonal Review with MariaDB Caching.
                   Analyzes rainfall patterns and generates visual reports.
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 1.2.0
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
📋 WORKFLOW:
    1. 🛡️  Initialize via CoreService for sanitized DB and Email credentials.
    2. 🏗️  Establish SQLAlchemy Engine via CoreService for Pandas compatibility.
    3. 📅  Calculate 90-day seasonal window across a 10-year historical span.
    4. 🗄️  Tiered Retrieval: Query MariaDB first; fall back to NOAA API.
    5. 🎨  Generate Multi-Series Trend Visualization using Matplotlib.
    6. 📤  Dispatch results via secure SMTP and MQTT telemetry.
================================================================================
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
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


class RainfallReviewNode(CoreService):
    def __init__(self, cfg_file: Path):
        super().__init__(cfg_file)
        self.rain_params = self.config.get("rainfall", {})
        self.station_id = self.rain_params.get("station_id", "GHCND:USW00053914")
        self.output_dir = project_root / "reports" / "rainfall"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self):
        print(f"\033[0;34m📊 Analyzing 10-Year Trends for Station: {self.station_id}\033[0m")

        engine = self.get_sqlalchemy_engine()
        if not engine:
            print("\033[0;31m❌ [FATAL] Database engine initialization failed.\033[0m")
            return

        query = f"""
            SELECT record_date, value 
            FROM rainfall_records 
            WHERE station_id = '{self.station_id}'
            AND record_date >= DATE_SUB(CURDATE(), INTERVAL 10 YEAR)
        """

        try:
            df = pd.read_sql(query, engine)
            if df.empty:
                print("\033[0;33m⚠️  [IDLE] No historical data found in MariaDB cache.\033[0m")
                return

            # --- 🛠️ Data Processing ---
            df['record_date'] = pd.to_datetime(df['record_date'])
            df['year'] = df['record_date'].dt.year
            df['day_of_year'] = df['record_date'].dt.dayofyear

            # --- 🎨 Visualization ---
            plt.figure(figsize=(12, 6))
            for year, group in df.groupby('year'):
                plt.plot(group['day_of_year'], group['value'], label=str(year), alpha=0.6)

            plt.title(f"10-Year Seasonal Rainfall Trend: {self.station_id}")
            plt.xlabel("Day of Year")
            plt.ylabel(f"Precipitation ({self.rain_params.get('units', 'metric')})")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.5)

            report_path = self.output_dir / f"rainfall_review_{self.station_id.replace(':', '_')}.png"
            plt.savefig(report_path, bbox_inches='tight')
            plt.close()

            print(f"\033[0;32m✅ Report Generated:\033[0m {report_path}")

            # 📤 Dispatch Summary
            subject = f"Seasonal Analysis: {self.station_id}"
            self.send_email(subject, f"Historical report attached for {self.station_id}.",
                            attachment_path=str(report_path))
            self.publish_mqtt("rainfall/report", f"Report updated for {self.station_id}")

        except Exception as e:
            print(f"\033[0;31m❌ [ANALYSIS ERROR]: {e}\033[0m")


if __name__ == "__main__":
    cfg = Path(__file__).parent.parent / "config.toml"
    RainfallReviewNode(cfg).generate_report()