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
