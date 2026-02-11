#!/usr/bin/env python3
"""
-------------------------------------------------------------------------------
Name:           space_status.py
Description:    Quick-look dashboard for the Space Weather Archive. Displays
                image counts, archive totals, and disk health.
License:        MIT License
Copyright:      (c) 2026 ParkCircus Productions; All Rights Reserved
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
-------------------------------------------------------------------------------
"""

import os
import tomllib
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    print(f"\n{'LOCATION':<25} | {'IMGS':<6} | {'VIDS':<6}")
    print("-" * 45)

    for target in config['targets']:
        root = target['instrument_root']
        img_path = os.path.join(root, target.get('subdir', 'images'))
        vid_path = os.path.join(root, "videos")

        ic = len(os.listdir(img_path)) if os.path.exists(img_path) else 0
        vc = len(os.listdir(vid_path)) if os.path.exists(vid_path) else 0

        label = f"{os.path.basename(root)}/{target.get('subdir', 'images')}"
        print(f"{label:<25} | {ic:<6} | {vc:<6}")


if __name__ == "__main__":
    main()
