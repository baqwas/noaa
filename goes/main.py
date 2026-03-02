#!/usr/bin/env python3
import datetime
import logging
import os
import argparse
import configparser
import requests
from requests.exceptions import RequestException

# Handle Python version differences for TOML parsing
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python < 3.11 (requires: pip install tomli)

def main():
    # 1. Setup Argument Parser
    parser = argparse.ArgumentParser(description="GOES Satellite Image Downloader")
    parser.add_argument(
        "--satellite",
        choices=["GOES16", "GOES18"],
        default="GOES16",
        help="Satellite to use: GOES16 (East) or GOES18 (West)"
    )
    parser.add_argument(
        "--log",
        dest="loglevel",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    args = parser.parse_args()

    # 2. Load Configuration
    config_file = "config.toml"
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found. Please create it.")
        return

    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    # 3. Setup Logging
    # Priority: Command line > Config file > Default (INFO)
    default_log = config.get('settings', {}).get('logging_level', 'INFO')
    numeric_level = getattr(logging, (args.loglevel or default_log).upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("goes_retriever")

    # 4. Dynamic Variable Assignment
    satellite = args.satellite
    filename_prefix = satellite

    # URL Logic
    url_template = config.get('network', {}).get('image_url_template', "")
    image_url = url_template.replace("{SATELLITE}", satellite)

    # Path Logic
    desktop_path = config.get('settings', {}).get('desktop_path', "/home/chowkidar/projects/noaa/goes-east")
    if satellite == "GOES18":
        desktop_path = desktop_path.replace("goes-east", "goes-west")

    # Ensure output directory exists
    os.makedirs(desktop_path, exist_ok=True)

    # 5. Generate Filename
    # Format: GOES16_2025-12-29T10_30_00.jpg
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%dT%H_%M_%S")
    output_filename = os.path.join(desktop_path, f"{filename_prefix}_{formatted_datetime}.jpg")

    # 6. HTTP Request with Error Handling
    logger.info(f"Targeting {satellite} at {image_url}")
    try:
        response = requests.get(image_url, stream=True, timeout=20)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Successfully saved: {output_filename}")

    except RequestException as e:
        logger.error(f"Network error downloading {satellite} image: {e}")
    except IOError as e:
        logger.error(f"File system error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
