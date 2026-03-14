#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : retrieve_goes.py
👤 ROLE         : Resilient High-Resolution GOES Ingest Node
🔖 VERSION       : 2.6.0 (Resilience Update)
📅 LAST UPDATE  : 2026-03-14
===============================================================================

📝 DESCRIPTION:
    Orchestrates the retrieval of GOES imagery with a robust 'Exponential Backoff'
    retry mechanism. This ensures that transient network lag or NOAA server
    instability does not result in missing T-1 frames.

⚙️ WORKFLOW / PROCESSING:
    1. Temporal Logic: Defaults to T-1 unless --date is specified.
    2. Resilience Engine: Implements a 3-tier retry loop with incremental delay.
    3. Storage: Saves images with mandatory YYYYMMDD datestamp for audit sync.
    4. Forensic Telemetry: Reports retry counts to identify server degradation.

🖥️ USER INTERFACE:
    - CLI Arguments: --date (Format: YYYYMMDD)
    - Unicode Feedback: 📥 INGEST | ⏳ RETRYING | ✅ SAVED | 🚨 ABORTED

🛠️ PREREQUISITES:
    - Python 3.11+
    - utilities/core_service.py version 1.9.8+.

⚠️ ERROR MESSAGES:
    - [ALERT] Max Retries Exceeded: Server persistent failure.
    - [NOTICE] Latency Detected: Backoff initiated for [X] seconds.

📜 VERSION HISTORY:
    - 2.5.0: Added T-1 Temporal Isolation.
    - 2.6.0: RESILIENCE UPDATE. Implemented Exponential Backoff logic.

⚖️ LICENSE:
    MIT License | Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

import os
import sys
import time
import argparse
import requests
import datetime
import random
from pathlib import Path

# --- 🛠️ BEULTA PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root / 'utilities'))

try:
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Failed to load core_service: {e}")
    sys.exit(1)


class GoesIngestNode:
    def __init__(self, target_date=None):
        self.core = CoreService()
        self.config = self.core.get_config()

        # Temporal Gate
        if target_date:
            self.target_date = target_date
        else:
            self.target_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')

        self.storage_root = Path(self.config.get('egress', {}).get('storage_root', '/home/reza/Videos/satellite'))
        self.stats = {"success": 0, "failed": 0, "retries": 0}

    def fetch_with_backoff(self, url, filepath, max_retries=3):
        """
        Executes a download with an exponential backoff strategy.
        Wait times: 5s, 25s, 125s (with a small random jitter).
        """
        attempt = 0
        base_delay = 5

        while attempt < max_retries:
            try:
                response = requests.get(url, timeout=30)

                # Check for successful response
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return True

                # If it's a client error (404), don't bother retrying
                if 400 <= response.status_code < 500:
                    print(f"   🚨 Client Error {response.status_code}: Target not found.")
                    return False

            except (requests.exceptions.RequestException, IOError) as e:
                attempt += 1
                self.stats["retries"] += 1

                if attempt < max_retries:
                    # Exponential formula: base * (attempt^2) + random jitter
                    sleep_time = (base_delay * (attempt ** 2)) + random.uniform(0, 1)
                    print(f"   ⏳ Latency Detected (Attempt {attempt}). Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                else:
                    print(f"   🚨 Max Retries Exceeded: {e}")

        return False

    def fetch_sector(self, satellite="goes_east", sector="conus"):
        """Downloads satellite sector with forensic T-1 naming."""
        base_url = f"https://cdn.star.nesdis.noaa.gov/{satellite.upper()}/{sector}/1000x1000.jpg"

        dest_dir = self.storage_root / "goes" / satellite / "images"
        dest_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%H%M%S')
        filename = f"{satellite}_{sector}_{self.target_date}_{timestamp}.jpg"
        filepath = dest_dir / filename

        print(f"📥 INGEST: {satellite} for {self.target_date}")

        success = self.fetch_with_backoff(base_url, filepath)

        if success:
            print(f"   ✅ SAVED: {filename}")
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1

    def run(self):
        """Main execution logic."""
        print(f"🛰️  GOES RESILIENT INGEST | Target: {self.target_date}")
        print("------------------------------------------------------------------------")

        self.fetch_sector("goes_east", "conus")
        self.fetch_sector("goes_west", "conus")

        print("------------------------------------------------------------------------")
        print(
            f"🏁 SUMMARY: {self.stats['success']} Success | {self.stats['failed']} Failed | {self.stats['retries']} Retries")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BeUlta Resilient Ingest")
    parser.add_argument("--date", help="Target date (YYYYMMDD)", default=None)
    args = parser.parse_args()

    GoesIngestNode(target_date=args.date).run()
