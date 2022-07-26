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
led_on = False

###### Pins ######
button_pin = 15
led_pin = 12
camera_pin = 2
poof_pin = 14

def countdown(count):
    global number_display
    global sequence_running
    cur_time = time.ticks_ms()
    start_time = cur_time
    # to help avoid infinite loop
    end_time = cur_time + (count * 1000) + 200
    countdown = None
    while cur_time < end_time:
        sequence_running = True
        tick = int(time.ticks_diff(time.ticks_ms(), start_time) / 1000)
        new_countdown = count - tick
        if new_countdown != countdown:
            countdown = new_countdown
            number_display.show(countdown)
        # logger.update('count', '%d' % countdown)
        time.sleep_ms(50)
        cur_time = time.ticks_ms()
    # logger.update('count', "~~~~~")
    animate_poof(times=1)

def animate_poof(times=3):
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
        poofer.trigger()
        # logger.update('btn', 'ready')
        sequence_running = False

def toggle_led():
    global led_on
    print("toggling LED")
    led_on = not led_on
    led.value(led_on)

def blinker():
    global sequence_running
    blink_ms = 150
    # logger.update('led', led.value())
    led.value(1)
    blinking = False
    while True:
        if sequence_running:
            always_on = True
            # logger.update('led', led.value())
            toggle_led()
            time.sleep_ms(blink_ms)
        else:
            # logger.update('led', 'wait' + '.' * dots)
            # Turn LED back on
            if blinking:
                blinking = False
                led.value(1)
            time.sleep_ms(100)

# logger = ScreenLogger(row_names=['btn', 'poof', 'count', 'led'])

number_display = Segments(offline=False)
poofer = PoofShot(camera_pin=camera_pin, poof_pin=poof_pin, poof_ms=200)
button = Button(pin=button_pin, callback=button_pressed)
led = Pin(led_pin, Pin.OUT)
start_new_thread("Blinker", blinker, ())
animate_poof(times=3)

while True:
    if(button.button.value() == 0):
        print("button pressed")
        button_pressed(button.button)
    else:
        print("sleeping")
        time.sleep_ms(100)