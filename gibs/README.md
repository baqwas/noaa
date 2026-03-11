# 🛰️ 2026 NASA GIBS Transition Notes

As of March 2026, this suite has migrated from the WMTS (Static Tile) protocol to the WMS (Web Map Service) protocol to accommodate the higher cadence and shifting identifiers of Near-Real-Time (NRT) satellite data.
## 🔄 Key Architectural Changes

* **Protocol Shift**: Moved to WMS to utilize `BBOX` (Bounding Box) cropping. This offloads the projection and cropping logic to NASA's servers, significantly reducing CPU overhead on SOHO single-board computers.

* **Parametric Lookback**: Implemented a dynamic `lookback_days` variable in `config.toml`. The ingest engine now performs a "Deep Search" (T-1 through T-n) to account for processing latency in 2026 sensor streams.

* **Centralized Geospatial Control**: All layers now reference a single texas_bbox string in the configuration, ensuring spatial alignment across the entire instrument cluster.

## ⚠️ Current Data State (March 2026)

Users may encounter `ERR_XML_001` (NASA XML Exception) for specific layers such as **Precipitation** or **Soil Moisture**. This is typically not a code failure, but a **Metadata Mismatch**.

To Resolve:

1. Run `python3 gibs/gibs_explorer.py` to identify the current "Live" identifier for the year 2026.

2. Update the `LAYERS=` parameter in `config.toml` with the new NRT string (e.g., switching from legacy v7 to `v8_NRT`).

## 🛠️ Maintenance & Integrity

Post-ingest integrity is managed by image_inspector.py. If NASA returns an error message instead of an image, the inspector will flag the file as a "Service Exception" and prevent it from polluting the Video/Dashboard generation pipeline.
