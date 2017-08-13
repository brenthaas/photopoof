import photo_taker
import picamera
import slideshow
import poofer
import smart_led
import sys
import time
import RPi.GPIO as GPIO

def setup_button(pin, callback):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
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
    camera.rotation = 270

def take_photo(pin):
    global taking_photo
    taking_photo = True
    button_led.blink(100)

def setup_taker(camera):
    taker = photo_taker.PhotoTaker(camera)
    taker.start_preview()
    return taker

def default_led():
    button_led.blink(200, 1000)

# setup board
GPIO.setmode(GPIO.BCM)

taking_photo = False
taker = None
camera_delay = 20
poof_start_at = None
default_dir = '/home/pi/images/'

slr_pin = 20

try:
    # setup LEDs
    button_led = smart_led.SmartLed(18)
    button_led.setup()
    default_led()

    # setup buttons
    button_pin = 25
    setup_button(button_pin, take_photo)

    # setup poofer
    poofer_pin = 16
    poofer = poofer.Poofer(
        pin= poofer_pin,
        flame_duration_ms= 20,
        callback= take_picture
    )
    poofer.setup()

    # setup camera
    setup_slr(slr_pin)

    # setup slideshow
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = default_dir

    slideshow = slideshow.Slideshow(folder= directory, duration= 2);

    with picamera.PiCamera() as camera:
        setup_camera(camera)

        while True:
            poofer.update()
            button_led.update()

            # if poof_start_at != None:
            #     delta = milli_time(time.time()) - poof_start_at
            #     if delta > camera_delay:
            #         poof_start_at = None
            #         take_picture(slr_pin)

            if taking_photo:
                taker = taker or setup_taker(camera)
                if taker.is_done():
                    poofer.poof()
                    poof_start_at = milli_time(time.time())
                    taker.stop_preview()
                    taker = None
                    taking_photo = False
                    default_led()
                    slideshow.reset_counter()
                else:
                    taker.update_display()
            else:
                slideshow.update()


except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    sys.exit()

GPIO.cleanup()           # clean up GPIO on normal exit
