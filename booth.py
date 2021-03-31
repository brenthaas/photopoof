#!/usr/bin/env python3
import photo_taker
import picamera
import slideshow
import poofer
import smart_led
import sys
import os
import time
import RPi.GPIO as GPIO

def poof_blackout():
    global poofed_at
    global poof_blackout_duration
    current_time = milli_time(time.time())
    blackout_until = poofed_at + poof_blackout_duration
    return current_time >= blackout_until

def setup_button(pin, callback):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=800)

def milli_time(time_float):
    return int(round(time_float * 1000))

def take_picture():
    GPIO.output(slr_pin, GPIO.LOW)
    time.sleep(.3)
    GPIO.output(slr_pin, GPIO.HIGH)

def setup_slr(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # turn off

def setup_camera(camera):
    # camera.rotation = 270
    camera.rotation = 90


def take_photo(pin):
    global taking_photo
    if poof_blackout():
        taking_photo = True
        button_led.blink(100)
    else:
        print('Button suppressed...')

def setup_taker(camera):
    taker = photo_taker.PhotoTaker(camera)
    taker.start_preview()
    return taker

def default_led():
    button_led.blink(200, 1000)

taking_photo = False
taker = None
camera_delay = 200
poofed_at = milli_time(time.time())
poof_blackout_duration = 500
default_dir = '/home/pi/images/photopoof/'
slr_pin = 22

# setup board
GPIO.setmode(GPIO.BCM)

try:
    # setup LEDs
    button_led = smart_led.SmartLed(18)
    button_led.setup()
    default_led()

    # setup buttons
    button_pin = 23
    setup_button(button_pin, take_photo)

    # setup poofer
    poofer_pin = 27
    poofer = poofer.Poofer(
        pin= poofer_pin,
        flame_duration_ms= 80,
        callback= take_picture,
        debug_level = 1
    )
    poofer.setup()

    # setup camera
    setup_slr(slr_pin)

    # setup slideshow
    # if len(sys.argv) > 1:
    #     directory = sys.argv[1]
    # else:
    #     directory = default_dir
    directory = default_dir

    print('Slideshow Directory: ' + directory)
    slideshow = slideshow.Slideshow(folder= directory, duration= 2);

    with picamera.PiCamera() as camera:
        setup_camera(camera)

        while True:
            poofer.update()
            button_led.update()

            if taking_photo:
                taker = taker or setup_taker(camera)
                taker.update_display()
                if taker.is_done():
                    poofer.poof()
                    poofed_at = milli_time(time.time())
                    # slideshow.update()
                    # os.system('/usr/bin/python3 /usr/local/share/python-gphoto2/examples/list-files.py')
                    # os.system('/usr/bin/python3 /home/pi/dev/photopoof/camera_downloader.py')
                    # slideshow.reload_files()
                    slideshow.reset_counter()
                    default_led()
                    taker.stop_preview()
                    taker = None
                    taking_photo = False
                    slideshow.update()
            else:
                slideshow.update()

except Exception as e:
    print(e)

finally:
    GPIO.cleanup()           # clean up GPIO on normal exit
    sys.exit()
