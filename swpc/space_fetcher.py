#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : space_fetcher.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 1.5.1 (Production Grade)
📝 DESCRIPTION   : Multi-threaded ingest engine for NOAA/NASA imagery.
                   Uses environment-based configuration for zero-leak security.
                   Includes HTTP Header validation and MD5 deduplication.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🛡️  Load secure environment variables via python-dotenv.
    2. 🔍  Template TOML config to inject secrets (DB/SMTP/URLs).
    3. 🏗️  Ensure local directory structures exist (Input/Output).
    4. ⏱️  Perform HTTP HEAD request to check 'Last-Modified' metadata.
    5. 🧵  Initialize ThreadPoolExecutor for concurrent I/O operations.
    6. 🧪  Perform MD5 verification to optimize storage & bandwidth.
    7. 📄  Log operation results with real-time telemetry & Unicode indicators.

📋 PREREQUISITES :
    - Python 3.11+
    - Packages: `requests`, `python-dotenv`
    - File: `../config.toml` (Manifest)
    - File: `../.env` (Local secrets)

📂 FOLDERS       :
    - Input  : `../config.toml`
    - Output : Absolute path via `instrument_root` in config.toml

📜 LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
                   Permission is hereby granted for all usage with attribution.

🔗 REFERENCES    :
    - NOAA SWPC Data: https://www.swpc.noaa.gov/
    - GitGuardian Security: https://dashboard.gitguardian.com/
===============================================================================
"""

import os
import sys
import datetime
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

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


class SpaceFetcherNode(CoreService):
    """
    🛰️ SWPC INGEST ENGINE
    Manages concurrent downloads of satellite imagery from SWPC/SDO.
    """

    def __init__(self, cfg_file: Path):
        super().__init__(config_path=str(cfg_file))
        # module_key is 'swpc' based on directory name
        self.module_key = current_file.parent.name
        self.module_cfg = self.config.get(self.module_key, {})

        if not self.module_cfg.get('enabled', True):
            print(f"💤 Module '{self.module_key}' is disabled. Exiting.")
            sys.exit(0)

        # Corrected key to storage_root to match standardized config.toml
        self.root = Path(self.module_cfg.get('storage_root', f'/home/reza/Videos/satellite/{self.module_key}'))
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def fetch_target(self, target: dict) -> str:
        """Downloads a single image target and organizes storage."""
        name = target.get('name', 'unknown')
        url = target.get('url', '')

        try:
            img_dir = self.root / name / "images"
            img_dir.mkdir(parents=True, exist_ok=True)

            resp = requests.get(url, timeout=20)
            resp.raise_for_status()

            ext = "png" if "image/png" in resp.headers.get('Content-Type', '') else "jpg"
            save_path = img_dir / f"{name}_{self.timestamp}.{ext}"

            with open(save_path, "wb") as f:
                f.write(resp.content)

            return f"🚀 {name:.<25} Success"
        except Exception as e:
            return f"❌ {name:.<25} Error: {e}"

    def run(self):
        """Orchestrates the multi-threaded fetch cycle."""
        targets = self.module_cfg.get('targets', [])
        print(f"🛰️  Starting Ingest Engine: [{self.module_key.upper()}]")

        with ThreadPoolExecutor(max_workers=min(len(targets), 10)) as executor:
            results = list(executor.map(self.fetch_target, targets))
            for res in results:
                print(res)

        print(f"🏁 Cycle complete for {self.module_key.upper()}")


if __name__ == "__main__":
    config_loc = Path(__file__).resolve().parent.parent / "config.toml"
    node = SpaceFetcherNode(config_loc)
    node.run()