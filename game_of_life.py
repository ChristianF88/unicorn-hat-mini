import time

import numpy as np

from globals import DISPLAY, TEXT
from animations import Animation
from utils import empty_queue


PRESETS = [
    # Glider
    [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    # R-pentomino
    [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    # Lightweight spaceship
    [(0, 0), (0, 3), (1, 4), (2, 0), (2, 4), (3, 1), (3, 2), (3, 3), (3, 4)],
    # Blinker
    [(0, 0), (0, 1), (0, 2)],
    # Block
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    # Pulsar fragment
    [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 1), (2, 2), (2, 3),
     (3, 1), (3, 2), (3, 3), (4, 0), (4, 4), (5, 1), (5, 2), (5, 3)],
]


class GameOfLife:
    WIDTH = 17
    HEIGHT = 7

    SPEED_MIN = 0.1
    SPEED_MAX = 2.0
    SPEED_DEFAULT = 0.5
    SPEED_STEP = 0.1

    RANDOM_DENSITY = 0.30

    COLOR_ALIVE = (0, 255, 0)
    COLOR_CURSOR = (0, 0, 255)
    COLOR_CURSOR_ON_ALIVE = (0, 255, 255)
    COLOR_PAUSED = (255, 165, 0)
    COLOR_PREVIEW = (255, 255, 0)
    COLOR_PREVIEW_ON_ALIVE = (255, 100, 0)
    COLOR_CURSOR_ON_PREVIEW = (255, 0, 255)
    COLOR_BANNER = (0, 200, 255)

    DROP_MODES = ("or", "xor", "replace")

    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        empty_queue(self.action_queue)
        self.running = True
        self.display = display
        self.animation = animation(display)

        self.grid = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)

        self.cursor_x = self.WIDTH // 2
        self.cursor_y = self.HEIGHT // 2

        self.sim_speed = self.SPEED_DEFAULT
        self.sim_paused = False
        self.preset_idx = 0
        self.drop_mode_idx = 0

        # Modes: edit (default), picker, sim
        self.edit_mode = True
        self.picker_mode = False

    def run(self):
        self._render_edit()
        while self.running:
            if self.picker_mode:
                self._loop_picker()
            elif self.edit_mode:
                self._loop_edit()
            else:
                self._loop_sim()

    # ---------- EDIT ----------

    def _loop_edit(self):
        while self.running and self.edit_mode and not self.picker_mode:
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
                    elif combo == "AX":
                        self.grid[self.cursor_y, self.cursor_x] = not self.grid[self.cursor_y, self.cursor_x]
                    elif combo == "BY":
                        self.edit_mode = False
                        self.sim_paused = False
                        empty_queue(self.action_queue)
                        self._banner("R")
                        break
                elif press == "long":
                    if combo == "A":
                        self._clear()
                        self._banner("C")
                    elif combo == "B":
                        self._randomize()
                        self._banner("?")
                    elif combo == "X":
                        self.picker_mode = True
                        empty_queue(self.action_queue)
                        self._banner("P")
                        break

                self._render_edit()
            time.sleep(0.02)

    def _render_edit(self):
        display_array = self.grid.copy()
        display_array[self.cursor_y, self.cursor_x] = True

        color_array = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)
        color_array[self.grid] = self.COLOR_ALIVE

        if self.grid[self.cursor_y, self.cursor_x]:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR_ON_ALIVE
        else:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR

        self.display.show_image_color_each_led(display_array, color_array)

    # ---------- PRESET PICKER ----------

    def _loop_picker(self):
        self._render_picker()
        while self.running and self.picker_mode:
            if not self.action_queue.empty():
                bp = self.action_queue.get()
                combo = bp["combination"]
                press = bp["press_type"]

                if press == "short":
                    if combo == "X":
                        self.preset_idx = (self.preset_idx - 1) % len(PRESETS)
                    elif combo == "Y":
                        self.preset_idx = (self.preset_idx + 1) % len(PRESETS)
                    elif combo == "XY":
                        self.drop_mode_idx = (self.drop_mode_idx + 1) % len(self.DROP_MODES)
                        self._banner(self.DROP_MODES[self.drop_mode_idx][0].upper())
                    elif combo == "A":
                        self._apply_preset(PRESETS[self.preset_idx], self.DROP_MODES[self.drop_mode_idx])
                        self.picker_mode = False
                        empty_queue(self.action_queue)
                        self._banner("E")
                        break
                    elif combo == "B":
                        self.picker_mode = False
                        empty_queue(self.action_queue)
                        self._banner("E")
                        break

                self._render_picker()
            time.sleep(0.02)

    def _preset_offsets(self, preset):
        ys = [y for y, x in preset]
        xs = [x for y, x in preset]
        cy = (min(ys) + max(ys)) // 2
        cx = (min(xs) + max(xs)) // 2
        return cy, cx

    def _preset_cells(self, preset):
        cy, cx = self._preset_offsets(preset)
        cells = []
        for y, x in preset:
            gy = (self.cursor_y + (y - cy)) % self.HEIGHT
            gx = (self.cursor_x + (x - cx)) % self.WIDTH
            cells.append((gy, gx))
        return cells

    def _apply_preset(self, preset, mode):
        cells = self._preset_cells(preset)
        if mode == "replace":
            self.grid[:] = False
            for gy, gx in cells:
                self.grid[gy, gx] = True
        elif mode == "xor":
            for gy, gx in cells:
                self.grid[gy, gx] = not self.grid[gy, gx]
        else:  # or
            for gy, gx in cells:
                self.grid[gy, gx] = True

    def _render_picker(self):
        cells = self._preset_cells(PRESETS[self.preset_idx])
        overlay = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)
        for gy, gx in cells:
            overlay[gy, gx] = True

        color_array = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)
        color_array[self.grid] = self.COLOR_ALIVE
        color_array[overlay & self.grid] = self.COLOR_PREVIEW_ON_ALIVE
        color_array[overlay & ~self.grid] = self.COLOR_PREVIEW

        if overlay[self.cursor_y, self.cursor_x]:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR_ON_PREVIEW
        elif self.grid[self.cursor_y, self.cursor_x]:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR_ON_ALIVE
        else:
            color_array[self.cursor_y, self.cursor_x] = self.COLOR_CURSOR

        display_array = self.grid | overlay
        display_array[self.cursor_y, self.cursor_x] = True
        self.display.show_image_color_each_led(display_array, color_array)

    # ---------- SIM ----------

    def _loop_sim(self):
        last_step = time.time()
        self._render_sim()

        while self.running and not self.edit_mode and not self.picker_mode:
            if not self.action_queue.empty():
                bp = self.action_queue.get()
                combo = bp["combination"]
                press = bp["press_type"]

                if press == "short":
                    if combo == "X":
                        self.sim_speed = max(self.SPEED_MIN, self.sim_speed - self.SPEED_STEP)
                    elif combo == "Y":
                        self.sim_speed = min(self.SPEED_MAX, self.sim_speed + self.SPEED_STEP)
                    elif combo == "A":
                        self.sim_paused = not self.sim_paused
                        self._render_sim()
                    elif combo == "B":
                        if self.sim_paused:
                            self._step()
                            self._render_sim()
                        else:
                            self.edit_mode = True
                            empty_queue(self.action_queue)
                            self._banner("E")
                            self._render_edit()
                            break
                elif press == "long":
                    if combo == "B":
                        self.edit_mode = True
                        empty_queue(self.action_queue)
                        self._banner("E")
                        self._render_edit()
                        break
                    elif combo == "Y":
                        self._randomize()
                        self._render_sim()

            now = time.time()
            if not self.sim_paused and (now - last_step) >= self.sim_speed:
                self._step()
                last_step = now
                self._render_sim()

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

    def _render_sim(self):
        color = self.COLOR_PAUSED if self.sim_paused else self.COLOR_ALIVE
        self.display.show_image(self.grid, color=color)

    # ---------- HELPERS ----------

    def _clear(self):
        self.grid[:] = False

    def _randomize(self, density=None):
        if density is None:
            density = self.RANDOM_DENSITY
        self.grid = np.random.random((self.HEIGHT, self.WIDTH)) < density

    def _banner(self, char):
        self.display.show_text(char, cycles=2, color=self.COLOR_BANNER)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)
