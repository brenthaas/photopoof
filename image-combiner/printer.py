import cups
import sys

''' WARNING: This script produces color artifacts. Do not use as is. Here to preserve what we tried'''

class Printer:
  def __init__(self):
    self.printer = 'HiTi-P525L'
    self.options = {
      'PageSize': 'P6x4_split',
      # 'document-format': 'application/pdf',
      'ColorModel': 'CMYK',
      'Resolution': '300dpi',
      'ColorPreference': 'Classic',
      'EnableMatte': '0',
      'number-up': '1',
      'number-of-documents': '1',
      'EnableMatte': '0',
      'ColorPreference': 'Classic'
    }
    self.connection = cups.Connection()

  def print(self, filename):
    self.connection.printFile(self.printer, filename, 'PhotoPoof!', options=self.options)

if __name__ == "__main__":
  Printer().print(sys.argv[1])
