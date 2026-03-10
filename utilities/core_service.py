"""
================================================================================
🌱 MODULE        : core_service.py
🚀 DESCRIPTION   : Centralized Handshake Engine for SMTP, MQTT, and MariaDB.
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 2.3.0
📅 UPDATED       : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
================================================================================

[Summary]
Provides a unified interface for system-wide services across the BeUlta Suite.
It automates the 'handshake' process for database connections, telemetry
messaging, and alert notifications, insulating functional scripts from
infrastructure configuration. Uses the native MariaDB connector.

[Prerequisites]
- Python 3.10+ with toml, mariadb, and paho-mqtt.
- Valid config.toml in the project root (~/noaa/).
- MariaDB Connector/C installed on the host system.

[Workflow Pipeline Description]
1. Bootstrapping: Reads config.toml into a global 'config' dictionary.
2. Initialization: Scripts call init_mariadb() or init_mqtt() to establish pointers.
3. Communication: Scripts use send_smtp_alert() for standardized MIME reporting.

[Unicode Icons Guide]
🤝 : Handshake Initiated          | 🟢 : Connection Successful
🚨 : Connection Failed            | 📧 : SMTP Message Dispatched
🔒 : Environment Variables Synced | 📊 : MariaDB Pointer Ready

[Error Messages Summary]
- "ER_ACCESS_DENIED_ERROR": Invalid MariaDB credentials.
- "ER_BAD_DB_ERROR": Target database does not exist.
- "ERR_MQ_001": MQTT Broker unreachable (check service status).

[Audit Trail]
Date       | Version | Author | Description
-----------|---------|--------|-----------------------------------------------
2025-11-15 | 1.0.0   | Matha  | Initial handshake logic for MQTT.
2026-02-12 | 2.0.0   | Matha  | Integrated MariaDB aircraft hydrator logic.
2026-03-10 | 2.3.0   | Matha  | Migrated to native mariadb connector & constants.

[References]
- MariaDB Python: https://mariadb.com/kb/en/python-connection/
- Paho MQTT: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
================================================================================
"""

import os
import sys
import toml
import smtplib
import mariadb  # Native MariaDB connector
import paho.mqtt.client as mqtt
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv

# --- 🛰️ ESTABLISHED GLOBAL POINTERS ---
config = {}
db_conn = None
mqtt_client = None


def get_config():
    """Reads and returns the central config.toml."""
    path = "/home/reza/PycharmProjects/noaa/config.toml"
    if os.path.exists(path):
        try:
            return toml.load(path)
        except Exception as e:
            print(f"🚨 ERR_CFG_001: Failed to parse TOML: {e}")
    return {}


def sync_env_to_config():
    """
    Parses .env and overlays secrets onto the global config.
    Maps prefixes: DB_ -> [mariadb], MQTT_ -> [mqtt], SMTP_ -> [smtp].
    """
    global config
    env_path = "/home/reza/PycharmProjects/noaa/.env"
    load_dotenv(env_path)

    mapping = {
        "DB_": "mariadb",
        "MQTT_": "mqtt",
        "SMTP_": "smtp"
    }

    for env_key, env_val in os.environ.items():
        for prefix, section in mapping.items():
            if env_key.startswith(prefix):
                clean_key = env_key.replace(prefix, "").lower()
                if section not in config:
                    config[section] = {}
                config[section][clean_key] = env_val


# --- 🤝 THE HANDSHAKES ---

def init_mariadb():
    """
    Establishes the native MariaDB pointer.
    Implements specific MariaDB Error constants for diagnostics.
    """
    global db_conn
    db_cfg = config.get('mariadb', {})

    try:
        db_conn = mariadb.connect(
            user=db_cfg.get('user'),
            password=db_cfg.get('password'),
            host=db_cfg.get('host', 'localhost'),
            port=int(db_cfg.get('port', 3306)),
            database=db_cfg.get('database')
        )
        db_conn.autocommit = True
        return db_conn

    except mariadb.Error as e:
        # Professional Error Differentiation
        if e.errno == mariadb.constants.ER.ACCESS_DENIED_ERROR:
            print(f"🚨 ERR_DB_AUTH: Invalid credentials.")
        elif e.errno == mariadb.constants.ER.BAD_DB_ERROR:
            print(f"🚨 ERR_DB_NAME: Database does not exist.")
        else:
            print(f"🚨 ERR_DB_GENERIC: {e}")
        return None


def init_mqtt():
    """Establishes the MQTT pointer for SOHO farm telemetry."""
    global mqtt_client
    mq_cfg = config.get('mqtt', {})
    try:
        client = mqtt.Client()
        client.connect(mq_cfg.get('broker', 'localhost'), int(mq_cfg.get('port', 1883)))
        client.loop_start()
        mqtt_client = client
        return mqtt_client
    except Exception as e:
        print(f"🚨 ERR_MQ_001: MQTT Handshake Failed: {e}")
        return None


def send_smtp_alert(subject, body):
    """Standardized SMTP helper using local relay settings."""
    smtp_cfg = config.get('smtp', {})
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"🚀 BeUlta: {subject}"
    msg['From'] = smtp_cfg.get('sender', 'reza@BeZaman.parkcircus.org')
    msg['To'] = smtp_cfg.get('receiver', 'reza@BeUlta')

    try:
        server = smtp_cfg.get('server', 'localhost')
        port = int(smtp_cfg.get('port', 587))
        with smtplib.SMTP(server, port) as s:
            if smtp_cfg.get('use_tls', True):
                s.starttls()
            if smtp_cfg.get('user'):
                s.login(smtp_cfg.get('user'), smtp_cfg.get('password'))
            s.send_message(msg)
    except Exception as e:
        print(f"🚨 ERR_SMTP_001: SMTP Dispatch Failed: {e}")


# --- ⚙️ AUTO-INITIALIZATION ---
config = get_config()
sync_env_to_config()
