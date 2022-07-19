#!/usr/bin/env python3

import time
from machine import Pin


class Segments:
    def __init__(self, bcm_gpio_clock=25, bcm_gpio_latch=33, bcm_gpio_data=27, num_displays=1, debug=False, offline=False):
        self._is_offline = offline
        self._is_debug = debug

        self._segment_clock = bcm_gpio_clock
        self._segment_latch = bcm_gpio_latch
        self._segment_data = bcm_gpio_data
        self._num_displays = num_displays
        self._num_segments = 8  # 7 + dot

        self._current_position = 0
        self._current_state = [' '] * self._num_displays
        self._all_states = []

        if not self._is_offline:
            self.seg_clock = Pin(self._segment_clock, Pin.OUT)
            self.seg_data = Pin(self._segment_data, Pin.OUT)
            self.seg_latch = Pin(self._segment_latch, Pin.OUT)

            self.seg_clock.value(0)
            self.seg_data.value(0)
            self.seg_latch.value(0)

    def shutdown(self):
        if not self._is_offline:
            self._debug('Shutting down...')

    def _debug(self, message):
        if self._is_debug:
            print(message)

    def clear(self):
        self._debug("Clearing displays")
        for i in range(self._num_segments - 1):
            self.post_character(" ")
            self.move_to_next_segment()

        while not self._current_position == 0:
            self.move_to_next_segment()
        return self._all_states

    def display_error(self, message, placeholder='-'):
        self._debug(message)
        self._show_string(placeholder * self._num_displays)

    def show(self, value, scroll_speed=0.3, pad_char=' '):
        self.clear()

        if type(value) is str:
            self._show_string(value, scroll_speed=scroll_speed, pad_char=pad_char)
        elif type(value) is int:
            self._show_string(str(value), scroll_speed=scroll_speed, pad_char=pad_char)
        elif type(value) is float:
            self._show_string(str(value), scroll_speed=scroll_speed, pad_char=pad_char)
        else:
            self._debug("Unhandled type for value {}, type is {}. Falling back to string".format(value, type(value)))
            self._show_string(str(value), scroll_speed=scroll_speed, pad_char=pad_char)

        return self._all_states

    def _show_string(self, value, scroll_speed=0.3, pad_char=' '):
        if len(value.replace('.', '').replace(',', '')) > self._num_displays:
            # Text is too wide, we'll go into scroll-mode:
            # Left-and-right-pad text so that the text scrolls from left to right, from 'outside' of the displays:
            display_value = '{padding}{text}{padding}'.format(padding=pad_char * self._num_displays, text=value)
            self._debug("String: In: '{}' Out: '{}'".format(value, display_value))

            for i in range(len(display_value) - self._num_displays + 1):
                # Adjust for punctuations, by adding more letters:
                num_punctuations = sum(display_value[i:i + self._num_displays].count(punctuation) for punctuation in ('.', ','))

                # Show one of the substrings of length that fits the displays:
                self._show_string(display_value[i:i + self._num_displays + num_punctuations])
                time.sleep(scroll_speed)

        else:
            display_value = "{text:>}".format(text=value)
            self._debug("String: In: '{}' Out: '{}'".format(value, display_value))

            if not (display_value[-1] == '.' or display_value[-1] == ','):
                for i in range(len(display_value)):
                    if display_value[i] == '.' or display_value[i] == ',':
                        continue

                    if i > 0 and (display_value[i - 1] == '.' or display_value[i - 1] == ','):
                        self.post_character(display_value[i], show_decimal=True)
                        self.move_to_next_segment()
                        i += 1
                    else:
                        self.post_character(display_value[i])
                        self.move_to_next_segment()

    @staticmethod
    def _get_next_digit(value):
        if value <= 9:
            return value, None
        else:
            digit = value % 10
            value = int(value / 10)
            return digit, value

    def move_to_next_segment(self):
        if not self._is_offline:
            self.seg_latch.value(0)
            self.seg_latch.value(1)

        self._debug("Moving to next segment, was {}".format(self._current_position))
        if self._current_position == self._num_displays - 1:
            self._current_position = 0
        else:
            self._current_position += 1

    # Given a number, or - shifts it out to the display
    def post_character(self, symbol, show_decimal=False):
        segments = bytes()
        a = 1 << 0
        b = 1 << 6
        c = 1 << 5
        d = 1 << 4
        e = 1 << 3
        f = 1 << 1
        g = 1 << 2
        dp = 1 << 7

        if symbol == 1 or symbol == "1": segments = b | c
        elif symbol == 2 or symbol == "2": segments = a | b | d | e | g
        elif symbol == 3 or symbol == "3": segments = a | b | c | d | g
        elif symbol == 4 or symbol == "4": segments = b | c | f | g
        elif symbol == 5 or symbol == "5": segments = a | c | d | f | g
        elif symbol == 6 or symbol == "6": segments = a | c | d | e | f | g
        elif symbol == 7 or symbol == "7": segments = a | b | c
        elif symbol == 8 or symbol == "8": segments = a | b | c | d | e | f | g
        elif symbol == 9 or symbol == "9": segments = a | b | c | d | f | g
        elif symbol == 0 or symbol == "0": segments = a | b | c | d | e | f
        elif symbol == "A" or symbol == "a": segments = a | b | c | e | f | g
        elif symbol == "B" or symbol == "b": segments = a | b | c | d | e | f | g
        elif symbol == 'C': segments = a | d | e | f
        elif symbol == 'c': segments = g | e | d
        elif symbol == 'D': segments = a | b | c | d | e | f
        elif symbol == 'd': segments = b | c | d | e | g
        elif symbol == "E" or symbol == "e": segments = a | d | e | f | g
        elif symbol == "F" or symbol == "f": segments = a | e | f | g
        elif symbol == "G" or symbol == "g": segments = a | c | d | e | f | g
        elif symbol == "H": segments = b | c | e | f | g
        elif symbol == "h": segments = c | e | f | g
        elif symbol == "I" or symbol == "i": segments = b | c
        elif symbol == "J" or symbol == "j": segments = b | c | d
        elif symbol == "K" or symbol == "k": segments = b | c | e | f | g
        elif symbol == "L": segments = d | e | f
        elif symbol == "l": segments = e | f
        elif symbol == "M" or symbol == "m": segments = b | c | e | f | g
        elif symbol == "N" or symbol == "n": segments = b | c | e | f | g
        elif symbol == "O": segments = a | b | f | g
        elif symbol == "o": segments = c | d | e | g
        elif symbol == "P" or symbol == "p": segments = a | b | e | f | g
        elif symbol == "Q": segments = a | b | f | g | c
        elif symbol == "q": segments = c | d | e | g | dp
        elif symbol == "R" or symbol == "r": segments = a | b | c | e | f | g
        elif symbol == "S" or symbol == "s": segments = a | c | d | f | g
        elif symbol == "T" or symbol == "t": segments = a | f | e
        elif symbol == "U" or symbol == "u": segments = b | c | d | e | f
        elif symbol == "V" or symbol == "v": segments = b | c | d | e | f
        elif symbol == "W" or symbol == "w": segments = b | c | d | e | f
        elif symbol == "X" or symbol == "x": segments = b | c | e | f | g
        elif symbol == "Y" or symbol == "y": segments = b | c | f | g
        elif symbol == "Z" or symbol == "z": segments = a | b | d | e | g
        elif symbol == "!": segments = b | c | dp
        elif symbol == "'": segments = dp
        elif symbol == ' ': segments = 0
        elif symbol == '_': segments = d
        elif symbol == '.': segments = dp
        elif symbol == ',': segments = dp
        elif symbol == '-': segments = g
        else: segments = 0

        if show_decimal:
            segments |= dp

        y = 0
        while y < self._num_segments:
            if not self._is_offline:
                self.seg_clock.value(0)
                self.seg_data.value(segments & 1 << (7 - y))
                self.seg_clock.value(1)
            y += 1

        if show_decimal:
            stored_state = symbol + '.'
        else:
            stored_state = symbol
        self._current_state[self._current_position] = stored_state
        self._all_states.append(self._current_state[-1])
        self._debug("Displaying symbol: {symbol}. Current state: {state}"
                    .format(symbol=stored_state, state=self._current_state[::-1]))
