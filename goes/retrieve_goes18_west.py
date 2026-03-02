#!/usr/bin/env python3
"""
    retrieve5.py retrieve NOAA GOES-EAST imagery for CONUS
    Copyright (C) 2023 ParkCircus Productions

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

    requests https://docs.python-requests.org/en/latest/user/quickstart/
    request
    r = requests.get('https://api.github.com/events')
    r = requests.post('https://httpbin.org/post', data={'key': 'value'})
    r = requests.put('https://httpbin.org/put', data={'key': 'value'})
    r = requests.head('https://httpbin.org/get')
    r = requests.options('https://httpbin.org/get')
    payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
    r = requests.get('https://httpbin.org/get', params=payload)
    response
    r.text
    r.encoding
    r.content
"""

import requests
import datetime


# from PIL import Image
# from io import BytesIO


def retrieve_image(data_url, folder):
    now = f'{datetime.datetime.now():%Y-%m-%dT%H:%M:%S%z}'
    image_file = folder + now + ".jpg"
    payload = {}
    try:
        response = requests.get(data_url, params=payload)
        if response.status_code == requests.codes.ok:
            # image = Image.open(BytesIO(response.content))
            with open(image_file, "wb") as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)
        else:
            response.raise_for_status()
        return
    except ConnectionRefusedError:
        print("Connection refused")
    except ConnectionError:
        print("Network connection issue")
    except TimeoutError:
        print("It is taking too long to get a response from the website")
    except Exception as e:
        print(e)

    return


# run only if file is launched as a script; don't run if it is imported
if __name__ == "__main__":
    #  noaa_goes_16_data = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/CONUS/GEOCOLOR/2500x1500.jpg"
    noaa_goes_18_data = "https://cdn.star.nesdis.noaa.gov/GOES18/ABI/CONUS/GEOCOLOR/2500x1500.jpg"
    download_folder = "/home/reza/Videos/satellite/noaa/goes-west/"  # goes-east for GOES16
    retrieve_image(noaa_goes_18_data, download_folder)
