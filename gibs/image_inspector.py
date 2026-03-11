#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : image_inspector.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.2.1
📅 LAST UPDATE  : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.1.0: Initial Integrity Checker (Basic JPEG header validation).
    - 1.2.0: Handshake 2.4.0 Migration. Implemented absolute path discovery
             to resolve [CRITICAL] utility import failures.
    - 1.2.1: Removed class inheritance to resolve CoreService import SNAFU.

📝 DESCRIPTION:
    Performs post-ingest integrity audits on satellite imagery.
    It ensures that the files saved by the fetcher are actual images and
    not NASA "Service Exception" XML files disguised as JPEGs.

🛠️ PREREQUISITES:
    - core_service.py in ~/PycharmProjects/noaa/utilities
    - Pillow (pip install Pillow)

[Workflow Pipeline Description]
1. Path Discovery: Locates the project root and utility folder dynamically.
2. Structural Audit: Validates JPEG magic bytes using the Pillow library.
3. Content Audit: Scans file headers for '<?xml' to catch NASA errors.
4. Reporting: Publishes corruption alerts via MQTT telemetry.
===============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from PIL import Image

# --- 🛠️ PRIORITY PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
util_path = project_root / "utilities"

if not (util_path / "core_service.py").exists():
    print(f"❌ [CRITICAL] Could not find core_service.py at: {util_path}")
    sys.exit(1)

if str(util_path) not in sys.path:
    sys.path.insert(0, str(util_path))

try:
    # Import functional helpers only - removed CoreService class inheritance
    from core_service import TerminalColor, init_mqtt
except ImportError as e:
    print(f"❌ [CRITICAL] Failed to load core_service components: {e}")
    sys.exit(1)


class ImageInspector:
    """
    Service class to audit JPEG integrity and detect NASA XML errors.
    Standardized for BeUlta Suite v2.4.0.
    """

    def __init__(self):
        self.clr = TerminalColor()
        # Direct path to satellite data root
        self.instr_root = Path("/home/reza/Videos/satellite/gibs")

        # Initialize logging for terminal visibility
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Initialize Telemetry (Optional Handshake)
        self.mqtt = init_mqtt()

    def is_valid_jpeg(self, file_path):
        """
        Performs a two-stage check:
        1. Checks for XML strings (NASA Service Exceptions).
        2. Verifies JPEG structure using Pillow.
        """
        try:
            # Check for XML "Leakage" (NASA errors saved as .jpg)
            with open(file_path, 'rb') as f:
                header = f.read(100)
                if b"<?xml" in header or b"<ServiceException" in header:
                    return False, "NASA Service Exception (XML body found)"

            # Structural validation
            with Image.open(file_path) as img:
                img.verify()
            return True, "Valid JPEG"
        except Exception as e:
            return False, f"Corruption detected: {str(e)}"

    def run_audit(self):
        """
        Recursively scans the instrument root for all JPEGs.
        """
        self.logger.info(f"{self.clr.BOLD}🔍 BeUlta Integrity Inspection Started{self.clr.ENDC}")

        if not self.instr_root.exists():
            self.logger.error(f"❌ Image root does not exist: {self.instr_root}")
            return

        image_files = list(self.instr_root.rglob("*.jpg"))

        if not image_files:
            self.logger.warning(f"⚠️ No images found in {self.instr_root}")
            return

        for img_path in image_files:
            valid, message = self.is_valid_jpeg(img_path)

            if valid:
                self.logger.info(f"✅ {img_path.name}: {message}")
            else:
                self.logger.error(f"{self.clr.FAIL}❌ {img_path.name}: {message}{self.clr.ENDC}")
                if self.mqtt:
                    self.mqtt.publish(f"beulta/health/corrupt_file", str(img_path.name))


if __name__ == "__main__":
    inspector = ImageInspector()
    inspector.run_audit()
