#!/usr/bin/env python3
"""
================================================================================
🛰️ MODULE        : retrieve_goes.py
🚀 DESCRIPTION   : Retrieval utility for GOES-East and GOES-West imagery.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 2.5.0 (Standardized Pathing & Core Alignment)
📅 UPDATED       : 2026-03-11
================================================================================
📜 VERSION HISTORY:
    - 2.4.8: TOML Array Alignment.
    - 2.5.0: PATH ALIGNMENT. Removed importlib in favor of sys.path injection.
             Synchronized with CoreService v1.9.8 absolute pathing.
================================================================================
"""
import os
import sys
import logging
import datetime
import requests
from pathlib import Path

# --- 🛠️ BEULTA PATH INJECTION ---
project_root = Path("/home/reza/PycharmProjects/noaa")
sys.path.insert(0, str(project_root / 'utilities'))

try:
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Dependency Resolution Error: {e}")
    sys.exit(1)


class GoesRetriever(CoreService):
    def __init__(self):
        super().__init__()
        self.targets = self.config.get('goes_targets', [])
        self.setup_logging()

    def setup_logging(self):
        log_path = self.config.get('goes', {}).get('log_dir', '/home/reza/Videos/satellite/goes/logs')
        log_dir = Path(log_path)
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "goes_retrieval.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def run(self):
        if not self.targets:
            print("⚠️ [IDLE] No GOES targets found in config.toml.")
            return

        print(f"🚀 Starting GOES Ingest Sequence...")
        for target in self.targets:
            name = target.get('name', 'Unknown')
            url = target.get('url')
            # Standardized dir resolution
            target_base = Path(target.get('dir'))

            save_dir = target_base / "images"
            save_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
            filepath = save_dir / f"{name}_{timestamp}.jpg"

            print(f"📡 Fetching {name:.<15} ", end="", flush=True)
            try:
                r = requests.get(url, timeout=30, stream=True)
                r.raise_for_status()
                with filepath.open('wb') as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                print("✅ [OK]")
                logging.info(f"✅ Saved: {name} snapshot to {filepath.name}")
            except Exception as e:
                print("❌ [FAILED]")
                logging.error(f"❌ {name} retrieval error: {e}")
                self.send_report(self.config, f"Target: {name}\nError: {e}", subject="🛰️ GOES INGEST ERROR")


if __name__ == "__main__":
    GoesRetriever().run()
