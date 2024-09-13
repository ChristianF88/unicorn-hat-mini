import threading
import time

from actions import Action1, Action2
from demo import GraphicsDemoAction


class Menu:
    def __init__(self, menu_queue, action_queue, text_display):
        self.menu_map = {"Show Buttons Pressed": Action1, "Action2": Action2, "Demo": GraphicsDemoAction}
        self.menu_items = list(self.menu_map)
        self.current_index = 0
        self.menu_queue = menu_queue
        self.action_queue = action_queue
        self.text_display = text_display
        self.running = True
        self.current_action_thread = None
        self.current_action = None

    def run(self):
        self.text_display.start_display(self.menu_items[self.current_index])
        while self.running:
            if not self.menu_queue.empty():
                button_event = self.menu_queue.get()
                if self.current_action is None:
                    self.handle_menu_control(button_event)
                elif self.current_action is not None and button_event.get('stop_action', False):
                    self.stop_action()
            time.sleep(0.02)

    def handle_menu_control(self, button_event):
        combination = button_event['combination']
        press_type = button_event['press_type']

        if combination == 'X' and press_type == "single":
            self.move_up()
        elif combination == 'Y' and press_type == "single":
            self.move_down()
        elif combination == 'A' and press_type == "single":
            self.select_action()

    def move_up(self):
        self.text_display.stop_display()
        self.current_index = (self.current_index - 1) % len(self.menu_items)
        self.text_display.start_display(self.menu_items[self.current_index])

    def move_down(self):
        self.text_display.stop_display()
        self.current_index = (self.current_index + 1) % len(self.menu_items)
        self.text_display.start_display(self.menu_items[self.current_index])

    def select_action(self):
        selected_action = self.menu_items[self.current_index]
        self.text_display.stop_display()
        self.run_action(selected_action)

    def run_action(self, action_name):
        if self.current_action_thread and self.current_action_thread.is_alive():
            self.stop_action()

        self.current_action = self.menu_map.get(action_name)

        if self.current_action:
            self.current_action = self.current_action(self.action_queue)
            self.current_action_thread = threading.Thread(target=self.current_action.run)
            self.current_action_thread.daemon = True
            self.current_action_thread.start()

    def stop_action(self):
        if self.current_action:
            self.current_action.stop()
            self.current_action = None
            if self.current_action_thread and self.current_action_thread.is_alive():
                self.current_action_thread.join()

        if self.text_display.display_running:
            self.text_display.stop_display()

        self.text_display.start_display(self.menu_items[self.current_index])

    def stop(self):
        self.stop_action()
        if self.running:
            self.running = False
