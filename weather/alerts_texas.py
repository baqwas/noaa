#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : alerts_texas.py
🚀 DESCRIPTION   : Robust NWS Alert Aggregator with MQTT Receipt Verification.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-03-01
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
📜 MIT LICENSE:
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
================================================================================
📋 WORKFLOW PROCESSING:
    1. 🛡️  Leverage CoreService to load config.toml with environment substitution.
    2. 🏗️  Initialize TexasAlertNode utilizing the sanitized CoreService parameters.
    3. 📡  Establish MQTT connection using modern Callback API (v2).
    4. ⏱️  Synchronize connection state to prevent "Not Connected" dispatch errors.
    5. 🌪️  Fetch real-time GeoJSON alerts from weather.gov (NWS).
    6. 📤  Broadcast alerts via MQTT QoS 1 with receipt verification.
    7. 🔒  Graceful session termination and status reporting.

🔗 REFERENCES:
    - NWS API: https://www.weather.gov/documentation/services-web-api
    - Paho MQTT: https://eclipse.dev/paho/files/jsdoc/symbols/paho.mqtt.client.html
================================================================================
"""

import sys
import os
import requests
import json
import time
from datetime import datetime
from typing import Any
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
try:
    current_file = Path(__file__).resolve()
    weather_dir = current_file.parent
    project_root = weather_dir.parent
    utilities_path = project_root / 'utilities'
    config_path = project_root / 'config.toml'

    if str(utilities_path) not in sys.path:
        sys.path.insert(0, str(utilities_path))
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Dependency Resolution Error: {e}")
    sys.exit(1)

import paho.mqtt.client as mqtt


class TexasAlertNode(CoreService):
    """
    ⚠️ WEATHER ALERT ENGINE
    Inherits from CoreService to handle all infrastructure connectivity.
    """

    def __init__(self, cfg_file: Path):
        # Initialize the parent CoreService which handles the secure config loading
        # and port integer conversion automatically.
        super().__init__(config_path=str(cfg_file))

        # Pull script-specific settings from the already-loaded self.config
        self.alert_params = self.config.get('weather_alerts', {})
        self.mqtt_topic = self.alert_params.get('mqtt_topic', 'weather/alerts/texas')
        self.area = self.alert_params.get('area', 'TX')

        self.published_count = 0
        self.acknowledged_count = 0

    def on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        """👤 UI: Track message delivery acknowledgments."""
        self.acknowledged_count += 1

    def fetch_and_publish(self):
        """
        🚀 MAIN EXECUTION ENGINE
        Manages the fetch-to-publish pipeline with connection safety checks.
        """
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_publish = self.on_publish

        # Handle username/password if provided in config
        if self.mqtt_params.get('user'):
            client.username_pw_set(self.mqtt_params['user'], self.mqtt_params.get('password'))

        try:
            # 📡 DYNAMIC BROKER: Resolve from the parent class's sanitized mqtt_params
            broker = self.mqtt_params.get('broker') or self.mqtt_params.get('host', 'localhost')
            port = self.mqtt_params.get('port', 1883)

            print(f"📡 Connecting to MQTT Broker: {broker}:{port}...")
            client.connect(broker, port, 60)
            client.loop_start()

            # ⏱️ CONNECTION SYNC: Wait for the network handshake to complete
            retries = 10
            while not client.is_connected() and retries > 0:
                time.sleep(0.5)
                retries -= 1

            if not client.is_connected():
                raise ConnectionError(f"Handshake failed with {broker}. Check listener settings.")

            # 🌪️ FETCH DATA
            url = f"https://api.weather.gov/alerts/active?area={self.area}"
            sender = self.smtp_params.get('sender', 'admin@local')
            headers = {'User-Agent': f"(TexasAlertNode, {sender})"}

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            features = response.json().get('features', [])

            if not features:
                print(f"✅ [IDLE] No active alerts found for {self.area}.")
                return

            # 📤 DISPATCH
            print(f"📤 Publishing {len(features)} alerts to {self.mqtt_topic}")
            for alert in features:
                payload = json.dumps(alert)
                # QoS 1 ensures the broker sends a PUBACK for every message
                result = client.publish(self.mqtt_topic, payload, qos=1)
                result.wait_for_publish()
                self.published_count += 1

            # Verification delay for final acknowledgments
            verify_timeout = time.time() + 5
            while self.acknowledged_count < self.published_count and time.time() < verify_timeout:
                time.sleep(0.1)

            print(f"🚀 [SUMMARY] Sent: {self.published_count} | Acknowledged: {self.acknowledged_count}")

        except Exception as e:
            print(f"❌ [SYSTEM ERROR] {e}")
        finally:
            client.loop_stop()
            client.disconnect()
            print("🔒 MQTT Session Closed.")


if __name__ == "__main__":
    # Dynamically locate config.toml relative to this script's location
    script_path = Path(__file__).resolve()
    target_config = script_path.parent.parent / "config.toml"

    node = TexasAlertNode(target_config)
    node.fetch_and_publish()
