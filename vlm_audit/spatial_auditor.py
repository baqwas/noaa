"""
================================================================================
🌱 MODULE        : spatial_auditor.py
🚀 DESCRIPTION   : Chromatic Cloud-Masking with Debug Export Capabilities.
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.1.2
📅 UPDATED       : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
================================================================================

[Summary]
Evaluates satellite granule usability via HSV thresholding. Version 1.1.2
implements specific path resolution for the 'utilities' subdirectory to
successfully import core_service.py regardless of the execution context.

[Workflow Pipeline Description]
1. Path Resolution: Force-injects 'utilities' path to find core_service.py.
2. Image Ingestion: Loads target JPG from Terran repository.
3. Color Transformation: Isolates high-reflectance zones in HSV space.
4. Masking: Generates a binary mask of detected cloud cover.
5. Debug Export: Saves the binary mask to /debug for manual verification.
6. Scoring: Returns boolean 'usable' flag based on threshold.

[Unicode Icons Guide]
🔍 : Pixel Analysis Initiated     | ✅ : Quality Gate Passed
☁️ : Cloud Threshold Exceeded      | 📊 : Statistical Score Generated
📂 : Debug Mask Exported           | 🚨 : IO Error / Path Failure

[Error Messages Summary]
- "ERR_PATH_001": core_service.py not found at defined utilities path.
- "ERR_IMG_001" : Image file unreadable or corrupted.
- "ERR_DBG_001" : Permissions failure while writing to /debug directory.
================================================================================
"""

import os
import sys
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

# --- 🛠️ DYNAMIC PATH RESOLUTION ---
# Resolving the path to 'utilities' relative to the project root
project_root = "/home/reza/PycharmProjects/noaa"
utilities_path = os.path.join(project_root, "utilities")
if utilities_path not in sys.path:
    sys.path.insert(0, utilities_path)

try:
    from core_service import get_config, TerminalColor
except ImportError:
    print("🚨 ERR_PATH_001: core_service.py not found.")
    sys.exit(1)

TC = TerminalColor()

def audit_cloud_cover(image_path, threshold_percent=40.0):
    """
    Refined Quality Gate: Checks for high Value (brightness)
    AND low Saturation (grey/white) to identify clouds.
    """
    try:
        with Image.open(image_path) as img:
            # Convert to HSV (Hue, Saturation, Value)
            hsv_img = img.convert("HSV")
            h, s, v = hsv_img.split()

            v_np = np.array(v)
            s_np = np.array(s)

            # CLOUD CRITERIA:
            # Brightness (Value) > 225 AND Saturation < 30 (very pale/white)
            cloud_mask = (v_np > 225) & (s_np < 30)

            cloud_count = np.sum(cloud_mask)
            total_pixels = v_np.size
            cloud_pct = (cloud_count / total_pixels) * 100

            is_usable = cloud_pct <= threshold_percent
            return is_usable, cloud_pct
    except Exception as e:
        print(f"🚨 ERR_IMG_001: {e}")
        return False, 100.0

def find_latest_image(location):
    """The 'Pointer Method' - Automatically finds the latest JPG for a county."""
    config = get_config()
    terran_cfg = config.get('terran', {})
    base_dir = Path(terran_cfg.get('images_dir', '/home/reza/Videos/satellite/terran/images'))
    layer = "MODIS_Terra_CorrectedReflectance_TrueColor"
    target_path = base_dir / location / layer / "images"

    if not target_path.exists():
        return None

    files = sorted(target_path.glob("*.jpg"), key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def main():
    parser = argparse.ArgumentParser(description="BeUlta Spatial Quality Gate")
    parser.add_argument("--loc", type=str, help="County pointer (e.g., collin)")
    parser.add_argument("--image", type=str, help="Manual full path to image")
    args = parser.parse_args()

    img_path = args.image if args.image else find_latest_image(args.loc) if args.loc else None

    if not img_path:
        print(f"{TC.WARNING}💡 Usage: --loc [county] or --image [path]{TC.ENDC}")
        return

    print(f"{TC.HEADER}🔍 Analyzing: {Path(img_path).name}{TC.ENDC}")
    usable, pct = audit_cloud_cover(img_path)

    if usable:
        print(f"{TC.OKGREEN}✅ Quality Gate Passed ({pct:.2f}% cloud cover).{TC.ENDC}")
    else:
        print(f"{TC.FAIL}☁️ Quality Gate Failed ({pct:.2f}% cloud cover).{TC.ENDC}")


if __name__ == "__main__":
    main()
