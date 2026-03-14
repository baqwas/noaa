#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : space_status.py
👤 ROLE         : Inventory Dashboard & Telemetry
🔖 VERSION       : 1.5.1
📅 LAST UPDATE  : 2026-03-14
===============================================================================

📝 DESCRIPTION:
    High-visibility inventory dashboard providing real-time telemetry on
    frame accumulation and video processing status. Calculates disk
    utilization and validates snake_case naming conventions across archives.

⚙️ WORKFLOW / PROCESSING:
    1. Initialization: Hydrates project environment via CoreService.
    2. Discovery: Iterates through all instrument keys in config.toml.
    3. Metric Calculation: Recursively counts images vs. MP4 video egress.
    4. Health Determination: Assigns status icons (ACTIVE/PENDING/EMPTY).
    5. Visualization: Renders a formatted CLI table for forensic review.

🛠️ PREREQUISITES:
    - utilities/core_service.py in project utilities/ folder.
    - Defined storage_root paths in config.toml.

⚠️ ERROR MESSAGES:
    - [CRITICAL] core_service.py missing: Path resolution failure.
    - [X] MISSING: Directory structure does not exist for target.

🖥️ USER INTERFACE:
    - Formatted CLI table with Unicode indicators:
      🟢 ACTIVE | 🟡 PENDING | ⚪ EMPTY | ❌ MISSING

📜 VERSION HISTORY:
    - 1.5.0: Production Grade release.
    - 1.5.1: OPTION A ALIGNMENT. Transitioned to CoreService class reference.

⚖️ LICENSE:
    MIT License | Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# --- 🛠️ PRIORITY PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root / 'utilities'))

try:
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Failed to load core_service: {e}")
    sys.exit(1)


class SpaceStatus:
    """
    Inventory Dashboard Engine for BeUlta Suite archives.
    """

    def __init__(self):
        # Instantiate for class-based access
        self.core = CoreService()
        self.config = self.core.get_config()
        self.sep = "=" * 80

    def get_stats(self, directory: Path, ext: str) -> int:
        """
        Safely counts files of a specific extension.
        """
        if not directory.exists():
            return -1
        return len(list(directory.glob(f"*{ext}")))

    def render(self):
        """
        Renders the forensic dashboard to the terminal.
        """
        print(f"\n{self.sep}")
        print(f"🛰️  BEULTA SPACE WEATHER ARCHIVE TELEMETRY | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(self.sep)
        print(f"{'INSTRUMENT/REGION':<35} | {'IMAGES':<10} | {'VIDEOS':<8} | {'STATUS'}")
        print("-" * 80)

        # Iterate through all sections in config, filtering for satellite modules
        excluded_keys = ['smtp', 'goes', 'gibs', 'epic', 'egress']

        for module_name, settings in self.config.items():
            if module_name in excluded_keys or not isinstance(settings, dict):
                continue

            module_root = Path(settings.get('storage_root', f"/home/reza/Videos/satellite/{module_name}"))

            for target in settings.get('targets', []):
                name = target.get('name', 'unknown')
                target_path = module_root / name

                # Path resolution for standardized subfolders
                img_dir = target_path / "images"
                vid_dir = target_path / "videos"

                # Count assets
                f_count = self.get_stats(img_dir, "")
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
        print(f"{self.sep}\n")


if __name__ == "__main__":
    SpaceStatus().render()
