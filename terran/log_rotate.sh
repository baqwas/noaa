#!/usr/bin/env bash
# 📂 New Log Path
LOG_DIR="/home/reza/Videos/satellite/terran/logs"
DATE_STAMP=$(date +%Y-%m)

mkdir -p "$LOG_DIR"

if [ -f "${LOG_DIR}/cron_output.log" ]; then
    # Archive into a hidden .archives folder to keep the main Videos folder tidy
    mkdir -p "${LOG_DIR}/.archives"
    tar -czf "${LOG_DIR}/.archives/archive_${DATE_STAMP}.tar.gz" -C "$LOG_DIR" ./*.log

    # Reset the active logs
    truncate -s 0 "${LOG_DIR}"/*.log
    echo "✅ Logs archived to .archives and truncated."
else
    echo "⚠️ No logs found to rotate in $LOG_DIR"
fi