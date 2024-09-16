import time
from random import choice

from globals import DISPLAY
from utils import empty_queue

import numpy as np


def blink_random(display: DISPLAY, array_to_show, indices_to_blink, leds_on=0.5):
    array_to_show[indices_to_blink[0],indices_to_blink[1]] = True
    display.show_image(array_to_show)
    started_blink = time.time()
    array_to_show[indices_to_blink[0],indices_to_blink[1]] = False
    return started_blink


class ReactionLevelOne:
    def __init__(self, action_queue, display=DISPLAY):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.display_array = np.full((7, 17), False)  # that's the screen resolution
        self.blinking_positions = {
            "A": [[1,1,2,2],[1,2,1,2]],
            "X": [[1,1,2,2],[14,15,14,15]],
            "B": [[4,4,5,5],[1,2,1,2]],
            "Y": [[4,4,5,5],[14,15,14,15]]
        }
        self.can_blink = list(self.blinking_positions)

    def run(self, pause_between_challenges=1.5, valid_reaction_time=1.4, failure_screen_time=0.5, lives=3, winning=20):
        used_lives = 0
        winning_count = 0
        while self.running:

            if used_lives == lives:
                print("your dead")
                self.display.blink_time(color_cycles=0, color=(255,0,0))
                break

            if winning_count == winning:
                print("you win")
                self.display.blink_time(color_cycles=0, color=(0, 0, 255))
                break


            button_to_blink = choice(self.can_blink)
            empty_queue(self.action_queue)
            self.display_array[self.blinking_positions[button_to_blink]] = True
            self.display.show_image(self.display_array)
            blink_start = time.time()
            self.display_array[self.blinking_positions[button_to_blink]] = False

            while self.running and self.action_queue.empty():
                time.sleep(0.01)

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = time.time() - blink_start
            print(reaction_time, button_press["combination"] == button_to_blink)

            if reaction_time > valid_reaction_time:
                used_lives += 1
                self.display.show_image(np.full((7, 17), True))
                time.sleep(0.5)
                self.display.clear_leds()

                time.sleep(pause_between_challenges-failure_screen_time)
                continue

            if button_press["combination"] == button_to_blink:
                winning_count += 1
                to_display = str(reaction_time)[:3]
            else:
                used_lives += 1
                to_display = "NO!"

            print(to_display)
            self.display.show_text(to_display)
            time.sleep(pause_between_challenges)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.01)