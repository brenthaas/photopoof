import time
import _thread
from machine import Pin

class PoofShot:
    def __init__(self, poof_pin=14, poof_ms=1000,
                 camera_pin=2, logger=None, log_name='poof',
                 debug=False):
        self.camera = Pin(camera_pin, Pin.OUT)
        self.camera.value(1)
        self.poof = Pin(poof_pin, Pin.OUT)
        self.poof.value(1)
        self.poof_ms = poof_ms
        self.logger = logger
        self.log_name = log_name

    def log(self, message):
        if self.debug:
            self.logger.update(self.log_name, message)

    def trigger(self, duration=None):
        self.log("POOF!")
        self.poof.value(0)
        time.sleep_us(self.poof_ms * 1000)
        self.camera.value(0)
        time.sleep_ms(50)
        self.camera.value(1)
        self.log("off")
        self.poof.value(1)


