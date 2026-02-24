#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : rainfall_bulk.py
🚀 DESCRIPTION   : Regional Multi-Station Rainfall Data Synchronizer.
                   Features exponential backoff for HTTP 503 error recovery.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-02-24
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
Station Result,Count,Action Taken
✅ SUCCESS,9,Data archived to weather_db.
⚠️ WARNING,2,"API responded, but no rain recorded for this window."
❌ API FAILURE,1,Server busy (503). No data fetched for this station.
================================================================================
"""

import sys
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Any

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


class RainfallBulkSync(CoreService):
    """
    🌊 REGIONAL SYNC ENGINE
    Orchestrates data ingestion with specialized error handling for NOAA API.
    """

    def __init__(self, config_path: str = "../swpc/config.toml"):
        super().__init__(config_path=config_path)
        self.rain_params: dict[str, Any] = self.config.get('rainfall', {})
        self.log_dir = self.rain_params.get('log_dir', '/tmp')
        os.makedirs(self.log_dir, exist_ok=True)

    def fetch_and_sync(self):
        """🛠️ MAIN DATA SYNC WORKFLOW"""

        conn = self.get_db_connection()
        if not conn:
            print("❌ CRITICAL: Database connection failed. Exiting.")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT station_id, name FROM stations")
            stations = cursor.fetchall()

            # Dynamic window from config.toml
            lookback_days = self.rain_params.get('default_lookback', 30)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')

            print(f"🌊 Starting Bulk Sync for {len(stations)} regional stations...")
            print(f"📅 Window: {start_date} to {end_date}\n" + "-" * 60)

            token = self.rain_params.get('token')
            request_headers = {'token': str(token).strip()}

            for s_id, s_name in stations:
                print(f"📡 Requesting: {s_name} ({s_id})...")

                api_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
                payload = {
                    'datasetid': 'GHCND',
                    'stationid': s_id,
                    'startdate': start_date,
                    'enddate': end_date,
                    'datatypeid': 'PRCP',
                    'limit': 1000,
                    'units': self.rain_params.get('units', 'standard')
                }

                # --- 🛡️ ROBUST RETRY LOGIC WITH EXPONENTIAL BACKOFF ---
                max_retries = 3
                success = False

                for attempt in range(max_retries + 1):
                    try:
                        response = requests.get(
                            api_url,
                            headers=request_headers,
                            params=payload,
                            timeout=self.rain_params.get('timeout', 40)
                        )

                        if response.status_code == 200:
                            data = response.json().get('results', [])
                            if data:
                                insert_query = """
                                INSERT INTO rainfall_records (station_id, record_date, value_in)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE value_in = VALUES(value_in)
                                """
                                records = [(s_id, e['date'].split('T')[0], e['value']) for e in data]
                                cursor.executemany(insert_query, records)
                                conn.commit()
                                print(f"   ✅ SUCCESS: {len(records)} records archived.")
                            else:
                                print("   ⚠️ WARNING: No new data available.")
                            success = True
                            break

                        elif response.status_code == 503:
                            # ⏳ Exponential Backoff: Wait 5s, 15s, then 45s
                            wait_time = 5 * (3 ** attempt)
                            print(
                                f"   ⏳ [503 ERROR] NOAA Server Busy. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)

                        else:
                            print(f"   ❌ API FAILURE: HTTP {response.status_code}")
                            break

                    except requests.exceptions.RequestException as e:
                        print(f"   ⚠️ NETWORK ERROR: {e}")
                        time.sleep(2)

                # Politeness delay between different stations
                time.sleep(0.5)

        except Exception as e:
            print(f"❌ SYSTEM EXCEPTION: {e}")

        finally:
            if conn:
                conn.close()
                print("-" * 60 + "\n🔒 Session complete.")


if __name__ == "__main__":
    sync_node = RainfallBulkSync()
    sync_node.fetch_and_sync()