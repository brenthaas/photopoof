#!/usr/bin/env python3

import locale
import sys
import os
from pathlib import Path
from combine_print import CombinePrint

def main(logo, path):
    # Setup
    locale.setlocale(locale.LC_ALL, '')
    # Init camera
    printer = CombinePrint(logo=logo)

    try:
        printer.print(path)
    except KeyboardInterrupt:
        print("Interrupt received... Quitting.")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: print_photo.py <photo_path>")
        sys.exit(1)

    photo_path = sys.argv[1]
    base_path = Path.home() / 'Pictures' / 'photopoof'
    default_logo = base_path / 'logo.jpg'

    sys.exit(main(default_logo, photo_path))
