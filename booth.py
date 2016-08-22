import photo_taker
import picamera
import smart_led
import sys
import RPi.GPIO as GPIO

def setup_button(pin, callback):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=800)

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

try:
    # setup LEDs
    button_led = smart_led.SmartLed(18)
    button_led.setup()
    default_led()

    # setup buttons
    button_pin = 25
    setup_button(button_pin, take_photo)

    with picamera.PiCamera() as camera:
        setup_camera(camera)

        while True:
            button_led.update()

            if taking_photo:
                taker = taker or setup_taker(camera)
                if taker.is_done():
                    taker.shutdown()
                    taker = None
                    taking_photo = False
                    default_led()
                else:
                    taker.update_display()


except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    sys.exit()

GPIO.cleanup()           # clean up GPIO on normal exit
