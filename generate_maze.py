import random
from multiprocessing.dummy import current_process

import numpy as np


def generate_maze(width, height, seed):
    random.seed(seed)
    assert width%2==1, "width must be uneven!"
    assert height % 2 == 1, "height must be uneven!"

    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    maze = np.ones((height, width), dtype=np.bool_)

    def carve_path(x, y):
        maze[y, x] = False
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + 2 * dx, y + 2 * dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny, nx] == True:
                maze[y + dy, x + dx] = False
                carve_path(nx, ny)

    start_x, start_y = random.randrange(1, width, 2), random.randrange(1, height, 2)
    carve_path(start_x, start_y)

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
    for i in range(9)[1:]:
        save_maze(level=i, seed=i)
