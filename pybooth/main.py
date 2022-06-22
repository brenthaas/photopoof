from screen_logger import ScreenLogger
from _thread import start_new_thread, allocate_lock
from button import Button
from poof_shot import PoofShot
import time

def countdown(count):
    for count in reversed(range(1, count + 1)):
        logger.update('count', "~ %d ~"%count)
        time.sleep(1)
    logger.update('count', "~~~~~")

def button_pressed(pin):
    countdown(5)
    logger.update('btn', 'now poof')
    poofer.trigger()
    logger.update('btn', 'ready')

def poof():
    logger.update('poof', 'POOF!')

    time.sleep_us((3000 * 1000))
    logger.update('poof', 'done')

lock = allocate_lock()
lock.acquire()
logger = ScreenLogger(row_names=['btn', 'poof', 'count'])

button = Button(pin=0, callback=button_pressed)
poofer = PoofShot(logger=logger, poof_ms=200)


# start_new_thread(blinker, (500, 500, logger, 'poof'))