import colorsys
import threading
import time

import numpy as np
from unicornhatmini import UnicornHATMini

from utils import text_to_image, image_to_arrays, pad_array


def get_color_cycler(cycles=10):
    if cycles == 0:
        cycles = 1

    def cycle_color():
        i = 0
        while True:
            yield [int(c * 255) for c in colorsys.hsv_to_rgb(i / (cycles - 1) % 1, 1.0, 1.0)]
            i += 1

    return cycle_color


class Display:
    def __init__(self, unicornhat_instance: UnicornHATMini, brightness=0.05):
        self.uh = unicornhat_instance
        self.default_brightness = brightness
        self.uh.set_brightness(self.default_brightness)
        self.lock = threading.Lock()
        self.w = 17
        self.h = 7
        self.cycling_text = False
        self.display_thread = None

    def set_brightness(self, value=None):
        if value is None:
            self.uh.set_brightness(self.default_brightness)
        else:
            self.uh.set_brightness(value)

    def turn_on_led(self, w, h, color):
        self.uh.set_pixel(w, h, *color)
        self.uh.show()

    def show_image(self, array, color=(255, 0, 0), padding=False):
        with self.lock:
            if padding:
                array = pad_array(array, self.w)

            self.uh.clear()
            for w in range(self.w):
                for h in range(self.h):
                    if array[h, w]:
                        self.uh.set_pixel(w, h, *color)
            self.uh.show()

    def show_image_color_each_led(self, array, color, padding=False):
        """
        Displays the image on the LED matrix with individual colors per pixel.

        Parameters:
        - array: 2D boolean numpy array where `True` means the LED is on.
        - color: 3D numpy array of shape (height, width, 3) where each element is an (R, G, B) tuple.
        """
        with self.lock:
            if padding:
                array = pad_array(array, self.w)
            self.uh.clear()

            assert array.shape == color.shape[:2], "Array and color dimensions must match."

            for w in range(self.w):
                for h in range(self.h):
                    if array[h, w]:
                        r, g, b = color[h, w]
                        self.uh.set_pixel(w, h, int(r), int(g), int(b))
            self.uh.show()

    def show_text(self, text, movement_delay=0.2, color=(255, 0, 0), color_cycles=0, cycles=1):
        self.cycling_text = True
        text_as_array = image_to_arrays(text_to_image(text))
        array_len = len(text_as_array)
        color_cycler = get_color_cycler(color_cycles)()
        if array_len == 1:
            current_cycle = 0
            while self.cycling_text and current_cycle // cycles < 1:
                if color_cycles:
                    color = next(color_cycler)
                self.show_image(text_as_array[0], color)
                time.sleep(movement_delay)
                current_cycle += 1
        else:
            increment = 0
            while self.cycling_text and (increment // (array_len - 1)) // cycles < 1:
                if color_cycles:
                    color = next(color_cycler)
                self.show_image(text_as_array[increment % array_len], color)
                time.sleep(movement_delay)
                increment += 1

        self.cycling_text = False

    def start_text_in_loop(self, *args, **kwargs):
        self.cycling_text = True

        def cycle(args, kwargs):
            self.show_text(*args, **kwargs, cycles=-1)

        self.display_thread = threading.Thread(target=cycle, args=(args, kwargs,))
        self.display_thread.daemon = True
        self.display_thread.start()

    def stop_text_in_loop(self):
        if self.cycling_text:
            self.cycling_text = False
        if self.display_thread is not None and self.display_thread.is_alive():
            self.display_thread.join()
        self.display_thread = None
        self.clear_leds()

    def update_leds(self, array=np.ones((7, 17)), incremental=False, dt_incremental=0.05, dt_func=lambda t: 0.9 ** t,
                    color=(255, 0, 255)):
        with self.lock:
            self.uh.clear()
            for w in range(self.w):
                r, g, b = color
                for h in range(self.h):
                    if array[h, w]:
                        self.uh.set_pixel(w, h, r, g, b)
                        if incremental:
                            self.uh.show()
                            time.sleep(dt_func(w + h) * dt_incremental)
            self.uh.show()

    def blink_count(self, count=20, dt_pause=0.2, dt_on=0.4, dt_func=lambda t: 0.93 ** t, color_cycles=10,
                    color=(255, 0, 255)):
        color_cycler = get_color_cycler(color_cycles)()
        for c in range(count):
            if color_cycles:
                color = next(color_cycler)
            self.update_leds(color=color)
            time.sleep(dt_func(c) * dt_on)
            self.clear_leds()
            time.sleep(dt_func(c) * dt_pause)

    def blink_time(self, _time=7, dt_pause=0.2, dt_on=0.4, dt_func=lambda t: 0.7 ** t, color_cycles=10,
                   color=(255, 0, 255)):
        time_st = time.time()
        color_cycler = get_color_cycler(color_cycles)()
        while (dt := (time.time() - time_st)) < _time:
            if color_cycles:
                color = next(color_cycler)
            self.update_leds(color=color)
            time.sleep(dt_func(dt) * dt_on)
            self.clear_leds()
            time.sleep(dt_func(dt) * dt_pause)

    def clear_leds(self):
        with self.lock:
            self.uh.clear()
            self.uh.show()

    def stop(self):
        self.uh.set_brightness(self.default_brightness)
        self.stop_text_in_loop()


if __name__ == "__main__":
    print("starting")
    uh = UnicornHATMini()
    d = Display(uh)
    # d.update_leds(incremental=True)
    # time.sleep(2)
    # d.blink_count(color_cycles=10)
    # time.sleep(2)
    # d.blink_time(color_cycles=10)
    # time.sleep(2)
    d.show_text("x", color_cycles=10, cycles=10)
    time.sleep(4)
    # d.show_text("X")
    # time.sleep(4)
    # d.show_text("ABCDEF")
    # time.sleep(4)
    # d.show_text("This is a longer text! :)",movement_delay=0.2, color_cycles=4)
    # time.sleep(4)
    # d.clear_leds()
    # print("threaded starts here")
    # st = time.time()
    # d.start_text_in_loop("Das ist auch ein ganz schöner Text!")
    # print("sleep here")
    # time.sleep(20)
    # print("stopping after", time.time()-st)
    # d.stop_text_in_loop()
    # print("Screen off for 4 seconds!")
    # time.sleep(4)
    # d.start_text_in_loop("Das ist krass!")
    # time.sleep(20)
    # d.stop_text_in_loop()
    d.clear_leds()
