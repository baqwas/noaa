#!/usr/bin/env python3
"""
🐕 NAME          : system_audit.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 1.2.0
📅 UPDATED       : 2026-02-10
📝 DESCRIPTION   : Watchdog for the BeUlta Suite. Validates directory trees, 
                   detects orphans, monitors storage, and verifies daily 
                   video generation.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
"""

import os
import time
from datetime import datetime, timedelta
import shutil

# --- ⚙️ CONFIGURATION ---
BASE_DIR = "/home/reza/Videos/satellite"
# Map of instruments to verify (Project:Sub-Category)
INSTRUMENTS = {
    "noaa": ["goes-east", "goes-west"],
    "swpc": ["aurora/north", "aurora/south", "solar_304", "lasco_c3"],
    "epic": ["global"]
}
STORAGE_THRESHOLD = 80  # Alert if > 80% used

def log_status(icon, level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} {icon} [{level}] {message}")

def audit_system():
    log_status("🚀", "START", "Initiating BeUlta Suite System Audit...")
    errors_found = False

    # --- 📂 1. HIERARCHY & ARCHIVE AUDIT ---
    for project, subs in INSTRUMENTS.items():
        for sub in subs:
            path = os.path.join(BASE_DIR, project, sub)
            img_dir = os.path.join(path, "images")
            vid_dir = os.path.join(path, "videos")

            # Validate Directories exist
            if not os.path.exists(img_dir) or not os.path.exists(vid_dir):
                log_status("❌", "FAIL", f"Missing structure for {project}/{sub}")
                errors_found = True
                continue

            # Check for Daily Video Generation (New Logic)
            recent_video_found = False
            now = time.time()
            day_ago = now - (24 * 3600)

            for f in os.listdir(vid_dir):
                if f.endswith(".mp4"):
                    file_path = os.path.join(vid_dir, f)
                    if os.path.getmtime(file_path) > day_ago:
                        recent_video_found = True
                        break
            
            if recent_video_found:
                log_status("🎬", "PASS", f"Recent video verified for {sub}")
            else:
                log_status("⚠️", "WARN", f"No new video generated in last 24h for {sub}")
                errors_found = True

    # --- 🔍 2. ORPHAN DETECTION ---
    # Locates files in parent folders that should be in /images
    for project in INSTRUMENTS.keys():
        proj_root = os.path.join(BASE_DIR, project)
        for item in os.listdir(proj_root):
            if os.path.isfile(os.path.join(proj_root, item)) and item.lower().endswith(('.jpg', '.png', '.jpeg')):
                log_status("🔵", "ORPHAN", f"Found loose file: {project}/{item}")

    # --- 🚨 3. STORAGE HEALTH ---
    usage = shutil.disk_usage("/home")
    percent_used = (usage.used / usage.total) * 100
    if percent_used > STORAGE_THRESHOLD:
        log_status("🔴", "CRITICAL", f"Storage alert! /home partition at {percent_used:.1f}%")
        errors_found = True
    else:
        log_status("💾", "HEALTH", f"Storage usage within limits: {percent_used:.1f}%")

    if not errors_found:
        log_status("✅", "SUCCESS", "All systems operational.")
    else:
        log_status("🛠️", "ATTN", "Audit complete with warnings. Review logs.")

if __name__ == "__main__":
    audit_system()

