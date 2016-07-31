import blinker
import sys
import time
import RPi.GPIO as GPIO

BUTTON_LED = 18     # pin of the LED on the button
BUTTON = 25         # pin of the button
working = True

def button_click(pin_clicked):
    global working
    working = not working

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_LED, GPIO.OUT)
flipper = True
led_blinker = blinker.Blinker(*sys.argv[1:])

try:
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_click, bouncetime=800)
    while 1:
        if working:
            led_state = GPIO.input(BUTTON_LED)
            if led_state != led_blinker.get_current_state():
                GPIO.output(BUTTON_LED, not led_state)
        else:
            GPIO.output(BUTTON_LED, 0)

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit
