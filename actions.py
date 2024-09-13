import time

from globals import TEXT_DISPLAY
from utils import empty_queue

"""
Action Ideas,
Reaction tests in different levels
Jokes to read - set read speed?
"""

class Action1:
    def __init__(self, action_queue, display=TEXT_DISPLAY):
        self.action_queue = action_queue
        empty_queue(self.action_queue)

        self.running = True
        self.display = display

    def run(self):
        while self.running:
            if not self.action_queue.empty():
                button_press = self.action_queue.get()
                if self.display.display_running:
                    self.display.stop_display()
                self.display.start_display(button_press["combination"], moving_text=False)

            time.sleep(0.02)

    def stop(self):
        self.running = False
        self.display.stop_display()



class Action2:
    def __init__(self, action_queue, display=TEXT_DISPLAY):
        self.action_queue = action_queue
        empty_queue(self.action_queue)

        self.running = True
        self.display = display

    def run(self):
        while self.running:
            if not self.action_queue.empty():
                button_press = self.action_queue.get()
                if self.display.display_running:
                    self.display.stop_display()
                self.display.start_display("2" + button_press["combination"])

            time.sleep(0.02)

    def stop(self):
        self.running = False
        self.display.stop_display()

