#!/usr/bin/env python3
"""
===============================================================================
🛰️ MODULE        : retrieve_goes.py
👤 ROLE         : GOES-R Series Image Retriever
🔖 VERSION       : 2.5.1
📅 UPDATED       : 2026-03-14
===============================================================================

📝 DESCRIPTION:
    Retrieves high-resolution Full Disk and Sector imagery from GOES-East
    and GOES-West satellites via public AWS S3 or NOAA HTTPS endpoints.

⚙️ WORKFLOW / PROCESSING:
    1. Inherits environment from CoreService parent class.
    2. Parses 'goes_targets' for specific sectors and bands.
    3. Validates timestamp alignment for near real-time (NRT) imagery.
    4. Downloads binary data and verifies file integrity.

🛠️ PREREQUISITES:
    - Valid Project Root defined in /home/reza/PycharmProjects/noaa.
    - Python requests library.

⚠️ ERROR MESSAGES:
    - [CRITICAL] Dependency Resolution Error: Missing core_service module.
    - [WARNING] Target Unavailable: Specified GOES band not found for timestamp.

⚖️ LICENSE:
    MIT License | Copyright (c) 2026 ParkCircus Productions

📚 REFERENCES:
    - NOAA GOES-R Series: https://www.goes-r.gov/
===============================================================================
"""
import sys
from pathlib import Path

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
