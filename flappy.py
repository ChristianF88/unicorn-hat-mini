import time
import random

import numpy as np

from globals import DISPLAY, TEXT
from animations import Animation
from utils import empty_queue, partial_class


class Flappy:
    WIDTH = 17
    HEIGHT = 7
    BIRD_COL = 4

    COLOR_BIRD = (255, 200, 0)
    COLOR_PIPE = (0, 200, 0)

    def __init__(self, action_queue, level=1, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.level = level

        if level == 1:
            self.gap_size = 3
            self.pipe_speed = 0.4
            self.spawn_interval = 20
        else:
            self.gap_size = 2
            self.pipe_speed = 0.6
            self.spawn_interval = 15

        self.tick_rate = 0.05
        self.gravity = 0.18
        self.flap_impulse = -0.7
        self.max_vy = 0.6

        self.bird_y = self.HEIGHT / 2
        self.bird_vy = 0.0

        # pipes: list of [col_float, gap_top_row, scored]
        self.pipes = []
        self.tick_count = 0
        self.score = 0

        self.frame = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)
        self.color = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)

    def run(self):
        self.start_sequence()
        empty_queue(self.action_queue)

        while self.running:
            self.process_input()
            if not self.update():
                self.display.show_text(str(self.score), cycles=4)
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break
            self.render()
            time.sleep(self.tick_rate)
            self.tick_count += 1

    def process_input(self):
        while not self.action_queue.empty():
            event = self.action_queue.get()
            if event["press_type"] == "long":
                continue
            if event["combination"] == "A":
                self.bird_vy = self.flap_impulse

    def update(self):
        # Gravity
        self.bird_vy += self.gravity
        if self.bird_vy > self.max_vy:
            self.bird_vy = self.max_vy
        self.bird_y += self.bird_vy

        # Floor / ceiling = death
        if self.bird_y < 0 or self.bird_y > self.HEIGHT - 1:
            return False

        # Move pipes
        for p in self.pipes:
            p[0] -= self.pipe_speed
        self.pipes = [p for p in self.pipes if p[0] > -1]

        # Spawn
        if self.tick_count % self.spawn_interval == 0:
            gap_top = random.randint(0, self.HEIGHT - self.gap_size)
            self.pipes.append([self.WIDTH - 1.0, gap_top, False])

        # Collision and score
        bx = self.BIRD_COL
        by = int(round(self.bird_y))
        for p in self.pipes:
            pcol = int(round(p[0]))
            if pcol == bx:
                gap_top = p[1]
                if not (gap_top <= by < gap_top + self.gap_size):
                    return False
            if not p[2] and p[0] < bx:
                p[2] = True
                self.score += 1

        return True

    def render(self):
        self.frame[:] = False
        self.color[:] = 0

        # Pipes
        for p in self.pipes:
            pcol = int(round(p[0]))
            if 0 <= pcol < self.WIDTH:
                gap_top = p[1]
                for r in range(self.HEIGHT):
                    if not (gap_top <= r < gap_top + self.gap_size):
                        self.frame[r, pcol] = True
                        self.color[r, pcol] = self.COLOR_PIPE

        # Bird
        by = int(round(self.bird_y))
        if 0 <= by < self.HEIGHT:
            self.frame[by, self.BIRD_COL] = True
            self.color[by, self.BIRD_COL] = self.COLOR_BIRD

        self.display.show_image_color_each_led(self.frame, self.color)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_flappy(level=1):
    return partial_class(Flappy, level=level)
