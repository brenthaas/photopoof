#!/usr/bin/env python3

import locale
import sys
import os
from datetime import datetime
from pathlib import Path
from camera import Camera
from combine_print import CombinePrint

def main(logo, path):
    # Setup
    locale.setlocale(locale.LC_ALL, '')
    # Init camera
    printer = CombinePrint(logo=logo)
    camera = Camera(callback=printer.print, folder=photo_path)

    try:
        while True:
            camera.wait()
        return 0
    except KeyboardInterrupt:
        print("Interrupt received... Quitting.")
        return 1

if __name__ == "__main__":
    os.system('gio mount -s gphoto') # Unmount any existing proceses holding on to the camera
    date = datetime.now().strftime("%Y-%m-%d")
    base_path = Path.home() / 'Pictures' / 'photopoof'
    photo_path = base_path / date
    default_logo = base_path / 'logo.jpg'
    sys.exit(main(default_logo, photo_path))
