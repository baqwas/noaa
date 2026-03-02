#!/usr/bin/env python3
"""
================================================================================
🛰️ MODULE        : retrieve_goes.py
🚀 DESCRIPTION   : Retrieval utility for GOES-East and GOES-West imagery.
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 2.4.8 (TOML Array Alignment)
📅 UPDATED       : 2026-03-01
================================================================================
"""

import os
import sys
import logging
import datetime
import requests
import importlib.util
from pathlib import Path

# --- 📁 Absolute File Import (Conflict Resolution) ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJ_ROOT = SCRIPT_DIR.parent
CORE_PATH = PROJ_ROOT / "utilities" / "core_service.py"

if not CORE_PATH.exists():
    print(f"❌ Critical: core_service.py not found at {CORE_PATH}")
    sys.exit(1)

spec = importlib.util.spec_from_file_location("core_service_local", CORE_PATH)
core_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core_mod)

# --- 🛠️ Instantiate Core Service ---
# The CoreService class handles config loading from PROJ_ROOT/config.toml
service = core_mod.CoreService(config_path="../config.toml")
config = service.config

# --- 🎨 Colors ---
C_YELLOW = '\033[1;33m';
C_RED = '\033[0;31m';
C_GREEN = '\033[0;32m';
C_NC = '\033[0m'


def setup_logging(cfg):
    # Use log_dir from [goes] block or default to script_dir/logs
    log_path = cfg.get('goes', {}).get('log_dir', SCRIPT_DIR / "logs")
    log_dir = Path(log_path)
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_dir / "goes_retrieval.log",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    setup_logging(config)
    print(f"{C_YELLOW}🚀 Starting GOES Ingest Sequence...{C_NC}")

    # 1. Access the top-level [[goes_targets]] array
    targets = config.get('goes_targets', [])

    if not targets:
        print(f"{C_RED}⚠️  [IDLE] No targets found. Key '[[goes_targets]]' appears empty or missing.{C_NC}")
        # Debug: Print top level keys found in config
        print(f"DEBUG: Available root keys: {list(config.keys())}")
        return

    for target in targets:
        name = target.get('name', 'Unknown')
        url = target.get('url')
        # Priority 1: Use 'dir' from target. Priority 2: storage_root/name
        target_base = target.get('dir')

        if not url or not target_base:
            print(f"⚠️  Skipping {name}: Missing URL or Directory in config.")
            continue

        save_dir = Path(target_base) / "images"
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
        filepath = save_dir / f"{name}_{timestamp}.jpg"

        print(f"📡 Fetching {name:.<15} ", end="", flush=True)

        try:
            r = requests.get(url, timeout=30, stream=True)
            r.raise_for_status()

            with filepath.open('wb') as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            print(f"{C_GREEN}[OK]{C_NC}")
            logging.info(f"✅ Saved: {name} snapshot to {filepath.name}")

        except Exception as e:
            print(f"{C_RED}[FAILED]{C_NC}")
            err_msg = f"❌ [FAILURE] {name} retrieval error: {e}"
            logging.error(err_msg)
            service.send_report(f"🛰️ GOES INGEST ERROR\nTarget: {name}\nError: {e}")


if __name__ == "__main__":
    main()
