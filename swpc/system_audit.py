#!/usr/bin/env python3
"""
🐕 NAME          : system_audit.py
👤 AUTHOR        : Reza (BeUlta) / Matha Goram
🔖 VERSION       : 1.4.0 (NAS-Aware)
📅 UPDATED       : 2026-02-10
📝 DESCRIPTION   : Watchdog for the BeUlta Suite. Monitors directory trees, 
                   storage health, daily video generation, and NAS mount status.
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
"""

import os
import time
import sys
import argparse
import shutil
import smtplib
from email.message import EmailMessage
from datetime import datetime

# --- ⚙️ CONFIGURATION ---
BASE_DIR = "/home/reza/Videos/satellite"
NAS_MOUNT_POINT = "/mnt/synology_backup"  # Path to verify
INSTRUMENTS = {
    "noaa": ["goes-east", "goes-west"],
    "swpc": ["aurora/north", "aurora/south", "solar_304", "lasco_c3"],
    "epic": ["global"],
    "terran": ["land_use", "ndvi_trends"]
}
STORAGE_THRESHOLD = 80

# --- 📧 SMTP CONFIGURATION ---
SMTP_SERVER = "localhost"
SMTP_PORT = 25
SENDER_EMAIL = "beulta-audit@yourdomain.lan"
RECEIVER_EMAIL = "reza@yourdomain.com"

def log_status(icon, level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"{timestamp} {icon} [{level}] {message}"
    print(formatted_msg)
    return formatted_msg

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
        print("📧 [MAIL] Email notification sent.")
    except Exception as e:
        print(f"❌ [MAIL] Failed to send email: {e}")

def audit_system(send_report=False):
    log_status("🚀", "START", "Initiating BeUlta Suite System Audit...")
    report_log = []
    errors_found = False

    # --- 📂 1. HIERARCHY & ARCHIVE AUDIT ---
    for project, subs in INSTRUMENTS.items():
        for sub in subs:
            path = os.path.join(BASE_DIR, project, sub)
            vid_dir = os.path.join(path, "videos")

            recent_video_found = False
            day_ago = time.time() - (24 * 3600)

            if os.path.exists(vid_dir):
                for f in os.listdir(vid_dir):
                    if f.endswith(".mp4") and os.path.getmtime(os.path.join(vid_dir, f)) > day_ago:
                        recent_video_found = True
                        break
            
            if recent_video_found:
                report_log.append(log_status("🎬", "PASS", f"Recent video verified for {sub}"))
            else:
                report_log.append(log_status("⚠️", "WARN", f"No new video in last 24h for {sub}"))
                errors_found = True

    # --- 🛰️ 2. NAS MOUNT AUDIT ---
    # Specifically verifies that the Synology shared folder is connected
    if os.path.ismount(NAS_MOUNT_POINT):
        report_log.append(log_status("🗄️", "PASS", f"NAS Backup Mount detected at {NAS_MOUNT_POINT}"))
    else:
        report_log.append(log_status("❌", "FAIL", f"NAS Backup Mount DISCONNECTED at {NAS_MOUNT_POINT}"))
        errors_found = True

    # --- 🚨 3. STORAGE HEALTH ---
    usage = shutil.disk_usage("/home")
    percent_used = (usage.used / usage.total) * 100
    storage_msg = log_status("💾", "HEALTH", f"Local storage usage: {percent_used:.1f}%")
    report_log.append(storage_msg)
    
    if percent_used > STORAGE_THRESHOLD:
        errors_found = True

    # --- 🏁 4. REPORTING LOGIC ---
    if errors_found:
        send_email("🚨 BeUlta Audit: CRITICAL/WARN Detected", "\n".join(report_log))
    elif send_report:
        send_email("✅ BeUlta Audit: Daily All Clear", "System Health: OK\n\n" + "\n".join(report_log))
    else:
        log_status("✅", "SILENT", "System healthy. No email required.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="Send email even if system is healthy")
    args = parser.parse_args()
    audit_system(send_report=args.report)

