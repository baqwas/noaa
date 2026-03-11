#!/bin/bash
# ===============================================================================
# 🚀 MODULE       : gibs_fetcher.sh
# 📝 DESCRIPTION   : Wrapper to initialize environment and run gibs_fetcher.py
# ===============================================================================

# 1. Define Paths
PROJECT_ROOT="/home/reza/PycharmProjects/noaa"
UTILITIES_PATH="$HOME/noaa/utilities"

# 2. Enter Project and Activate Environment
cd "$PROJECT_ROOT" || exit
source .venv/bin/activate

# 3. Export Python Path so it can find your utility classes
export PYTHONPATH="$UTILITIES_PATH:$PROJECT_ROOT:$PYTHONPATH"

# 4. Execute the Python Script
# Passing any arguments ($@) received by the shell script to the Python script
python3 gibs/gibs_fetcher.py "$@"
