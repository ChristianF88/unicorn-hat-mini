import threading
import time
import RPi.GPIO as GPIO
from queue import Queue, Empty

from globals import BUTTON_MAP, ACTION_QUEUE, MENU_QUEUE, LONG_PRESS_DURATION, RELEASE_WAIT_TIME, TEXT_DISPLAY
from menu import Menu


GPIO.setmode(GPIO.BCM)
EVENT_QUEUE = Queue()

# Setup buttons with internal pull-up resistors
for pin in BUTTON_MAP.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button_states = {name: {'press_time': None, 'pressed': False} for name in BUTTON_MAP.values()}
shutdown_flag = threading.Event()


def button_listener():
    while not shutdown_flag.is_set():
        for pin, name in BUTTON_MAP.items():
            if GPIO.input(pin) == GPIO.LOW and not button_states[name]['pressed']:
                # Button is pressed, record press time and mark as pressed
                press_time = time.time()
                button_states[name]['pressed'] = True
                button_states[name]['press_time'] = press_time

            if GPIO.input(pin) == GPIO.HIGH and button_states[name]['pressed']:
                # Button is released, calculate press duration and queue the event
                release_time = time.time()
                duration = release_time - button_states[name]['press_time']
                EVENT_QUEUE.put({'button': name, 'press_time': button_states[name]['press_time'], 'duration': duration})
                button_states[name]['pressed'] = False
                button_states[name]['press_time'] = None

        time.sleep(0.01)  # Sleep briefly to reduce CPU usage


def event_detector():
    while not shutdown_flag.is_set():
        event_log = []
        start_time = time.time()

        # Gather events from EVENT_QUEUE
        while (time.time() - start_time) < RELEASE_WAIT_TIME or not EVENT_QUEUE.empty():
            try:
                event = EVENT_QUEUE.get(timeout=0.01)
                event_log.append(event)
            except Empty:
                pass

        if event_log:
            analysis_result = event_analysis(event_log)
            if analysis_result:
                ACTION_QUEUE.put(analysis_result)
                MENU_QUEUE.put(analysis_result)

        time.sleep(0.01)  # Sleep briefly to reduce CPU usage


def event_analysis(event_log, long_press_duration=LONG_PRESS_DURATION):
    result = {'combination': None, 'press_type': 'single', 'stop_action': False}

    # Sort button press events by press time to maintain the correct order
    event_log.sort(key=lambda e: e['press_time'])

    pressed_buttons = sorted({e['button'] for e in event_log})
    combination_key = ''.join(pressed_buttons)
    result['combination'] = combination_key

    # Determine if a long press occurred
    long_press_detected = False
    for event in event_log:
        if event['duration'] >= long_press_duration:
            result['press_type'] = 'long'
            long_press_detected = True
            break

    if not long_press_detected:
        result['press_type'] = 'single'  # Default to single press if no long press detected

    # Special case: if all four buttons are pressed and held long, stop the action
    if all(button in pressed_buttons for button in ['A', 'B', 'X', 'Y']) and result['press_type'] == 'long':
        result['stop_action'] = True

    print(result)  # Debugging output to verify event analysis
    return result


def main_program():
    # Start the button listener thread
    button_thread = threading.Thread(target=button_listener)
    button_thread.daemon = True
    button_thread.start()

    # Start the event detector thread
    detector_thread = threading.Thread(target=event_detector)
    detector_thread.daemon = True
    detector_thread.start()

    # Start the menu thread
    menu = Menu(MENU_QUEUE, ACTION_QUEUE, TEXT_DISPLAY)
    menu_thread = threading.Thread(target=menu.run)
    menu_thread.daemon = True
    menu_thread.start()

    try:
        while True:
            time.sleep(1)  # Main loop can handle other tasks or be replaced as needed
    except KeyboardInterrupt:
        print("Exiting...")
        shutdown_flag.set()  # Signal all threads to stop

        button_thread.join()
        detector_thread.join()
        menu.stop()
        menu_thread.join()

        TEXT_DISPLAY.stop_display()


if __name__ == "__main__":
    main_program()