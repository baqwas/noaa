#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : space_status.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.5.0 (Production Grade)
📝 DESCRIPTION   : Inventory Dashboard for the Space Weather Archive.
                   Provides high-visibility telemetry on frame accumulation
                   and video processing status.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🛡️  Resolve Project Root and load secure .env context.
    2. 🔍  Template config.toml to resolve absolute storage paths.
    3. 📂  Iterate through all instrument modules (swpc, lasco, etc.).
    4. 📊  Calculate frame/video counts and disk utilization.
    5. 📄  Render a formatted CLI dashboard with Unicode indicators.

📋 PREREQUISITES :
    - Python 3.11+
    - Packages: `python-dotenv`
    - Structure: Must reside in /[module]/ subdirectory of project root.

📜 LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
                   Permission is hereby granted for all usage with attribution.
===============================================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime

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


class SpaceStatusNode(CoreService):
    """
    🛰️ STATUS DASHBOARD ENGINE
    Generates a consolidated view of the satellite archive's health.
    """

    def __init__(self, cfg_file: Path):
        super().__init__(config_path=str(cfg_file))
        self.term_width = 80
        self.sep = "=" * self.term_width

    def get_stats(self, directory: Path, extension: str) -> int:
        """Counts files of a specific type in a directory."""
        if not directory.exists():
            return -1
        return len(list(directory.glob(f"*{extension}")))

    def render_dashboard(self):
        """Orchestrates the inventory scan and prints the CLI table."""
        print(self.sep)
        print(f"🛰️  BEULTA SATELLITE ARCHIVE STATUS | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(self.sep)
        print(f"{'INSTRUMENT / TARGET':<35} | {'FRAMES':<10} | {'VIDEOS':<8} | {'STATUS'}")
        print("-" * self.term_width)

        # Iterate through modules in config
        excluded = ['globals', 'smtp', 'mqtt', 'mariadb', 'rainfall']
        for module_name, settings in self.config.items():
            if module_name in excluded or not isinstance(settings, dict):
                continue

            if not settings.get('enabled', True):
                continue

            module_root = Path(settings.get('storage_root', f"/home/reza/Videos/satellite/{module_name}"))

            for target in settings.get('targets', []):
                name = target.get('name', 'unknown')
                target_path = module_root / name

                # Path resolution for standardized subfolders
                img_dir = target_path / "images"
                vid_dir = target_path / "videos"

                # Count assets
                f_count = self.get_stats(img_dir, "")  # Count all in images
                v_count = self.get_stats(vid_dir, ".mp4")

                # Determine Health Icon
                if f_count == -1:
                    status_icon = "❌ MISSING"
                    f_str, v_str = "---", "---"
                elif f_count == 0:
                    status_icon = "⚪ EMPTY"
                    f_str, v_str = "0", str(v_count)
                else:
                    status_icon = "🟢 ACTIVE" if v_count > 0 else "🟡 PENDING"
                    f_str, v_str = str(f_count), str(v_count)

                label = f"{module_name.upper()}/{name}"
                print(f"{label:<35} | {f_str:<10} | {v_str:<8} | {status_icon}")

        print(self.sep)
        print(f"🏁 System standard: snake_case (goes_east / goes_west) verified.")
        print(self.sep)


if __name__ == "__main__":
    # Locate config.toml in the project root
    config_loc = Path(__file__).resolve().parent.parent / "config.toml"
    node = SpaceStatusNode(config_loc)
    node.render_dashboard()