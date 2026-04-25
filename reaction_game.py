import time
from random import choice, uniform, sample, randint, Random

import numpy as np

from globals import DISPLAY, LIVES_IN_GAME, TEXT
from animations import Animation
from utils import empty_queue

def vary_randomly(value, _range=0.5):
    portion = value * _range
    return uniform(value - portion, value + portion)


BLINKING_POSITIONS = {
    "A": ([1, 1, 2, 2], [1, 2, 1, 2]),
    "X": ([1, 1, 2, 2], [14, 15, 14, 15]),
    "B": ([4, 4, 5, 5], [1, 2, 1, 2]),
    "Y": ([4, 4, 5, 5], [14, 15, 14, 15])
}
NON_RED_COLORS = [(0, 255, 0), (0, 0, 255)]
SIMON_BUTTONS = ["A", "X", "B", "Y"]


def _generate_simon_sequences(seed, max_length, count):
    rng = Random(seed)
    out = {}
    for n in range(1, max_length + 1):
        out[n] = [tuple(rng.choice(SIMON_BUTTONS) for _ in range(n)) for _ in range(count)]
    return out


SIMON_SEQUENCES = _generate_simon_sequences(seed=42, max_length=15, count=3)


class ReactionLevelOne:
    def __init__(self, action_queue, display=DISPLAY, animation = Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.display_array = np.full((7, 17), False)  # that's the screen resolution
        self.blinking_positions = {
            "A": ([1, 1, 2, 2], [1, 2, 1, 2]),
            "X": ([1, 1, 2, 2], [14, 15, 14, 15]),
            "B": ([4, 4, 5, 5], [1, 2, 1, 2]),
            "Y": ([4, 4, 5, 5], [14, 15, 14, 15])
        }
        self.can_blink = list(self.blinking_positions)
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.5, failure_screen_time=0.5, winning=15):
        lives = LIVES_IN_GAME
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if lives == 0:
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if winning_count == winning:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            button_to_blink = choice(self.can_blink)
            empty_queue(self.action_queue)
            self.display_array[self.blinking_positions[button_to_blink]] = True
            self.display.show_image(self.display_array)
            blink_start = time.time()
            self.display_array[self.blinking_positions[button_to_blink]] = False

            while self.running and self.action_queue.empty():
                time.sleep(0.005)

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            if reaction_time > valid_reaction_time:
                lives -= 1
                self.animation.life_lost(lives)
                self.display.clear_leds()

                time.sleep(pause_between_challenges - failure_screen_time)
                continue

            if button_press["combination"] == button_to_blink:
                winning_count += 1
                to_display = str(reaction_time)[:3]
                self.display.show_text(to_display)
            else:
                lives -= 1
                self.animation.life_lost(lives)


            time.sleep(pause_between_challenges)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


class ReactionLevelTwo:
    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.display_array = np.full((7, 17), False)  # that's the screen resolution
        self.blinking_positions = {
            "A": ([1, 1, 2, 2], [1, 2, 1, 2]),
            "X": ([1, 1, 2, 2], [14, 15, 14, 15]),
            "B": ([4, 4, 5, 5], [1, 2, 1, 2]),
            "Y": ([4, 4, 5, 5], [14, 15, 14, 15])
        }
        self.can_blink = list(self.blinking_positions)
        self.colors = ((0,0,255),(255,0,0))
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.5, failure_screen_time=0.3, display_time=1, winning=15):
        lives = LIVES_IN_GAME
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if lives == 0:
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if winning_count == winning:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            button_to_blink = choice(self.can_blink)
            color_to_blink = choice(self.colors)
            empty_queue(self.action_queue)
            self.display_array[self.blinking_positions[button_to_blink]] = True
            self.display.show_image(array=self.display_array, color=color_to_blink)
            blink_start = time.time()
            self.display_array[self.blinking_positions[button_to_blink]] = False

            timeout = False
            while self.running and self.action_queue.empty() and not timeout:
                timeout = (time.time() - blink_start) > display_time
                time.sleep(0.005)

            if timeout:
                time.sleep(pause_between_challenges - display_time)
                self.display.clear_leds()
                continue

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            if reaction_time > valid_reaction_time:
                lives -= 1
                self.animation.life_lost(lives)
                self.display.clear_leds()

                time.sleep(vary_randomly(pause_between_challenges - failure_screen_time))
                continue

            if button_press["combination"] == button_to_blink and color_to_blink == (255,0,0):
                winning_count += 1
                to_display = str(reaction_time)[:3]
                self.display.show_text(to_display)
            else:
                lives -= 1
                self.animation.life_lost(lives)

            time.sleep(vary_randomly(pause_between_challenges))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


