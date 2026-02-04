🚀 Space Weather Archive Wiki

Welcome to the internal documentation for the NOAA Image Capture and Processing Suite. This system automates the acquisition of Aurora, Solar EUV, and CME imagery, generating weekly timelapse archives.
📋 System Overview

The system consists of three primary components:

    Ingestion (space_fetcher.py): A Python script running every 30 minutes to capture data and check disk health.

    Processing (compile_weekly.sh): A Bash script running weekly to encode MP4s and purge raw frames.

    Configuration (config.toml): The central "brain" containing API endpoints, local paths, and SMTP credentials.

🛠 Installation & Setup
1. Prerequisites

Ensure the following tools are installed on the host machine:

    Python 3.11+: For TOML parsing and image retrieval.

    FFmpeg: For video encoding.

    Requests library: pip install requests

    Mail Utilities: mailx or sendmail (for bash error reporting).

2. Directory Structure

The scripts expect a structured environment. Create the base directories:
Bash

mkdir -p ~/space_weather/{logs,data}

3. Permissions

The Bash script must be executable to run under the cron scheduler:
Bash

chmod +x /path/to/compile_weekly.sh

⚙️ Housekeeping & Management
Managing Storage

The system includes a 2.0 GB fail-safe. If disk space falls below this, downloads stop and an alert is sent.

    To clear space: Navigate to your data/ folder. You can delete older .mp4 files in the archive/ subfolders without affecting the script logic.

    Manual Purge: If the bash script fails to run, raw images will accumulate. You can manually trigger a cleanup by running:
    Bash

    find ~/space_weather/data -name "*.jpg" -delete

Monitoring Logs

If you stop receiving emails but notice gaps in your archive, check the logs:

    Python Log: tail -f logs/space_fetcher.log (Check for 404 errors or SMTP failures).

    Bash Log: tail -f logs/weekly_conversion.log (Check for FFmpeg encoding errors).

📡 Adding New Data Sources

To track a new NOAA instrument:

    Find the Static Image URL on the NOAA SWPC website.

    Open config.toml.

    Add a new [[targets]] block:
    Ini, TOML

    [[targets]]
    name = "new_instrument"
    url = "https://services.swpc.noaa.gov/images/..."
    dir = "/path/to/data/new_instrument"

    The system will automatically create the folder and begin capturing on the next 30-minute cycle.

📜 License & Legal

This project is licensed under the MIT License. All data retrieved is sourced from NOAA/SWPC and is in the public domain. When using these images for publication, please credit: "Image courtesy of NOAA/Space Weather Prediction Center".

## Troubleshooting Guide
When an error occurs, the system will attempt to send an email notification. If the notification fails or the data is missing, use the table below to identify the culprit.

### Error Diagnosis Matrix 

Component,Symptom,Possible Cause,Solution
SMTP,ConnectionRefusedError,LAN SMTP server is down or port 587 is blocked.,Verify server status; check firewall rules for internal traffic.
SMTP,SMTPAuthenticationError,Credentials in config.toml are incorrect or expired.,Update user and password in config.toml.
Python,Low Disk Space Warning,Partition has less than 2GB free.,Delete old MP4 archives or increase disk quota.
Python,404 Client Error,NOAA has changed the static URL or the satellite is offline.,"Check the URL in a browser; if it's broken, find the new endpoint on SWPC."
FFmpeg,Pattern not found,The directory contains no .jpg or .png files to process.,Ensure space_fetcher.py is actually saving files to the correct path.
FFmpeg,Dimensions not divisible by 2,"Image resolution changed, breaking H.264 constraints.","The script uses a scale filter to fix this, but ensure ffmpeg is up to date."
Cron,Script doesn't run,Relative paths used or incorrect permissions.,Ensure crontab uses absolute paths and chmod +x was applied to .sh.

Common FFmpeg Exit Codes

If you see these specific exit codes in weekly_conversion.log, here is what they generally mean:

    Exit Code 1: General error. Usually a syntax error in the command or a missing dependency.

    Exit Code 127: Command not found. This means ffmpeg is not in the system's PATH. Use the absolute path /usr/bin/ffmpeg in the script.

    Exit Code 137: Out of Memory. The system killed the process because it ran out of RAM while encoding. Try reducing the number of target folders processed at once.

Verification Commands

You can run these manually to verify the environment is healthy:

#### Test Python Dependencies: 

```bash
python3 -c "import requests, tomllib; print('Environment OK')"
```

#### SMTP Connectivity

```bash
telnet your.smtp.server 587
```

#### Test FFmpeg Version: 

```bash
ffmpeg -version
```

## Logrotate Configuration

Create a new file at `/etc/logrotate.d/space-weather` with elevated privileges.

```bash
/path/to/logs/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 0640 youruser yourgroup
}
```

### Key Directives

* `weekly`: Rotates the logs every 7 days.

* `rotate 4`: Keeps four weeks of backlogs. After a month, the oldest log is deleted.

* `compress`: Zips old logs (as .gz) to save massive amounts of space.

* `missingok`: If a log file hasn't been created yet (e.g., no errors occurred), don't throw an error.

* `notifempty`: Don't rotate the log if it's 0 bytes.

* `create 0640`: Creates a fresh, empty log file after rotation with secure permissions.

## Log Management 

The system uses `logrotate` to prevent log files from bloating. 

* **Active logs**: `space_fetcher.log` and `weekly_conversion.log`.

* **Archived logs**: Files named `*.log.1.gz` are compressed historical logs.

* **Manual Trigger**: To force a rotation immediately (for testing), run:

```bash
logrotate -f /etc/logrotate.d/space-weather
```
### System Status Checks

Users can run the dashboard manually to ensure images are being collected and weekly videos are being generated.

* **Command**: `python3 space_status.py`
* **What to look for**: 
  * **Images**: This count should grow daily (approx +48 per day). If it exceeds 400-500, it indicates the `compile_weekly.sh` script has not run successfully.
  * **Archived Videos**: This should increment by 1 every Sunday.
  * **Storage**: If this turns Red, manual intervention is required to delete old archives or expand disk space.

### File Manifest

Your project folder should now look like this: 

File,Role
`config.toml`,Central settings and credentials.
`space_fetcher.py`,"The ""Inhibitor"" (Downloads data, checks disk)."
`compile_weekly.sh`,"The ""Processor"" (Encodes MP4s, cleans folders)."
`space_status.py`,"The ""Dashboard"" (Visual status report)."
`README.md`,Documentation and troubleshooting.




## Final System Architecture 

With log rotation in place, your system is now a fully self-sustaining loop. 

Task,Frequency,Tool,Purpose
Ingestion,30 Mins,Python / Cron,Fetch data & Check Disk
Processing,Weekly,Bash / Cron,Create MP4 & Purge Frames
Maintenance,Weekly,Logrotate,Compress & Rotate Logs

