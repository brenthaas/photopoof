import time

class Blinker(object):
    """Blinker will flip `get_current_state` between True and False with the duration(s) given"""

    ON = True
    OFF = False

    def milli_time(self, time_float):
        return int(round(time_float * 1000))

    def change_state(self, state, current_time):
        if self.debug:
            print("Changing state from {} to {} at {}".format(self.current_state, state, current_time))
        self.current_state = state
        self.last_change_time = current_time

    def __init__(self, duration, on_duration= None, start_time= time.time(), debug= False):
        self.debug = debug
        self.duration = duration
        self.on_duration = on_duration or duration
        self.last_change_time = self.milli_time(start_time)
        self.current_state = self.OFF
        if debug:
            print("Starting Blinker at {} in the {} state".format(self.last_change_time, self.current_state))

    def get_current_state(self, current_time= None):
        if current_time == None: current_time = time.time()
        current_milli_time = self.milli_time(current_time)
        delta = current_milli_time - self.last_change_time
        if self.current_state == self.ON:
            if delta >= self.on_duration:
                self.change_state(self.OFF, current_milli_time)
        else:
            if delta >= self.duration:
                self.change_state(self.ON, current_milli_time)


if __name__ == "__main__":
    blink = Blinker(1000, 100, debug=True)
    while True:
        blink.get_current_state()
