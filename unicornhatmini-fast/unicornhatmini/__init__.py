#!/usr/bin/env python3
"""Optimized driver for Pimoroni Unicorn HAT Mini (17x7 RGB LED matrix).

Drop-in replacement for the official library with numpy-accelerated bulk
operations and bytearray-based SPI transfers. All Python-level pixel loops
in the hot path have been replaced with vectorized numpy operations.

Compatible with both RPi.GPIO and rpi-lgpio (drop-in on Bookworm+).
"""

import atexit

import numpy as np
import spidev

import RPi.GPIO as GPIO

__version__ = '1.0.0'

# Holtek HT16D35 commands
CMD_SOFT_RESET = 0xCC
CMD_GLOBAL_BRIGHTNESS = 0x37
CMD_COM_PIN_CTRL = 0x41
CMD_ROW_PIN_CTRL = 0x42
CMD_WRITE_DISPLAY = 0x80
CMD_READ_DISPLAY = 0x81
CMD_SYSTEM_CTRL = 0x35
CMD_SCROLL_CTRL = 0x20

_COLS = 17
_ROWS = 7
_NUM_PIXELS = _COLS * _ROWS  # 119
_BUF_SIZE = 28 * 8  # 224 bytes per matrix, 448 total

BUTTON_A = 5
BUTTON_B = 6
BUTTON_X = 16
BUTTON_Y = 24

# Raw LUT from the original library: maps pixel index to (R, G, B) buffer positions
_RAW_LUT = [
    [139, 138, 137], [223, 222, 221], [167, 166, 165], [195, 194, 193],
    [111, 110, 109], [55, 54, 53], [83, 82, 81], [136, 135, 134],
    [220, 219, 218], [164, 163, 162], [192, 191, 190], [108, 107, 106],
    [52, 51, 50], [80, 79, 78], [113, 115, 114], [197, 199, 198],
    [141, 143, 142], [169, 171, 170], [85, 87, 86], [29, 31, 30],
    [57, 59, 58], [116, 118, 117], [200, 202, 201], [144, 146, 145],
    [172, 174, 173], [88, 90, 89], [32, 34, 33], [60, 62, 61],
    [119, 121, 120], [203, 205, 204], [147, 149, 148], [175, 177, 176],
    [91, 93, 92], [35, 37, 36], [63, 65, 64], [122, 124, 123],
    [206, 208, 207], [150, 152, 151], [178, 180, 179], [94, 96, 95],
    [38, 40, 39], [66, 68, 67], [125, 127, 126], [209, 211, 210],
    [153, 155, 154], [181, 183, 182], [97, 99, 98], [41, 43, 42],
    [69, 71, 70], [128, 130, 129], [212, 214, 213], [156, 158, 157],
    [184, 186, 185], [100, 102, 101], [44, 46, 45], [72, 74, 73],
    [131, 133, 132], [215, 217, 216], [159, 161, 160], [187, 189, 188],
    [103, 105, 104], [47, 49, 48], [75, 77, 76], [363, 362, 361],
    [447, 446, 445], [391, 390, 389], [419, 418, 417], [335, 334, 333],
    [279, 278, 277], [307, 306, 305], [360, 359, 358], [444, 443, 442],
    [388, 387, 386], [416, 415, 414], [332, 331, 330], [276, 275, 274],
    [304, 303, 302], [337, 339, 338], [421, 423, 422], [365, 367, 366],
    [393, 395, 394], [309, 311, 310], [253, 255, 254], [281, 283, 282],
    [340, 342, 341], [424, 426, 425], [368, 370, 369], [396, 398, 397],
    [312, 314, 313], [256, 258, 257], [284, 286, 285], [343, 345, 344],
    [427, 429, 428], [371, 373, 372], [399, 401, 400], [315, 317, 316],
    [259, 261, 260], [287, 289, 288], [346, 348, 347], [430, 432, 431],
    [374, 376, 375], [402, 404, 403], [318, 320, 319], [262, 264, 263],
    [290, 292, 291], [349, 351, 350], [433, 435, 434], [377, 379, 378],
    [405, 407, 406], [321, 323, 322], [265, 267, 266], [293, 295, 294],
    [352, 354, 353], [436, 438, 437], [380, 382, 381], [408, 410, 409],
    [324, 326, 325], [268, 270, 269], [296, 298, 297],
]


