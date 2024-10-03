import time

import numpy as np

from globals import DISPLAY
from utils import empty_queue
from animations import generate_contrast_colors


class Lampe:
    def __init__(self, action_queue, display=DISPLAY, num_colors=6):
        self.action_queue = action_queue
        empty_queue(self.action_queue)

        self.running = True
        self.display = display
        self.colors = generate_contrast_colors(num_colors)
        self.current_color = 0
        self.array = np.ones((self.display.h, self.display.w))

    def _move(self, by=1):
        self.display.stop()
        self.current_color = (self.current_color + by) % len(self.colors)

    def use_button_press(self, pressed):
        if pressed["combination"] == "X":
            self._move(1)
        elif pressed["combination"] == "Y":
            self._move(-1)

    def run(self):
        self.display.show_image(self.array, color=self.colors[self.current_color])
        while self.running:
            if not self.action_queue.empty():
                button_press = self.action_queue.get()
                self.use_button_press(button_press)
                self.display.show_image(self.array, color=self.colors[self.current_color])

            time.sleep(0.01)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.02)
