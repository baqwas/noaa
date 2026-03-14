#!/bin/bash
# ==============================================================================
# 🛰️  SCRIPT      : retrieve_goes.sh
# 🚀 DESCRIPTION : Specific T-1 Ingest Gate for GOES-East and GOES-West imagery.
#                  Calculates the target date and orchestrates the Python fetcher.
# 👤 AUTHOR      : Matha Goram
# 🔖 VERSION     : 2.1.0 (Temporal Isolation Edition)
# 📅 UPDATED     : 2026-03-14
# ==============================================================================
# 📑 VERSION HISTORY:
#     - 1.0.0: Initial build for high-cadence GOES retrieval.
#     - 2.0.0: Integrated CoreService path resolution.
#     - 2.1.0: TEMPORAL ISOLATION. Enforces T-1 date string to prevent
#              multi-day video bloat and ensure clean post-render purging.
#
# ⚙️ WORKFLOW / PROCESSING:
#     1. Runtime Sync: Validates the project root and virtual environment.
#     2. Temporal Logic: Computes YESTERDAY (T-1) in YYYYMMDD format.
#     3. Execution: Triggers retrieve_goes.py with explicit date constraints.
#     4. Verification: Logs exit status to the satellite/goes/logs directory.
#
# ⚠️ ERROR MESSAGES:
#     - [EXIT 1]: Python VENV not found or inaccessible.
#     - [EXIT 2]: retrieve_goes.py missing from the expected /goes/ directory.
#     - [EXIT 3]: Python fetcher returned non-zero status (HTTP/Network fail).
#
# 📋 PREREQUISITES:
#     - GNU Coreutils (for 'date -d' support).
#     - retrieve_goes.py must support the --date argument.
#
# 🔗 REFERENCES:
#     - NOAA STAR GOES Image Viewer (Satellite Ingest Source).
#
# ⚖️ LICENSE:
#     MIT License | Copyright (c) 2026 ParkCircus Productions
# ==============================================================================

# --- ⚙️ ENVIRONMENT & PATHING ---
PROJ="/home/reza/PycharmProjects/noaa"
VENV_PY="$PROJ/.venv/bin/python3"
LOG_DIR="/home/reza/Videos/satellite/goes/logs"
mkdir -p "$LOG_DIR"

# --- 📅 TEMPORAL ISOLATION (T-1) ---
# We compute YESTERDAY here to act as the "Hard Gate" for the cycle.
YESTERDAY=$(date -d "yesterday" +%Y%m%d)

echo "========================================================================"
echo "🛰️  GOES INGEST GATE | TARGET: $YESTERDAY"
echo "========================================================================"

# --- 🛡️ PRE-FLIGHT CHECKS ---
if [ ! -f "$VENV_PY" ]; then
    echo "🚨 [ERROR] Virtual Environment not found at $VENV_PY"
    exit 1
fi

if [ ! -f "$PROJ/goes/retrieve_goes.py" ]; then
    echo "🚨 [ERROR] Fetcher script missing at $PROJ/goes/retrieve_goes.py"
    exit 2
fi

# --- 🏃 EXECUTION ---
echo "🚀 Dispatching fetcher for GOES-East and GOES-West..."
$VENV_PY "$PROJ/goes/retrieve_goes.py" --date "$YESTERDAY"

FETCH_EXIT=$?

# --- 📊 FINALIZATION ---
if [ $FETCH_EXIT -eq 0 ]; then
    echo "✅ SUCCESS: Ingest cycle for $YESTERDAY complete."
else
    echo "❌ FAILURE: Fetcher returned error code $FETCH_EXIT."
    exit 3
fi

echo "========================================================================"