class ReactionLevelThree:
    """Combo press — two corners blink red, both must be pressed."""
    PAIRS = ["AB", "AX", "AY", "BX", "BY", "XY"]

    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.display_array = np.full((7, 17), False)
        self.blinking_positions = BLINKING_POSITIONS
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.7, failure_screen_time=0.5, winning=15):
        lives = LIVES_IN_GAME
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if lives == 0:
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if winning_count == winning:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            pair = choice(self.PAIRS)
            empty_queue(self.action_queue)
            for b in pair:
                self.display_array[self.blinking_positions[b]] = True
            self.display.show_image(self.display_array)
            blink_start = time.time()
            for b in pair:
                self.display_array[self.blinking_positions[b]] = False

            while self.running and self.action_queue.empty():
                time.sleep(0.005)

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            if reaction_time > valid_reaction_time:
                lives -= 1
                self.animation.life_lost(lives)
                self.display.clear_leds()

                time.sleep(pause_between_challenges - failure_screen_time)
                continue

            if button_press["combination"] == pair:
                winning_count += 1
                to_display = str(reaction_time)[:3]
                self.display.show_text(to_display)
            else:
                lives -= 1
                self.animation.life_lost(lives)

            time.sleep(pause_between_challenges)

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


class ReactionLevelFour:
    """Decoy — 3 corners blink in red/green/blue, exactly one red. Press red corner."""

    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.display_array = np.full((7, 17), False)
        self.blinking_positions = BLINKING_POSITIONS
        self.buttons = list(self.blinking_positions)
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def _build_frame(self, corners, red_corner):
        array = np.full((7, 17), False)
        colors = np.zeros((7, 17, 3), dtype=np.uint8)
        for c in corners:
            ys, xs = self.blinking_positions[c]
            array[ys, xs] = True
            color = (255, 0, 0) if c == red_corner else choice(NON_RED_COLORS)
            for y, x in zip(ys, xs):
                colors[y, x] = color
        return array, colors

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.5, failure_screen_time=0.3,
            display_time=1.2, winning=15):
        lives = LIVES_IN_GAME
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if lives == 0:
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if winning_count == winning:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            corners = sample(self.buttons, 3)
            red_corner = choice(corners)
            array, colors = self._build_frame(corners, red_corner)

            empty_queue(self.action_queue)
            self.display.show_image_color_each_led(array, colors)
            blink_start = time.time()

            timeout = False
            while self.running and self.action_queue.empty() and not timeout:
                timeout = (time.time() - blink_start) > display_time
                time.sleep(0.005)

            self.display.clear_leds()

            if timeout:
                lives -= 1
                self.animation.life_lost(lives)
                time.sleep(vary_randomly(pause_between_challenges - failure_screen_time))
                continue

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            if reaction_time > valid_reaction_time:
                lives -= 1
                self.animation.life_lost(lives)
                self.display.clear_leds()
                time.sleep(vary_randomly(pause_between_challenges - failure_screen_time))
                continue

            if button_press["combination"] == red_corner:
                winning_count += 1
                to_display = str(reaction_time)[:3]
                self.display.show_text(to_display)
            else:
                lives -= 1
                self.animation.life_lost(lives)

            time.sleep(vary_randomly(pause_between_challenges))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


