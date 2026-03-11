"""
================================================================================
🌱 MODULE        : core_service.py
🚀 DESCRIPTION   : Centralized Handshake Engine for SMTP, MQTT, and MariaDB.
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 2.4.0
📅 UPDATED       : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
================================================================================

[Summary]
Provides a unified interface for system-wide services across the BeUlta Suite.
It automates the 'handshake' process for database connections, telemetry
messaging, and alert notifications. This version includes the TerminalColor
class for standardized status-coded ANSI output across the fleet.

[Prerequisites]
- Python 3.10+ with toml, mariadb, and paho-mqtt.
- Valid config.toml in the project root (/home/reza/PycharmProjects/noaa/).
- MariaDB Connector/C installed on the host system.

[Workflow Pipeline Description]
1. Bootstrapping: Reads config.toml into a global 'config' dictionary.
2. Initialization: Scripts call init_mariadb() or init_mqtt() to establish pointers.
3. Aesthetics: Scripts leverage TerminalColor for unified UI status reporting.
4. Communication: Scripts use send_smtp_alert() for standardized MIME reporting.

[Unicode Icons Guide]
🤝 : Handshake Initiated          | 🟢 : Connection Successful
🚨 : Connection Failed            | 📧 : SMTP Message Dispatched
🔒 : Environment Variables Synced | 🎨 : Terminal Aesthetics Initialized

[Error Messages Summary]
- "ERR_CFG_001": Failed to parse TOML configuration.
- "ERR_DB_AUTH": Access denied to MariaDB (ER_ACCESS_DENIED_ERROR).
- "ERR_DB_NAME": Target database does not exist (ER_BAD_DB_ERROR).
- "ERR_MQ_001": MQTT broker handshake failed.
- "ERR_SMTP_001": Standardized SMTP helper dispatch failure.

[Audit Trail]
Date       | Version | Author | Description
-----------|---------|--------|-----------------------------------------------
2025-07-15 | 1.0.0   | Reza   | Initial core service foundation.
2026-03-10 | 2.3.0   | Reza   | Added sync_env_to_config for .env secrets.
2026-03-10 | 2.4.0   | Gemini | Integrated TerminalColor class and UI standards.
================================================================================
"""

import os
import sys
import toml
import smtplib
import mariadb
import paho.mqtt.client as mqtt
from email.message import EmailMessage
from dotenv import load_dotenv


class TerminalColor:
    """ANSI Escape Sequences for status-coded terminal output."""
    HEADER = '\033[95m'  # Light Magenta/Purple
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


# --- 🛰️ GLOBAL POINTERS ---
config = {}
db_conn = None
mqtt_client = None
TC = TerminalColor()


def get_config():
    """Reads and returns the central config.toml using absolute pathing."""
    path = "/home/reza/PycharmProjects/noaa/config.toml"
    if os.path.exists(path):
        try:
            return toml.load(path)
        except Exception as e:
            print(f"{TC.FAIL}🚨 ERR_CFG_001: Failed to parse TOML: {e}{TC.ENDC}")
    return {}


def sync_env_to_config():
    """Parses .env and overlays secrets onto the global configuration."""
    global config
    env_path = "/home/reza/PycharmProjects/noaa/.env"
    if os.path.exists(env_path):
        load_dotenv(env_path)

        # Mapping .env secrets into the config dictionary
        if 'smtp' in config:
            config['smtp']['server'] = os.getenv('SMTP_SERVER', config['smtp'].get('server'))
            config['smtp']['user'] = os.getenv('SMTP_USER', config['smtp'].get('user'))
            config['smtp']['password'] = os.getenv('SMTP_PASSWORD', config['smtp'].get('password'))
            config['smtp']['sender'] = os.getenv('SMTP_SENDER', config['smtp'].get('sender'))
            config['smtp']['receiver'] = os.getenv('SMTP_RECEIVER', config['smtp'].get('receiver'))

        if 'mariadb' in config:
            config['mariadb']['host'] = os.getenv('DB_HOST', config['mariadb'].get('host'))
            config['mariadb']['user'] = os.getenv('DB_USER', config['mariadb'].get('user'))
            config['mariadb']['password'] = os.getenv('DB_PASSWORD', config['mariadb'].get('password'))
            config['mariadb']['database'] = os.getenv('DB_DATABASE', config['mariadb'].get('database'))

        if 'mqtt' in config:
            config['mqtt']['broker'] = os.getenv('MQTT_BROKER', config['mqtt'].get('broker'))
            config['mqtt']['user'] = os.getenv('MQTT_USER', config['mqtt'].get('user'))
            config['mqtt']['password'] = os.getenv('MQTT_PASSWORD', config['mqtt'].get('password'))

        print(f"{TC.OKCYAN}🔒 🤝 Environment variables synchronized with configuration.{TC.ENDC}")


def init_mariadb():
    """Establishes the MariaDB pointer using production credentials."""
    global db_conn
    db_cfg = config.get('mariadb', {})
    try:
        conn = mariadb.connect(
            user=db_cfg.get('user'),
            password=db_cfg.get('password'),
            host=db_cfg.get('host'),
            port=int(db_cfg.get('port', 3306)),
            database=db_cfg.get('database')
        )
        db_conn = conn
        print(f"{TC.OKGREEN}🟢 📊 MariaDB Handshake Successful.{TC.ENDC}")
        return db_conn
    except mariadb.Error as e:
        if e.errno == 1045:
            print(f"{TC.FAIL}🚨 ERR_DB_AUTH: Access denied to MariaDB.{TC.ENDC}")
        elif e.errno == 1049:
            print(f"{TC.FAIL}🚨 ERR_DB_NAME: Database does not exist.{TC.ENDC}")
        else:
            print(f"{TC.FAIL}🚨 ERR_DB_GENERIC: {e}{TC.ENDC}")
        return None


def init_mqtt():
    """Establishes the MQTT pointer for SOHO farm telemetry."""
    global mqtt_client
    mq_cfg = config.get('mqtt', {})
    try:
        client = mqtt.Client()
        if mq_cfg.get('user'):
            client.username_pw_set(mq_cfg.get('user'), mq_cfg.get('password'))
        client.connect(mq_cfg.get('broker', 'localhost'), int(mq_cfg.get('port', 1883)))
        client.loop_start()
        mqtt_client = client
        print(f"{TC.OKGREEN}🟢 🛰️ MQTT Handshake Successful.{TC.ENDC}")
        return mqtt_client
    except Exception as e:
        print(f"{TC.FAIL}🚨 ERR_MQ_001: MQTT Handshake Failed: {e}{TC.ENDC}")
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
            if smtp_cfg.get('user') and smtp_cfg.get('password'):
                s.login(smtp_cfg.get('user'), smtp_cfg.get('password'))
            s.send_message(msg)
        print(f"{TC.OKCYAN}📧 SMTP Message Dispatched: {subject}{TC.ENDC}")
    except Exception as e:
        print(f"{TC.FAIL}🚨 ERR_SMTP_001: Mail dispatch failure: {e}{TC.ENDC}")


# --- 🚀 BOOTSTRAP ON IMPORT ---
config = get_config()
sync_env_to_config()
