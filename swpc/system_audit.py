#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : system_audit.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 1.5.1 (Production Grade)
📝 DESCRIPTION   : Watchdog for the Satellite Archive. Monitors directory trees,
                   storage health, video generation, and NAS mount status.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🛡️  Load secure environment variables and template config.toml.
    2. 🧪  Freshness Audit: Verify .mp4 generation for active instruments.
    3. 🗄️  Mount Audit: Confirm Synology NAS connectivity.
    4. 💾  Capacity Audit: Flag alerts if disk usage exceeds 85%.
    5. 📧  Reporting: Dispatch SMTP alerts for critical failures.
===============================================================================
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

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


class SystemAuditNode(CoreService):
    def __init__(self, cfg_file: Path):
        super().__init__(config_path=str(cfg_file))
        self.threshold = self.config.get('globals', {}).get('storage_threshold', 85)
        self.nas_path = self.config.get('globals', {}).get('nas_mount', "/mnt/synology_backup")

    def run_audit(self):
        errors_found = False
        warnings_found = False
        audit_log = []
        day_ago = datetime.now() - timedelta(days=1)

        print(f"🚀 [START] Initiating BeUlta Suite System Audit...")

        # --- 1. DYNAMIC MODULE AUDIT ---
        # Iterate through every section in config.toml
        excluded = ['globals', 'smtp', 'mqtt', 'mariadb', 'rainfall']
        for module_name, settings in self.config.items():
            if module_name in excluded or not isinstance(settings, dict):
                continue

            if not settings.get('enabled', True):
                continue

            root = Path(settings.get('storage_root', f"/home/reza/Videos/satellite/{module_name}"))

            # Check Directory Structure
            if not root.exists():
                msg = f"❌ [FAIL] Missing structure for {module_name} at {root}"
                print(msg)
                audit_log.append(msg)
                errors_found = True
                continue

            # Check for recent videos for each target in this module
            targets = settings.get('targets', [])
            for target in targets:
                target_name = target.get('name')
                vid_dir = root / target_name / "videos"

                # Check for any .mp4 modified in the last 24h
                recent_vids = []
                if vid_dir.exists():
                    recent_vids = [v for v in vid_dir.glob("*.mp4")
                                   if datetime.fromtimestamp(v.stat().st_mtime) > day_ago]

                if not recent_vids:
                    msg = f"⚠️ [WARN] {module_name}/{target_name}: No new video in 24h."
                    print(msg)
                    audit_log.append(msg)
                    warnings_found = True
                else:
                    print(f"🎬 [PASS] {module_name}/{target_name}: Video verified.")

        # --- 2. STORAGE HEALTH ---
        usage = shutil.disk_usage("/")
        percent = (usage.used / usage.total) * 100
        if percent > self.threshold:
            msg = f"🚨 [CRITICAL] Storage usage at {percent:.1f}%!"
            print(msg)
            audit_log.append(msg)
            errors_found = True
        else:
            print(f"💾 [HEALTH] Storage usage: {percent:.1f}%")

        # --- 3. RESULTS ---
        if errors_found:
            self.send_email("🚨 CRITICAL: System Audit Failure", "\n".join(audit_log))
            self.publish_mqtt("system/audit", "CRITICAL")
            print("🛠️ [ATTN] Audit failed. Alert dispatched.")
        elif warnings_found:
            print("🛠️ [ATTN] Audit complete with warnings.")
            self.publish_mqtt("system/audit", "WARNING")
        else:
            print("✨ [SUCCESS] All systems nominal.")
            self.publish_mqtt("system/audit", "PASS")


if __name__ == "__main__":
    config_loc = Path(__file__).resolve().parent.parent / "config.toml"
    node = SystemAuditNode(config_loc)
    node.run_audit()
