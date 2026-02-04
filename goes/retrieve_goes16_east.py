#!/usr/bin/env python3
"""
retrieve_goes16_east.py
Download current weather image from NOAA GOES website
2023-12-30 v0.1 armw Initial DRAFT
Copyright (C) 2023 ParkCircus Productions
All Rights Reserved

    This program is free software: you can redistribute it and / or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
import datetime
import logging
import os
import requests  # simple HTTP library

logging.basicConfig(level=logging.INFO)  # Set default level to INFO
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(os.path.basename(__file__))  # Get logger for the current module

filename_prefix = "GOES16"  # string preparation for URL
# image_preference = "5000x3000"
# image_preference = "2500x1500"
image_preference = "latest.jpg"
image_url = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/" + image_preference
#  https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/latest.jpg

desktop_path = os.path.expanduser("/home/reza/Videos/satellite/noaa/goes-east")  # desktop path based on OS

current_datetime = datetime.datetime.now()  # get the current datetime
formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")  # 24-hour format
output_filename_prep = filename_prefix + "_" + formatted_datetime + ".jpg"
output_filename = os.path.join(desktop_path, output_filename_prep)  # Create the full path to the output image file

response = requests.get(image_url, stream=True)  # Download the image using requests

if response.status_code == 200:
    with open(output_filename, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    logger.info("Image downloaded successfully to" + output_filename)  # FYI only
else:
    logger.error("Error downloading image:" + str(response.status_code))  # problem needs investigation
