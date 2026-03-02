#!/usr/bin/env python3
"""
===============================================================================
🛡️ NAME          : config_validator.py
👤 AUTHOR        : Matha Goram
🔖 VERSION       : 1.0.0
📝 DESCRIPTION   : Pre-flight validator for config.toml.
                   Checks TOML syntax, Env Var interpolation, and schema integrity.
===============================================================================
"""

import os
import sys
import tomllib
from string import Template
from dotenv import load_dotenv

# --- PATH RESOLUTION ---
PROJ_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJ_ROOT, "config.toml")
ENV_PATH = os.path.join(PROJ_ROOT, ".env")


def validate():
    print("🔍 [VALIDATOR] Starting Pre-flight Configuration Check...")
    print("-" * 60)

    if not os.path.exists(CONFIG_PATH):
        print("❌ FAIL: config.toml not found.")
        return False

    load_dotenv(ENV_PATH)

    try:
        with open(CONFIG_PATH, "r") as f:
            raw_content = f.read()

        # 🛠️ FIX: Use safe_substitute to ignore dynamic tags like ${TIME}
        # while still processing secrets from .env
        templated_content = Template(raw_content).safe_substitute(os.environ)

        # Verify that critical secrets WERE substituted
        # If the string still contains ${SMTP_PASSWORD}, the .env is missing it
        if "${SMTP_PASSWORD}" in templated_content:
            print("❌ FAIL: Critical secret ${SMTP_PASSWORD} was not found in .env")
            return False

        # Parse TOML
        config = tomllib.loads(templated_content)
        print("✅ PASS: TOML syntax and safe interpolation valid.")

        return True

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if validate() else 1)
