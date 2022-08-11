#!/usr/bin/env python3

from image_combiner import ImageCombiner
from sys import argv
import os

class CombinePrint:
    def __init__(self, logo, debug=True, delete_files=True):
        self.debug = debug
        self.combiner = ImageCombiner(logo=logo)
        self.print_command = 'gimpprint '
        self.delete_files = delete_files

    def print(self, filename):
        combined_image = self.combiner.combine(filename)
        print("Printing combined file: %s" % self.print_command + combined_image)
        os.system(self.print_command + combined_image)
        if self.delete_files:
            if self.debug: print("Deleting file...")
            os.remove(combined_image)


if __name__ == "__main__":
    if len(argv) == 2:
        CombinePrint().print(argv[1])
    elif len(argv) == 3:
        CombinePrint(logo= argv[2]).print(argv[1])
    else:
        print("You must provide an image as the 1st argument")
