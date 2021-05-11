from __future__ import print_function

import os
import sys

import gphoto2 as gp


def main():
    # Init camera
    camera = gp.Camera()
    camera.init()
    timeout = 3000  # milliseconds
    while True:
        event_type, event_data = camera.wait_for_event(timeout)
        if event_type == gp.GP_EVENT_FILE_ADDED:
            cam_file = camera.file_get(
                event_data.folder, event_data.name, gp.GP_FILE_TYPE_NORMAL)
            target_path = os.path.join(os.getcwd(), event_data.name)
            print("Image is being saved to {}".format(target_path))
            cam_file.save(target_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
