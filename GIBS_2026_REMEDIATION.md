# 🛰️ GIBS 2026 Remediation & Cheat Sheet
## 📍 Current Status

The BeUlta Ingest Pipeline (v2.4.2) is confirmed functional. All pathing, MQTT handshakes, and BBOX injection logic are passing. The ERR_XML_001 failures on specific layers are due to Identifier Mismatch between the 2025 legacy strings and the 2026 Near-Real-Time (NRT) manifest.

## 🛠️ Action Items (To-be-completed)

1. [ ] **Launch Discovery UI**: Run `python3 gibs/gibs_explorer.py`.

2. [ ] **Audit NRT Heartbeats**: Search for the keywords below and verify the "End Date" is current (March 2026).

3. [ ] **Update** `config.toml`: Replace the `url` identifiers with the verified strings.

### 🔍 Search Keywords & Suspected Identifiers

Layer Goal | Explorer Keyword | Suspected 2026 Identifier
--- | --- | ---
**Precipitation** | GMI | GMI_Precipitation_Rate_Asc_v8_NRT
**Aerosols** | Aerosol | MODIS_Terra_Aerosol_Optical_Depth_Land_Ocean
**Total Water** | Precipitable | AMSR2_Total_Precipitable_Water_Day
**Soil Moisture** | Soil | SMAP_L3_Soil_Moisture_Active_Passive_Daily
**Carbon Monoxide | Monoxide | AIRS_L2_Carbon_Monoxide_Total_Column_Day

## 📐 Global Constraints

The following Texas BBOX is active and verified for the 2026-03-10 epoch:

* **BBOX**: `25.8,-106.6,36.5,-93.5` (Lat/Lon order)

* **WMS Endpoint**: `https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi`

## 📝 Developer Notes

* **Lookback Logic*: If data is consistently missing, increase `lookback_days` in the `[gibs]` section of `config.toml` to `7` or `10`.

* **Integrity: Always run `gibs/image_inspector.py` after a fix to ensure NASA isn't serving "Service Exception" XMLs disguised as JPEGs.
