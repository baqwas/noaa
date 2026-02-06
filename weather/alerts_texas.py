#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
Name:           alerts_texas.py
Version:        1.2.0
Description:    Texas Weather Alert Monitor with SMTP and MQTT notifications.
-------------------------------------------------------------------------------
"""

import argparse
import os
import logging
import requests
import tomllib
import smtplib
import json
import paho.mqtt.client as mqtt
from email.message import EmailMessage


def resolve_path(path_str):
    if not path_str: return None
    return os.path.expanduser(os.path.expandvars(path_str))


def publish_mqtt(config, event, severity, headline):
    """Publishes alert data to the LAN MQTT broker."""
    mqtt_cfg = config.get('mqtt', {})
    client = mqtt.Client()

    try:
        if mqtt_cfg.get('user'):
            client.username_pw_set(mqtt_cfg['user'], mqtt_cfg['password'])

        client.connect(mqtt_cfg['host'], mqtt_cfg.get('port', 1883), 60)

        payload = json.dumps({
            "event": event,
            "severity": severity,
            "headline": headline,
            "timestamp": requests.utils.quote(headline[:20])  # or current time
        })

        topic = mqtt_cfg.get('topic_prefix', 'home/science/alerts/texas')
        client.publish(topic, payload, qos=1, retain=True)
        client.disconnect()
    except Exception as e:
        logging.error(f"MQTT Publish Error: {e}")


def send_alert(config, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"WEATHER ALERT: {subject}"
    msg['From'] = config['smtp']['sender']
    msg['To'] = config['smtp']['receiver']
    try:
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['user'], config['smtp']['password'])
            server.send_message(msg)
    except Exception as e:
        logging.error(f"SMTP Notification Error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    weather_cfg = config.get('weather_alerts', {})
    base_data_dir = resolve_path(weather_cfg.get('base_data_dir', '~/Videos/satellite/weather'))
    log_dir = resolve_path(weather_cfg.get('log_dir', os.path.join(base_data_dir, 'alerts/logs')))
    storage_dir = resolve_path(weather_cfg.get('storage_dir', os.path.join(base_data_dir, 'alerts/data')))

    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(storage_dir, exist_ok=True)

    logging.basicConfig(filename=os.path.join(log_dir, "alerts.log"), level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Heartbeat log to ensure we see file creation even on sunny days
    logging.info("Checking NWS API for active alerts...")

    headers = {'User-Agent': '(TexasAlertMonitor/1.2, contact@reza.com)', 'Accept': 'application/geo+json'}
    url = f"https://api.weather.gov/alerts/active?area={weather_cfg.get('area', 'TX')}"

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        alerts = response.json().get('features', [])
        cache_file = os.path.join(storage_dir, "seen_alerts.json")

        seen_ids = set()
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                seen_ids = set(json.load(f))

        current_active_ids = []
        for alert in alerts:
            props = alert['properties']
            alert_id = props['id']
            current_active_ids.append(alert_id)

            if alert_id not in seen_ids:
                severity = props.get('severity', 'Unknown')
                event = props.get('event', 'Weather Event')
                headline = props.get('headline', 'No headline available.')
                instruction = props.get('instruction', 'Follow local guidance.')

                logging.info(f"PROCESSING NEW ALERT: {event} ({severity})")

                # 1. Send Email
                send_alert(config, f"{event} - {severity}", f"{headline}\n\nINSTRUCTIONS:\n{instruction}")

                # 2. Publish MQTT
                publish_mqtt(config, event, severity, headline)

        with open(cache_file, 'w') as f:
            json.dump(current_active_ids, f)

    except Exception as e:
        logging.error(f"Execution Error: {e}")


if __name__ == "__main__":
    main()