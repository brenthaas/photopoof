from datetime import datetime
from PIL import Image

class ImageCombiner:
    def __init__(self, logo='./default_logo.jpg', working_folder='/tmp/', debug=True):
        self.debug = debug
        if debug: print("Working folder for combined images: %s" % working_folder)
        self.output_folder = working_folder
        self.canvas_size = [1200, 1800] # w, h
        self.image_size = [900, 600] # w, h
        self.image_rotation = 'ccw' # cw | ccw (default)
        if debug: print("Using Logo: %s" % logo)
        self.logo_image = Image.open(logo)

    ## merge 2 images using a positional directive
    def merge(self, im1, im2, position="right"):

        ### if position is top or left, re-run using "right" or "bottom" with the images in the opposite order
        if position == "top" or position == "left":
            if position == "top":
                position = "bottom"
            elif position == "left":
                position = "right"
            return self.merge(im2, im1, position)

        if position == "bottom":
            w = max(im1.size[0], im2.size[0])
            h = im1.size[1] +  im2.size[1]
            x = 0
            y = im1.size[1]
        else: # default: right
            w = im1.size[0] + im2.size[0]
            h = max(im1.size[1], im2.size[1])
            x = im1.size[0]
            y = 0

        im = Image.new("RGB", (w, h))
        im.paste(im1)
        im.paste(im2, (x, y))
        return im
    
    def process_image(self, image):
        ## resize the image
        image = image.resize((self.image_size[0], self.image_size[1]))
        ## merge the logo to the right of the image
        image = self.merge(image, self.logo_image, "right")
        return image

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d_%HH%M-%S")

    def combine(self, filename, filename2=None):
        if self.debug: print("Combining Image: %s" % filename)
        image = self.process_image(Image.open(filename))

        # what to put of the bottom row?
        if filename2 is None:
            ## no second image. duplicate our first one.
            if self.debug: print("Repeating Image: %s" % filename)
            image2 = image    
        else:
            ## process second image
            if self.debug: print("Combining Image: %s" % filename2)
            image2 = self.process_image(Image.open(filename2))

        ## create the bottom row
        image = self.merge(image, image2, "bottom")

        ## rotate
        if self.image_rotation == "cw":
            image_rotation = Image.Transpose.ROTATE_270
        else: # default: ccw
            image_rotation = Image.Transpose.ROTATE_90
        image = image.transpose(image_rotation)

        ## create the destination image per the canvas size
        dst_image = Image.new("RGB", (self.canvas_size[0], self.canvas_size[1]))

        ## paste onto the destination image
        dst_image.paste(image)

        ## save to output folder
        dst_image_path = "%sPhotoPoof_%s.jpg" % (self.output_folder, self.timestamp())
        dst_image.save(dst_image_path, "JPEG")
        if self.debug: print("Saving combined image: " + dst_image_path)
        return dst_image_path
