from datetime import datetime
from PIL import Image

class ImageCombiner:
    def __init__(self, debug=False):
        # config
        self.output_folder = './images-output/'
        self.canvas_size = [1200, 1800] # w, h
        self.image_size = [900, 600] # w, h
        self.image_rotation = 'ccw' # cw | ccw (default)
        logo_image_path = './logo.jpg'
        self.logo_image = Image.open(logo_image_path)
        self.debug = debug
        # logo_path = Path(logo_image_path)
        # ## ensure the logo exists and is a valid image
        # if not logo_path.is_file():
        #     print('Error: Logo image does not exist > ' + logo_image_path)
        #     quit()
        # try:
        #     self.logo_image = Image.open(logo_image_path)
        # except:
        #     print('Error: Invalid logo > ' + logo_image_path)
        #     quit()

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

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d_%HH%M-%S")

    def combine(self, filename):
        src_image = Image.open(filename)

        ## resize the source image
        src_image = src_image.resize((self.image_size[0], self.image_size[1]))

        ## merge the logo
        src_image = self.merge(src_image, self.logo_image, "right")

        ## duplicate on a second row
        src_image = self.merge(src_image, src_image, "bottom")

        ## rotate
        if self.image_rotation == "cw":
            image_rotation = Image.Transpose.ROTATE_270
        else: # default: ccw
            image_rotation = Image.Transpose.ROTATE_90
        src_image = src_image.transpose(image_rotation)

        ## create the destination image per the canvas size
        dst_image = Image.new("RGB", (self.canvas_size[0], self.canvas_size[1]))

        ## paste onto the destination image
        dst_image.paste(src_image)

        ## save to output folder
        dst_image_path = self.output_folder + "PhotoPoof_" + self.timestamp() + '.png'
        dst_image.save(dst_image_path, "PNG")
        if self.debug: print("Saving converted file: " + dst_image_path)
        return dst_image_path
