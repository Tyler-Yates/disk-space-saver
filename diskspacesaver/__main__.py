import json
import os
import shutil

import requests

from .drive import Drive
from .mongo_util import MongoUtil

STARTING_DRIVE_LETTER = 'H'


def get_drives_info() -> list[Drive]:
    drives = []

    # Get a list of all possible drive letters
    for drive_letter in range(ord(STARTING_DRIVE_LETTER), ord('Z') + 1):
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
    with open("config.json", mode="r") as config_file:
        config = json.load(config_file)
    healthcheck_url = config["healthcheck_url"]

    mongo_util = MongoUtil(config)

    drives = get_drives_info()
    for drive in drives:
        print(drive)

    mongo_util.save_drive_info(drives)

    response = requests.get(healthcheck_url)
    print(f"Healthcheck response: HTTP {response.status_code} - {response.text}")


if __name__ == "__main__":
    main()
