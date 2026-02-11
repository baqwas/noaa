#!/usr/bin/env python3
"""
⚠️ NAME           : alerts_texas.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 2.0.0 (Geofence-Ready)
📝 DESCRIPTION   : Publishes NWS alerts with geometry to MQTT for Node-RED filtering.
"""

import requests
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# --- ⚙️ CONFIGURATION ---
NWS_API_URL = "https://api.weather.gov/alerts/active?area=TX"
MQTT_BROKER = "raspbari7.parkcircus.org"
MQTT_TOPIC = "weather/alerts/texas/ingest"
HEADERS = {'User-Agent': '(parkcircus.org, reza@parkcircus.org)'}

def fetch_and_publish():
    client = mqtt.Client()
    try:
        # Connect to LAN Broker
        client.connect(MQTT_BROKER, 1883, 60)
        
        response = requests.get(NWS_API_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
        data = response.json()
        features = data.get('features', [])

        for alert in features:
            # We preserve the 'geometry' key here so Node-RED can geofence
            # This was missing in your previous version.
            client.publish(MQTT_TOPIC, json.dumps(alert))

        print(f"[{datetime.now()}] ✅ Published {len(features)} geofence-ready alerts.")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ MQTT/NWS Error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    fetch_and_publish()

