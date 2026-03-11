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

📂 Workflow A: Standard Daily Ingest

Use Case: You want to check for the most recent data available (looking back at the last 4 days from today). This is your "set it and forget it" mode.

Command:
Bash

./terran_watch.sh

    What it does: Searches for granules starting from T-1 (yesterday).

    Expected Result: If yesterday was clear, it downloads it. If cloudy, it automatically hunts back to T-4 to find the best available image.

📂 Workflow B: The Temporal Fallback (Deep Search)

Use Case: A massive storm front has been stalled over Collin County for days. You need to "jump" over the current week of clouds to find clear historical data for the VLM.

Command:
Bash

./terran_watch.sh [NUMBER]

    Example (3-day jump): ./terran_watch.sh 3

        What it does: Shifts the search window. Instead of starting at yesterday, it starts searching from T-4 and looks back to T-7.

    Example (1-week jump): ./terran_watch.sh 7

        What it does: Looks for data from exactly one week ago.

📋 Post-Download Verification

Regardless of which variation you run, the "Next Step" for a beginner is always the same: Verify the Quality.

    Run the Auditor:
    Bash

    python3 vlm_audit/spatial_auditor.py

    Check the Results:

        Green (✅): Data is clear. Proceed to VLM Analysis.

        Yellow/Red (☁️): Too many clouds. Run Workflow B with a higher number (e.g., add +3 to your previous lookback).

💡 Summary Table for Beginners
Goal	Command	Lookback Range
Get Latest Data	./terran_watch.sh	Days 1–4
Skip Recent Storms	./terran_watch.sh 4	Days 5–8
Historical Archive	./terran_watch.sh 10	Days 11–14
