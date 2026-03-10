"""
================================================================================
🌱 MODULE        : terran_watch.py
🚀 DESCRIPTION   : NASA GIBS Ingest Engine - WMS GetMap Robust Ingest.
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 2.8.0
📅 UPDATED       : 2026-03-10
================================================================================

[Workflow Pipeline Description]
1. Runtime Sync: Validates .env via core_service.py and hydrates config.toml.
2. BBOX Scaling: Uses WMS GetMap to bypass restrictive WMTS tile grid math.
3. Temporal Search: Iterates back 4 days (T-3) to find the 'best' available granule.
4. Path Sharding: Stores images in structured subdirectories: {location}/{layer}/images/.
5. Audit Trail: Generates a status report of SUCCESS/FAILED for SMTP finalization.

[Unicode Icons Guide]
📡 : Hunting/Seeking Map          | 🟢 : Success [OK]
🟡 : Temporal Retry [RETRY]       | 🔴 : Failure [FAILED]
📧 : SMTP Report Dispatched       | 🏁 : Cycle Complete

[Prerequisites]
- core_service.py must be in PYTHONPATH for .env/config management.
- Valid write permissions for 'images_dir' defined in config.toml.
- Dnsmasq or stable local network for SMTP relay to BeZaman.

[Exception Handling]
- Global Try/Except: Catches all runtime failures, emails a full traceback via
  core_service.send_smtp_alert, and exits with status 1.

[Audit Trail]
Date       | Version | Author | Description
-----------|---------|--------|-----------------------------------------------
2026-03-09 | 1.8.2   | Matha  | Initial version with NASA 288-deg grid math.
2026-03-10 | 2.8.0   | Matha  | Pivot to WMS GetMap for BBOX reliability.
================================================================================
"""

import os
import sys
import requests
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# --- 🛠️ DYNAMIC PATH RESOLUTION ---
project_root = "/home/reza/PycharmProjects/noaa"
utilities_path = os.path.join(project_root, "utilities")
if utilities_path not in sys.path:
    sys.path.insert(0, utilities_path)

from core_service import get_config, send_smtp_alert, sync_env_to_config

# --- ANSI COLOR CODES ---
C_GREEN, C_YELLOW, C_RED, C_NC = "\033[0;32m", "\033[0;33m", "\033[0;31m", "\033[0m"

sync_env_to_config()
config = get_config()
start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
host_id = os.uname().nodename
status_report = []


def ingest_wms_map(loc_name, bbox, layer_key, date_str, dest_dir):
    """Downloads high-res imagery using WMS GetMap BBOX protocol."""
    # Format: BBOX is [lon_min, lat_min, lon_max, lat_max] in config
    # WMS 1.3.0 EPSG:4326 requires [lat_min, lon_min, lat_max, lon_max]
    wms_bbox = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"

    dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
    file_tag = dt_obj.strftime('%Y%j')
    full_path = dest_dir / f"{loc_name}_{layer_key}_{file_tag}.jpg"

    if full_path.exists():
        return "EXISTS"

    print(f"📡 Hunting {loc_name:.<12} | {layer_key:.<15} ({date_str}) ", end="", flush=True)

    # Use WMS best endpoint for high-fidelity daily granules
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
    params = {
        "SERVICE": "WMS",
        "REQUEST": "GetMap",
        "VERSION": "1.3.0",
        "LAYERS": layer_key,
        "STYLES": "",
        "FORMAT": "image/jpeg",
        "CRS": "EPSG:4326",
        "BBOX": wms_bbox,
        "WIDTH": "1024",  # Optimal for VLM resolution
        "HEIGHT": "1024",
        "TIME": date_str
    }

    try:
        resp = requests.get(base_url, params=params, timeout=20)
        if resp.status_code == 200:
            # Check if we got an image or a WMS Service Exception XML
            if b"ServiceException" in resp.content[:200]:
                return "RETRY"

            with open(full_path, 'wb') as f:
                f.write(resp.content)
            print(f"{C_GREEN}[OK]{C_NC}")
            return "SUCCESS"
        else:
            return "RETRY"
    except Exception:
        return "RETRY"


def main():
    try:
        terran_cfg = config.get('terran', {})
        # Fallback to absolute path if config is missing
        raw_storage = terran_cfg.get('images_dir', '/home/reza/Videos/satellite/terran/images')
        root_storage = Path(os.path.expanduser(raw_storage))

        # Core layers for VLM Analysis
        active_layers = [
            "MODIS_Terra_CorrectedReflectance_TrueColor",
            "MODIS_Aqua_CorrectedReflectance_TrueColor",
            "VIIRS_SNPP_CorrectedReflectance_TrueColor",
            "MODIS_Terra_NDVI_8Day"
        ]

        for loc in terran_cfg.get('locations', []):
            loc_name = loc.get('name')
            bbox = loc.get('bbox')

            for layer in active_layers:
                dest_dir = root_storage / loc_name / layer / "images"
                dest_dir.mkdir(parents=True, exist_ok=True)

                success = False
                # Temporal search window T-1 to T-4
                for i in range(1, 5):
                    req_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    result = ingest_wms_map(loc_name, bbox, layer, req_date, dest_dir)

                    if result in ["SUCCESS", "EXISTS"]:
                        if result == "SUCCESS":
                            status_report.append(f"SUCCESS: {loc_name} | {layer} | {req_date}")
                        success = True
                        break

                if not success:
                    print(f"{C_RED}[FAILED]{C_NC}")
                    status_report.append(f"FAILED:  {loc_name} | {layer}")

        # --- 📧 SMTP FINALIZATION ---
        summary_body = "\n".join(status_report)
        full_email_body = f"""
SYSTEM REPORT: Terran Watch Ingest Cycle
------------------------------------------
TIMESTAMP    : {start_time}
NODE         : {host_id} (BeUlta Suite)
METHOD       : WMS GetMap BBOX Pivot (v2.8.0)

INGEST SUMMARY:
{summary_body}

--
Automated Report from BeUlta Satellite Suite
(c) 2026 ParkCircus Productions
"""
        send_smtp_alert(subject="[INFO] Terran Cycle Complete", body=full_email_body)
        print(
            f"\n{C_YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - TerranEngine - INFO - 📧 SMTP Alert Dispatched.{C_NC}")

    except Exception:
        err_msg = traceback.format_exc()
        send_smtp_alert(subject="[ALRT] Terran Engine Failure", body=err_msg)
        print(f"\n{C_RED}❌ CRITICAL: Failure.{C_NC}\n{err_msg}")
        sys.exit(1)

    print(f"\n{C_GREEN}✅ [SUCCESS] Terran update completed.{C_NC}")


if __name__ == "__main__":
    main()
