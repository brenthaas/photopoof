#!/usr/bin/env python3

from image_combiner import ImageCombiner
from sys import argv
import os

class CombinePrint:
    def __init__(self, logo='./logo.jpg', debug=True, delete_files=False):
        self.debug = debug
        self.combiner = ImageCombiner(logo=logo)
        self.print_command = 'gimpprint '
        self.delete_files = delete_files

    def print(self, filename, filename2=None):
        combined_image = self.combiner.combine(filename, filename2)
        print("Printing combined file: %s" % self.print_command + combined_image)
        os.system(self.print_command + combined_image)
        if self.delete_files:
            if self.debug: print("Deleting file...")
            os.remove(combined_image)


if __name__ == "__main__":
    number_of_arguments = len(argv)
    if number_of_arguments < 2:
        print("You must provide an image as the 1st argument")
    else:
        files_list = [argv[1]]
        constructor_params = []
        if number_of_arguments > 2:
            files_list.append(argv[2])
        if number_of_arguments > 3:
            for n in range(3, number_of_arguments):
                constructor_params.append(argv[n])
        CombinePrint(*constructor_params).print(*files_list)