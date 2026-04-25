import time

import numpy as np

from globals import DISPLAY, TEXT
from animations import Animation
from utils import empty_queue, partial_class


class MashDuel:
    WIDTH = 17
    HEIGHT = 7

    COLOR_RED = (255, 0, 0)
    COLOR_BLUE = (0, 80, 255)
    COLOR_SEPARATOR = (40, 40, 40)
    COLOR_CENTER = (180, 180, 0)

    TICK = 0.05

    def __init__(self, action_queue, level=1, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.level = level

        if level == 1:
            self.target = 30
        else:
            self.target_per_bar = 25
            if level == 3:
                self.decay_per_tick = 0.04
            else:
                self.decay_per_tick = 0.0

        # L1 state
        self.pressure = 0.0

        # L2/L3 state
        self.counts = {"A": 0.0, "B": 0.0, "X": 0.0, "Y": 0.0}

        self.frame = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)
        self.color = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)

    def run(self):
        self.start_sequence()
        empty_queue(self.action_queue)

        if self.level == 1:
            self._run_l1()
        else:
            self._run_multi_bar()

    def _drain_inputs(self):
        red = 0
        blue = 0
        per_button = {"A": 0, "B": 0, "X": 0, "Y": 0}
        while not self.action_queue.empty():
            event = self.action_queue.get()
            if event["press_type"] == "long":
                continue
            combo = event["combination"]
            for ch in combo:
                if ch in per_button:
                    per_button[ch] += 1
                    if ch in ("A", "B"):
                        red += 1
                    else:
                        blue += 1
        return red, blue, per_button

    # ---------- LEVEL 1 ----------

    def _run_l1(self):
        self._render_l1()
        while self.running:
            red, blue, _ = self._drain_inputs()
            if red or blue:
                self.pressure += (red - blue) / self.target
                if self.pressure > 1.0:
                    self.pressure = 1.0
                elif self.pressure < -1.0:
                    self.pressure = -1.0

            self._render_l1()

            if self.pressure >= 1.0:
                self._winner_screen(self.COLOR_RED, "R")
                break
            if self.pressure <= -1.0:
                self._winner_screen(self.COLOR_BLUE, "B")
                break

            time.sleep(self.TICK)

    def _render_l1(self):
        boundary = int(round((self.WIDTH - 1) / 2 + self.pressure * (self.WIDTH - 1) / 2))
        self.frame[:] = True
        self.color[:] = 0
        for c in range(self.WIDTH):
            if c < boundary:
                self.color[:, c] = self.COLOR_RED
            elif c > boundary:
                self.color[:, c] = self.COLOR_BLUE
            else:
                self.color[:, c] = self.COLOR_CENTER
        self.display.show_image_color_each_led(self.frame, self.color)

    # ---------- LEVELS 2 & 3 ----------

    def _run_multi_bar(self):
        self._render_multi_bar()
        while self.running:
            _, _, per = self._drain_inputs()
            for ch, n in per.items():
                if n:
                    self.counts[ch] += n

            if self.decay_per_tick:
                for ch in self.counts:
                    self.counts[ch] = max(0.0, self.counts[ch] - self.decay_per_tick)

            self._render_multi_bar()

            winner = self._check_winner()
            if winner is not None:
                color, banner = winner
                self._winner_screen(color, banner)
                break

            time.sleep(self.TICK)

    def _check_winner(self):
        # Pairing 1: A vs X. Pairing 2: B vs Y.
        # First bar to reach target wins its pairing => overall.
        for ch in ("A", "B"):
            if self.counts[ch] >= self.target_per_bar:
                return self.COLOR_RED, "R"
        for ch in ("X", "Y"):
            if self.counts[ch] >= self.target_per_bar:
                return self.COLOR_BLUE, "B"
        return None

    def _render_multi_bar(self):
        self.frame[:] = False
        self.color[:] = 0

        layout = [
            (0, "A", self.COLOR_RED),
            (1, "X", self.COLOR_BLUE),
            (4, "B", self.COLOR_RED),
            (5, "Y", self.COLOR_BLUE),
        ]
        for row, ch, color in layout:
            fill = int(round(min(self.counts[ch], self.target_per_bar) * (self.WIDTH - 1) / self.target_per_bar))
            for c in range(fill + 1):
                self.frame[row, c] = True
                self.color[row, c] = color

        for sep_row in (2, 3, 6):
            self.frame[sep_row, self.WIDTH // 2] = True
            self.color[sep_row, self.WIDTH // 2] = self.COLOR_SEPARATOR

        self.display.show_image_color_each_led(self.frame, self.color)

    # ---------- COMMON ----------

    def _winner_screen(self, color, banner):
        for _ in range(3):
            self.display.show_image(np.full((self.HEIGHT, self.WIDTH), True), color=color)
            time.sleep(0.2)
            self.display.clear_leds()
            time.sleep(0.15)
        self.display.show_text(banner, cycles=4, color=color)
        self.display.start_text_in_loop(TEXT.get("ABXY"))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_mash_duel(level=1):
    return partial_class(MashDuel, level=level)
