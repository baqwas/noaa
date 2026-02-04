# 🌌 NOAA Space Weather Archiver

A robust, automated pipeline for capturing and archiving high-cadence imagery from the NOAA Space Weather Prediction Center (SWPC). This suite allows you to build a long-term visual history of solar activity and terrestrial auroral responses.
## 🌟 Key Features 
* **Multi-Source Capture**: Automatically downloads the latest Aurora forecasts (North/South poles), Solar EUV (SUVI), and Coronagraph (LASCO/CME) imagery. 
* **Weekly Timelapses**: Automatically compiles individual frames into high-quality MP4 videos for each data category. 
* **Health Monitoring**: Integrated disk-space checks and error reporting via SMTP notifications. 
* **Self-Cleaning**: Intelligent housekeeping that archives final videos and purges thousands of raw image frames to save disk space. 
* **Real-time Dashboard**: A command-line status report to view system health and archive counts at a glance. 

## 🚀 Quick Start 
1. **Configure**: Add your SMTP credentials and local folder paths to the `config.toml` file that you need to create in your project folder. 
2. **Initialize**: Set up the provided `crontab` entries to schedule the 30-minute capture and weekly processing.
* **Monitor* : Run the dashboard at any time to see the system in action: 

```bash
python3 space_status.py
```

## 📁 System Architecture 
The solution follows a strictly organized directory structure: 
* `/data`: Organized subfolders for each instrument (Aurora, SUVI, LASCO). 
* `/data/[category]/archive`: Permanent home for compiled weekly MP4 files.
* `/logs`: Compressed historical logs for system auditing. 

## 🛠 Prerequisites 
* **Python 3.11+** 
* **FFmpeg** (for video encoding) 
* **SMTP Access** (for automated alerts)

## 📂 Directory Architecture

The system is designed to be self-organizing. Once the scripts are initiated, they will automatically build and maintain the following structure: 

```text
space_weather/
├── config.toml            # Central configuration & SMTP credentials
├── space_fetcher.py       # Ingestion script (30m interval)
├── compile_weekly.sh      # Processing script (Weekly interval)
├── space_status.py        # Dashboard script (On-demand)
│
├── logs/                  # System logs
│   ├── space_fetcher.log
│   └── weekly_conversion.log
│
└── data/                  # Root data directory
    ├── aurora/            # Specific instrument folder
    |   ├── north/
    │   │     ├── archive/ # <--- FINAL MP4 VIDEOS SAVED HERE
    │   │     │       └── aurora_north_2026-05.mp4
    │   │     ├── frame_001.jpg  # Temporary raw frames (deleted weekly)
    │   │     ├──── frame_002.jpg
    │   │     ├── frame_001.jpg  # Temporary raw frames (deleted weekly)
    │   │     └── archive/       # Compiled solar timelapses
    │   └── south/
    │         ├── archive/ # <--- FINAL MP4 VIDEOS SAVED HERE
    │         │       └── aurora_south_2026-05.mp4
    │         ├── frame_001.jpg  # Temporary raw frames (deleted weekly)
    │         ├── frame_001.jpg  # Temporary raw frames (deleted weekly)
    │         ├── frame_001.jpg  # Temporary raw frames (deleted weekly)
    │         └── archive/       # Compiled solar timelapses
    │
    ├── solar_304/         # Solar EUV folder
    │   └── archive/       # Compiled solar timelapses
    │
    └── lasco_c3/          # CME/Coronagraph folder
        └── archive/       # Compiled CME timelapses
```

#### Initialize Folders
Use the suggested command to set up the directory tree structure with discretion based on your nomenclature in your infrastructure farm:

```bash
mkdir -p logs data/{aurora/{north,south}/archive,solar_304/archive,lasco_c3/archive}
```

## 🔄 Data Lifecycle

Understanding where files go is key to managing your storage: 
1. **Incoming**: New images are saved directly into the instrument subfolder (_e.g._, `data/aurora/north/`).
2.  **Processing**: Every Sunday, `ffmpeg` scans these folders to create the `.mp4` datasets.
3. **Archiving**: The finished video is moved into the local `archive/` subfolder. 
4. **Purge**: All individual `.jpg` and `.png` files are deleted from the instrument subfolder to prepare for the new week.

## ⚖️ License

This project is licensed under the **MIT License**.
Copyright © 2026 ParkCircus Productions; All Rights Reserved.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
Disclaimer: This tool is an independent implementation and is not affiliated with or endorsed by NOAA or the US Department of Commerce. All data is sourced from public domain NOAA assets.
