#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : core_service.py
🚀 DESCRIPTION   : Centralized Utility Service for Database, SMTP, and MQTT.
                   Supports both legacy DBAPI2 and modern SQLAlchemy engines.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-03-01
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
"""

import os
import sys
import toml
import mariadb
import smtplib
import paho.mqtt.client as mqtt
from email.message import EmailMessage
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from typing import Optional, Any
from string import Template
from dotenv import load_dotenv


class CoreService:
    """
    🛠️ CORE SERVICE FOUNDATION
    Central utility class providing infrastructure connectivity for NOAA nodes.
    """

    def __init__(self, config_path: str = "../config.toml"):
        # Resolve absolute path relative to this script's location
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.abspath(os.path.join(base_path, config_path))

        self.config: dict[str, Any] = {}
        self._load_config()

        # Extract specific configuration blocks
        self.mariadb_params = self.config.get('mariadb', {})
        self.mqtt_params = self.config.get('mqtt', {})
        self.smtp_params = self.config.get('smtp', {})
        self.rain_params = self.config.get('rainfall', {})

    def _load_config(self) -> None:
        """🔍 Internal: Loads, substitutes, and validates the TOML configuration."""
        if not os.path.exists(self.config_path):
            print(f"❌ [CRITICAL] Configuration file missing: {self.config_path}")
            sys.exit(1)

        # 🛡️ Load environment variables from .env located next to config.toml
        env_path = os.path.join(os.path.dirname(self.config_path), ".env")
        load_dotenv(dotenv_path=env_path)

        try:
            with open(self.config_path, "r") as f:
                # Inject environment variables into the raw TOML string
                raw_content = f.read()
                substituted_content = Template(raw_content).safe_substitute(os.environ)
                self.config = toml.loads(substituted_content)

            # ⚙️ RELIABLE PORT CASTING
            # Ensure port values are integers for all service blocks
            for block in ['mariadb', 'mqtt', 'smtp']:
                if block in self.config and 'port' in self.config[block]:
                    try:
                        self.config[block]['port'] = int(self.config[block]['port'])
                    except (ValueError, TypeError):
                        print(f"⚠️ [CONFIG] Invalid port in [{block}]. Defaulting to standard.")
                        # Standard defaults if conversion fails
                        defaults = {'mariadb': 3306, 'mqtt': 1883, 'smtp': 587}
                        self.config[block]['port'] = defaults.get(block)

            print(f"✅ Configuration loaded & sanitized: {self.config_path}")
        except Exception as e:
            print(f"❌ [CRITICAL] Failed to parse TOML: {e}")
            sys.exit(1)

    # --- 🗄️ DATABASE CONNECTIVITY TIER ---

    def get_db_connection(self) -> Optional[mariadb.connection]:
        """
        🔗 LEGACY: Returns a raw MariaDB connection.
        Used for manual SQL execution and cursor-based operations.
        """
        try:
            return mariadb.connect(**self.mariadb_params)
        except mariadb.Error as e:
            print(f"❌ [DB ERROR] Raw Connection failed: {e}")
            return None

    def get_db_engine(self) -> Any:
        """
        🏗️ MODERN: Returns a SQLAlchemy Engine for Pandas compatibility.
        Eliminates 'UserWarning' regarding DBAPI2 objects.
        """
        m = self.mariadb_params
        try:
            connection_url = URL.create(
                drivername="mariadb+mariadbconnector",
                username=m['user'],
                password=m['password'],
                host=m.get('host', 'localhost'),
                port=m.get('port', 3306),
                database=m['database']
            )
            return create_engine(connection_url)
        except Exception as e:
            print(f"❌ [DB ERROR] SQLAlchemy Engine creation failed: {e}")
            raise

    # --- 📧 COMMUNICATION & MESSAGING TIER ---

    def send_email(self, subject: str, body: str, attachment_path: Optional[str] = None) -> None:
        """
        ✨ SMTP DISPATCH (STARTTLS SECURED)
        Connects to the LAN SMTP server and upgrades the connection to TLS.
        """
        msg = EmailMessage()
        prefix = self.rain_params.get('subject_prefix', 'Node22')
        msg['Subject'] = f"{prefix} | {subject}"
        msg['From'] = self.smtp_params.get('user')
        msg['To'] = self.smtp_params.get('recipients')
        msg.set_content(body)

        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    msg.add_attachment(
                        f.read(),
                        maintype='application',
                        subtype='octet-stream',
                        filename=os.path.basename(attachment_path)
                    )
            except Exception as e:
                print(f"⚠️ [SMTP] Failed to attach file: {e}")

        # 🔄 Reconciliation: Resolve the server address and port
        smtp_host = self.smtp_params.get('server') or self.smtp_params.get('host')
        smtp_port = self.smtp_params.get('port', 587)

        if not smtp_host:
            print("❌ [SMTP ERROR] Missing 'server' key in [smtp] configuration.")
            return

        try:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            server.ehlo()

            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()

            server.login(self.smtp_params['user'], self.smtp_params['password'])
            server.send_message(msg)
            server.quit()
            print("✨ Email dispatched successfully.")
        except Exception as e:
            print(f"❌ [SMTP ERROR] Dispatch failed: {e}")

    def publish_mqtt(self, topic_suffix: str, payload: str) -> None:
        """📡 MQTT TELEMETRY: Publishes script status to the network broker."""
        # Check both 'broker' and 'host' keys for compatibility
        host = self.mqtt_params.get('broker') or self.mqtt_params.get('host')
        if not host:
            print("❌ [MQTT ERROR] No broker/host defined in config.")
            return

        prefix = self.rain_params.get('subject_prefix', 'Node22')
        topic = f"nodes/{prefix}/{topic_suffix}"

        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            if self.mqtt_params.get('user'):
                client.username_pw_set(self.mqtt_params['user'], self.mqtt_params.get('password'))

            client.connect(host, self.mqtt_params.get('port', 1883), 60)
            client.publish(topic, payload, qos=1)
            client.disconnect()
        except Exception as e:
            print(f"❌ [MQTT ERROR] Publishing failed: {e}")