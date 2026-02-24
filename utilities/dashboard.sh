#!/usr/bin/env bash
# Script to launch the Streamlit UI on Node 22
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../.venv/bin/activate"

echo "📡 Launching Environmental Dashboard..."
streamlit run "$SCRIPT_DIR/dashboard.py" --server.port 8501 --server.address 0.0.0.0