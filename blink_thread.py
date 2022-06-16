import threading
import logging
from signal import signal, SIGTERM, SIGHUP, pause
import sys
import RPi.GPIO as GPIO
from time import sleep

def safe_exit(signum, frame):
    GPIO.cleanup()           # clean up GPIO on normal exit
    sys.exit()
    exit(1)

signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

GPIO.setmode(GPIO.BCM)

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class Blinker(threading.Thread):

    def __init__(self, kill_event, group=None, target=None, name=None, sleep_time=1):
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.event = kill_event
        self.sleep_time = sleep_time
        GPIO.setup(12, GPIO.OUT)
        self.state = GPIO.LOW
        return

    def flip(self):
        if self.state == GPIO.LOW:
            self.state = GPIO.HIGH
        else:
            self.state = GPIO.LOW

    def run(self):
        try:
            while not event.isSet():
                logging.debug('Turning LED %s', self.state)
                GPIO.output(12, self.state)
                event.wait(timeout=self.sleep_time)
                self.flip()
        finally:
            GPIO.output(12, GPIO.LOW)
            logging.debug('All Done!')

try:

    event = threading.Event()

    t = Blinker(event, sleep_time=5)
    t.setDaemon(True)
    t.start()
    pause()

except Exception as e:
    print(e)

finally:
    t.alive = False
    event.set()
    t.join()
    GPIO.cleanup()           # clean up GPIO on normal exit
    sys.exit()