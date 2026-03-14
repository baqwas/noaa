#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : test_core_contract.py
👤 ROLE         : Baseline Contract Protection & Environment Validator
🔖 VERSION       : 1.2.0 (Environment Hydration Edition)
📅 LAST UPDATE  : 2026-03-14
===============================================================================

📝 DESCRIPTION:
    Serves as the primary 'Safety Gate' for the BeUlta Suite. This unit test
    validates the structural integrity of core_service.py and the successful
    hydration of environment variables from the local .env file. It prevents
    'Two Steps Back' regressions by ensuring the Handshake Contract is
    satisfied before production execution.

⚙️ WORKFLOW / PROCESSING:
    1. Initialization: Locates utilities and injects into the Python PATH.
    2. Path Audit: Confirms project_root aligns with SOHO absolute paths.
    3. Structural Audit: Verifies [smtp], [goes], [swpc], and [gibs] blocks.
    4. Hydration Audit: Ensures ${VAR} placeholders are replaced by real data.
    5. Result Reporting: Returns Exit 0 for pass, Exit 1 for contract break.

🖥️ USER INTERFACE:
    - Standard Python Unittest CLI (Verbosity Level 2).
    - Forensic Indicators: 🔍 CHECK | ✅ OK | 🚨 FAIL

🛠️ PREREQUISITES:
    - Python 3.11+
    - Local .env file with valid SOHO credentials.
    - utilities/core_service.py version 1.9.8+.

⚠️ ERROR MESSAGES:
    - [FAIL] Contract Break: project_root mismatch.
    - [FAIL] Contract Break: Missing REQUIRED section [X].
    - [FAIL] Contract Break: Environment variable hydration failed.

📜 VERSION HISTORY:
    - 1.0.0: Initial release; established handshake logic.
    - 1.1.0: Correction; removed hallucinated 'egress' key, aligned with Day 0.
    - 1.2.0: Added Environment Hydration Check to detect uninitialized .env.

⚖️ LICENSE:
    MIT License | Copyright (c) 2026 ParkCircus Productions
===============================================================================
"""

import unittest
import sys
from pathlib import Path

# --- 🛠️ BEULTA PATH INJECTION ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
util_path = project_root / "utilities"

if str(util_path) not in sys.path:
    sys.path.insert(0, str(util_path))

try:
    from core_service import CoreService
except ImportError as e:
    print(f"❌ [CRITICAL] Dependency Resolution Error: Cannot find core_service.py at {util_path}")
    sys.exit(1)


class TestCoreContract(unittest.TestCase):
    """🔍 Validates the Handshake and Environment Integrity for the BeUlta Suite."""

    def setUp(self):
        """Initialize CoreService for each test case."""
        try:
            self.service = CoreService()
            self.config = self.service.get_config()
        except Exception as e:
            self.fail(f"🚨 [CRITICAL] CoreService failed to initialize: {e}")

    def test_01_project_root_integrity(self):
        """🔍 CHECK: Does project_root still point to the correct SOHO path?"""
        expected_root = "/home/reza/PycharmProjects/noaa"
        actual_root = str(self.service.project_root)
        self.assertEqual(actual_root, expected_root,
                         f"🚨 Contract Break: project_root mismatch.\nExp: {expected_root}\nAct: {actual_root}")

    def test_02_config_type_health(self):
        """🔍 CHECK: Is get_config() returning a valid, populated dictionary?"""
        self.assertIsInstance(self.config, dict, "🚨 Contract Break: config must be a dict.")
        self.assertTrue(len(self.config) > 0, "🚨 Contract Break: config.toml is empty.")

    def test_03_day_zero_top_level_keys(self):
        """🔍 CHECK: Are the foundational Day 0 keys present in config.toml?"""
        required_keys = ['smtp', 'swpc', 'gibs', 'goes', 'epic', 'landsat']
        for key in required_keys:
            with self.subTest(key=key):
                self.assertIn(key, self.config,
                              f"🚨 Contract Break: Missing REQUIRED section '{key}' in config.toml.")

    def test_04_smtp_forensic_keys(self):
        """🔍 CHECK: Does [smtp] contain the sub-keys required for reporting?"""
        smtp = self.config.get('smtp', {})
        # Checking actual Day 0 keys from Reza's configuration
        expected_keys = ['server', 'port', 'user', 'password', 'sender', 'receiver']
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, smtp, f"🚨 Contract Break: SMTP sub-key '{key}' missing.")

    def test_05_goes_path_resolution(self):
        """🔍 CHECK: Does the [goes] block have valid, absolute storage paths?"""
        goes = self.config.get('goes', {})
        self.assertIn('storage_root', goes, "🚨 Contract Break: [goes] storage_root missing.")
        path_str = str(goes.get('storage_root', ''))
        self.assertTrue(path_str.startswith('/home/reza'),
                        f"🚨 Contract Break: GOES path not resolved to absolute SOHO root: {path_str}")

    def test_06_env_hydration_integrity(self):
        """🔍 CHECK: Have ${VAR} placeholders been replaced by local .env data?"""
        smtp = self.config.get('smtp', {})
        server = str(smtp.get('server', ''))
        user = str(smtp.get('user', ''))

        # Validation Logic: If placeholders remain, hydration failed.
        # Check for the characteristic '${' prefix used in config.toml
        self.assertFalse(server.startswith('${'),
                         "🚨 Contract Break: .env hydration FAILED. '${SMTP_SERVER}' placeholder detected.")
        self.assertFalse(user.startswith('${'),
                         "🚨 Contract Break: .env hydration FAILED. '${SMTP_USER}' placeholder detected.")

        # Verify specific credentials aren't empty (Existence check only)
        self.assertTrue(len(server) > 0, "🚨 Contract Break: SMTP_SERVER variable is empty.")
        self.assertTrue(len(user) > 0, "🚨 Contract Break: SMTP_USER variable is empty.")


if __name__ == "__main__":
    print("======================================================================")
    print("🧪 BEULTA CORE CONTRACT AUDIT (v1.2.0)")
    print("======================================================================")
    unittest.main(verbosity=2)
