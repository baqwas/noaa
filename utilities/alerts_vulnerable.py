#!/usr/bin/env python3
import json
import os
import smtplib
import tomllib
from email.message import EmailMessage

# --- Configuration Paths ---
PROJ_ROOT = "/home/reza/PycharmProjects/noaa"
HEALTH_FILE = os.path.join(PROJ_ROOT, "logs/qlog_system_health.json")
CONFIG_FILE = os.path.join(PROJ_ROOT, "config.toml")


def get_config():
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def send_alert(secrets_status):
    config = get_config()
    # Assuming config.toml has a [smtp] section
    smtp_cfg = config.get("smtp", {})

    msg = EmailMessage()
    msg.set_content(f"⚠️ SECURITY ALERT: Secrets status has changed to: {secrets_status}\n\n"
                    f"System: {os.uname().nodename}\n"
                    f"Check: {HEALTH_FILE}")

    msg['Subject'] = f"🚨 SECURITY ALERT: Secrets {secrets_status}"
    msg['From'] = smtp_cfg.get("user")
    msg['To'] = smtp_cfg.get("admin_email", smtp_cfg.get("user"))

    try:
        with smtplib.SMTP(smtp_cfg.get("server"), smtp_cfg.get("port")) as server:
            if smtp_cfg.get("use_tls"):
                server.starttls()
            server.login(smtp_cfg.get("user"), smtp_cfg.get("password"))
            server.send_message(msg)
            print("✅ Alert email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def check_health():
    if not os.path.exists(HEALTH_FILE):
        return

    with open(HEALTH_FILE, 'r') as f:
        data = json.load(f)

    if data.get("secrets") == "VULNERABLE":
        print("🚨 VULNERABILITY DETECTED! Triggering alert...")
        send_alert("VULNERABLE")


if __name__ == "__main__":
    check_health()