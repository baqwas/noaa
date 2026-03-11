import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

# Use tomllib (Python 3.11+) or tomli for parsing
try:
    import tomllib
except ImportError:
    import tomli as tomllib


def validate_beulta_bbox():
    # Path resolution based on your directory structure
    config_path = Path(__file__).resolve().parent.parent / "config.toml"

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)

        # Extract BBOX from [gibs] section
        bbox_string = config.get('gibs', {}).get('bbox')
        if not bbox_string:
            print("❌ Error: 'bbox' not found in [gibs] section of config.toml")
            return

        # Parsing the Longitude/Latitude (X,Y) order
        # Based on your config: -106.6, 25.8, -93.5, 36.5
        min_lon, min_lat, max_lon, max_lat = map(float, bbox_string.split(','))

    except Exception as e:
        print(f"❌ Failed to read config.toml: {e}")
        return

    # Visualization Setup
    fig = plt.figure(figsize=(12, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linewidth=0.5)

    # Define Polygon
    lons = [min_lon, max_lon, max_lon, min_lon, min_lon]
    lats = [min_lat, min_lat, max_lat, max_lat, min_lat]

    # Plot BBOX
    ax.plot(lons, lats, color='red', linewidth=3, marker='o', transform=ccrs.PlateCarree())
    ax.fill(lons, lats, color='red', alpha=0.3, transform=ccrs.PlateCarree())

    plt.title(f"BeUlta Infrastructure Verification\nSource: {config_path}\nBBOX: {bbox_string}")

    # Zoomed Inset
    ax_ins = fig.add_axes([0.7, 0.15, 0.2, 0.2], projection=ccrs.PlateCarree())
    ax_ins.set_extent([min_lon - 5, max_lon + 5, min_lat - 5, max_lat + 5])
    ax_ins.stock_img()
    ax_ins.add_feature(cfeature.COASTLINE)
    ax_ins.add_feature(cfeature.STATES)
    ax_ins.plot(lons, lats, color='red', linewidth=2, transform=ccrs.PlateCarree())

    plt.show()


if __name__ == "__main__":
    validate_beulta_bbox()
