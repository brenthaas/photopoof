#!/usr/bin/env python3
"""Display a slideshow from a list of filenames"""

import os
import tkinter

from itertools import cycle
from PIL import Image, ImageTk

class Slideshow(tkinter.Tk):
    """Display a slideshow from a list of filenames"""
    def __init__(self, images, slide_interval):
        """Initialize

        images = a list of filename
        slide_interval = milliseconds to display image
        """
        tkinter.Tk.__init__(self)
        self.geometry("+0+0")
        self.slide_interval = slide_interval
        self.images = None
        self.set_images(images)
        self.slide = tkinter.Label(self)
        self.slide.pack()


    def set_images(self, images):
         self.images = cycle(images)

    def center(self):
        """Center the slide window on the screen"""
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        self.geometry("+%d+%d" % (x, y))

    def set_image(self):
        """Setup image to be displayed"""
        self.image_name = next(self.images)
        image = Image.open(self.image_name)
        fullscreen_image = image.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(fullscreen_image)

    def main(self):
        """Display the images"""
        self.set_image()
        self.slide.config(image=self.image)
        self.title(self.image_name)
        self.center()
        self.after(self.slide_interval, self.start)

    def start(self):
        """Start method"""
        self.main()
        self.mainloop()


if __name__ == "__main__":
    slide_interval = 2500

    # use a list
    #images = ["image1.jpg",
              #"image2.jpeg",
              #"/home/pi/image3.gif",
              #"/home/pi/images/image4.png",
              #"images/image5.bmp"]

    # all the specified file types in a directory
    # "." us the directory the script is in.
    # exts is the file extentions to use.  it can be any extention that pillow supports
    # http://pillow.readthedocs.io/en/3.3.x/handbook/image-file-formats.html
    import glob
    images = glob.glob("*.jpg")
    path = "/Users/brent/Pictures/PhotoPoof_BlackRock_jpgs/"
    exts = ["jpg", "bmp", "png", "gif", "jpeg"]
    images = [fn for fn in os.listdir(path) if any(fn.endswith(ext) for ext in exts)]
    # images = [path + "IMG_0487.JPG", path + "IMG_0488.JPG", path + "IMG_0489.JPG"]
    filenames = ['{0}{1}'.format(path, img) for img in images]

    # start the slideshow
    slideshow = Slideshow(filenames, slide_interval)
    slideshow.start()
