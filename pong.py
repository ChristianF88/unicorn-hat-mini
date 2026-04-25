import time
import random

import numpy as np

from globals import DISPLAY, TEXT
from animations import Animation
from utils import empty_queue, partial_class


class Pong:
    WIDTH = 17
    HEIGHT = 7
    PADDLE_HALF = 1  # paddle is 2*PADDLE_HALF + 1 = 3 cells

    COLOR_PLAYER = (0, 255, 0)
    COLOR_AI = (0, 100, 255)
    COLOR_BALL = (0, 255, 255)
    COLOR_MID = (40, 40, 40)
    COLOR_FLASH_PLAYER = (0, 255, 0)
    COLOR_FLASH_AI = (255, 0, 0)

    def __init__(self, action_queue, level=1, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.level = level

        if level == 1:
            self.ball_speed_x = 0.5
            self.ball_speed_y = 0.35
            self.ai_step = 4
            self.win_score = 5
        else:
            self.ball_speed_x = 0.7
            self.ball_speed_y = 0.5
            self.ai_step = 2
            self.win_score = 7

        self.tick_rate = 0.05

        self.player_y = 3
        self.ai_y = 3

        self.ball_x = self.WIDTH / 2
        self.ball_y = self.HEIGHT / 2
        self.ball_vx = self.ball_speed_x
        self.ball_vy = self.ball_speed_y

        self.player_score = 0
        self.ai_score = 0

        self.ai_tick = 0

        self.frame = np.zeros((self.HEIGHT, self.WIDTH), dtype=bool)
        self.color = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)

    def reset_ball(self, toward_player):
        self.ball_x = self.WIDTH / 2
        self.ball_y = self.HEIGHT / 2
        self.ball_vx = -self.ball_speed_x if toward_player else self.ball_speed_x
        self.ball_vy = random.choice([-1, 1]) * self.ball_speed_y

    def run(self):
        self.start_sequence()
        empty_queue(self.action_queue)

        while self.running:
            if self.player_score >= self.win_score:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break
            if self.ai_score >= self.win_score:
                self.animation.death(self.animation.shapes.skull)
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            self.process_input()
            self.update()
            self.render()
            time.sleep(self.tick_rate)
            self.ai_tick += 1

    def process_input(self):
        while not self.action_queue.empty():
            event = self.action_queue.get()
            combo = event["combination"]
            if combo == "X":
                if self.player_y > 1:
                    self.player_y -= 1
            elif combo == "Y":
                if self.player_y < self.HEIGHT - 2:
                    self.player_y += 1

    def update_ai(self):
        if self.ai_tick % self.ai_step != 0:
            return
        target = int(round(self.ball_y))
        if target < self.ai_y and self.ai_y > 1:
            self.ai_y -= 1
        elif target > self.ai_y and self.ai_y < self.HEIGHT - 2:
            self.ai_y += 1

    def update(self):
        self.update_ai()

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # Bounce off top/bottom
        if self.ball_y < 0:
            self.ball_y = -self.ball_y
            self.ball_vy = -self.ball_vy
        elif self.ball_y > self.HEIGHT - 1:
            self.ball_y = 2 * (self.HEIGHT - 1) - self.ball_y
            self.ball_vy = -self.ball_vy

        bx = int(round(self.ball_x))
        by = int(round(self.ball_y))

        # Player paddle (col 0): bounce when ball reaches col 0..1 moving left
        if self.ball_vx < 0 and bx <= 0:
            if abs(by - self.player_y) <= self.PADDLE_HALF:
                self.ball_x = 0
                self.ball_vx = -self.ball_vx
                # spin: paddle offset adds to vy
                self.ball_vy += (by - self.player_y) * 0.15
            else:
                self.ai_score += 1
                self.flash_score(self.COLOR_FLASH_AI)
                self.reset_ball(toward_player=False)

        # AI paddle (col WIDTH-1)
        elif self.ball_vx > 0 and bx >= self.WIDTH - 1:
            if abs(by - self.ai_y) <= self.PADDLE_HALF:
                self.ball_x = self.WIDTH - 1
                self.ball_vx = -self.ball_vx
                self.ball_vy += (by - self.ai_y) * 0.15
            else:
                self.player_score += 1
                self.flash_score(self.COLOR_FLASH_PLAYER)
                self.reset_ball(toward_player=True)

    def flash_score(self, color):
        self.display.show_image(np.full((self.HEIGHT, self.WIDTH), True), color=color)
        time.sleep(0.3)

    def render(self):
        self.frame[:] = False
        self.color[:] = 0

        # Mid-line dim dots
        for r in range(0, self.HEIGHT, 2):
            self.frame[r, self.WIDTH // 2] = True
            self.color[r, self.WIDTH // 2] = self.COLOR_MID

        # Player paddle (col 0)
        for dy in range(-self.PADDLE_HALF, self.PADDLE_HALF + 1):
            r = self.player_y + dy
            if 0 <= r < self.HEIGHT:
                self.frame[r, 0] = True
                self.color[r, 0] = self.COLOR_PLAYER

        # AI paddle (col 16)
        for dy in range(-self.PADDLE_HALF, self.PADDLE_HALF + 1):
            r = self.ai_y + dy
            if 0 <= r < self.HEIGHT:
                self.frame[r, self.WIDTH - 1] = True
                self.color[r, self.WIDTH - 1] = self.COLOR_AI

        # Ball
        bx = int(round(self.ball_x))
        by = int(round(self.ball_y))
        if 0 <= bx < self.WIDTH and 0 <= by < self.HEIGHT:
            self.frame[by, bx] = True
            self.color[by, bx] = self.COLOR_BALL

        self.display.show_image_color_each_led(self.frame, self.color)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_pong(level=1):
    return partial_class(Pong, level=level)
