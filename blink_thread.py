import threading
import logging
from signal import signal, SIGINT, SIGTERM, SIGHUP, pause
import sys
import RPi.GPIO as GPIO
from time import sleep

class Blinker(threading.Thread):
    def __init__(self, kill_event, pause_flag, pin=12, sleep_time=1,
                 group=None, target=None, name=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.kill = kill_event
        self.pause = pause_flag
        self.pin = pin
        self.sleep_time = sleep_time
        GPIO.setup(pin, GPIO.OUT)
        self.state = GPIO.LOW
        return

    def flip(self):
        if self.state == GPIO.LOW:
            self.state = GPIO.HIGH
        else:
            self.state = GPIO.LOW
        logging.debug('Turning LED %s', self.state)
        GPIO.output(self.pin, self.state)

    def run(self):
        try:
            while not self.kill.isSet():
                if not self.pause.isSet():
                    self.flip()
                else:
                    logging.debug('No blink, Paused')
                self.kill.wait(timeout=self.sleep_time) # threaded sleep
        finally:
            GPIO.output(self.pin, GPIO.LOW)
            logging.debug('All Done!')

class PauseButton(threading.Thread):
    def __init__(self, pause_flag, pin=20,
                 group=None, target=None, name=None):
        self.pause_flag = pause_flag
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING,
            callback=self.button_pressed_callback, bouncetime=1000)

    def button_pressed_callback(self, channel):
        logging.debug("Button Pressed")
        if self.pause_flag.isSet():
            self.pause_flag.clear()
        else:
            self.pause_flag.set()

################################
#
# Main Thread
#
################################

kill_event = threading.Event()
pause_flag = threading.Event()

def quit(signo, _frame):
    logging.debug("Interrrupt received, shutting down")
    cleanup()
    sys.exit()

def setup():
    logging.basicConfig(
        level=logging.DEBUG,
        format='(%(threadName)-10s) %(message)s',
    )
    for sig in (SIGINT, SIGHUP, SIGTERM):
        signal(sig, quit)
    GPIO.setmode(GPIO.BCM)

def cleanup():
    kill_event.set()
    blinker.join()
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    blinker = Blinker(kill_event, pause_flag, sleep_time=2, name='Blinker')
    blinker.setDaemon(True)
    button = PauseButton(pause_flag)

    blinker.start()
    pause()