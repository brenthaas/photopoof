#!/usr/bin/env python3
"""Display a slideshow from a list of filenames"""

import os
import tkinter as tk

from itertools import cycle
from PIL import Image, ImageTk
from printer import Printer

class Slideshow():
    """Display a slideshow from a list of filenames"""
    def __init__(self, images, slide_interval):
        """Initialize

        images = a list of filename
        slide_interval = milliseconds to display image
        """
        # tkinter.Tk.__init__(self)
        self.root = tk.Tk()
        self.root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit(), self.destroy()))
        self.root.geometry("+0+0")
        # self.overrideredirect(True)
        self.root.attributes('-fullscreen', True)
        self.slide_interval = slide_interval

        # Setup image canvas
        self.images = None
        self.set_images(images)
        self.slide = tk.Label(self.root, image=None)
        self.slide.pack()

        # Setup Quit button
        self.frame = tk.Frame(self.root)
        self.frame.place(x=0, y=770)
        self.button = tk.Button(self.frame, text="QUIT", bg="black", fg="red", command=quit, highlightthickness = 0, bd = 0)
        self.button.pack(side=tk.BOTTOM)

    @property
    def screen_width(self):
        return self.root.winfo_screenwidth()

    @property
    def screen_height(self):
        return self.root.winfo_screenheight()

    def set_images(self, images):
         self.images = cycle(images)

    def center(self):
        """Center the slide window on the screen"""
        self.root.update_idletasks()
        size = tuple(int(_) for _ in self.root.geometry().split('+')[0].split('x'))
        x = self.screen_width / 2 - size[0] / 2
        y = self.screen_height / 2 - size[1] / 2
        self.root.geometry("+%d+%d" % (x, y))

    def use_next_image(self):
        """Setup image to be displayed"""
        self.image_name = next(self.images)
        image = Image.open(self.image_name)
        fullscreen_image = image.resize(
            (self.screen_width, self.screen_height), 
            Image.ANTIALIAS
        )
        self.image = ImageTk.PhotoImage(fullscreen_image)

    def main(self):
        """Display the images"""
        self.use_next_image()
        self.slide.config(image=self.image)
        self.root.title(self.image_name)
        self.center()
        self.root.after(self.slide_interval, self.start)

    def start(self):
        """Start method"""
        self.main()
        self.root.mainloop()


if __name__ == '__main__':
    slide_interval = 5500

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
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "~/Pictures/photopoof/"
    print("Using Path %s" % path)
    images = glob.glob("*.jpg")
    exts = ["JPG", "jpg", "bmp", "png", "gif", "jpeg"]
    images = [fn for fn in os.listdir(path) if any(fn.endswith(ext) for ext in exts)]
    filenames = ['{0}{1}'.format(path, img) for img in images]

    # start the slideshow
    slideshow = Slideshow(filenames, slide_interval)
    try:
        slideshow.start()
    except Exception as e:
        print("Exited with error: {}".format(e))
        sys.exit()
