from _thread import start_new_thread
from button import Button
from machine import Pin
from poof_shot import PoofShot
# from screen_logger import ScreenLogger
from segments import Segments
import time

###### Variables ######
debounce_ms = 5000
last_tick = time.ticks_ms() - debounce_ms
sequence_running = False
current_count = None
led_on = False

###### Pins ######
button_pin = 15
led_pin = 12
camera_pin = 2
poof_pin = 17

def countdown(count):
    global number_display
    global sequence_running
    global current_count
    cur_time = time.ticks_ms()
    start_time = cur_time
    # to help avoid infinite loop
    end_time = cur_time + (count * 1000) + 200
    while cur_time < end_time:
        sequence_running = True
        tick = int(time.ticks_diff(time.ticks_ms(), start_time) / 1000)
        count_now = count - tick
        if count_now != current_count:
            current_count = count_now
            number_display.show(current_count)
            # logger.update('count', '%d' % countdown)
        cur_time = time.ticks_ms()
    # logger.update('count', "~~~~~")

def animate_poof(times=1):
    characters = ["'", 'o', '-', 'O']
    for _x in range(0,times):
        for char in characters:
            number_display.show(char)
            time.sleep_ms(50)
    number_display.show(" ")

def button_pressed(pin):
    global debounce_ms
    global last_tick
    global sequence_running
    # logger.update('btn', 'pressed')
    delta = time.ticks_diff(last_tick, time.ticks_ms())
    if delta < debounce_ms:
        debounce_until = time.ticks_ms() + debounce_ms
        sequence_running = True
        # logger.update('btn', 'wait')
        countdown(5)
        # logger.update('btn', 'now poof')
        start_new_thread("Animation", animate_poof, ())
        poofer.trigger()
        # logger.update('btn', 'ready')
        sequence_running = False

def toggle_led():
    global led_on
    led_on = not led_on
    led.value(led_on)

def blinker():
    global sequence_running
    global current_count
    slow_blink_ms = 150
    fast_blink_ms = 75
    # logger.update('led', led.value())
    led.value(1)
    blinking = False
    while True:
        if sequence_running:
            blinking = True
            # logger.update('led', led.value())
            toggle_led()
            if current_count <= 1:
                time.sleep_ms(fast_blink_ms)
            else:
                time.sleep_ms(slow_blink_ms)
        else:
            # logger.update('led', 'wait' + '.' * dots)
            if blinking: # Turn LED back on
                blinking = False
                led.value(1)
            time.sleep_ms(100)

# logger = ScreenLogger(row_names=['btn', 'poof', 'count', 'led'])

if __name__ == '__main__':
    number_display = Segments(offline=False)
    poofer = PoofShot(camera_pin=camera_pin, poof_pin=poof_pin, poof_ms=500)
    button = Button(pin=button_pin, callback=button_pressed)
    led = Pin(led_pin, Pin.OUT)
    start_new_thread("Blinker", blinker, ())
    animate_poof(times=3)

    while True:
        if(button.button.value() == 0):
            button_pressed(button.button)
            time.sleep_ms(1000)
        else:
            time.sleep_ms(100)