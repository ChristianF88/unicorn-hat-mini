import time
from time import sleep

import numpy as np

from animations import Animation
from globals import DISPLAY, TEXT
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

    def window(self, m, n, maze=None):  # m - height, n - width
        if maze is None:
            maze = self.maze
        return maze[
               (m-self.padding_vertical-1):(m+self.padding_vertical+2),
               (n-self.padding_horizontal):(n+self.padding_horizontal+1)
        ]

    def solve_maze(self, current_position, display_solution=True):
        padded_end = self.maze_stop
        current = None
        stack = [current_position]
        visited = set()
        path = {}

        self.display.show_image(self.window(*current_position))
        self.display.turn_on_led(8, 3, (0, 0, 255))
        time.sleep(0.5)
        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            self.display.show_image(self.window(*current))
            self.display.turn_on_led(8, 3, (0, 0, 255))
            time.sleep(0.0001)  # Delay to visualize the search process

            if current == padded_end:
                break

            m, n = current
            # Directions: LEFT, RIGHT, UP, DOWN
            directions = {
                (0, -1): 'LEFT',
                (0, 1): 'RIGHT',
                (-1, 0): 'UP',
                (1, 0): 'DOWN'
            }

            for (dm, dn), direction in directions.items():
                next_position = (m + dm, n + dn)
                # Check if within maze bounds and not a wall
                if (0 <= next_position[0] < self.maze.shape[0] and
                        0 <= next_position[1] < self.maze.shape[1] and
                        self.maze[next_position] == False and
                        next_position not in visited):
                    stack.append(next_position)
                    path[next_position] = current

        if display_solution:
            time.sleep(0.5)
            solution_path = []
            while current != current_position:
                solution_path.append(current)
                current = path[current]
            solution_path.append(current_position)
            solution_path.reverse()

            maze = self.maze.copy()
            h, w = maze.shape
            colors = np.full((h, w, 3), (255, 0, 0))

            pm, pn = solution_path[0]
            for m, n in solution_path:
                maze[m ,n] = True
                colors[pm, pn] =  (0, 0, 255)  # covered path
                colors[m, n] = (0, 255, 0)
                self.display.show_image_color_each_led(self.window(m, n, maze), self.window(m, n, colors))
                pm, pn = m, n
                time.sleep(0.1)  # Pause to visualize the solution
            return solution_path


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
            if button_press["combination"] in ["A"]:  # LEFT
                if current_position == self.maze_start:  # Can not move to the left from the start position
                    continue
                if self.maze[m, n - 1]:
                    continue
                current_position = m, n - 1
            elif button_press["combination"] in ["B"]:  # RIGHT
                if self.maze[m, n + 1]:
                    continue
                current_position = m, n + 1
            elif button_press["combination"] in ["X"]:  # UP
                if self.maze[m - 1, n]:
                    continue
                current_position = m - 1, n
            elif button_press["combination"] in ["Y"]:  # DOWN
                if self.maze[m + 1, n]:
                    continue
                current_position = m + 1, n

            elif button_press["combination"] in ["ABX"] and button_press["press_type"] == "long":  # DOWN
                self.solve_maze(current_position)
                self.animation.spider_with_movement()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if current_position == self.maze_stop:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            self.display.show_image(self.window(*current_position))
            self.display.turn_on_led(8, 3, (0, 0, 255))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


def init_maze(level=1):
    return partial_class(Maze, level = level)
