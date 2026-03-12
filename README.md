# 🌌 Satellite & Weather Suite using NASA/NOAA Data Sources
> **A unified atmospheric, terrestrial, and deep-space data orchestration engine.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.org/)
![Repo Size](https://img.shields.io/github/repo-size/baqwas/noaa?color=success)

### 📊 Project Pulse
[![Last Commit](https://img.shields.io/github/last-commit/baqwas/noaa?color=orange)](https://github.com/baqwas/noaa/commits/master)
[![Security & Integrity Master](https://github.com/baqwas/noaa/actions/workflows/security_master.yml/badge.svg)](https://github.com/baqwas/noaa/actions/workflows/security_master.yml)
![Status](https://img.shields.io/badge/System-Operational-green?style=flat-square)
![Maintenance](https://img.shields.io/badge/Maintenance-Weekly-green)

### 🛰️ System Health
_Last Health Check: 2026-03-12 21:28 | Drift:   km_

---

## 📖 1. Overview
The **BeUlta Satellite Suite** is a high-availability automation framework designed to fetch, archive, and visualize multispectral satellite imagery and terrestrial weather data. It bridges the gap between raw government APIs (NASA, NOAA, NWS) and local visualization platforms like **Node-RED** and custom **Dashboard 2.0** environments.

---

## 🧩 2. Integrated Modules
The suite manages five distinct data pipelines, categorized by their temporal and spatial focus:

* 🌍 **NASA EPIC**: Deep space global Earth rotation imagery from the L1 Lagrange point.
* 🛰️ **NOAA GOES**: High-cadence geostationary atmospheric weather imagery (East/West).
* ☀️ **SWPC Space Weather**: Aurora forecasts (North/South), Solar EUV (SUVI), and Coronagraph (LASCO) imagery.
* 🌱 **Terran**: Land-use and NDVI (Vegetation Index) trend monitoring.
* ⚠️ **NWS Weather**: Active Texas weather alerts via MQTT for real-time Dashboard 2.0 notifications.

---

## 🏗️ 3. System Architecture
The solution follows a **Producer-Consumer** architecture using Bash wrappers for environment isolation and Python engines for logic and API interaction.



### 📂 Standardized Storage Hierarchy
All instruments adhere to a unified directory structure to ensure auditability:
`{Project_Root}/{Instrument}/{Sub-Category}/{images|videos}`

| 📁 Directory | 🎯 Purpose | ⏳ Retention |
| :--- | :--- | :--- |
| `/images` | Source frames (JPG/PNG) | Purged after video compilation |
| `/videos` | Rendered MP4 timelapses | **Permanent Archive** |
| `/logs` | System traces & cron output | Rotated monthly |

---

## ⚙️ 4. Automation Logic (The Cron Engine)
Tasks are staggered to optimize CPU/IO load, ensuring `ffmpeg` rendering doesn't interfere with high-priority data ingestion.

1.  📥 **Ingestion**: `*_fetcher.sh` scripts run at 10–15m intervals.
2.  📢 **Alerting**: `weather_alerts.sh` (Texas) runs every 5m for real-time MQTT delivery.
3.  🛡️ **Auditing**: `system_audit.sh` runs every 6h to validate structural integrity.
4.  🎬 **Processing**: Nightly `ffmpeg` renders occur at 23:50 to close the daily data loop.

---

## 🩺 5. Diagnostics & Health Monitoring
### 🐕 The Auditor (`system_audit.py`)
This central watchdog script performs three critical checks every 6 hours:
* ✅ **Hierarchy Integrity**: Validates mandated `/images` and `/videos` directories.
* 🔍 **Orphan Detection**: Locates raw frames sitting outside of designated folders.
* 🚨 **Storage Health**: Dispatches a `[CRITICAL]` SMTP alert if `/home` usage exceeds 80%.

### ⚠️ Error Matrix
| 🏷️ Code | ⚡ Severity | 🛠️ Resolution |
| :--- | :--- | :--- |
| `[CRITICAL]` | 🔴 High | Clear storage; check for runaway log files. |
| `[FAIL]` | 🟡 Med | Re-create missing sub-directories via `mkdir -p`. |
| `[ORPHAN]` | 🔵 Low | Run migration script to move loose files into `/images`. |

---

## 🚀 6. Installation & Deployment

### 📋 Prerequisites
* **Python 3.11+**
* **FFmpeg** (for video encoding)
* **Paho-MQTT** (for Node-RED integration)
* **SMTP Access** (LAN-based credentials in `config.toml`)

### 🛠️ Quick Start

# 1. Setup Environment

```bash
git clone [https://github.com/BeUlta/satellite-suite.git](https://github.com/BeUlta/satellite-suite.git)
cd satellite-suite
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# 2. Initialize Infrastructure (Example for SWPC)

```bash
mkdir -p logs data/{aurora/{north,south}/images,solar_304/images,lasco_c3/images}
```

# 3. Configure & Test

```bash
nano swpc/config.toml
./swpc/system_audit.sh
```

---
> 📢 Disclaimer

This tool is an independent implementation and is not affiliated with or endorsed by NOAA or the US Department of Commerce. All data is sourced from public domain NOAA assets.

## ⚖️ 7. License

Copyright © 2026 ParkCircus Productions. Distributed under the MIT License.
