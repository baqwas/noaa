#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : universal_watchdog.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 3.4.0
📝 DESCRIPTION   : Dynamically audits satellite imagery directories for cleanup.
                   Ensures post-render success across the entire storage tree.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🛡️  Initialize secure context via advanced load_secure_config().
    2. 🔍  Recursively discover all 'images' directories in the satellite root.
    3. 📊  Audit file counts and compare against MAX_IMAGE_THRESHOLD.
    4. 🔐  Secure SMTP transaction (STARTTLS + Expired LAN Cert Bypass).
    5. 📧  Dispatch status report to reza@parkcircus.org.

📋 PREREQUISITES :
    - Python 3.11+
    - Packages: `python-dotenv`, `tomllib`

📜 LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

import os
import sys
import smtplib
import tomllib
import logging
import ssl
import shutil
import csv
from datetime import datetime, timedelta
from pathlib import Path
from email.message import EmailMessage
from string import Template
from typing import Any
from dotenv import load_dotenv

# --- ANSI UI CONSTANTS ---
G, B, Y, R, C, NC = '\033[92m', '\033[94m', '\033[93m', '\033[91m', '\033[96m', '\033[0m'

# --- DYNAMIC PATH RESOLUTION ---
SCRIPT_DIR = Path(__file__).parent
PROJ_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJ_ROOT / "config.toml"
ENV_PATH = PROJ_ROOT / ".env"

# --- CONFIGURE LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Watchdog")


