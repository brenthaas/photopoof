import 'blinker'
import RPi.GPIO as GPIO

BUTTON_LED = 18     # pin of the LED on the button
BUTTON = 25         # pin of the button
working = True

def flip_pin(pin):
    flip_value = not GPIO.input(pin)
    GPIO.output(pin, flip_value)

def button_click(pin_clicked):
    working = not working

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_LED, GPIO.OUT)

flipper = True

try:
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_click, bouncetime=800)
    while 1:
        if working:
            flip_pin(BUTTON_LED)
        time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # clean up GPIO on normal exit
