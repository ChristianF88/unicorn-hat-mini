import time
import random

import numpy as np

from globals import DISPLAY, LIVES_IN_GAME, TEXT
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
            self.pipe_speed = 0.35
            self.spawn_interval = 24
            self.gravity = 0.10
            self.flap_impulse = -0.55
            self.max_vy = 0.45
        else:
            self.gap_size = 2
            self.pipe_speed = 0.5
            self.spawn_interval = 18
            self.gravity = 0.14
            self.flap_impulse = -0.6
            self.max_vy = 0.55

        self.tick_rate = 0.05

        self.lives = LIVES_IN_GAME
        self.score = 0

        self.frame = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)
        self.color = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

        self._reset_round()

    def _reset_round(self):
        self.bird_y = self.HEIGHT / 2
        self.bird_vy = self.flap_impulse * 0.5  # tiny upward hop on (re)start
        self.pipes = []
        self.tick_count = 0
        self.invincible_ticks = 16  # ~0.8 s grace after spawn / respawn

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
                self.lives -= 1
                if self.lives > 0:
                    self.animation.life_lost(self.lives)
                    self.display.clear_leds()
                    self._reset_round()
                    empty_queue(self.action_queue)
                    continue
                # final life
                self.animation.life_lost(0)
                self.display.show_text(str(self.score), cycles=4)
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break
            self.render()
            time.sleep(self.tick_rate)
            self.tick_count += 1

    def process_input(self):
        while not self.action_queue.empty():
            event = self.action_queue.get()
            if "A" in event["combination"]:
                self.bird_vy = self.flap_impulse

    def update(self):
        if self.invincible_ticks > 0:
            self.invincible_ticks -= 1

        self.bird_vy += self.gravity
        if self.bird_vy > self.max_vy:
            self.bird_vy = self.max_vy
        self.bird_y += self.bird_vy

        if self.bird_y < 0:
            self.bird_y = 0
            self.bird_vy = 0
        if self.bird_y > self.HEIGHT - 1:
            if self.invincible_ticks > 0:
                self.bird_y = self.HEIGHT - 1
                self.bird_vy = 0
            else:
                return False

        for p in self.pipes:
            p[0] -= self.pipe_speed
        self.pipes = [p for p in self.pipes if p[0] > -1]

        if self.tick_count % self.spawn_interval == 0 and self.invincible_ticks == 0:
            gap_top = random.randint(0, self.HEIGHT - self.gap_size)
            self.pipes.append([self.WIDTH - 1.0, gap_top, False])

        bx = self.BIRD_COL
        by = int(round(self.bird_y))
        for p in self.pipes:
            pcol = int(round(p[0]))
            if pcol == bx:
                gap_top = p[1]
                if not (gap_top <= by < gap_top + self.gap_size):
                    if self.invincible_ticks == 0:
                        return False
            if not p[2] and p[0] < bx:
                p[2] = True
                self.score += 1

        return True

    def render(self):
        self.frame[:] = False
        self.color[:] = 0

        for p in self.pipes:
            pcol = int(round(p[0]))
            if 0 <= pcol < self.WIDTH:
                gap_top = p[1]
                for r in range(self.HEIGHT):
                    if not (gap_top <= r < gap_top + self.gap_size):
                        self.frame[r, pcol] = True
                        self.color[r, pcol] = self.COLOR_PIPE

        by = int(round(self.bird_y))
        if 0 <= by < self.HEIGHT:
            if self.invincible_ticks == 0 or self.tick_count % 4 < 2:
                self.frame[by, self.BIRD_COL] = True
                self.color[by, self.BIRD_COL] = self.COLOR_BIRD

        self.display.show_image_color_each_led(self.frame, self.color)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_flappy(level=1):
    return partial_class(Flappy, level=level)