def _build_offset_table(rotation):
    """Pre-compute a (width, height) -> flat offset mapping for a given rotation.

    For rotations 0/180, display shape is (17, 7) so table is (17, 7).
    For rotations 90/270, display shape is (7, 17) so table is (7, 17).
    Table is indexed as table[x, y] matching the set_pixel(x, y, ...) convention.
    """
    if rotation in (90, 270):
        w, h = _ROWS, _COLS
    else:
        w, h = _COLS, _ROWS

    table = np.empty((w, h), dtype=np.intp)
    for x in range(w):
        for y in range(h):
            if rotation == 0:
                table[x, y] = x * _ROWS + y
            elif rotation == 90:
                table[x, y] = (_COLS - 1 - y) * _ROWS + x
            elif rotation == 180:
                table[x, y] = (_COLS - 1 - x) * _ROWS + (_ROWS - 1 - y)
            elif rotation == 270:
                table[x, y] = y * _ROWS + (_ROWS - 1 - x)
    return table


class UnicornHATMini:
    def __init__(self, spi_max_speed_hz=600000):
        """Initialise unicornhatmini.

        :param spi_max_speed_hz: SPI speed in Hz
        """
        # Display buffer: flat array of interleaved RGB, 6-bit per channel
        self.disp = np.zeros((_NUM_PIXELS, 3), dtype=np.uint8)

        # SPI output buffer as bytearray for writebytes2
        self.buf = bytearray(_BUF_SIZE * 2)

        # Pre-compute LUT as numpy index arrays for vectorized show()
        lut_arr = np.array(_RAW_LUT, dtype=np.intp)  # (119, 3)
        self._lut_r = lut_arr[:, 0]
        self._lut_g = lut_arr[:, 1]
        self._lut_b = lut_arr[:, 2]
        # numpy view over the bytearray for fancy indexing in show()
        self._buf_np = np.frombuffer(self.buf, dtype=np.uint8)

        # Pre-compute offset tables for all rotations (done once)
        self._offset_tables = {r: _build_offset_table(r) for r in (0, 90, 180, 270)}
        self._rotation = 0
        self._offset_table = self._offset_tables[0]

        # Pre-allocate SPI command buffers (header + payload, no alloc in show())
        self._spi_buf_left = bytearray(2 + _BUF_SIZE)
        self._spi_buf_right = bytearray(2 + _BUF_SIZE)
        self._spi_buf_left[0] = CMD_WRITE_DISPLAY
        self._spi_buf_right[0] = CMD_WRITE_DISPLAY
        # second byte is 0x00 (already zero from bytearray init)

        # SPI setup
        self.left_matrix = (spidev.SpiDev(0, 0), 8, 0, self._spi_buf_left)
        self.right_matrix = (spidev.SpiDev(0, 1), 7, _BUF_SIZE, self._spi_buf_right)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for device, pin, _, _ in (self.left_matrix, self.right_matrix):
            device.no_cs = True
            device.max_speed_hz = spi_max_speed_hz
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
            self._xfer(device, pin, [CMD_SOFT_RESET])
            self._xfer(device, pin, [CMD_GLOBAL_BRIGHTNESS, 0x01])
            self._xfer(device, pin, [CMD_SCROLL_CTRL, 0x00])
            self._xfer(device, pin, [CMD_SYSTEM_CTRL, 0x00])
            self._xfer(device, pin, [CMD_WRITE_DISPLAY, 0x00] + [0] * _BUF_SIZE)
            self._xfer(device, pin, [CMD_COM_PIN_CTRL, 0xff])
            self._xfer(device, pin, [CMD_ROW_PIN_CTRL, 0xff, 0xff, 0xff, 0xff])
            self._xfer(device, pin, [CMD_SYSTEM_CTRL, 0x03])

        atexit.register(self._exit)

    def _xfer(self, device, pin, command):
        GPIO.output(pin, GPIO.LOW)
        device.xfer2(command)
        GPIO.output(pin, GPIO.HIGH)

    def _write(self, device, pin, data):
        """Write-only SPI transfer using writebytes2 (faster than xfer2)."""
        GPIO.output(pin, GPIO.LOW)
        device.writebytes2(data)
        GPIO.output(pin, GPIO.HIGH)

    def _shutdown(self):
        for device, pin, _, _ in (self.left_matrix, self.right_matrix):
            self._xfer(device, pin, [CMD_COM_PIN_CTRL, 0x00])
            self._xfer(device, pin, [CMD_ROW_PIN_CTRL, 0x00, 0x00, 0x00, 0x00])
            self._xfer(device, pin, [CMD_SYSTEM_CTRL, 0x00])

    def _exit(self):
        self._shutdown()

    def set_rotation(self, rotation=0):
        """Set display rotation (0, 90, 180, 270)."""
        if rotation not in (0, 90, 180, 270):
            raise ValueError("Rotation must be one of 0, 90, 180, 270")
        self._rotation = rotation
        self._offset_table = self._offset_tables[rotation]

    def get_shape(self):
        """Return (width, height) accounting for rotation."""
        if self._rotation in (90, 270):
            return _ROWS, _COLS
        return _COLS, _ROWS

    def set_pixel(self, x, y, r, g, b):
        """Set a single pixel (backward-compatible)."""
        offset = self._offset_table[x, y]
        self.disp[offset, 0] = r >> 2
        self.disp[offset, 1] = g >> 2
        self.disp[offset, 2] = b >> 2

    def set_all(self, r, g, b):
        """Set all pixels to the same colour."""
        self.disp[:, 0] = r >> 2
        self.disp[:, 1] = g >> 2
        self.disp[:, 2] = b >> 2

    def set_pixels(self, mask, colors):
        """Bulk-set pixels from a boolean mask and colour array.

        This is the fast path for game rendering — no Python pixel loops.
        Assumes rotation 0 (mask shape is (height=7, width=17)).

        :param mask: (7, 17) boolean numpy array — True = pixel on
        :param colors: Either an (R, G, B) tuple for uniform colour,
                       or a (7, 17, 3) uint8 numpy array for per-pixel colours.
        """
        self.disp[:] = 0  # clear

        # mask is (rows, cols) = (7, 17) indexed as [y, x]
        # _offset_table is (width, height) indexed as [x, y]
        ys, xs = np.where(mask)
        if len(xs) == 0:
            return

        offsets = self._offset_table[xs, ys]

        if isinstance(colors, tuple):
            self.disp[offsets, 0] = colors[0] >> 2
            self.disp[offsets, 1] = colors[1] >> 2
            self.disp[offsets, 2] = colors[2] >> 2
        else:
            pixel_colors = colors[ys, xs]  # (N, 3)
            self.disp[offsets] = pixel_colors >> 2

    def set_image(self, image, offset_x=0, offset_y=0, wrap=False, bg_color=(0, 0, 0)):
        """Set a PIL image to the display buffer (backward-compatible).

        For best performance with numpy arrays, use set_pixels() instead.
        """
        image_width, image_height = image.size

        if image.mode != "RGB":
            image = image.convert("RGB")

        display_width, display_height = self.get_shape()

        # Convert PIL image to numpy array once (avoid per-pixel getpixel)
        img_arr = np.asarray(image)  # (height, width, 3)

        for y in range(display_height):
            for x in range(display_width):
                i_x = x + offset_x
                i_y = y + offset_y
                if wrap:
                    i_x = i_x % image_width
                    i_y = i_y % image_height
                if 0 <= i_x < image_width and 0 <= i_y < image_height:
                    r, g, b = img_arr[i_y, i_x]
                else:
                    r, g, b = bg_color
                offset = self._offset_table[x, y]
                self.disp[offset, 0] = r >> 2
                self.disp[offset, 1] = g >> 2
                self.disp[offset, 2] = b >> 2

    def clear(self):
        """Set all pixels to 0."""
        self.disp[:] = 0

    def set_brightness(self, b=0.2):
        """Set global brightness (0.0 to 1.0)."""
        for device, pin, _, _ in (self.left_matrix, self.right_matrix):
            self._xfer(device, pin, [CMD_GLOBAL_BRIGHTNESS, int(63 * b)])

    def show(self):
        """Push the display buffer to the hardware via SPI.

        Uses numpy fancy indexing to scatter RGB values into the LUT-mapped
        buffer positions, then writebytes2 for the SPI transfer.
        Zero allocations in the hot path.
        """
        buf = self._buf_np

        # Vectorized LUT scatter — replaces the 119-iteration Python loop
        buf[self._lut_r] = self.disp[:, 0]
        buf[self._lut_g] = self.disp[:, 1]
        buf[self._lut_b] = self.disp[:, 2]

        # Copy into pre-allocated SPI command buffers (payload starts at byte 2)
        for device, pin, offset, spi_buf in (self.left_matrix, self.right_matrix):
            spi_buf[2:] = self.buf[offset:offset + _BUF_SIZE]
            self._write(device, pin, spi_buf)


if __name__ == "__main__":
    import time
    from colorsys import hsv_to_rgb

    unicornhatmini = UnicornHATMini()

    while True:
        for y in range(_ROWS):
            for x in range(_COLS):
                hue = (time.time() / 4.0) + (x / float(_COLS * 2)) + (y / float(_ROWS))
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                unicornhatmini.set_pixel(x, y, r, g, b)
        unicornhatmini.show()
        time.sleep(1.0 / 60)
