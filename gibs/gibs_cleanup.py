#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gibs_cleanup.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.0.0
📅 LAST UPDATE  : 2026-03-11
===============================================================================
📑 DESCRIPTION:
    Prunes old satellite imagery to prevent disk exhaustion.
    Scans for .jpg and .png files older than X days.
===============================================================================
"""

import os
import sys
import time
import logging
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
project_root = "/home/reza/PycharmProjects/noaa"
util_path = os.path.join(project_root, "utilities")
if util_path not in sys.path:
    sys.path.insert(0, util_path)

try:
    from core_service import get_config, TerminalColor
except ImportError:
    print(f"❌ [CRITICAL] Could not find core_service.py")
    sys.exit(1)

# --- ⚙️ SETTINGS ---
DRY_RUN = False  # Set to True to see what would be deleted without doing it.
RETENTION_DAYS = 30


def run_cleanup():
    config = get_config()
    clr = TerminalColor()
    gibs_cfg = config.get('gibs', {})
    target_root = Path(gibs_cfg.get('images_dir', '/tmp/satellite'))

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger("BeUlta.Cleanup")

    if not target_root.exists():
        logger.error(f"❌ Target directory {target_root} does not exist.")
        return

    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)

    count = 0
    freed_space = 0

    logger.info(f"🧹 Starting cleanup in {target_root} (Retention: {RETENTION_DAYS} days)")
    if DRY_RUN:
        logger.info("🧪 [DRY RUN MODE] No files will be harmed.")

    # Walk through layer subdirectories
    for file_path in target_root.rglob("*"):
        # Only target imagery and old dashboards
        if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.png', '.mp4']:
            file_mod_time = file_path.stat().st_mtime

            if file_mod_time < cutoff:
                file_size = file_path.stat().st_size
                count += 1
                freed_space += file_size

                if DRY_RUN:
                    logger.info(f"🔍 Would delete: {file_path.name} ({file_size / 1024:.1f} KB)")
                else:
                    try:
                        file_path.unlink()
                        logger.info(f"🗑️ Deleted: {file_path.name}")
                    except Exception as e:
                        logger.error(f"❌ Failed to delete {file_path.name}: {e}")

    # Summary
    status_clr = clr.OKBLUE if DRY_RUN else clr.OKGREEN
    logger.info("-" * 40)
    logger.info(f"{status_clr}✅ Cleanup Complete.{clr.ENDC}")
    logger.info(f"📦 Files processed: {count}")
    logger.info(f"💾 Space {'potentially ' if DRY_RUN else ''}freed: {freed_space / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    run_cleanup()
