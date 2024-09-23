import threading
import time

from actions import Action1, Action2
from demo import GraphicsDemoAction
from display import Display
from maze import init_maze
from reaction_game import ReactionLevelOne, ReactionLevelTwo


class Menu:
    def __init__(self, menu_queue, action_queue, display: Display):
        self.menu_map = {
            "Labyrinth": {
                f"Lvl-{i}":init_maze(level=i) for i in range(10)[1:]
            },
            "Reaktion": {
                "Lvl-1": ReactionLevelOne,
                "Lvl-2": ReactionLevelTwo
            },
            "Demo": { "Bling-bling":
                GraphicsDemoAction
            },
            "Testing": {
                "Action1": Action1,
                "Action2": Action2
            }
        }
        self.menu_list_main = list(self.menu_map)
        self.menu_list_sub = [list(sub) for sub in self.menu_map.values()]
        self.menu_indices = [0, 0]  # index for main, and sub
        self.menu_idx = 0  # main menu

        self.menu_queue = menu_queue
        self.action_queue = action_queue
        self.display = display
        self.running = True
        self.current_action_thread = None
        self.current_action = None

    def select_menu(self):
        if self.menu_idx == 0:
            return self.menu_list_main
        else:
            return self.menu_list_sub[self.menu_indices[0]]

    def select_text(self):
        if self.menu_idx == 0:
            return self.menu_list_main[self.menu_indices[0]]
        else:
            return self.menu_list_sub[self.menu_indices[0]][self.menu_indices[1]]

    def select_action(self):
        return self.menu_map.get(
            self.menu_list_main[self.menu_indices[0]]
        ).get(
            self.menu_list_sub[self.menu_indices[0]][self.menu_indices[1]]
        )

    def run(self):
        self.display.start_text_in_loop(self.menu_list_main[self.menu_indices[self.menu_idx]])
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

        if combination == 'X' and press_type == "short":
            self.move_up()
        elif combination == 'Y' and press_type == "short":
            self.move_down()
        elif combination == 'A' and press_type == "short":
            self.enter()
        elif combination == 'B' and press_type == "short":
            self.back()

    def _move(self, by=1):
        self.display.stop_text_in_loop()
        self.menu_indices[self.menu_idx] = (self.menu_indices[self.menu_idx] + by) % len(self.select_menu())
        self.display.start_text_in_loop(self.select_text())

    def move_up(self):
        self._move(-1)

    def move_down(self):
        self._move(1)

    def enter(self):
        self.display.stop_text_in_loop()
        if self.menu_idx == 0:
            self.menu_idx = 1
            self.display.start_text_in_loop(self.select_text())
        elif self.menu_idx == 1:
            self.run_action(self.select_action())

    def back(self):
        if self.menu_idx == 1:
            self.menu_idx = 0
            self.menu_indices[1] = 0
            self.display.stop_text_in_loop()
            self.display.start_text_in_loop(self.select_text())


    def run_action(self, action):
        if self.current_action_thread and self.current_action_thread.is_alive():
            self.stop_action()

        self.current_action = action

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

        self.display.start_text_in_loop(self.select_text())

    def stop(self):
        self.stop_action()
        if self.running:
            self.running = False
