import sys, time
from pathlib import Path
from PIL import Image


# config
logo_image_path = './logo.jpg'
output_folder = './images-output/'
canvas_size = [1200, 1800] # w, h
image_size = [900, 600] # w, h
image_rotation = 'ccw' # cw | ccw (default)




# validation

## needs a source image
src_image_path = ''
#src_image_path = './example-src-image.jpg' # uncomment for testing fallback
if len(sys.argv) > 1:
  src_image_path = sys.argv[1]
if src_image_path == "":
  print('Error: No image specified')
  quit()

## ensure source image exists
path = Path(src_image_path)
if not path.is_file():
  print('Error: File does not exist > ' + src_image_path)
  quit()

## ensure it properly reads as an image object
try:
  src_image = Image.open(src_image_path)
except:
  print('Error: Invalid image > ' + src_image_path)
  quit()

## ensure the logo exists and is a valid image
path = Path(logo_image_path)
if not path.is_file():
  print('Error: Logo image does not exist > ' + logo_image_path)
  quit()
try:
  logo_image = Image.open(logo_image_path)
except:
  print('Error: Invalid logo > ' + logo_image_path)
  quit()





# functions

## merge 2 images using a positional directive
def merge(im1, im2, position="right"):

    ### if position is top or left, re-run using "right" or "bottom" with the images in the opposite order
    if position == "top" or position == "left":
      if position == "top":
        position = "bottom"
      elif position == "left":
        position = "right"  
      return merge(im2, im1, position)

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





# process

## resize the source image
src_image = src_image.resize((image_size[0], image_size[1]))

## merge the logo
src_image = merge(src_image, logo_image, "right")

## duplicate on a second row
src_image = merge(src_image, src_image, "bottom")

## rotate
if image_rotation == "cw":
  image_rotation = Image.Transpose.ROTATE_270
else: # default: ccw
  image_rotation = Image.Transpose.ROTATE_90
src_image = src_image.transpose(image_rotation)

## create the destination image per the canvas size
dst_image = Image.new("RGB", (canvas_size[0], canvas_size[1]))

## paste onto the destination image
dst_image.paste(src_image) 

## save to output folder
dst_image_path = output_folder + str(time.time()) + '.jpg' 
dst_image.save(dst_image_path, "JPEG")
print("Success: Saved image to " + dst_image_path)