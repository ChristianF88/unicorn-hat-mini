import time
from random import choice, uniform

import numpy as np

from globals import DISPLAY, LIVES_IN_GAME
from utils import empty_queue

def vary_randomly(value, _range=0.5):
    portion = value * _range
    return uniform(value - portion, value + portion)


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
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.45, failure_screen_time=0.5, winning=15):
        used_lives = 0
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if used_lives == LIVES_IN_GAME:
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
        time.sleep(0.05)


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
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.5, failure_screen_time=0.3, blink_time=1, winning=15):
        used_lives = 0
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if used_lives == LIVES_IN_GAME:
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
            self.display.show_image(array=self.display_array, color=color_to_blink)
            blink_start = time.time()
            self.display_array[self.blinking_positions[button_to_blink]] = False

            timeout = False
            while self.running and self.action_queue.empty() and not timeout:
                timeout = (time.time() - blink_start) > blink_time
                print(timeout)
                time.sleep(0.005)

            if timeout:
                time.sleep(pause_between_challenges - blink_time)
                self.display.clear_leds()
                continue

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            print("TIME:", reaction_time)
            if reaction_time > valid_reaction_time:
                used_lives += 1
                self.display.show_image(np.full((7, 17), True))
                time.sleep(failure_screen_time)
                self.display.clear_leds()

                time.sleep(vary_randomly(pause_between_challenges - failure_screen_time))
                continue

            if button_press["combination"] == button_to_blink and color_to_blink == (255,0,0):
                winning_count += 1
                to_display = str(reaction_time)[:3]
            else:
                used_lives += 1
                to_display = "NO!"

            self.display.show_text(to_display)
            time.sleep(vary_randomly(pause_between_challenges))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)

