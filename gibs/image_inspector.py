#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : image_inspector.py
👤 AUTHOR       : Matha Goram
🔖 VERSION      : 1.1.0
📅 LAST UPDATE  : 2026-03-07
⚖️ COPYRIGHT    : (c) 2026 ParkCircus Productions
📜 LICENSE      : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.0.0: Initial Integrity Checker (Basic JPEG header validation).
    - 1.1.0: Refactored to inherit CoreService; integrated central logging.

📝 DESCRIPTION:
    Performs post-ingest integrity audits on satellite imagery.
    Detects truncated downloads or NASA-side Service Exceptions by
    validating JPEG magic bytes and checking for XML error strings.

🛠️ PREREQUISITES:
    - core_service.py in ~/noaa/utilities
    - Pillow (pip install Pillow)
===============================================================================
"""

import os
import sys
from pathlib import Path
from PIL import Image

# --- 🛠️ PRIORITY PATH INJECTION ---
util_path = os.path.expanduser("~/PycharmProjects/noaa/utilities")
if util_path not in sys.path:
    sys.path.insert(0, util_path)

try:
    from core_service import CoreService, TerminalColor
except ImportError:
    print(f"❌ [CRITICAL] Could not find core_service.py in: {util_path}")
    sys.exit(1)


class ImageInspector(CoreService):
    """
    Service class for auditing the integrity of downloaded GIBS imagery.
    """

    def __init__(self):
        # Initialize CoreService which sets up logging to satellite_health.log
        super().__init__("IMAGE_INSPECTOR")
        gibs_cfg = self.config.get("gibs", {})
        self.instr_root = Path(gibs_cfg.get("instrument_root", "/tmp"))

    def is_valid_jpeg(self, file_path: Path) -> tuple[bool, str]:
        """
        Validates that a file is a real JPEG and not a NASA XML error.
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(100)
                # Check for XML/Service Exception
                if b"<?xml" in header or b"ServiceException" in header:
                    return False, "NASA Service Exception (XML body found)"

            # Use Pillow for structural validation
            with Image.open(file_path) as img:
                img.verify()
            return True, "Valid JPEG"
        except Exception as e:
            return False, f"Corruption detected: {str(e)}"

    def run_audit(self):
        """
        Recursively scans the instrument root for today's and yesterday's files.
        """
        self.logger.info(f"{self.clr.BOLD}🔍 BeUlta Integrity Inspection Started{self.clr.ENDC}")

        # Scan all subdirectories in the instrument root
        image_files = list(self.instr_root.rglob("*.jpg"))

        if not image_files:
            self.logger.warning("No images found to inspect.")
            return

        for img_path in image_files:
            valid, message = self.is_valid_jpeg(img_path)

            if valid:
                self.logger.info(f"✅ {img_path.name}: {message}")
            else:
                self.logger.error(f"{self.clr.FAIL}❌ {img_path.name}: {message}{self.clr.ENDC}")
                self.mqtt_publish(f"beulta/health/corrupt_file", str(img_path.name))

                # OPTIONAL: Move corrupt file to a quarantine folder
                # quarantine = self.instr_root / "quarantine"
                # quarantine.mkdir(exist_ok=True)
                # img_path.rename(quarantine / img_path.name)


if __name__ == "__main__":
    inspector = ImageInspector()
    inspector.run_audit()
