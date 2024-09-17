import time
from random import choice

import numpy as np

from globals import DISPLAY
from utils import empty_queue


class ReactionLevelOne:
    def __init__(self, action_queue, display=DISPLAY):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.display_array = np.full((7, 17), False)  # that's the screen resolution
        self.blinking_positions = {
            "A": ([1, 1, 2, 2], [1, 2, 1, 2]),
            "X": ([1, 1, 2, 2], [14, 15, 14, 15]),
            "B": ([4, 4, 5, 5], [1, 2, 1, 2]),
            "Y": ([4, 4, 5, 5], [14, 15, 14, 15])
        }
        self.can_blink = list(self.blinking_positions)

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.63, failure_screen_time=0.5, lives=3, winning=10):
        used_lives = 0
        winning_count = 0
        while self.running:

            if used_lives == lives:
                self.display.blink_time(color_cycles=0, color=(255, 0, 0))
                self.display.start_text_in_loop("Long press ABXY to exit!")
                break

            if winning_count == winning:
                self.display.blink_time(color_cycles=0, color=(0, 255, 0))
                self.display.show_image(np.full((7, 17), True), color=(0, 255, 0))
                self.display.start_text_in_loop("Long press ABXY to exit!")
                break

            button_to_blink = choice(self.can_blink)
            empty_queue(self.action_queue)
            self.display_array[self.blinking_positions[button_to_blink]] = True
            self.display.show_image(self.display_array)
            blink_start = time.time()
            self.display_array[self.blinking_positions[button_to_blink]] = False

            while self.running and self.action_queue.empty():
                time.sleep(0.005)

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            print("TIME:", reaction_time)
            if reaction_time > valid_reaction_time:
                used_lives += 1
                self.display.show_image(np.full((7, 17), True))
                time.sleep(0.5)
                self.display.clear_leds()

                time.sleep(pause_between_challenges - failure_screen_time)
                continue

            if button_press["combination"] == button_to_blink:
                winning_count += 1
                to_display = str(reaction_time)[:3]
            else:
                used_lives += 1
                to_display = "NO!"

            self.display.show_text(to_display)
            time.sleep(pause_between_challenges)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.01)


class ReactionLevelTwo:
    def __init__(self, action_queue, display=DISPLAY):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.display_array = np.full((7, 17), False)  # that's the screen resolution
        self.blinking_positions = {
            "A": ([1, 1, 2, 2], [1, 2, 1, 2]),
            "X": ([1, 1, 2, 2], [14, 15, 14, 15]),
            "B": ([4, 4, 5, 5], [1, 2, 1, 2]),
            "Y": ([4, 4, 5, 5], [14, 15, 14, 15])
        }
        self.can_blink = list(self.blinking_positions)
        self.colors = ((0,0,255),(255,0,0))

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.8, failure_screen_time=0.5, show_blink_for=1, lives=3, winning=10):
        used_lives = 0
        winning_count = 0
        while self.running:

            if used_lives == lives:
                self.display.blink_time(color_cycles=0, color=(255, 0, 0))
                self.display.start_text_in_loop("Long press ABXY to exit!")
                break

            if winning_count == winning:
                self.display.blink_time(color_cycles=0, color=(0, 255, 0))
                self.display.show_image(np.full((7, 17), True), color=(0, 255, 0))
                self.display.start_text_in_loop("Long press ABXY to exit!")
                break

            button_to_blink = choice(self.can_blink)
            color_to_blink = choice(self.colors)
            empty_queue(self.action_queue)
            self.display_array[self.blinking_positions[button_to_blink]] = True
            self.display.show_image(self.display_array, color=color_to_blink)
            blink_start = time.time()
            self.display_array[self.blinking_positions[button_to_blink]] = False

            while self.running and self.action_queue.empty() and (reaction_time := (time.time() - blink_start)) < show_blink_for:
                time.sleep(0.005)

            if color_to_blink != (255, 0, 0):
                self.display.clear_leds()
                continue

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            print("TIME:", reaction_time)
            if reaction_time > valid_reaction_time:
                used_lives += 1
                self.display.show_image(np.full((7, 17), True))
                time.sleep(0.5)
                self.display.clear_leds()

                time.sleep(pause_between_challenges - failure_screen_time)
                continue

            if button_press["combination"] == button_to_blink and color_to_blink == (255,0,0):
                winning_count += 1
                to_display = str(reaction_time)[:3]
            else:
                used_lives += 1
                to_display = "NO!"

            self.display.show_text(to_display)
            time.sleep(pause_between_challenges)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.01)


