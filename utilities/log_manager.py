#!/usr/bin/env python3
"""
===============================================================================
🚀 NAME          : log_manager.py
👤 AUTHOR        : Matha Goram / BeUlta Suite
🔖 VERSION       : 4.0.0 (Enterprise Python Edition)
📝 DESCRIPTION   : Universal Log Rotation and SMTP Reporting Engine.
                   Dynamically discovers, compresses, and audits satellite logs.
-------------------------------------------------------------------------------
🛠️  WORKFLOW      :
    1. 🛡️  Initialize secure context and load SMTP/Path configs.
    2. 🔍  Recursively discover all *.log files in the satellite root.
    3. ♻️  Perform GZIP rotation with historical retention logic.
    4. ✉️  Execute granular SMTP transaction with failure handling.
    5. 📊  Provide a colorized CLI dashboard and email summary.

📋 PREREQUISITES :
    - Python 3.11+
    - Packages: `python-dotenv`, `tomllib`
    - System: `gzip` support

📜 LICENSE       : MIT License
                   Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

import os
import sys
import gzip
import shutil
import smtplib
import tomllib
import logging
import ssl
from datetime import datetime
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
logger = logging.getLogger("LogManager")


def load_secure_config(path: Path) -> dict[str, Any]:
    """Advanced TOML loader with ENV substitution and placeholder safety."""
    load_dotenv(dotenv_path=ENV_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    with open(path, "r") as f:
        content = Template(f.read()).safe_substitute(os.environ)
        return tomllib.loads(content)


class LogRotationEngine:
    def __init__(self, config_path: Path):
        self.report_lines = []
        try:
            self.config = load_secure_config(config_path)
            self.smtp_cfg = self.config.get('smtp', {})
        except Exception as e:
            logger.error(f"💀 {R}[CONFIG ERROR]{NC} {e}")
            sys.exit(1)

        self.sat_root = Path("/home/reza/Videos/satellite")
        self.max_retention = 7

    def rotate_file(self, log_path: Path):
        """Performs GZIP rotation and historical aging."""
        try:
            for i in range(self.max_retention - 1, 0, -1):
                old = log_path.with_name(f"{log_path.name}.{i}.gz")
                new = log_path.with_name(f"{log_path.name}.{i + 1}.gz")
                if old.exists():
                    old.rename(new)

            archive = log_path.with_name(f"{log_path.name}.1.gz")
            with open(log_path, 'rb') as f_in:
                with gzip.open(archive, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            log_path.write_text("")
            msg = f"✅ {G}SUCCESS:{NC} {log_path.relative_to(self.sat_root)} rotated."
            logger.info(msg)
            self.report_lines.append(msg)
        except Exception as e:
            err = f"❌ {R}ERROR:{NC} Failed rotating {log_path.name}: {e}"
            logger.error(err)
            self.report_lines.append(err)

    def run(self):
        """Main execution loop using universal discovery."""
        logger.info(f"{B}🧹 Starting Universal Log Rotation Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}")
        print("-" * 70)

        logs = list(self.sat_root.rglob("*.log"))
        if not logs:
            logger.warning(f"⚠️ {Y}No logs found in {self.sat_root}{NC}")
            return

        for log in logs:
            if log.exists() and log.stat().st_size > 0:
                self.rotate_file(log)

        self.send_report()

    def send_report(self):
        """Granular SMTP transaction: Handles STARTTLS and Expired LAN Certs."""
        try:
            msg = EmailMessage()
            msg.set_content("\n".join(self.report_lines))
            msg['Subject'] = f"🚀 Log Rotation Report: {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.smtp_cfg.get('sender', "automation@parkcircus.org")
            msg['To'] = self.smtp_cfg.get('receiver', "reza@parkcircus.org")

            host = self.smtp_cfg.get('server')
            port = int(self.smtp_cfg.get('port', 25))
            user = self.smtp_cfg.get('user')
            password = self.smtp_cfg.get('password')

            # --- 🛡️ RELAXED SSL CONTEXT FOR LAN ---
            # This bypasses the 'CERTIFICATE_VERIFY_FAILED' error for internal servers
            context = ssl._create_unverified_context()

            with smtplib.SMTP(host, port) as server:
                server.ehlo()

                if "starttls" in server.esmtp_features:
                    server.starttls(context=context)
                    server.ehlo()
                    logger.info(f"✨ {G}TLS Encryption enabled (Unverified Context).{NC}")

                if user and password:
                    if "auth" in server.esmtp_features:
                        server.login(user, password)
                        logger.info(f"🔐 {G}Authenticated successfully.{NC}")
                    else:
                        logger.warning(f"⚠️ {Y}Server does not support AUTH. Sending anonymously...{NC}")

                server.send_message(msg)

            logger.info(f"{B}📧 Report sent successfully to {msg['To']}{NC}")

        except Exception as e:
            logger.error(f"💀 {R}SMTP TRANSACTION FAILED:{NC} {e}")


if __name__ == "__main__":
    LogRotationEngine(CONFIG_PATH).run()
