import time
from globals import SHUTDOWN_FLAG

from shapes import Shapes
from utils import pad_array
import numpy as np
import random



def generate_contrast_colors(num_colors):
    def hsl_to_rgb(h, s, l):
        if s == 0:
            return (l, l, l)

        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)
        return (int(r * 255), int(g * 255), int(b * 255))

    colors = []
    for i in range(num_colors):
        h = i / num_colors
        s = 1.0
        l = 0.5
        colors.append(hsl_to_rgb(h, s, l))

    return colors


def twinkling_stars(display, duration=3, pause=0.1, num_stars=10):
    display.uh.set_brightness(0.1)
    end_time = time.time() + duration

    while not SHUTDOWN_FLAG.is_set() and time.time() < end_time:
        frame = np.zeros((7, 17), dtype=bool)
        rows = np.random.randint(0, 7, num_stars)
        cols = np.random.randint(0, 17, num_stars)
        frame[rows, cols] = True

        display.show_image(frame, color=(255, 255, 255))  # White
        time.sleep(pause)
    display.uh.set_brightness(display.default_brightness)


def fireworks(display, pause=0.01, num_bursts=20, num_colors=4):
    height, width = 7, 17  # Dimensions of the display

    contrast_colors = generate_contrast_colors(num_colors)

    color_frame = np.zeros((height, width, 3), dtype=np.uint8)
    _num_bursts = 0
    while not SHUTDOWN_FLAG.is_set() and _num_bursts < num_bursts:
        _num_bursts += 1

        center_y = np.random.randint(0, height)
        center_x = np.random.randint(0, width)

        frame = np.zeros((height, width), dtype=bool)
        num_rings = random.randint(3,6)
        for radius in range(num_rings):
            y, x = np.ogrid[:height, :width]
            dist_sq = (y - center_y) ** 2 + (x - center_x) ** 2
            ring_mask = (dist_sq <= (radius + 1) ** 2) & (dist_sq > radius ** 2)

            if np.any(ring_mask):
                color = contrast_colors[radius % num_colors]
                color_frame[ring_mask] = color
                frame[ring_mask] = True

                display.show_image_color_each_led(frame, color=color_frame)
                time.sleep(pause)

        time.sleep(0.7**(1 + _num_bursts/10))


class Animation:
    def __init__(self, display, shapes=Shapes()):
        self.shapes = shapes
        self.display = display

    def death(self, array, pause=0.25, clear_after=True):
        padded = pad_array(array)
        _movement = 0
        while not SHUTDOWN_FLAG.is_set() and _movement < 17:  # because of display height
            padded[::2, _movement] = True
            padded[1::2, 16-_movement] = True
            self.display.show_image(padded)
            time.sleep(pause)
            _movement += 1
        if clear_after:
            self.display.clear_leds()

    def life_lost(self, life_count, long_display=0.6, short_display=0.4, display_off=0.1, blinks=4):
        """
        full to 2/3
        2/3 to 1/3
        1/3 to empty
        empty to dead?
        """
        _map = {
            3: self.shapes.heart_filled,
            2: self.shapes.heart_one_lost,
            1: self.shapes.heart_two_lost,
            0: self.shapes.heart_empty
        }
        self.display.show_image(_map[life_count+1], padding=True)
        time.sleep(long_display)
        _blinks = 0
        while not SHUTDOWN_FLAG.is_set() and _blinks < blinks:
            _blinks += 1
            self.display.show_image(_map[life_count], padding=True)
            time.sleep(short_display)
            if _blinks != blinks:
                self.display.clear_leds()
                time.sleep(display_off)

        if life_count == 0:
            self.death(_map[0])

    def winning(self):
        twinkling_stars(self.display)
        fireworks(self.display)
        self.display.clear_leds()


    def demo(self):
        self.winning()
        time.sleep(1)
        for i in [2,1,0]:
            self.life_lost(i)
            self.display.clear_leds()
            time.sleep(1)





if __name__ == "__main__":
    from globals import DISPLAY
    Animation(DISPLAY, Shapes()).demo()