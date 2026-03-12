#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : sync_audit.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.1.0
📅 LAST UPDATE  : 2026-03-12
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY (2026-03-12 Audit Trail):
    - 1.0.0: Initial Release. Implemented 24-hour lookback logic to verify
             T-1 alignment following the gibs_fetcher.py v2.8.3 update.
    - 1.1.0: DATA DENSITY UPDATE. Added file size calculation (KB/MB) to
             distinguish between valid imagery and NASA Service Exceptions.

📝 DESCRIPTION:
    A forensic precision tool designed to verify the success of overnight
    satellite data ingests. It calculates the 'Sync Delta' and file size
    across all instrument subdirectories to ensure that the fleet is
    receiving high-density data within nominal time windows.

🛠️ PREREQUISITES:
    - Pathlib (Standard Library)
    - Validated directory structure at /home/reza/Videos/satellite/gibs
===============================================================================
"""

from pathlib import Path
from datetime import datetime, timedelta
import os

# --- ⚙️ CONFIGURATION ---
GIBS_ROOT = Path("/home/reza/Videos/satellite/gibs")
WINDOW_HOURS = 24


def format_size(size_bytes):
    """Converts raw bytes to a human-readable string (KB/MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def run_precision_audit():
    """
    Performs a recursive scan of the GIBS_ROOT directory to report on
    temporal alignment and data density (file size).
    """
    print(f"{'=' * 80}")
    print(f"🛰️  BEULTA SYNC PRECISION AUDIT | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")
    print(f"{'FILE NAME':<40} | {'SYNC DELTA':<15} | {'DENSITY'}")
    print(f"{'-' * 80}")

    if not GIBS_ROOT.exists():
        print(f"❌ ERROR: GIBS Root not found at {GIBS_ROOT}")
        return

    now = datetime.now()
    threshold = now - timedelta(hours=WINDOW_HOURS)
    found_any = False

    for instrument_dir in GIBS_ROOT.iterdir():
        if instrument_dir.is_dir():
            recent_files = []

            for file in instrument_dir.glob("*.*"):
                stats = file.stat()
                mtime = datetime.fromtimestamp(stats.st_mtime)

                if mtime > threshold:
                    recent_files.append({
                        "name": file.name,
                        "mtime": mtime,
                        "size": stats.st_size
                    })

            if recent_files:
                found_any = True
                print(f"\n📂 INSTRUMENT: {instrument_dir.name}")
                for item in recent_files:
                    delta = now - item['mtime']
                    delta_str = f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m ago"
                    density = format_size(item['size'])

                    # Alert if density is suspiciously low (typical for XML errors)
                    alert = "⚠️ LOW DENSITY" if item['size'] < 5000 else "✅"

                    print(f"  {alert} {item['name']:<38} | {delta_str:<15} | {density}")
            else:
                print(f"\n⚠️  STALL DETECTED: {instrument_dir.name} (No updates in {WINDOW_HOURS}h)")

    if not found_any:
        print(f"\n🚨 [CRITICAL] No files synchronized within the last {WINDOW_HOURS} hours.")

    print(f"\n{'=' * 80}")
    print("🏁 Audit Complete.")


if __name__ == "__main__":
    run_precision_audit()
