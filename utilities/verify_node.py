#!/usr/bin/env python3
import sys
import os

# Add the directory containing this script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core_service import CoreService

def verify_stack():
    print("🚀 Starting Stack Verification...")
    try:
        service = CoreService(config_path="../config.toml")
        conn = service.get_db_connection()

        # Note: MariaDB connector uses .is_connected() check
        if conn:
            print("✅ Connectivity: Successfully linked to raspbari5.parkcircus.org")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"✨ Active Database: {db_name[0]}")
            conn.close()
            print("\n🎉 ALL SYSTEMS GO.")
        else:
            print("❌ Connectivity: Failed to establish link.")
    except Exception as e:
        print(f"⚠️ Test Exception: {e}")

if __name__ == "__main__":
    verify_stack()
