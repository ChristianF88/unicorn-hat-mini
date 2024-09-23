import time
import numpy as np

from animations import Animation
from globals import DISPLAY
from utils import empty_queue, partial_class


class Maze:
    def __init__(self, action_queue, level=1, display=DISPLAY, animation = Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.maze = np.load(f'mazes/level_{level}.npy')
        self.start = (0, 1)
        self.padding_vertical = 2
        self.padding_horizontal = 8
        self.pad_maze()

    @property
    def maze_start(self):  # Center position
        return (1 + self.padding_vertical, 0 + self.padding_horizontal)

    @property
    def maze_stop(self):
        return (self.maze.shape[0] - 2 - self.padding_vertical, self.maze.shape[1] - 1 - self.padding_horizontal)

    def pad_maze(self):
        self.maze = np.pad(
        self.maze,
        pad_width=((self.padding_vertical, self.padding_vertical),
                   (self.padding_horizontal, self.padding_horizontal)),
        mode='constant',
        constant_values=False
    )

    def window(self, m, n):  # m - height, n - width
        return self.maze[
               (m-self.padding_vertical-1):(m+self.padding_vertical+2),
               (n-self.padding_horizontal):(n+self.padding_horizontal+1)
        ]


    def run(self):

        current_position = self.maze_start
        self.display.show_image(self.window(*current_position))
        self.display.turn_on_led(8, 3, (0,0,255))
        empty_queue(self.action_queue)
        while self.running:
            while self.running and self.action_queue.empty():
                time.sleep(0.01)

            if not self.running:
                self.stop()
                break

            button_press = self.action_queue.get()
            m, n = current_position
            if button_press["combination"] == "A":  # LEFT
                if current_position == self.maze_start:  # Can not move to the left from the start position
                    continue
                if self.maze[m, n - 1]:
                    continue
                current_position = m, n - 1
            elif button_press["combination"] == "B":  # RIGHT
                if self.maze[m, n + 1]:
                    continue
                current_position = m, n + 1
            elif button_press["combination"] == "X":  # UP
                if self.maze[m - 1, n]:
                    continue
                current_position = m - 1, n
            elif button_press["combination"] == "Y":  # DOWN
                if self.maze[m + 1, n]:
                    continue
                current_position = m + 1, n
            if current_position == self.maze_stop:
                self.animation.winning()
                self.display.start_text_in_loop("Long press ABXY to exit!")
                break

            self.display.show_image(self.window(*current_position))
            self.display.turn_on_led(8, 3, (0, 0, 255))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_maze(level=1):
    return partial_class(Maze, maze_level = level)
