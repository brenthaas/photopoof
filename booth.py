import photo_taker
import picamera
import smart_led
import sys
import RPi.GPIO as GPIO

def setup_button(pin, callback):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=800)

def take_photo(pin):
    print "Taking Photos!!!"

# setup board
GPIO.setmode(GPIO.BCM)

try:
    # setup LEDs
    button_led = smart_led.SmartLed(18)
    button_led.setup()
    button_led.blink(200)

    # setup buttons
    button_pin = 25
    setup_button(button_pin, take_photo)

    with picamera.PiCamera() as camera:
        camera.rotation = 270

        taker = photo_taker.PhotoTaker(camera)

        while True:
            button_led.update()

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    sys.exit()

GPIO.cleanup()           # clean up GPIO on normal exit
