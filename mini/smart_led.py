import blinker
import RPi.GPIO as GPIO
import time

class SmartLed(object):
    ON = GPIO.HIGH
    OFF = GPIO.LOW

    """A smart LED that allows setting of abstract states (i.e. blinking)"""
    def __init__(self, pin, default_state=ON):
        self.pin = pin
        self.current_state = default_state
        self.onoff = default_state
        self.blinker = None

    def state(self, at_time=None):
        current_time = at_time or time.time()
        if self.blinker == None:
            return self.onoff
        else:
            return self.blinker.get_current_state(current_time)

    def setup(self):
        GPIO.setup(self.pin, GPIO.OUT)
        self.change_state(self.current_state)

    def change_state(self, state):
        GPIO.output(self.pin, state)
        self.current_state = state

    def blink(self, duration, on_duration= None, blink_count= 1):
        on_duration = on_duration or duration
        self.blinker = blinker.Blinker(
                        duration=duration, on_duration=on_duration, blink_count=blink_count
                       )

    def update(self, at_time=None):
        current_time = at_time or time.time()
        value = GPIO.input(self.pin)
        if value != self.state(current_time):
            self.change_state(self.state(current_time))
