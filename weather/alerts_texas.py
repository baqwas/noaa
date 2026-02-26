#!/usr/bin/env python3
"""
================================================================================
📦 MODULE        : alerts_texas.py
🚀 DESCRIPTION   : Robust NWS Alert Aggregator with MQTT Receipt Verification.
👤 AUTHOR        : Matha Goram
📅 UPDATED       : 2026-02-24
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
"""

import sys
import os
import requests
import json
import time
from datetime import datetime
from typing import Any

# --- 🛠️ PRIORITY PATH INJECTION ---
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    utilities_path = os.path.abspath(os.path.join(current_dir, '..', 'utilities'))
    if utilities_path not in sys.path:
        sys.path.insert(0, utilities_path)
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] CoreService Resolution Error: {e}")
    sys.exit(1)

import paho.mqtt.client as mqtt


class TexasAlertNode(CoreService):
    """
    ⚠️ WEATHER ALERT ENGINE
    Synchronous MQTT publishing with delivery confirmation (QoS 1).
    """

    def __init__(self, config_path: str = "../swpc/config.toml"):
        super().__init__(config_path=config_path)
        self.alert_params: dict[str, Any] = self.config.get('weather_alerts', {})
        self.mqtt_cfg: dict[str, Any] = self.config.get('mqtt', {})

        # Resolve dynamic settings
        self.area = self.alert_params.get('area', 'TX')
        self.api_url = f"https://api.weather.gov/alerts/active?area={self.area}"
        self.mqtt_topic = self.alert_params.get('mqtt_topic', 'HA/alerts/weather')
        self.user_agent = f"(parkcircus.org, {self.config['smtp']['user']})"

        # Internal Tracking
        self.published_count = 0
        self.acknowledged_count = 0

    def on_publish(self, client, userdata, mid):
        """Callback triggered when the broker acknowledges a QoS 1 message."""
        self.acknowledged_count += 1
        # print(f"   📥 [DEBUG] Broker acknowledged message ID: {mid}")

    def fetch_and_publish(self) -> None:
        """📡 Synchronize NWS alerts with confirmed delivery logic."""
        headers = {'User-Agent': self.user_agent, 'Accept': 'application/geo+json'}

        # 🏗️ Initialize Dedicated Robust Client
        client = mqtt.Client(client_id="TexasAlertNode_Prod", clean_session=True)
        client.on_publish = self.on_publish

        if self.mqtt_cfg.get('user'):
            client.username_pw_set(self.mqtt_cfg['user'], self.mqtt_cfg['password'])

        try:
            # 1. Connect and Start Loop
            print(f"📡 Connecting to Broker: {self.mqtt_cfg['broker']}...")
            client.connect(self.mqtt_cfg['broker'], self.mqtt_cfg.get('port', 1883), 60)
            client.loop_start()  # Start background thread for callbacks

            # 2. Fetch Data
            print(f"📡 Querying NWS for active alerts in {self.area}...")
            response = requests.get(self.api_url, headers=headers, timeout=20)
            response.raise_for_status()
            features = response.json().get('features', [])

            if not features:
                print(f"✅ [IDLE] No active alerts found for {self.area}.")
                return

            # 3. Publish with QoS 1 (Guaranteed Delivery)
            print(f"📤 Publishing {len(features)} alerts to topic: {self.mqtt_topic}")
            for alert in features:
                payload = json.dumps(alert)
                # qos=1 ensures the broker must send a PUBACK back to us
                result = client.publish(self.mqtt_topic, payload, qos=1)
                result.wait_for_publish()  # Block until the message actually leaves the NIC
                self.published_count += 1

            # 4. Verification Sync
            # Wait up to 5 seconds for all acknowledgments to return from the broker
            timeout = time.time() + 5
            while self.acknowledged_count < self.published_count and time.time() < timeout:
                time.sleep(0.1)

            print(f"🚀 [SUMMARY] Sent: {self.published_count} | Acknowledged by Broker: {self.acknowledged_count}")

            if self.acknowledged_count < self.published_count:
                print(f"⚠️ [WARNING] {self.published_count - self.acknowledged_count} messages were not acknowledged.")

        except Exception as e:
            print(f"❌ [SYSTEM ERROR] {e}")
        finally:
            client.loop_stop()
            client.disconnect()
            print("🔒 MQTT Session Closed.")


if __name__ == "__main__":
    node = TexasAlertNode()
    node.fetch_and_publish()