import time
import random

import numpy as np

from globals import DISPLAY, LIVES_IN_GAME, TEXT
from animations import Animation
from utils import empty_queue, partial_class


class SpaceShooter:
    def __init__(self, action_queue, level=1, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)

        # Ship state (center row of 3-pixel body, valid range 1..5)
        self.ship_y = 3

        # Game objects as lists of small lists (cheap, mutated in place)
        # projectiles: [col, row]
        self.projectiles = []
        # meteors: [col, row, tick_counter, speed]
        self.meteors = []

        # Timing
        self.tick_rate = 0.05  # 50ms = ~20 FPS
        self.tick_count = 0

        # Level-dependent settings
        self.level = level
        if level == 1:
            self.spawn_interval = 12
            self.meteor_speed = 3
            self.max_spawn = 1
            self.win_score = 30
        else:
            self.spawn_interval = 10
            self.meteor_speed = 3
            self.max_spawn = 3
            self.win_score = 50

        self.projectile_speed = 2

        # Score / lives
        self.score = 0
        self.lives = LIVES_IN_GAME

        # Pre-allocated frame buffers (reused every frame)
        self.frame = np.zeros((7, 17), dtype=bool)
        self.color = np.zeros((7, 17, 3), dtype=np.uint8)

        # Colors
        self.ship_color = (0, 255, 0)
        self.projectile_color = (0, 255, 255)
        self.meteor_colors = [
            (255, 0, 0),
            (255, 80, 0),
            (255, 40, 0),
        ]

        # Invincibility after being hit
        self.invincible_ticks = 0

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)

    def run(self):
        self.start_sequence()
        empty_queue(self.action_queue)

        while self.running:
            if self.lives <= 0:
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if self.score >= self.win_score:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            self.process_input()
            self.update()
            self.render()
            time.sleep(self.tick_rate)
            self.tick_count += 1

    def process_input(self):
        while not self.action_queue.empty():
            event = self.action_queue.get()
            combo = event["combination"]

            if combo == "X":
                if self.ship_y > 1:
                    self.ship_y -= 1
            elif combo == "Y":
                if self.ship_y < 5:
                    self.ship_y += 1
            elif combo == "A":
                self.projectiles.append([2, self.ship_y])

    def update(self):
        # Move projectiles
        if self.tick_count % self.projectile_speed == 0:
            new_projectiles = []
            for p in self.projectiles:
                p[0] += 1
                if p[0] < 17:
                    new_projectiles.append(p)
            self.projectiles = new_projectiles

        # Move meteors (each has its own speed)
        new_meteors = []
        for m in self.meteors:
            m[2] += 1
            if m[2] >= m[3]:
                m[2] = 0
                m[0] -= 1
            if m[0] >= 0:
                new_meteors.append(m)
        self.meteors = new_meteors

        # Spawn meteors
        if self.tick_count % self.spawn_interval == 0:
            self._spawn_meteors()

        # Projectile-meteor collisions
        self._check_projectile_collisions()

        # Meteor-ship collisions
        if self.invincible_ticks > 0:
            self.invincible_ticks -= 1
        else:
            self._check_ship_collisions()

        # Difficulty scaling
        self._update_difficulty()

    def _spawn_meteors(self):
        count = random.randint(1, self.max_spawn)
        rows_used = set()
        for _ in range(count):
            row = random.randint(0, 6)
            if row in rows_used:
                continue
            rows_used.add(row)
            speed = max(2, self.meteor_speed + random.randint(-1, 1))
            self.meteors.append([16, row, 0, speed])

    def _check_projectile_collisions(self):
        hit_p = set()
        hit_m = set()
        for pi, p in enumerate(self.projectiles):
            for mi, m in enumerate(self.meteors):
                if p[0] == m[0] and p[1] == m[1]:
                    hit_p.add(pi)
                    hit_m.add(mi)
                    self.score += 1
        if hit_p:
            self.projectiles = [p for i, p in enumerate(self.projectiles) if i not in hit_p]
            self.meteors = [m for i, m in enumerate(self.meteors) if i not in hit_m]

    def _check_ship_collisions(self):
        ship_pixels = {
            (0, self.ship_y - 1),
            (0, self.ship_y),
            (0, self.ship_y + 1),
            (1, self.ship_y),
        }
        hit = set()
        for mi, m in enumerate(self.meteors):
            if (m[0], m[1]) in ship_pixels:
                hit.add(mi)

        if hit:
            self.meteors = [m for i, m in enumerate(self.meteors) if i not in hit]
            self.lives -= 1
            self.animation.life_lost(self.lives)
            self.display.clear_leds()
            self.invincible_ticks = 20
            empty_queue(self.action_queue)

    def _update_difficulty(self):
        if self.level == 1:
            if self.score >= 20:
                self.spawn_interval = 8
                self.meteor_speed = 2
            elif self.score >= 10:
                self.spawn_interval = 10
                self.meteor_speed = 3
        else:
            if self.score >= 40:
                self.spawn_interval = 6
                self.meteor_speed = 2
                self.max_spawn = 4
            elif self.score >= 25:
                self.spawn_interval = 7
                self.meteor_speed = 2
                self.max_spawn = 3
            elif self.score >= 15:
                self.spawn_interval = 8
                self.meteor_speed = 2
                self.max_spawn = 3
            elif self.score >= 8:
                self.spawn_interval = 9
                self.meteor_speed = 3
                self.max_spawn = 3

    def render(self):
        self.frame[:] = False
        self.color[:] = 0

        # Ship (blink during invincibility)
        if self.invincible_ticks == 0 or self.tick_count % 4 < 2:
            for r in (self.ship_y - 1, self.ship_y, self.ship_y + 1):
                self.frame[r, 0] = True
                self.color[r, 0] = self.ship_color
            self.frame[self.ship_y, 1] = True
            self.color[self.ship_y, 1] = self.ship_color

        # Projectiles
        for p in self.projectiles:
            col, row = p
            self.frame[row, col] = True
            self.color[row, col] = self.projectile_color

        # Meteors
        for m in self.meteors:
            col, row = m[0], m[1]
            self.frame[row, col] = True
            self.color[row, col] = self.meteor_colors[(col + row) % len(self.meteor_colors)]

        self.display.show_image_color_each_led(self.frame, self.color)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_space_shooter(level=1):
    return partial_class(SpaceShooter, level=level)
