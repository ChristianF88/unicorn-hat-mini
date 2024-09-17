import queue

from unicornhatmini import UnicornHATMini

from display import Display

DISPLAY_BRIGHTNESS = 0.03
BUTTON_MAP = {5: "A", 6: "B", 16: "X", 24: "Y"}
EVENT_QUEUE = queue.Queue()  # For event detection
MENU_QUEUE = queue.Queue()  # For sending button presses to action classes
ACTION_QUEUE = queue.Queue()  # For sending button presses to action classes
LONG_PRESS_DURATION = 1.1  # Long press threshold (in seconds)
RELEASE_WAIT_TIME = 0.17

UHM = UnicornHATMini()
DISPLAY = Display(UHM)
