from PIL import Image
import numpy as np
import time

class Shapes:
    heart_filled = np.array(
        [
            [0, 1, 1, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ]
    ).astype(bool)
    heart_one_lost = np.array(
        [
            [0, 1, 1, 0, 1, 1, 0],
            [1, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ]
    ).astype(bool)
    heart_two_lost = np.array(
        [
            [0, 1, 1, 0, 1, 1, 0],
            [1, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ]
    ).astype(bool)
    heart_empty = np.array(
        [
            [0, 1, 1, 0, 1, 1, 0],
            [1, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
         ]
    ).astype(bool)

    check = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0],
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ]
    ).astype(bool)
    cross = np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ]
    ).astype(bool)

    def show_shapes(self, display):
        for name in dir(self):
            if not name.startswith("_") and name != "show_shapes":
                shape = getattr(self, name)
                display.show_image(shape, padding=True)
                time.sleep(2)
                display.clear_leds()
                time.sleep(1)

if __name__ == "__main__":
    def simplify_image(in_file, alpha_cut_off=128, bw_cut_off=128):
        original = Image.open(in_file)
        ar = np.asarray(original).copy()
        ar[ar[:, :, 0] > alpha_cut_off] = 0
        simplified = np.max(ar, axis=2)
        simplified[simplified <= bw_cut_off] = 0
        simplified = simplified.astype("bool")
        original.close()
        return simplified

    #print(repr(simplify_image(
    #    '/Users/foech/Downloads/Love_Heart_SVG.png',
    #)))
    from globals import DISPLAY
    Shapes().show_shapes(DISPLAY)