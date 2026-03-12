#!/usr/bin/env python3
"""
================================================================================
🛠️ MODULE        : core_service.py
🔖 VERSION       : 1.9.8 (Interpolation Reliability Update)
================================================================================
"""
import os
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate
from dotenv import load_dotenv

try:
    import tomllib
except ImportError:
    import toml as tomllib

class CoreService:
    def __init__(self):
        load_dotenv()
        self.project_root = Path("/home/reza/PycharmProjects/noaa")
        self.config = self.get_config()

    @staticmethod
    def get_config():
        root = Path("/home/reza/PycharmProjects/noaa")
        config_path = root / "config.toml"
        if config_path.exists():
            with open(config_path, "r") as f:
                raw_contents = f.read()
                interpolated_contents = os.path.expandvars(raw_contents)
                return tomllib.loads(interpolated_contents)
        return {}

    def send_report(self, config, body, subject="🚀 BeUlta: System Notification"):
        smtp_cfg = config.get('smtp', {})
        srv, port = smtp_cfg.get('server'), int(smtp_cfg.get('port', 587))
        user, passwd = smtp_cfg.get('user'), smtp_cfg.get('password')
        sender, receiver = smtp_cfg.get('sender'), smtp_cfg.get('receiver')

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"BeUlta Auditor <{sender}>"
        msg['To'] = receiver
        msg['Message-ID'] = make_msgid(domain='parkcircus.org')
        msg['Date'] = formatdate(localtime=True)
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(srv, port, timeout=15) as server:
                server.starttls()
                server.login(user, passwd)
                server.send_message(msg)
            print(f"📧 Report delivered to {receiver} ✅")
        except Exception as e:
            print(f"❌ SMTP FAILURE: {e}")
