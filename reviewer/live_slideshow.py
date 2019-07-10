import glob
import os
from file_monitor import Watcher
from slideshow import Slideshow

class LiveSlideshow:
    def __init__(self, dir, display_duration=3500):
        """Cycles through photos in a directory and updates with changes"""
        self.photo_dir = dir
        self.watcher = Watcher(dir, self.add_image_and_restart, True)
        self.setup_images()
        self.slideshow = Slideshow(self.images, display_duration)

    def start(self):
        self.watcher.run()
        self.slideshow.start()

    def close(self):
        self.slideshow.destroy()
        self.watcher.finish()

    def reset_slideshow(self):
        self.slideshow.set_images(self.images)

    def add_image_and_restart(self, file_path):
        """Adds the given file to the front of the slideshow"""
        if file_path.endswith('.jpg'):
            self.images = [file_path] + self.images[0:4]
            self.reset_slideshow()

    def setup_images(self):
        """Pulls all jpgs from a directory into slideshow"""
        files = glob.glob(self.photo_dir + "*.jpg")
        files.sort(key=os.path.getmtime)
        files.reverse()
        self.images = files[0:5]



if __name__ == '__main__':
    import sys

    try:
        path = sys.argv[1] if len(sys.argv) > 1 else "/home/pi/Desktop/photopoof"
        viewer = LiveSlideshow(path)
        viewer.start()
    except Exception as ex:
        print("Closing due to exception" + ex)
        viewer.close()
