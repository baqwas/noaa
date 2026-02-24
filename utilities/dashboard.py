#!/usr/bin/env python3
"""
================================================================================
📦 MODULE      : dashboard.py
🚀 DESCRIPTION   : Interactive Streamlit UI for Park Circus Environmental Nodes.
                   Visualizes historical rainfall trends from MariaDB.
👤 AUTHOR        : Gemini & Matha Goram
⚖️ LICENSE       : MIT License (c) 2026 ParkCircus Productions
================================================================================
PREREQUISITES:
    - streamlit, pandas, mysql-connector-python
    - core_service.py must reside in the same directory.
    - Active MariaDB server at raspbari5.parkcircus.org.

PROCESSING WORKFLOW:
    1. Initialize CoreService to retrieve centralized TOML configurations.
    2. Establish a connection to the LAN MariaDB server (raspbari5).
    3. Query 'rainfall_records' for the most recent 90-day window.
    4. Render data using Streamlit's native charting and metric components.
================================================================================
"""

import streamlit as st
import pandas as pd
import sys
import os

# Inject the /utilities path so we can find CoreService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utilities')))

from core_service import CoreService

# Initialize Base Service
core = CoreService(config_path="../swpc/config.toml")

st.set_page_config(page_title="Park Circus Weather Node", layout="wide")
st.title(f"🚀 {core.rain_params['subject_prefix']} Environmental Dashboard")

# Database Fetch
conn = core.get_db_connection()
if conn:
    query = "SELECT record_date, value_in FROM rainfall_records ORDER BY record_date DESC LIMIT 90"
    df = pd.read_sql(query, conn)
    conn.close()

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recent Rainfall Metrics")
        st.line_chart(df.set_index('record_date'))
    with col2:
        st.subheader("Node Status")
        st.info(f"Target Station: {core.rain_params['station_id']}")
        st.success("MariaDB Connection: Active")
else:
    st.error("Could not connect to MariaDB on raspbari5.")
