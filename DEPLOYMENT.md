This **Master Deployment Summary** is rendered in Markdown syntax, designed for direct inclusion in your project's technical documentation or a `DEPLOYMENT.md` file.

---

# 🛰️ Master Deployment Summary: BeUlta Suite v2.2.0

> **A unified atmospheric and terrestrial data orchestration framework.**

---

## 🏗️ System Architecture & Standards

The suite follows a **Producer-Consumer** model where specialized fetchers ingest raw data, and a centralized processor transforms it into long-term archives.

* **Idempotency**: All scripts utilize `mkdir -p` and existence checks to ensure the system can be restarted at any point without data loss or structural duplication.
* **Visual Indicators**: High-visibility Unicode icons (🚀, ✅, 🎬, ❌) are standardized across all bash and python logs to facilitate rapid human auditing.
* **Temporal Logic**: Video compilation targets "yesterday" via `date -d "yesterday"` to ensure a complete 24-hour dataset is captured.

---

## 🗓️ Master Cron Schedule

The schedule is staggered to prevent resource contention and ensure high-availability for real-time alerting.

### 📥 1. Data Ingestion & Alerts

| Frequency | Minute | Script | Primary Purpose |
| --- | --- | --- | --- |
| **5 min** | `*/5` | `swpc/weather_alerts.sh` | NWS Texas Alerts to MQTT |
| **10 min** | `0,10...` | `swpc/space_fetcher.sh` | Aurora & Solar Data Ingestion |
| **10 min** | `2,12...` | `goes/retrieve_goes.sh` | GOES-East/West 10-min Satellite Frames |
| **6 hours** | `15 */6` | `epic/epic_fetcher.sh` | NASA EPIC Deep Space Imagery |
| **Daily** | `04:15` | `terran/terran_watch.sh` | Collin County Land-Use Snapshots |

### 🎬 2. Video Processing (The Recap Cycle)

*Daily videos are rendered from 00:00 to 23:59 of the previous day.*

| Time (HH:MM) | Instrument | Label | Source Images Directory |
| --- | --- | --- | --- |
| **00:10** | Aurora North | `aurora_north` | `.../swpc/aurora/north/images` |
| **00:15** | Aurora South | `aurora_south` | `.../swpc/aurora/south/images` |
| **00:20** | GOES-East | `goes_east` | `.../noaa/goes-east/images` |
| **00:25** | GOES-West | `goes_west` | `.../noaa/goes-west/images` |
| **01:10** | Terran Land-Use | `terran_land_use` | `.../terran/land_use/images` |

---

## 🩺 Monitoring & Maintenance

### 🛡️ System Audit (`system_audit.py`)

The auditor acts as the primary fail-safe for the entire farm.

1. **Watchdog Mode (`5 */6 * * *`)**: Monitors `/home` disk usage (Alert at 80%) and structural integrity. Remains silent unless a failure occurs.
2. **Integrity Report (`0 1 * * * --report`)**: Runs 1-hour post-midnight. It specifically verifies the existence of the newly rendered `.mp4` files and dispatches a **Daily All-Clear** email.

### 📂 Directory Hierarchy

All data is stored relative to `/home/reza/Videos/satellite/`:

* **`/images`**: Temporary landing for raw frames (purged daily after success).
* **`/videos`**: Permanent MP4 archive storage.
* **`/logs`**: Centralized execution and error traces for the specific instrument.

---
