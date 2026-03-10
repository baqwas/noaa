#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : gibs_fetcher.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 1.3.0
📅 LAST UPDATE  : 2026-03-07
===============================================================================

📑 VERSION HISTORY:
    - 1.0.0: Initial NASA GIBS Fetcher (Basic requests implementation).
    - 1.1.0: Path Logic Unification (instrument_root + subdir resolution).
    - 1.2.0: Atomic Ingest Integration (stream_binary_resource & .tmp swap).
    - 1.3.0: Smart Retry Logic (T-2 fallback & XML Service Exception detection).

📝 DESCRIPTION:
    Iterative NASA GIBS fetcher. Processes satellite layers defined in
    config.toml. Implements automated date fallback logic; if T-1 data
    is not yet finalized (returns XML), it rolls back to T-2.

🛠️ PREREQUISITES:
    - core_service.py in ~/noaa/utilities
    - requests (pip install requests)

===============================================================================
"""

import os
import sys
import datetime
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
# 1. Force your local utilities directory to the absolute front
util_path = str(Path.home() / "PycharmProjects" / "noaa" / "utilities")
if util_path in sys.path:
    sys.path.remove(util_path)
sys.path.insert(0, util_path)

# 2. Clear any 'core_service' already cached from the .venv package
if 'core_service' in sys.modules:
    del sys.modules['core_service']

# 3. Now import your custom code safely
from core_service import CoreService, load_safe_config, TerminalColor


class GibsFetcher(CoreService):
    """
    Service class for NASA GIBS ingest with automated date fallback logic.
    """

    def __init__(self, cfg_file: Path):
        super().__init__("GIBS_FETCHER")
        self.full_config = load_safe_config(str(cfg_file))
        if not self.full_config:
            raise RuntimeError(f"Failed to load config at {cfg_file}")

        self.gibs_cfg = self.full_config.get("gibs", {})
        self.instr_root = Path(self.gibs_cfg.get("instrument_root", "/tmp"))

        # Load the config
        self.full_config = load_safe_config(str(cfg_file))
        gibs_cfg = self.full_config.get("gibs", {})

        # Define the new log path
        log_base = Path(gibs_cfg.get("log_dir", "/tmp"))
        log_base.mkdir(parents=True, exist_ok=True)
        log_file = log_base / "satellite_health.log"

    def _attempt_download(self, url: str, save_path: Path, days_back: int) -> bool:
        """
        Internal helper to perform the stream and verify the content type.
        """
        success = self.stream_binary_resource(url, str(save_path))

        if success:
            # SANITY CHECK: Did we get a real JPEG or an XML Error?
            with open(save_path, 'rb') as f:
                header = f.read(5)
                if b"<?xml" in header or b"<Serv" in header:
                    self.logger.warning(
                        f"{self.clr.WARNING}⚠️  NASA Exception at T-{days_back}. Data not ready.{self.clr.ENDC}")
                    save_path.unlink()  # Delete the "fake" JPEG (XML file)
                    return False
            return True
        return False

    def fetch_all_targets(self):
        """
        Iterates through targets. If T-1 fails/XMLs, it attempts T-2.
        """
        targets = self.gibs_cfg.get("targets", [])
        if not targets:
            self.logger.warning("No targets found in config.")
            return

        self.logger.info(f"{self.clr.BOLD}📡 Starting GIBS Ingest Cycle (with T-2 Fallback){self.clr.ENDC}")

        for target in targets:
            name = target.get("name")
            base_url = target.get("url")
            subdir = target.get("subdir", "general")

            # Resolve Directory
            out_path = self.instr_root / subdir
            out_path.mkdir(parents=True, exist_ok=True)

            downloaded = False
            # Try T-1, then Fallback to T-2
            for days_back in [1, 2]:
                target_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
                filename = f"{name}_{target_date}.jpg"
                save_file = out_path / filename
                request_url = base_url.replace("{TIME}", target_date)

                self.logger.info(f"🔄 Attempting {name} for {target_date} (T-{days_back})")

                if self._attempt_download(request_url, save_file, days_back):
                    self.mqtt_publish(f"beulta/gibs/{name}/status", f"SUCCESS_T{days_back}")
                    downloaded = True
                    break  # Move to next target

            if not downloaded:
                self.logger.error(f"{self.clr.FAIL}❌ Failed to retrieve {name} after T-2 fallback.{self.clr.ENDC}")
                self.mqtt_publish(f"beulta/gibs/{name}/status", "CRITICAL_FAILURE")


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    config_path = current_dir.parent / "config.toml"

    try:
        fetcher = GibsFetcher(config_path)
        fetcher.fetch_all_targets()
        print(f"\n{TerminalColor.OKGREEN}🏁 Ingest Cycle Complete.{TerminalColor.ENDC}")
    except Exception as e:
        print(f"\n{TerminalColor.FAIL}💥 Fatal Execution Error: {e}{TerminalColor.ENDC}")
        sys.exit(1)
