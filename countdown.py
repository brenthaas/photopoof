import math
import sys
import time

class Countdown(object):
    """Time-based countdown"""
    def __init__(self, count=5, final_message="Done",
                    wait_count=4, wait_message="Get Ready",
                    start_time=None):
        self.count = int(count)
        self.message = final_message
        self.wait_message = wait_message
        self.wait_count = int(wait_count)
        self.start_time = start_time or time.time()
        self.end_time = self.start_time + self.count + self.wait_count

    def is_finished(self, at_time=None):
        if at_time == None: at_time = time.time()
        return int(self.end_time - at_time) < 0

    def get_count(self, at_time=None):
        if at_time == None: at_time = time.time()
        delta = int(self.end_time - at_time)
        if delta > self.count:
            return self.wait_message
        elif delta > 0:
            return str(int(math.ceil(delta)))
        else:
            return self.message

if __name__ == "__main__":
    countdown = Countdown(*sys.argv[1:])
    while True:
        curr_time = time.time()
        count = countdown.get_count(curr_time)
        print("Count is: {} (at {})".format(count, curr_time))
