# 🛰️ Terran: Collin County Land Use Monitor
This project automates the ingestion and analysis of NASA MODIS satellite imagery to track environmental trends in Collin County, TX.
## 📂 Directory Architecture
* **Code Root**: `/home/reza/PycharmProjects/noaa/terran`
  * Contains Python logic, Bash wrappers, and config.toml.
* **Data Root**: `/home/reza/Videos/satellite/terran`
  * High-volume storage for raw PNGs and processed MP4 videos.
* **Logs**: `/home/reza/PycharmProjects/noaa/logs`
  * Chronological output from automated tasks.

## ⚙️ Automation Workflow (Crontab)
1. **Daily Ingest (04:15)**: `terran_watch.sh` downloads the latest NDVI and Land Cover layers.
2. **Monthly Trends (05:00, 1st of month)**: `terran_trends.sh` compiles timelapses, saves snapshots, and clears disk space.
3. **Monthly Report (05:15, 1st of month)**: `terran_report.sh` sends a manifest of new media to reza@parkcircus.org.

## 🔐 Security & SMTP
* **Credentials**: Password is obfuscated.
* **Relay**: Uses `msmtp` via a LAN SMTP server with TLS enabled.

## 📉 Layers
1. VIIRS Nighttime Lights (The "Growth" Layer)
Unlike the NDVI which shows plants, this shows **infrastructure**. For Kaufman County, you will see tiny clusters of light appear where there was previously blackness. For Harris County, you can track the "halo" effect as Houston’s light pollution expands further into rural peripheries.
2. MODIS Land Surface Temperature (The "Heat" Layer)
Urban areas (Harris County) often stay **3–10°F** warmer than surrounding rural areas. By comparing LST_Day with LST_Night, you can see which neighborhoods are "thermal batteries" that stay hot all night. This is a critical metric for urban health and electricity demand.
