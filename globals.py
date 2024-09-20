import queue
import threading

from unicornhatmini import UnicornHATMini

from display import Display

DISPLAY_BRIGHTNESS = 0.03
BUTTON_MAP = {5: "A", 6: "B", 16: "X", 24: "Y"}
EVENT_QUEUE = queue.Queue()  # For event detection
MENU_QUEUE = queue.Queue()  # For sending button presses to action classes
ACTION_QUEUE = queue.Queue()  # For sending button presses to action classes
LONG_PRESS_DURATION = 1.1  # Long press threshold (in seconds)
RELEASE_WAIT_TIME = 0.17
LIVES_IN_GAME = 3

UHM = UnicornHATMini()
DISPLAY = Display(UHM)


SHUTDOWN_FLAG = threading.Event()