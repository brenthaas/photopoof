#! /usr/bin/python3

from __future__ import print_function
from datetime import datetime

import os
import sys

import gphoto2 as gp

class CameraDownloader(object):
    """Watches for photos taken and downloads image"""
    def __init__(self, dir=None):
        self.dir = dir or os.path.join(os.path.expanduser("~"), "photopoof")
        print("Saving new photos to {}".format(self.dir))
        self.camera = gp.Camera()
        try:
            self.camera.init()
        except Exception as e:
            print(e)

    def mainloop(self):
        timeout = 3000  # milliseconds
        while True:
            event_type, event_data = self.camera.wait_for_event(timeout)
            if event_type == gp.GP_EVENT_FILE_ADDED:
                cam_file = self.camera.file_get(
                    event_data.folder, event_data.name, gp.GP_FILE_TYPE_NORMAL
                )
                current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                target_path = os.path.join(self.dir, "poof_{}.jpg".format(current_timestamp))
                print("New Photo! ({})".format(target_path))
                cam_file.save(target_path)
        return 0


if __name__ == "__main__":
    downloader = CameraDownloader(*sys.argv[1:])
    sys.exit(downloader.mainloop())