def load_secure_config(path: Path) -> dict[str, Any]:
    """Advanced TOML loader with ENV substitution and placeholder safety."""
    load_dotenv(dotenv_path=ENV_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    with open(path, "r") as f:
        content = Template(f.read()).safe_substitute(os.environ)
        return tomllib.loads(content)


class StorageWatchdog:
    def __init__(self, config_path: Path):
        self.report_lines = []
        self.stats = {"scanned": 0, "passed": 0, "failed": 0}
        self.top_consumer = {"path": "None", "count": 0}
        self.forecast_msg = "Calculating... (Need 2+ days of data)"

        try:
            self.config = load_secure_config(config_path)
            self.smtp_cfg = self.config.get('smtp', {})
        except Exception as e:
            logger.error(f"💀 {R}[CONFIG ERROR]{NC} {e}")
            sys.exit(1)

        self.sat_root = Path("/home/reza/Videos/satellite")
        self.history_log = self.sat_root / "logs" / "storage_trends.csv"
        self.threshold = 500

    def run_audit(self):
        """Discovers imagery folders and audits file counts."""
        logger.info(f"{B}🛡️  Starting Universal Storage Audit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}")
        print("-" * 75)

        if not self.sat_root.exists():
            logger.error(f"{R}💀 CRITICAL: Storage root missing!{NC}")
            return

        image_dirs = list(self.sat_root.rglob("images"))
        self.stats["scanned"] = len(image_dirs)

        for img_dir in image_dirs:
            img_count = len([f for f in img_dir.iterdir() if f.is_file()])
            rel_path = img_dir.relative_to(self.sat_root)

            if img_count > self.top_consumer["count"]:
                self.top_consumer = {"path": str(rel_path), "count": img_count}

            if img_count > self.threshold:
                self.stats["failed"] += 1
                msg = f"🚨 FAIL: {rel_path} - Found {img_count} files"
                self.report_lines.append(msg)
            else:
                self.stats["passed"] += 1

        # Perform logic sequence
        self.log_historical_stats()
        self.calculate_forecast()
        self.send_report()

    def log_historical_stats(self):
        """Appends top consumer and current free space to CSV."""
        try:
            self.history_log.parent.mkdir(parents=True, exist_ok=True)
            write_header = not self.history_log.exists()

            disk_info = shutil.disk_usage(self.sat_root)
            free_gb = disk_info.free / (2 ** 30)

            with open(self.history_log, "a", newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["Timestamp", "Module", "Files", "Free_GB"])
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.top_consumer["path"],
                    self.top_consumer["count"],
                    round(free_gb, 2)
                ])
            logger.info(f"{G}📈 Storage trends logged successfully.{NC}")
        except Exception as e:
            logger.error(f"⚠️ {Y}Logging failed:{NC} {e}")

    def calculate_forecast(self):
        """Analyzes the last 7 entries in the CSV to predict depletion."""
        try:
            if not self.history_log.exists(): return

            with open(self.history_log, "r") as f:
                data = list(csv.DictReader(f))

            if len(data) < 2:
                self.forecast_msg = "Insufficient data (Collecting daily samples)"
                return

            # Analyze last 7 samples (roughly 1 week)
            samples = data[-7:]
            first = samples[0]
            last = samples[-1]

            # Calculate delta
            days_delta = (datetime.strptime(last['Timestamp'], '%Y-%m-%d %H:%M:%S') -
                          datetime.strptime(first['Timestamp'], '%Y-%m-%d %H:%M:%S')).days

            if days_delta <= 0: days_delta = 1  # Avoid division by zero

            space_lost = float(first['Free_GB']) - float(last['Free_GB'])
            burn_rate = space_lost / days_delta  # GB per day

            if burn_rate <= 0:
                self.forecast_msg = "Stable (Usage not increasing)"
            else:
                days_left = float(last['Free_GB']) / burn_rate
                date_full = (datetime.now() + timedelta(days=days_left)).strftime('%Y-%m-%d')
                self.forecast_msg = f"{round(days_left)} Days (~{date_full}) @ {round(burn_rate, 2)} GB/day"

        except Exception as e:
            self.forecast_msg = "Forecast unavailable (Data Parse Error)"
            logger.debug(f"Forecast Error: {e}")

    def generate_signature(self):
        """Creates a substantive signature with the storage forecast."""
        disk_info = shutil.disk_usage(self.sat_root)
        free_gb = disk_info.free // (2 ** 30)

        sig = [
            "\n" + "=" * 50,
            "📊 STORAGE WATCHDOG EXECUTION SUMMARY",
            "=" * 50,
            f"📅 Timestamp      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"🔍 Modules Scanned: {self.stats['scanned']}",
            f"✅ Successes       : {self.stats['passed']}",
            f"🚨 Failures        : {self.stats['failed']}",
            f"🔝 Top Consumer   : {self.top_consumer['path']} ({self.top_consumer['count']} files)",
            f"💾 Current Space  : {free_gb} GB free",
            f"🔮 Storage Forecast: {self.forecast_msg}",
            "-" * 50,
            "🛡️  Automated by BeUlta Suite Watchdog Engine v3.4.0",
            "📧 Systems Admin: durwan@parkcircus.org",
            "=" * 50
        ]
        return "\n".join(sig)

    def send_report(self):
        """Robust SMTP logic with confirmation Heartbeat."""
        try:
            body = "✅ CLEANUP VERIFIED: All imagery directories passed.\n" if not self.report_lines else \
                "🚨 CLEANUP FAILURE: The following directories require attention:\n\n" + "\n".join(
                    self.report_lines) + "\n"

            body += self.generate_signature()

            msg = EmailMessage()
            msg.set_content(body)
            msg[
                'Subject'] = f"{'🚨' if self.stats['failed'] > 0 else '✅'} Storage Audit: {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.smtp_cfg.get('sender', "automation@parkcircus.org")
            msg['To'] = self.smtp_cfg.get('receiver', "reza@parkcircus.org")

            context = ssl._create_unverified_context()
            with smtplib.SMTP(self.smtp_cfg.get('server'), int(self.smtp_cfg.get('port', 25))) as server:
                server.ehlo()
                if "starttls" in server.esmtp_features:
                    server.starttls(context=context)
                    server.ehlo()
                if self.smtp_cfg.get('user') and self.smtp_cfg.get('password'):
                    if "auth" in server.esmtp_features:
                        server.login(self.smtp_cfg.get('user'), self.smtp_cfg.get('password'))
                server.send_message(msg)
            logger.info(f"{B}📧 Report sent successfully.{NC}")
        except Exception as e:
            logger.error(f"💀 SMTP ERROR: {e}")


if __name__ == "__main__":
    StorageWatchdog(CONFIG_PATH).run_audit()
