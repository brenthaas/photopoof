import glob
import os
import sys
import time

from PIL import Image
from PIL import ImageTk

import tkinter as tk

def images():
    im = []
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            im.extend(images_for(path))
    else:
        im.extend(images_for(os.getcwd()))
    return sorted(im)

def images_for(path):
    if os.path.isfile(path):
        return [path]
    i = []
    for match in glob.glob("%s/*" % path):
        if match.lower()[-4:] in ('.jpg'):
            i.append(match)
    return i

class App():
    def __init__(self):
        self.root = tk.Tk()
        self.root.pack_propagate(False)
        self.root.config(bg="black", width=500, height=500)
        self.root.attributes('-fullscreen', True)
        self._images = images()
        self._image_pos = -1

        # self.root.bind("<Enter>", self.mouse_enter_handler)
        self.root.after(100, self.show_next_image)

        # Set up image "canvas"
        self.label = tk.Label(self.root, image=None)
        self.label.configure(borderwidth=0)
        self.label.pack()

        # Set up Quit button
        self.frame = tk.Frame(self.root)
        self.frame.place(x=0, y=770)
        self.button = tk.Button(self.frame, text="QUIT", bg="black", fg="red", command=quit, highlightthickness = 0, bd = 0)
        self.button.pack(side=tk.BOTTOM)

        self.set_timer()
        self.root.mainloop()
   
    slide_show_time = 4
    last_view_time = 0
    paused = False
    image = None

    def mouse_enter_handler(self, _):
        self.pause_slideshow()

    def pause_slideshow(self):
        self.paused = not self.paused

    def set_timer(self):
        self.root.after(300, self.update_clock)

    def update_clock(self):
        if time.time() - self.last_view_time > self.slide_show_time \
           and not self.paused:
            self.show_next_image()
        self.set_timer()
        self.check_image_size()

    def show_next_image(self, e=None):
        fname = self.next_image()
        if not fname:
            return
        self.show_image(fname)

    def show_image(self, fname):
        self.original_image = Image.open(fname)
        self.image = None
        self.fit_to_box()
        self.last_view_time = time.time()

    def check_image_size(self):
        if not self.image:
            return
        self.fit_to_box()

    def fit_to_box(self):
        if self.image:
            if self.image.size[0] == self.box_width: return
            if self.image.size[1] == self.box_height: return
        width, height = self.original_image.size
        new_size = self.scaled_size(width, height, self.box_width, self.box_height)
        self.image = self.original_image.resize(new_size, Image.ANTIALIAS)
        self.label.place(x=self.box_width/2, y=self.box_height/2, anchor=tk.CENTER)
        tkimage = ImageTk.PhotoImage(self.image)
        self.label.configure(image=tkimage)
        self.label.image = tkimage

    @property
    def box_width(self):
        return self.root.winfo_width()

    @property
    def box_height(self):
        return self.root.winfo_height()

    def next_image(self):
        if not self._images: 
            return None
        self._image_pos += 1
        self._image_pos %= len(self._images)
        return self._images[self._image_pos]

    def scaled_size(self, width, height, box_width, box_height):
        source_ratio = width / float(height)
        box_ratio = box_width / float(box_height)
        if source_ratio < box_ratio:
            return int(box_height/float(height) * width), box_height
        else:
            return box_width, int(box_width/float(width) * height)

if __name__ == '__main__': app=App()