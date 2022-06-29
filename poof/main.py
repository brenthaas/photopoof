from screen_logger import ScreenLogger
from _thread import start_new_thread, allocate_lock
from button import Button
from poof_shot import PoofShot
from machine import Pin
import time

###### Variables ######
debounce_ms = 5000
last_tick = time.ticks_ms() - debounce_ms

###### Pins ######
button_pin = 0
led_pin = 12
camera_pin = 2
poof_pin = 14

def countdown(count):
    cur_time = time.ticks_ms()
    start_time = cur_time
    # to help avoid infinite loop
    end_time = cur_time + (count * 1000) + 200
    while cur_time < end_time:
        tick = int(time.ticks_diff(time.ticks_ms(), start_time) / 1000)
        countdown = count - tick
        logger.update('count', '%d' % countdown)
        time.sleep_ms(200)
        cur_time = time.ticks_ms()
    logger.update('count', "~~~~~")

def button_pressed(pin):
    global debounce_ms
    global last_tick
    global lock
    logger.update('btn', 'pressed')
    delta = time.ticks_diff(last_tick, time.ticks_ms())
    if delta < debounce_ms:
        debounce_until = time.ticks_ms() + debounce_ms
        lock.acquire(1)
        logger.update('btn', 'wait')
        countdown(5)
        logger.update('btn', 'now poof')
        poofer.trigger()
        logger.update('btn', 'ready')
        lock.release()


def poof():
    logger.update('poof', 'POOF!')

    time.sleep_us((3000 * 1000))
    logger.update('poof', 'done')

def blinker():
    global lock
    blink_ms = 250
    led.value(1)
    logger.update('led', led.value())
    dots = 0
    while True:
        if lock.locked():
            logger.update('led', led.value())
            led.value(not led.value())
            time.sleep_ms(blink_ms)
        else:
            logger.update('led', 'wait' + '.' * dots)
            dots = (dots + 1) % 3
            led.value(1)
            time.sleep_ms(100)

lock = allocate_lock()
logger = ScreenLogger(row_names=['btn', 'poof', 'count', 'led'])

button = Button(pin=button_pin, callback=button_pressed)
poofer = PoofShot(logger=logger, camera_pin=camera_pin, poof_pin=poof_pin, poof_ms=200)
led = Pin(led_pin, Pin.OUT)
start_new_thread(blinker, ())