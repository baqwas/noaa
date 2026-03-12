#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Network Suite
📦 MODULE       : net_headroom.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.5.0
📅 LAST UPDATE  : 2026-03-12
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY (2026-03-12):
    - 1.4.0: FQDN & ISP Trace (Local reverse DNS).
    - 1.5.0: PRIVACY & GATEWAY UPDATE.
             - Removed local FQDN lookup to protect 'bezaman.parkcircus.org'.
             - Implemented ISP Gateway Discovery (external hop identification).
             - Added scapy-lite logic to find the first public ISP FQDN.

📝 DESCRIPTION:
    A high-fidelity "Flight Recorder" that identifies the ISP's entry point
    while keeping the user's local gateway server FQDN private.
===============================================================================
"""

import psutil
import time
import sys
import requests
import socket
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess

# --- ⚙️ CONFIGURATION ---
TOTAL_CAPACITY_MBPS = 1000
REFRESH_RATE = 1.0
LOOKUP_URL = 'https://icanhazip.com'


def get_isp_gateway_fqdn():
    """
    Identifies the first public ISP hop to avoid displaying the user's
    local gateway (bezaman.parkcircus.org).
    """
    try:
        # We run a short traceroute and look for the first hop that doesn't
        # look like a local IP (192.168.x.x, 10.x.x.x, etc.)
        cmd = ["traceroute", "-m", "5", "-n", "8.8.8.8"]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()

        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 2 or "traceroute" in line:
                continue

            ip = parts[1]
            # Skip local/private IP ranges
            if ip.startswith(("192.168.", "10.", "172.16.", "127.")):
                continue

            # This is the first public hop (The ISP Server)
            try:
                isp_fqdn = socket.gethostbyaddr(ip)[0]
                return isp_fqdn
            except Exception:
                return f"ISP Gateway ({ip})"

    except Exception:
        return "Pavlov Media Infrastructure"
    return "ISP Gateway"


def get_network_metadata():
    """Retrieves WAN IP and Remote Server FQDN."""
    metadata = {
        "ip": "Unknown IP",
        "isp_fqdn": "Unknown ISP",
        "remote_fqdn": "Unknown Remote Host"
    }
    try:
        # 1. Get Public IP
        response = requests.get(LOOKUP_URL, timeout=5)
        metadata["ip"] = response.text.strip()

        # 2. Identify Remote Server (Participating Server)
        remote_addr = socket.gethostbyname(LOOKUP_URL.replace('https://', ''))
        metadata["remote_fqdn"] = socket.getfqdn(remote_addr)

        # 3. Discover ISP Gateway (Privacy-safe)
        metadata["isp_fqdn"] = get_isp_gateway_fqdn()

    except Exception:
        pass
    return metadata


def generate_report(telemetry_data, meta):
    """Generates visual and data artifacts after the flight session."""
    if not telemetry_data:
        print("\n⚠️  No telemetry data captured.")
        return

    print(f"\n[ANALYSIS] Generating artifacts...")

    df = pd.DataFrame(telemetry_data)
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 1. Export Data
    csv_file = f"net_telemetry_{timestamp_str}.csv"
    df.to_csv(csv_file, index=False)

    # 2. Plotting
    plt.style.use('bmh')
    plt.figure(figsize=(12, 8))
    plt.plot(df['Time'], df['DL_Mbps'], label='Download (Mbps)', color='#1f77b4', lw=2)
    plt.plot(df['Time'], df['UL_Mbps'], label='Upload (Mbps)', color='#d62728', lw=1.5, alpha=0.7)

    # Title showing the ISP entry point, not the user's gateway
    full_title = (
        f"BeUlta Network Telemetry Analysis\n"
        f"Session: {timestamp_str}\n"
        f"ISP Entry Point: {meta['isp_fqdn']}\n"
        f"Telemetry Endpoint: {meta['remote_fqdn']}"
    )
    plt.title(full_title, fontsize=12, pad=20)
    plt.xlabel('Time (HH:MM:SS)')
    plt.ylabel('Throughput (Mbps)')

    tick_spacing = max(1, len(df) // 12)
    plt.xticks(df['Time'][::tick_spacing], rotation=45)
    plt.legend(loc='upper right')
    plt.tight_layout()

    img_file = f"net_analysis_{timestamp_str}.png"
    plt.savefig(img_file)

    print(f"✅ Analysis saved: {img_file}")


def get_bandwidth_usage():
    """Calculates throughput Mbps."""
    try:
        old_io = psutil.net_io_counters()
        time.sleep(REFRESH_RATE)
        new_io = psutil.net_io_counters()
        dl_mbps = ((new_io.bytes_recv - old_io.bytes_recv) * 8) / (1024 * 1024) / REFRESH_RATE
        ul_mbps = ((new_io.bytes_sent - old_io.bytes_sent) * 8) / (1024 * 1024) / REFRESH_RATE
        return dl_mbps, ul_mbps
    except Exception:
        return 0.0, 0.0


def main():
    session_data = []
    print(f"🌐 Identifying ISP Infrastructure...")
    meta = get_network_metadata()

    print(f"============================================================")
    print(f"🛰️  BEULTA NETWORK RECORDER | Version 1.5.0")
    print(f"▶️  START TIME   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏢 ISP ENTRY    : {meta['isp_fqdn']}")
    print(f"📡 REMOTE FQDN  : {meta['remote_fqdn']}")
    print(f"------------------------------------------------------------")
    print(f"RECORDER ACTIVE: Collecting telemetry in the background...")
    print(f"ACTION REQUIRED: Press [Ctrl+C] to stop and generate plot.")
    print(f"============================================================")

    try:
        while True:
            dl, ul = get_bandwidth_usage()
            now_time = datetime.now().strftime('%H:%M:%S')
            session_data.append({"Time": now_time, "DL_Mbps": round(dl, 2), "UL_Mbps": round(ul, 2)})

    except KeyboardInterrupt:
        generate_report(session_data, meta)
        sys.exit(0)


if __name__ == "__main__":
    main()
