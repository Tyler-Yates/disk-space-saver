import json
import os
import platform
import shutil
import sys

import requests

from .drive import Drive
from .mongo_util import MongoUtil


def get_drives_info(starting_drive_letter: str) -> list[Drive]:
    if len(starting_drive_letter) != 1:
        raise ValueError(f"Only a single letter should be provided for 'starting_drive_letter',"
                         f" but {starting_drive_letter!r} was found instead.")

    starting_drive_letter = starting_drive_letter.upper()

    drives = []

    # Get a list of all possible drive letters
    for drive_letter in range(ord(starting_drive_letter), ord('Z') + 1):
        drive = f"{chr(drive_letter)}:\\"
        if not os.path.exists(drive):
            continue

        try:
            total, used, free = shutil.disk_usage(drive)
            drive = Drive(drive_letter=chr(drive_letter), capacity_bytes=total, free_bytes=free, used_bytes=used)
            drives.append(drive)
        except Exception as e:
            print(f"Error retrieving info for {drive}: {e}")

    return drives

def main():
    # This code only works on Windows
    if platform.system() != "Windows":
        sys.exit(1)

    with open("config.json", mode="r") as config_file:
        config = json.load(config_file)

    starting_drive_letter = config["starting_drive_letter"]
    healthcheck_url = config["healthcheck_url"]

    mongo_util = MongoUtil(config)

    drives = get_drives_info(starting_drive_letter)
    print(f"Found {len(drives)} drive(s):")
    for drive in drives:
        print(drive)

    if drives:
        mongo_util.save_drive_info(drives)
        response = requests.get(healthcheck_url)
        print(f"Healthcheck response: HTTP {response.status_code} - {response.text}")


if __name__ == "__main__":
    main()
