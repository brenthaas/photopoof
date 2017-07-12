import time
import RPi.GPIO as GPIO

class Poofer(object):
    """Poofer encompases state and timing behavior for a flame effect"""

    ON = 0
    OFF = 1

    def milli_time(self, time_float):
        return int(round(time_float * 1000))

    def poof(self, callback= None, current_time= None):
        GPIO.output(self.pin, self.ON)
        if current_time == None: current_time = time.time()
        if self.debug: print("POOF!!! at " + current_time)
        self.poof_start_at = self.milli_time(current_time)
        self.current_state = self.ON

    def turn_off(self):
        if self.current_state != self.OFF:
            if self.debug: print("Turning OFF")
            if self.callback != None: self.callback()
            GPIO.output(self.pin, self.OFF)
            self.poof_start_at = None
            self.current_state = self.OFF
        else:
            if self.debug: print("Already OFF")

    def __init__(self, pin, callback= None, flame_duration_ms= 20, debug= False):
        self.pin = pin
        self.callback = callback
        self.debug = debug
        self.flame_duration = int(flame_duration_ms)
        self.current_state = self.OFF
        self.poof_start_at = None

    def setup(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self.OFF)  # make sure it's off

    def update(self, current_time= None):
        if self.poof_start_at == None:
            if self.debug: print("Not poofing...")
            return self.turn_off()
        if current_time == None: current_time = time.time()
        time_delta = self.milli_time(current_time) - self.poof_start_at
        if time_delta > self.flame_duration:
            if self.debug: print("Time expired - turn OFF")
            self.turn_off()
