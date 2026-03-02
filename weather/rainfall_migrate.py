#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall_migrate.py
🚀 DESCRIPTION   : Historical Data Migration Tool for NOAA Rainfall Records.
                   Backfills 3 years of precipitation data into MariaDB.
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
    1. 🛡️  Inherit CoreService for configuration and MariaDB connectivity.
    2. 📅  Generate date ranges for the past 3 calendar years.
    3. 🌪️  Execute bulk API requests to NOAA CDO (GHCND dataset).
    4. 📥  Batch insert records into the 'rainfall_records' table.
    5. 🔄  Handle API rate limiting and 503 Service Unavailable errors.
    6. 📡  Broadcast migration summary via MQTT.
================================================================================
"""

import sys
import requests
import time
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


class RainfallMigration(CoreService):
    """
    🏗️ DATA HYDRATION ENGINE
    Synchronizes historical NOAA data with local MariaDB storage.
    """

    def __init__(self, cfg_file: Path):
        super().__init__(config_path=str(cfg_file))
        self.station_id = self.rain_params.get('station_id')
        self.token = self.rain_params.get('token')
        self.units = self.rain_params.get('units', 'metric')

    def fetch_chunk(self, start_date: str, end_date: str):
        """Fetches a specific date range from NOAA API."""
        url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
        headers = {'token': self.token}
        params = {
            'datasetid': 'GHCND',
            'stationid': self.station_id,
            'startdate': start_date,
            'enddate': end_date,
            'datatypeid': 'PRCP',
            'units': self.units,
            'limit': 1000  # Max allowed per request
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                return response.json().get('results', [])
            elif response.status_code == 503:
                print(f"⚠️  NOAA Server Busy (503). Waiting 10s...")
                time.sleep(10)
                return self.fetch_chunk(start_date, end_date)  # Retry once
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return []

    def run_migration(self):
        """🚀 Orchestrates the 3-year migration process."""
        print(f"🏗️  Starting Migration for Station: {self.station_id}")

        db = self.get_db_connection()
        if not db:
            print("❌ Database connection failed. Aborting.")
            return

        cursor = db.cursor()
        total_inserted = 0

        # Calculate year chunks
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=3 * 365)

        # We'll process in 1-year chunks
        current_start = start_dt
        while current_start < end_dt:
            current_end = min(current_start + timedelta(days=365), end_dt)

            s_str = current_start.strftime('%Y-%m-%d')
            e_str = current_end.strftime('%Y-%m-%d')

            print(f"📅 Requesting Data: {s_str} to {e_str}...")
            results = self.fetch_chunk(s_str, e_str)

            if results:
                batch_count = 0
                for record in results:
                    # NOAA dates come in 'YYYY-MM-DDTHH:MM:SS'
                    date_val = record['date'].split('T')[0]
                    value = record['value']

                    try:
                        cursor.execute(
                            "INSERT INTO rainfall_records (station_id, record_date, value) "
                            "VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE value = VALUES(value)",
                            (self.station_id, date_val, value)
                        )
                        batch_count += 1
                    except Exception as e:
                        print(f"⚠️ SQL Error on {date_val}: {e}")

                db.commit()
                total_inserted += batch_count
                print(f"✅ Successfully cached {batch_count} records for this period.")
            else:
                print(f"ℹ️  No records found for period {s_str} to {e_str}.")

            current_start = current_end + timedelta(days=1)
            time.sleep(1)  # Polite pause between API chunks

        summary = f"Migration Complete: {total_inserted} records synchronized."
        print(f"✨ {summary}")
        self.publish_mqtt("rainfall/migration", summary)

        cursor.close()
        db.close()


if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    target_config = script_path.parent.parent / "config.toml"

    migrator = RainfallMigration(target_config)
    migrator.run_migration()
