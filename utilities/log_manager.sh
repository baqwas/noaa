#!/usr/bin/env bash
# -------------------------------------------------------------------------------
# ♻️ NAME          : run_log_manager.sh
# 📝 DESCRIPTION   : Standardized wrapper for the Enterprise Log Manager.
# -------------------------------------------------------------------------------

# 1. Define Absolute Paths
PROJ_ROOT="/home/reza/PycharmProjects/noaa"
PYTHON_BIN="${PROJ_ROOT}/.venv/bin/python3"
SCRIPT_PATH="${PROJ_ROOT}/utilities/log_manager.py"

# 2. Move to the script's directory so relative 'config.toml' lookups work
cd "${PROJ_ROOT}/utilities" || exit 1

# 3. Execute
echo "🚀 [$(date)] Launching BeUlta Log Maintenance..."
"$PYTHON_BIN" "$SCRIPT_PATH"