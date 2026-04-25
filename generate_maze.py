import random
import sys
from multiprocessing.dummy import current_process

import numpy as np

sys.setrecursionlimit(50000)


def generate_maze(width, height, seed):
    random.seed(seed)
    assert width%2==1, "width must be uneven!"
    assert height % 2 == 1, "height must be uneven!"

    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    maze = np.ones((height, width), dtype=np.bool_)

    start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    maze[start_y, start_x] = False
    stack = [(start_x, start_y)]
    while stack:
        x, y = stack[-1]
        candidates = []
        for dx, dy in dirs:
            nx, ny = x + 2 * dx, y + 2 * dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny, nx]:
                candidates.append((dx, dy, nx, ny))
        if not candidates:
            stack.pop()
            continue
        dx, dy, nx, ny = random.choice(candidates)
        maze[y + dy, x + dx] = False
        maze[ny, nx] = False
        stack.append((nx, ny))

    maze[1, 0] = False  # Entrance
    maze[height - 2, width - 1] = False  # Exit
    return maze


def display_maze(maze):
    display = np.where(maze, '##', '  ')
    for row in display:
        print(''.join(row))

def save_maze(level=1, _print=True, seed=1):
    width, height = level*10 + 1, level*10 + 1
    maze = generate_maze(width, height, seed)
    display_maze(maze)
    if _print:
        print(repr(maze))
    np.save(f'mazes/level_{level}.npy', maze)  # .npy extension is added if not given


if __name__ == "__main__":
    for i in range(1, 16):
        save_maze(level=i, seed=i)
