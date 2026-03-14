import requests

def debug_usgs_connection():
    # TEST 1: Simple GET to see if the WAF blocks your IP
    url_base = "https://m2m.cr.usgs.gov/api/api/json/v1.5/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("--- TEST 1: WAF Connectivity ---")
    try:
        r1 = requests.get("https://m2m.cr.usgs.gov/", headers=headers, timeout=10)
        print(f"🌍 Root Access: {r1.status_code}")
    except Exception as e:
        print(f"❌ Root Access Failed: {e}")

    print("\n--- TEST 2: API Protocol Test ---")
    # Sending an empty POST to see if we get a JSON error (Good) or HTML 403 (Bad)
    try:
        r2 = requests.post(url_base + "scene-search", headers=headers, json={}, timeout=10)
        print(f"📡 API Response Code: {r2.status_code}")
        print(f"📄 Content Type: {r2.headers.get('Content-Type')}")
        # If this is 'text/html', the WAF is blocking you.
        # If this is 'application/json', the API is reachable.
    except Exception as e:
        print(f"❌ API Test Failed: {e}")

if __name__ == "__main__":
    debug_usgs_connection()
