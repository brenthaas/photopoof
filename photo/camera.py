#!/usr/bin/python3

import locale
import sys
from datetime import datetime
from pathlib import Path

import gphoto2 as gp

class Camera:
    def __init__(self, callback=None, event_name=None, folder=None, debug=False):
        event_name = event_name or datetime.now().strftime("%Y%m%d")
        self.debug = debug
        self.camera = gp.Camera()
        self.camera.init()
        self.callback = callback
        self.folder = folder or Path.home() / 'Pictures' / 'photopoof' / event_name
        if not self.folder.exists():
            Path.mkdir(self.folder, parents=True, exist_ok=True)

    def wait(self, timeout=3000):
        event_type, event_data = self.camera.wait_for_event(timeout)
        if event_type == gp.GP_EVENT_FILE_ADDED:
            if self.debug: print("Photo Taken!!")
            self.get_photo(event_data.folder, event_data.name)

    def get_photo(self, folder, name):
        cam_file = self.camera.file_get(folder, name, gp.GP_FILE_TYPE_NORMAL)
        filename = datetime.now().strftime("PhotoPoof_%Y-%m-%d-%H_%M_%S")
        target_path = str(self.folder / filename)
        if self.debug: print("Saving new photo ({} -> {})".format(name, target_path))
        cam_file.save(target_path)
        if self.callback: self.callback(target_path)


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
