import time

from globals import DISPLAY
from utils import empty_queue

"""
Action Ideas,
Reaction tests in different levels
Jokes to read - set read speed?
"""


class Action1:
    def __init__(self, action_queue, display=DISPLAY):
        self.action_queue = action_queue
        empty_queue(self.action_queue)

        self.running = True
        self.display = display

    def run(self):
        while self.running:
            if not self.action_queue.empty():
                button_press = self.action_queue.get()
                self.display.show_text(button_press["combination"])
            time.sleep(0.02)

    def stop(self):
        self.running = False
        self.display.stop()


class Action2:
    def __init__(self, action_queue, display=DISPLAY):
        self.action_queue = action_queue
        empty_queue(self.action_queue)

        self.running = True
        self.display = display

    def run(self):
        while self.running:
            if not self.action_queue.empty():
                button_press = self.action_queue.get()
                self.display.stop_text_in_loop()
                time.sleep(0.01)
                self.display.start_text_in_loop("2" + button_press["combination"], color_cycles=5)
            time.sleep(0.02)

    def stop(self):
        self.running = False
        self.display.stop_text_in_loop()
        time.sleep(0.01)
