#!/usr/bin/env python3

from image_combiner import ImageCombiner
from sys import argv
from os import system

class CombinePrint:
    def __init__(self, logo, debug=True):
        self.combiner = ImageCombiner(logo=logo)
        self.print_command = 'gimpprint '

    def print(self, filename):
        combined_image = self.combiner.combine(filename)
        print("Printing file: %s" % self.print_command + filename)
        system(self.print_command + filename)


if __name__ == "__main__":
    if len(argv) == 2:
        CombinePrint().print(argv[1])
    elif len(argv) == 3:
        CombinePrint(logo=argv[2]).print(argv[1])
    else:
        print("You must provide an image as the 1st argument")
