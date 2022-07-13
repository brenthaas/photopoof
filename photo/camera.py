#!/usr/bin/python3

import locale
import sys
from datetime import datetime
from pathlib import Path

import gphoto2 as gp

class Camera:
    def __init__(self, event_name=None):
        event_name = event_name or datetime.now().strftime("%Y%m%d")
        self.camera = gp.Camera()
        self.camera.init()
        self.directory = Path.home() / 'Pictures' / 'photopoof' / event_name
        if not self.directory.exists():
            Path.mkdir(self.directory, parents=True, exist_ok=True)

    def wait(self, timeout=3000):
        event_type, event_data = self.camera.wait_for_event(timeout)
        if event_type == gp.GP_EVENT_FILE_ADDED:
            self.get_photo(event_data.folder, event_data.name)

    def get_photo(self, folder, name):
        cam_file = self.camera.file_get(folder, name, gp.GP_FILE_TYPE_NORMAL)
        filename = datetime.now().strftime("poof-%Y%m%d-%H_%M_%S")
        target_path = str(self.directory / filename)
        print("Saving {} to {}".format(name, target_path))
        cam_file.save(target_path)


def main():
    locale.setlocale(locale.LC_ALL, '')
    # Init camera
    camera = Camera()
    try:
        while True:
            camera.wait()
        return 0
    except KeyboardInterrupt:
        print("Interrupt received... Quitting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
