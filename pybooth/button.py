import time
from machine import Pin

class Button:
    def __init__(self, pin=0, callback=None, debounce_ms=250):
        self.pin = pin
        self.callback = callback
        self.debounce_ms = debounce_ms
        self.last_pressed_ms = 0
        button = Pin(0, Pin.IN, pull=Pin.PULL_UP)
        button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)

    def button_pressed(self, pin):
        if (time.ticks_ms() - self.last_pressed_ms) > self.debounce_ms:
            self.callback(pin)
            self.last_pressed_ms = time.ticks_ms()