import time

import numpy as np

from globals import DISPLAY, TEXT
from animations import Animation
from utils import empty_queue


PRESETS = [
    # Glider
    [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    # R-pentomino
    [(1, 9), (1, 10), (2, 8), (2, 9), (3, 9)],
    # Lightweight spaceship
    [(1, 1), (1, 4), (2, 5), (3, 1), (3, 5), (4, 2), (4, 3), (4, 4), (4, 5)],
    # Blinker + block
    [(3, 3), (3, 4), (3, 5), (1, 8), (1, 9), (2, 8), (2, 9)],
    # Pulsar fragment (small, fits 7-high grid)
    [(1, 7), (1, 8), (1, 9), (2, 6), (2, 10), (3, 7), (3, 8), (3, 9),
     (4, 7), (4, 8), (4, 9), (5, 6), (5, 10), (6, 7), (6, 8), (6, 9)],
]


class GameOfLife:
    WIDTH = 17
    HEIGHT = 7

    SPEED_MIN = 0.1
    SPEED_MAX = 2.0
    SPEED_DEFAULT = 0.5
    SPEED_STEP = 0.1

    # Colors
    COLOR_ALIVE = (0, 255, 0)
    COLOR_CURSOR = (0, 0, 255)
    COLOR_CURSOR_ON_ALIVE = (0, 255, 255)
    COLOR_PAUSED = (255, 165, 0)

    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        empty_queue(self.action_queue)
        self.running = True
        self.display = display
        self.animation = animation(display)

        # Grid
        self.grid = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)

        # Cursor (starts at center)
        self.cursor_x = self.WIDTH // 2
        self.cursor_y = self.HEIGHT // 2

        # Simulation state
        self.sim_speed = self.SPEED_DEFAULT
        self.sim_paused = False
        self.preset_idx = 0

        # Mode: True = setting, False = game
        self.setting_mode = True

    def run(self):
        self._render_setting()
        while self.running:
            if self.setting_mode:
                self._loop_setting()
            else:
                self._loop_game()

    def _loop_setting(self):
        while self.running and self.setting_mode:
            if not self.action_queue.empty():
                bp = self.action_queue.get()
                combo = bp["combination"]
                press = bp["press_type"]

                if press == "short":
                    if combo == "X":
                        self.cursor_y = (self.cursor_y - 1) % self.HEIGHT
                    elif combo == "Y":
                        self.cursor_y = (self.cursor_y + 1) % self.HEIGHT
                    elif combo == "A":
                        self.cursor_x = (self.cursor_x - 1) % self.WIDTH
                    elif combo == "B":
                        self.cursor_x = (self.cursor_x + 1) % self.WIDTH

                if combo == "AX":
                    # Toggle cell at cursor
                    self.grid[self.cursor_y, self.cursor_x] = not self.grid[self.cursor_y, self.cursor_x]
                elif combo == "BY":
                    # Start simulation
                    self.setting_mode = False
                    self.sim_paused = False
                    empty_queue(self.action_queue)
                    break
                elif combo == "XY":
                    # Load next preset
                    self.grid[:] = False
                    for y, x in PRESETS[self.preset_idx]:
                        if 0 <= y < self.HEIGHT and 0 <= x < self.WIDTH:
                            self.grid[y, x] = True
                    self.preset_idx = (self.preset_idx + 1) % len(PRESETS)

                self._render_setting()
            time.sleep(0.1)

    def _loop_game(self):
        last_step = time.time()
        self._render_game()

        while self.running and not self.setting_mode:
            if not self.action_queue.empty():
                bp = self.action_queue.get()
                combo = bp["combination"]

                if combo == "X":
                    self.sim_speed = max(self.SPEED_MIN, self.sim_speed - self.SPEED_STEP)
                elif combo == "Y":
                    self.sim_speed = min(self.SPEED_MAX, self.sim_speed + self.SPEED_STEP)
                elif combo == "A":
                    self.sim_paused = not self.sim_paused
                    self._render_game()
                elif combo == "B":
                    self.setting_mode = True
                    empty_queue(self.action_queue)
                    self._render_setting()
                    break

            now = time.time()
            if not self.sim_paused and (now - last_step) >= self.sim_speed:
                self._step()
                last_step = now
                self._render_game()

            time.sleep(0.02)

    def _step(self):
        g = self.grid.astype(np.int8)
        neighbors = np.zeros((self.HEIGHT, self.WIDTH), dtype=np.int8)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                neighbors += np.roll(np.roll(g, dy, axis=0), dx, axis=1)
        self.grid = (self.grid & ((neighbors == 2) | (neighbors == 3))) | (~self.grid & (neighbors == 3))

    def _render_setting(self):
        display_array = self.grid.copy()
        display_array[self.cursor_y, self.cursor_x] = True

        color_array = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)
        color_array[self.grid] = self.COLOR_ALIVE

        if self.grid[self.cursor_y, self.cursor_x]:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR_ON_ALIVE
        else:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR

        self.display.show_image_color_each_led(display_array, color_array)

    def _render_game(self):
        color = self.COLOR_PAUSED if self.sim_paused else self.COLOR_ALIVE
        self.display.show_image(self.grid, color=color)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)
