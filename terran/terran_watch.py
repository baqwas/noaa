"""
================================================================================
🌱 MODULE        : terran_watch.py
🚀 DESCRIPTION   : NASA GIBS Ingest Engine - WMS GetMap Robust Ingest.
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 2.9.0
📅 UPDATED       : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
================================================================================

[Workflow Pipeline Description]
1. Runtime Sync: Validates .env via core_service.py and hydrates config.toml.
2. Parameter Parsing: Accepts --lookback to shift the temporal search window.
3. BBOX Scaling: Uses WMS GetMap to bypass restrictive WMTS tile grid math.
4. Temporal Search: Iterates back 4 days from the lookback offset to find
   the 'best' available granule.
5. Path Sharding: Stores images in structured subdirectories.
6. Audit Trail: Generates a status report for SMTP finalization.

[Unicode Icons Guide]
📡 : Hunting/Seeking Map          | 🟢 : Success [OK]
🟡 : Temporal Retry [RETRY]       | 🔴 : Failure [FAILED]
📧 : SMTP Report Dispatched       | 🏁 : Cycle Complete

[Prerequisites]
- core_service.py must be in PYTHONPATH (typically in ../utilities).
- Valid write permissions for 'images_dir' defined in config.toml.

[Audit Trail]
Date       | Version | Author | Description
-----------|---------|--------|-----------------------------------------------
2026-03-09 | 2.8.0   | Matha  | Initial WMS GetMap pivot.
2026-03-10 | 2.9.0   | Matha  | Added argparse for --lookback temporal offset.
================================================================================
"""

import os
import sys
import argparse
import requests
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# --- 🛠️ DYNAMIC PATH RESOLUTION ---
project_root = "/home/reza/PycharmProjects/noaa"
utilities_path = os.path.join(project_root, "utilities")
if utilities_path not in sys.path:
    sys.path.insert(0, utilities_path)

try:
    from core_service import config, send_smtp_alert, TerminalColor
except ImportError:
    print("🚨 ERR_PATH_001: core_service.py not found in utilities.")
    sys.exit(1)

# Initialize Aesthetic Pointer
TC = TerminalColor()

# ANSI fallback for internal strings if TerminalColor fails
C_YELLOW = TC.WARNING
C_RED = TC.FAIL
C_GREEN = TC.OKGREEN
C_NC = TC.ENDC


def ingest_wms_map(loc_name, bbox, layer, date_str, dest_dir):
    """Fetches a high-res 1024x1024 image via WMS GetMap protocol."""
    filename = f"{loc_name}_{layer}_{date_str.replace('-', '')}.jpg"
    filepath = dest_dir / filename

    if filepath.exists():
        return "EXISTS"

    # NASA GIBS WMS Endpoint
    base_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "LAYERS": layer,
        "FORMAT": "image/jpeg",
        "TRANSPARENT": "false",
        "STYLES": "",
        "CRS": "EPSG:4326",
        "BBOX": f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}",  # Lat/Lon order for WMS 1.3.0
        "WIDTH": "1024",
        "HEIGHT": "1024",
        "TIME": date_str
    }

    print(f"{TC.OKCYAN}📡 Seeking {loc_name} | {date_str}...{TC.ENDC}", end=" ", flush=True)

    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"{C_GREEN}🟢 [OK]{C_NC}")
            return "SUCCESS"
        else:
            print(f"{C_YELLOW}🟡 [RETRY]{C_NC}")
            return "RETRY"
    except Exception as e:
        print(f"{C_RED}🔴 [ERROR: {e}]{C_NC}")
        return "ERROR"


def main():
    # --- 🔍 CLI PARAMETER PARSING ---
    parser = argparse.ArgumentParser(description="Terran Watch Ingest Engine")
    parser.add_argument("--config", type=str, help="Path to config.toml")
    parser.add_argument("--lookback", type=int, default=0,
                        help="Days to shift the search window (e.g., 2 for T-2)")
    args = parser.parse_args()

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    host_id = os.uname()[1]
    status_report = []

    try:
        terran_cfg = config.get('terran', {})
        raw_storage = terran_cfg.get('images_dir', '/home/reza/Videos/satellite/terran/images')
        root_storage = Path(os.path.expanduser(raw_storage))

        active_layers = [
            "MODIS_Terra_CorrectedReflectance_TrueColor",
            "MODIS_Aqua_CorrectedReflectance_TrueColor",
            "VIIRS_SNPP_CorrectedReflectance_TrueColor"
        ]

        # base_offset shifts the 4-day search window
        base_offset = args.lookback

        for loc in terran_cfg.get('locations', []):
            loc_name = loc.get('name')
            bbox = loc.get('bbox')

            for layer in active_layers:
                dest_dir = root_storage / loc_name / layer / "images"
                dest_dir.mkdir(parents=True, exist_ok=True)

                success = False
                # Search window: 4 days starting from the offset
                for i in range(1 + base_offset, 5 + base_offset):
                    req_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    result = ingest_wms_map(loc_name, bbox, layer, req_date, dest_dir)

                    if result in ["SUCCESS", "EXISTS"]:
                        if result == "SUCCESS":
                            status_report.append(f"✅ SUCCESS: {loc_name} | {layer} | {req_date}")
                        success = True
                        break

                if not success:
                    status_report.append(f"❌ FAILED:  {loc_name} | {layer}")

        # --- 📧 SMTP FINALIZATION ---
        summary_body = "\n".join(status_report)
        full_email_body = f"""
SYSTEM REPORT: Terran Watch Ingest Cycle
------------------------------------------
TIMESTAMP    : {start_time}
NODE         : {host_id} (BeUlta Suite)
LOOKBACK     : {args.lookback} days
METHOD       : WMS GetMap BBOX Pivot (v2.9.0)

INGEST SUMMARY:
{summary_body}

--
Automated Report from BeUlta Satellite Suite
(c) 2026 ParkCircus Productions
"""
        send_smtp_alert(subject="[INFO] Terran Cycle Complete", body=full_email_body)
        print(f"\n{C_YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 🏁 Cycle Complete. Alert Dispatched.{C_NC}")

    except Exception:
        err_msg = traceback.format_exc()
        send_smtp_alert(subject="[ALERT] Terran Engine Failure", body=err_msg)
        print(f"{C_RED}❌ CRITICAL FAILURE: Check Logs/Email.{C_NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
