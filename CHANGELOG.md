# Changelog

# 0.1.0 (2026-03-14)


### Bug Fixes

* convert drift to float for comparison and add status icon ([cb4693b](https://github.com/baqwas/noaa/commit/cb4693bb083091eadb4d5f41f1000b2a5fc9159b))
* expose DRIFT_VALUE for automated README injection ([1d85313](https://github.com/baqwas/noaa/commit/1d853134f1b9d14cf443e34756340149e1803ed7))
* extra statement ([47e2918](https://github.com/baqwas/noaa/commit/47e29189a3e250e245e2ad618f32b1d3419d698a))
* update sed delimiter to handle timestamp slashes ([3f919d3](https://github.com/baqwas/noaa/commit/3f919d395f257701b20f375de13013d8b59d8038))
* use pipe delimiter in sed and finalize backup scripts ([4f0b4ab](https://github.com/baqwas/noaa/commit/4f0b4abc66876b39bc0c0f8e982b4b702403a276))
* use pipe delimiter in sed to handle slashes in stats ([d6aff33](https://github.com/baqwas/noaa/commit/d6aff335c049859e541a7e5759c989078e8cfa0c))


### Features

* **core:** implement core contract test and resilience logic ([11d09ac](https://github.com/baqwas/noaa/commit/11d09ace0004af998f49cf2147dc437b25cb8882))
* integrate security_master workflow ([7fc907f](https://github.com/baqwas/noaa/commit/7fc907f2801645e7c2eb8baa6e167f2b43c3086f))
* synchronize local and remote dashboards with status icons ([91acc6e](https://github.com/baqwas/noaa/commit/91acc6eb2c52486a5f21d69a44a40d1e4e1c36ef))
* **terran:** pivot to WMS GetMap protocol for robust BBOX ingest ([d52a7d0](https://github.com/baqwas/noaa/commit/d52a7d03abd4d362cc4384be5d2e1a590a27e1c4)), closes [hi#res](https://github.com/hi/issues/res)

# 📓 Changelog: BeUlta Satellite Suite
All notable changes to this project will be documented in this file.

## [3.0.0] - 2026-03-14
### 🚀 Added
- **Contract Auditor**: Introduced `test_core_contract.py` to validate `config.toml` structure and `.env` hydration before execution.
- **Resilience Engine**: Implemented Exponential Backoff with jitter in `retrieve_goes.py` to handle NOAA/NASA server latency.
- **Temporal Isolation**: Forced T-1 date-locking across ingest and rendering pipelines to prevent multi-day video bloat.

### 🔧 Changed
- **Renumbered Documentation**: Reorganized `README.md` to prioritize Diagnostics (Section 5) and Resilience Standards (Section 7).
- **Hard-Gate Purging**: Modified `compile_all_daily.sh` to only delete source frames if the `ffmpeg` render exit status is 0.

### 🛡️ Fixed
- **Key Resolution**: Removed incorrect `[egress]` logic from tests; aligned audit with Day 0 `[goes]` configuration.
- **Path Resolution**: Fixed environment variable interpolation check in `CoreService` to ensure absolute paths are correctly resolved.

## [2.0.0] - 2026-02-24
### 🚀 Added
- Initial Unified Infrastructure Configuration (`config.toml`).
- Migration to absolute pathing for SOHO farm stability.
