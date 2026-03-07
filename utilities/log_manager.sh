#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# 🧹 NAME          : log_manager.sh
# 🚀 DESCRIPTION   : Automated maintenance for BeUlta Suite logs and archives.
#                   Includes 7-day retention policy and storage audit.
# 👤 AUTHOR        : Matha Goram
# 📅 UPDATED       : 2026-03-07
# ⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
# -----------------------------------------------------------------------------

SATELLITE_ROOT="/home/reza/Videos/satellite"
SYSTEM_AUDIT_LOG="${SATELLITE_ROOT}/logs/system_audit.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[${TIMESTAMP}] Starting Universal Maintenance Cycle..."

# 1. --- 🛰️ IMAGE ARCHIVE CLEANUP (7-Day Retention) ---
# Calculates space before and after to log reclaimed storage.
if [ -d "$SATELLITE_ROOT" ]; then
    PRE_CLEAN=$(du -sh "$SATELLITE_ROOT" | cut -f1)

    echo "Purging imagery archives older than 7 days..."
    # Explicitly targets the /archive/YYYY-MM-DD structure
    find "$SATELLITE_ROOT" -type d -path "*/archive/*" -mtime +7 -exec rm -rf {} +

    POST_CLEAN=$(du -sh "$SATELLITE_ROOT" | cut -f1)
    echo "[${TIMESTAMP}] [MAINTENANCE] Cleanup complete. Storage: ${PRE_CLEAN} -> ${POST_CLEAN}" >> "$SYSTEM_AUDIT_LOG"
fi

# 2. --- 📝 LOG ROTATION & TRUNCATION ---
# Truncates large logs to 0 to prevent disk-fill while keeping the file descriptor.
find "$SATELLITE_ROOT" -name "*.log" -type f -size +10M -exec truncate -s 0 {} +

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Maintenance Complete."
