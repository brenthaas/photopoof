#! /usr/bin/python3

import sys
import time

class Blinker(object):
    """Blinker will flip `get_current_state` between True and False with the duration(s) given"""

    ON = 1
    OFF = 0

    def milli_time(self, time_float):
        return int(round(time_float * 1000))

    def change_state(self, state, current_time):
        if self.debug:
            print("Changing state from {} to {} at {}".format(self.current_state, state, current_time))
        self.current_state = state
        self.last_change_time = current_time

    def __init__(self, duration, on_duration= None, blink_count= 1,
                    start_time= time.time(), debug= False):
        self.debug = debug
        self.duration = int(duration)
        self.blink_count = int(blink_count) + 1  # add 1 to allow modulous to work
        self.blink_total = 0
        self.on_duration = int(on_duration) or duration
        self.last_change_time = self.milli_time(start_time)
        self.current_state = self.OFF
        if debug:
            print("Starting Blinker at {} in the {} state".format(self.last_change_time, self.current_state))

    def get_duration(self):
        return self.duration

    def get_current_state(self, current_time= None):
        if current_time == None: current_time = time.time()
        current_milli_time = self.milli_time(current_time)
        delta = current_milli_time - self.last_change_time
        if self.current_state == self.ON:
            if delta >= self.on_duration:
                self.change_state(self.OFF, current_milli_time)
        else:
            if delta >= self.duration:
                self.blink_total += 1
                if self.blink_total % self.blink_count == 0:
                    self.last_change_time = current_milli_time   # Skip change
                else:
                    self.change_state(self.ON, current_milli_time)

        return self.current_state


if __name__ == "__main__":
    blink = Blinker(*sys.argv[1:], debug=True)
    while True:
        blink.get_current_state()