class ReactionLevelFive:
    """Multi-decoy — all 4 corners blink, 1 or 2 red. Press combination of reds."""

    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.display_array = np.full((7, 17), False)
        self.blinking_positions = BLINKING_POSITIONS
        self.buttons = list(self.blinking_positions)
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def _build_frame(self, red_corners):
        array = np.full((7, 17), False)
        colors = np.zeros((7, 17, 3), dtype=np.uint8)
        for c in self.buttons:
            ys, xs = self.blinking_positions[c]
            array[ys, xs] = True
            color = (255, 0, 0) if c in red_corners else choice(NON_RED_COLORS)
            for y, x in zip(ys, xs):
                colors[y, x] = color
        return array, colors

    def run(self, pause_between_challenges=1.5, valid_reaction_time=0.8, failure_screen_time=0.3,
            display_time=1.5, winning=15):
        lives = LIVES_IN_GAME
        winning_count = 0
        while self.running:
            if not self.start_sequence_ran:
                self.start_sequence()
            if lives == 0:
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            if winning_count == winning:
                self.animation.winning()
                self.display.start_text_in_loop(TEXT.get("ABXY"))
                break

            n_red = randint(1, 2)
            red_corners = sample(self.buttons, n_red)
            expected = ''.join(sorted(red_corners))
            array, colors = self._build_frame(red_corners)

            empty_queue(self.action_queue)
            self.display.show_image_color_each_led(array, colors)
            blink_start = time.time()

            timeout = False
            while self.running and self.action_queue.empty() and not timeout:
                timeout = (time.time() - blink_start) > display_time
                time.sleep(0.005)

            self.display.clear_leds()

            if timeout:
                lives -= 1
                self.animation.life_lost(lives)
                time.sleep(vary_randomly(pause_between_challenges - failure_screen_time))
                continue

            if not self.running:
                self.stop()

            button_press = self.action_queue.get()
            reaction_time = button_press["press_time"] - blink_start
            if reaction_time > valid_reaction_time:
                lives -= 1
                self.animation.life_lost(lives)
                self.display.clear_leds()
                time.sleep(vary_randomly(pause_between_challenges - failure_screen_time))
                continue

            if button_press["combination"] == expected:
                winning_count += 1
                to_display = str(reaction_time)[:3]
                self.display.show_text(to_display)
            else:
                lives -= 1
                self.animation.life_lost(lives)

            time.sleep(vary_randomly(pause_between_challenges))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


class ReactionLevelSix:
    """Simon — fixed deterministic sequences. Length grows 1..15. Repeat full sequence."""

    def __init__(self, action_queue, display=DISPLAY, animation=Animation):
        self.action_queue = action_queue
        self.running = True
        self.display = display
        self.animation = animation(display)
        self.display_array = np.full((7, 17), False)
        self.blinking_positions = BLINKING_POSITIONS
        self.start_sequence_ran = False

    def start_sequence(self, count_down_time=0.6):
        for i in ["3", "2", "1"]:
            self.display.show_text(i)
            time.sleep(count_down_time)
        self.start_sequence_ran = True

    def get_sequence(self, length, attempt):
        pool = SIMON_SEQUENCES[length]
        return pool[attempt % len(pool)]

    def play_sequence(self, sequence, on_time=0.4, gap=0.15):
        for b in sequence:
            self.display_array[self.blinking_positions[b]] = True
            self.display.show_image(self.display_array)
            time.sleep(on_time)
            self.display_array[self.blinking_positions[b]] = False
            self.display.clear_leds()
            time.sleep(gap)

    def read_press(self, window):
        start = time.time()
        while self.running and self.action_queue.empty():
            if time.time() - start > window:
                return None
            time.sleep(0.005)
        if not self.running or self.action_queue.empty():
            return None
        return self.action_queue.get()

    def run(self, per_button_window=0.75, max_length=15):
        lives = LIVES_IN_GAME
        if not self.start_sequence_ran:
            self.start_sequence()

        for length in range(1, max_length + 1):
            attempt = 0
            cleared = False
            while not cleared and self.running:
                if lives == 0:
                    self.display.start_text_in_loop(TEXT.get("ABXY"))
                    return

                sequence = self.get_sequence(length, attempt)
                attempt += 1

                self.play_sequence(sequence)
                time.sleep(1.5)
                self.display.show_text("R", cycles=5)
                time.sleep(0.5)
                empty_queue(self.action_queue)
                self.display.show_text("G", cycles=3)

                failed = False
                for expected in sequence:
                    press = self.read_press(per_button_window)
                    if not self.running:
                        self.stop()
                        return
                    if press is None or press["combination"] != expected:
                        failed = True
                        break

                if failed:
                    lives -= 1
                    self.animation.life_lost(lives)
                    self.display.clear_leds()
                    time.sleep(1.0)
                else:
                    cleared = True
                    self.display.show_text(str(length), cycles=2)
                    time.sleep(0.3)

            if not self.running:
                return

        self.animation.winning()
        self.display.start_text_in_loop(TEXT.get("ABXY"))

    def stop(self):
        self.running = False
        self.display.stop()
        time.sleep(0.05)


class ReactionLevelSeven(ReactionLevelSix):
    """Simon — fully random sequences each play. Length grows 1..15."""

    def get_sequence(self, length, attempt):
        return tuple(choice(SIMON_BUTTONS) for _ in range(length))
