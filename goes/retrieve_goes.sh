#!/usr/bin/env bash
# retrieve NOAA GOES color images
FOL=/home/reza/PycharmProjects/noaa
python3 ${FOL}/retrieve_goes16_east.py
python3 ${FOL}/retrieve_goes18_west.py
