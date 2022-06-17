import sys
import glob
import countdown
import image_viewer

class Slideshow(object):
    """Displays images in a slideshow"""

    def __init__(self, folder, duration, extension= 'JPG'):
        self.duration = duration
        self.folder = folder
        self.extension = extension
        self.files = glob.glob(folder + '*.' + extension)
        self.file_index = 0
        self.image_viewer = image_viewer.ImageViewer()
        self.reset_counter()

    def update(self):
        if self.counter.is_finished():
            self.file_index = (self.file_index + 1) % len(self.files)
            filename = self.files[-1 - self.file_index]
            self.image_viewer.display_image(filename)
            self.reset_counter()

    def reload_files(self):
        self.files = glob.glob(self.folder + '*.' + self.extension)

    def reset_counter(self):
        self.counter = countdown.Countdown(count = self.duration)

if __name__ == "__main__":
    folder = sys.argv[1]
    slideshow = Slideshow(folder= folder, duration= 1)
    while True:
        slideshow.update()
