import requests
from pathlib import Path

# Test one failing URL from your log
test_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&LAYERS=VIIRS_SNPP_CorrectedReflectance_TrueColor&FORMAT=image/jpeg&HEIGHT=4096&WIDTH=4096&VERSION=1.3.0&TIME=2026-03-09&BBOX=25.8,-106.6,36.5,-93.5&CRS=EPSG:4326"

print("🔍 Inspecting NASA GIBS Response...")
r = requests.get(test_url)
if b"ServiceException" in r.content:
    print("❌ ERROR FOUND:")
    print(r.text) # This will tell us if it's "Width/Height too large" or "Invalid BBOX"
else:
    print("✅ Layer is valid at these parameters.")
