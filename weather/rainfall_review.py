#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall_review.py
🚀 DESCRIPTION   : 10-Year Historical Seasonal Review with MariaDB Caching.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-02-24
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
PREREQUISITES:
1. MariaDB table 'rainfall_records' must exist in the target database.
2. config.toml must be populated in ../swpc/
3. NOAA CDO API Token must be active.
4. Python Packages: pandas, sqlalchemy, mysql-connector-python/mariadb.

WORKFLOW PROCESSING:
1. Path Normalization: Injects /utilities into sys.path to resolve CoreService.
2. SQLAlchemy Engine: Establishes a formal engine to prevent DBAPI2 warnings.
3. Window Calculation: Determines a 90-day window centered on the current date.
4. Historical Iteration: Loops through 10 years of data (handling leap years).
5. Tiered Data Retrieval: Checks MariaDB cache first; falls back to NOAA API.
6. Visualization: Renders a comparative multi-line plot for seasonal trends.
7. Distribution: Dispatches PNG report via SMTP and MQTT telemetry.
================================================================================
"""

import os
import sys
import time
import warnings
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Any

# --- 🛠️ PRIORITY PATH INJECTION ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    utilities_path = os.path.abspath(os.path.join(current_dir, '..', 'utilities'))

    if utilities_path not in sys.path:
        sys.path.insert(0, utilities_path)

    from core_service import CoreService

    print(f"✅ [INIT] Local CoreService resolved: {utilities_path}")

except (ImportError, ModuleNotFoundError) as imp_err:
    print(f"❌ [CRITICAL] Dependency Resolution Error: {imp_err}")
    sys.exit(1)

# --- 🔕 WARNING MANAGEMENT ---
warnings.filterwarnings("ignore", category=UserWarning, module='pandas')

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


class RainfallReviewNode(CoreService):
    """
    📅 HISTORICAL REVIEW ENGINE
    Inherits service connectivity (DB, SMTP, MQTT) from CoreService.
    """

    def __init__(self, config_path: str = "../swpc/config.toml"):
        super().__init__(config_path=config_path)
        self.rain_params: dict[str, Any] = self.config.get('rainfall', {})
        self.midpoint_str: str = ""
        self.station_id: str = self.rain_params.get('station_id', 'UNKNOWN')

        # Paths from config.toml
        self.output_dir = self.rain_params.get('output_dir', './')
        self.log_dir = self.rain_params.get('log_dir', './logs')

        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def get_annual_data(self, year: int) -> pd.DataFrame:
        """
        🔄 Retrieves data for a specific year window, prioritizing Local Cache.
        """
        today = datetime.now()

        try:
            midpoint = datetime(year, today.month, today.day)
        except ValueError:
            midpoint = datetime(year, today.month, today.day - 1)

        start_dt = (midpoint - timedelta(days=45)).strftime('%Y-%m-%d')
        end_dt = (midpoint + timedelta(days=45)).strftime('%Y-%m-%d')
        self.midpoint_str = midpoint.strftime('%B %d')

        conn = self.get_db_connection()
        df = pd.DataFrame()

        try:
            if conn is not None:
                query = """
                    SELECT record_date as date, value_in as value 
                    FROM rainfall_records 
                    WHERE station_id = %s AND record_date BETWEEN %s AND %s
                    ORDER BY record_date ASC
                """
                df = pd.read_sql(query, conn, params=(self.station_id, start_dt, end_dt))

            if df.empty or len(df) < 70:
                print(f"📡 Cache miss/low density for {year}. Querying NOAA CDO...")
                url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
                headers = {'token': self.rain_params.get('token')}
                api_params = {
                    'datasetid': 'GHCND',
                    'stationid': self.station_id,
                    'startdate': start_dt,
                    'enddate': end_dt,
                    'datatypeid': 'PRCP',
                    'units': self.rain_params.get('units', 'standard'),
                    'limit': 1000
                }

                res = requests.get(url, headers=headers, params=api_params, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    if 'results' in data:
                        df = pd.DataFrame(data['results'])
                        df['date'] = pd.to_datetime(df['date']).dt.date

                        if conn is not None:
                            cursor = conn.cursor()
                            sql = "INSERT IGNORE INTO rainfall_records (station_id, record_date, value_in) VALUES (%s, %s, %s)"
                            for _, row in df.iterrows():
                                cursor.execute(sql, (self.station_id, row['date'], row['value']))
                            conn.commit()
                            cursor.close()

                time.sleep(0.4)

            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df['date'] = df['date'].dt.normalize()
                df['day_idx'] = (df['date'] - df['date'].min()).dt.days

            return df

        except Exception as e:
            print(f"❌ Error during historical fetch for {year}: {e}")
            return pd.DataFrame()
        finally:
            if conn is not None:
                conn.close()

    def run_review(self) -> None:
        """📈 Execute the 10-year comparative visualization workflow."""
        current_year = datetime.now().year
        years_to_review = self.rain_params.get('review_years', 10)

        plt.style.use(self.rain_params.get('theme', 'dark_background'))
        fig, ax = plt.subplots(figsize=(14, 8))

        has_plot_data = False
        print(f"📊 Analyzing {years_to_review}-year seasonal trends for Station: {self.station_id}")

        for yr in range(current_year, current_year - years_to_review, -1):
            df = self.get_annual_data(yr)
            if not df.empty:
                has_plot_data = True
                is_current = (yr == current_year)

                ax.plot(
                    df['day_idx'],
                    df['value'],
                    label=str(yr),
                    linewidth=4.5 if is_current else 1.2,
                    alpha=1.0 if is_current else 0.4,
                    zorder=10 if is_current else 1
                )

        if not has_plot_data:
            print("❌ Processing Aborted: No valid data found.")
            return

        ax.set_title(f"{years_to_review}-Year Historical Review: {self.station_id}", fontsize=18, pad=20)
        ax.set_xlabel(f"Days into Seasonal Window (Centered on {self.midpoint_str})", fontsize=12)
        ax.set_ylabel(f"Daily Precipitation ({self.rain_params.get('units', 'Inches')})", fontsize=12)
        ax.grid(True, linestyle=':', alpha=0.3)
        ax.legend(title="Year", loc='upper left', bbox_to_anchor=(1, 1), frameon=False)

        plt.tight_layout()

        # Target absolute path for output PNG
        out_filename = "rainfall_review_10y.png"
        out_path = os.path.join(self.output_dir, out_filename)

        plt.savefig(out_path, dpi=self.rain_params.get('dpi', 200))
        plt.close()

        print(f"✅ [SUCCESS] Visual report generated: {out_path}")

        self.send_email(
            subject=f"{years_to_review}-Year Rainfall Review [{self.midpoint_str}]",
            body=f"Seasonal historical analysis complete for station {self.station_id}. Report saved to {out_path}.",
            attachment_path=out_path
        )
        self.publish_mqtt("rainfall/review_complete", datetime.now().isoformat())


if __name__ == "__main__":
    node = RainfallReviewNode()
    node.run_review()