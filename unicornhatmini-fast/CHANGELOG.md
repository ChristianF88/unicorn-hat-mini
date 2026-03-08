# Changelog

All changes relative to the [official Pimoroni unicornhatmini-python library](https://github.com/pimoroni/unicornhatmini-python) (v0.0.2).

## v1.0.0 — Optimized rewrite

### Performance: `show()` — LUT scatter (biggest win)

**Before:** A 119-iteration Python `for` loop copies RGB values from `self.disp`
into `self.buf` using the hardware LUT, one pixel at a time.

**After:** Three numpy fancy-index assignments scatter all 119 pixels in one
operation each. Measured **~16x faster** than the Python loop on desktop;
the speedup on RPi Zero W's single-core ARM11 will be larger since Python
loop overhead is proportionally more expensive there.

### Performance: `show()` — SPI transfer

**Before:** `xfer2()` with a Python `list[int]` built via concatenation
(`[CMD, 0x00] + self.buf[offset:...]`). Allocates a new list every frame.

**After:** `writebytes2()` with pre-allocated `bytearray` command buffers.
`writebytes2` is write-only (fine for this display) and ~20% faster than
`xfer2` because it accepts buffer-protocol objects directly without
converting from a Python list. Zero allocations in the hot path.

### Performance: `set_all()` and `clear()`

**Before:** `set_all()` uses a 119-iteration Python loop. `clear()` calls
`set_all(0, 0, 0)`.

**After:** `set_all()` uses three numpy slice assignments. `clear()` uses a
single `disp[:] = 0`. Both are constant-time numpy operations.

### Performance: `set_pixel()` — rotation handling

**Before:** Four `if` branches executed on every `set_pixel()` call to compute
the buffer offset based on the current rotation.

**After:** Rotation-aware offset tables are pre-computed for all four rotations
at init time. `set_pixel()` is now a single table lookup + three assignments.
`set_rotation()` just swaps which table is active.

### Performance: `set_image()` — PIL image reading

**Before:** `image.getpixel((x, y))` called per pixel (Python method call +
PIL internal lookup each time).

**After:** `np.asarray(image)` converts the image to a numpy array once,
then pixels are read via fast array indexing.

### New: `set_pixels(mask, colors)` — bulk rendering

A new method for game/animation rendering that accepts:
- A `(7, 17)` boolean numpy mask (True = pixel on)
- Either an `(R, G, B)` tuple (uniform colour) or a `(7, 17, 3)` uint8
  array (per-pixel colours)

This eliminates all Python-level pixel loops from the caller side entirely.
Combined with the vectorized `show()`, a full frame render goes from
~238 Python loop iterations + 119 function calls to ~3 numpy operations.

### Internal: buffer types

**Before:** `self.disp` is a Python `list` of 119 `[r, g, b]` lists.
`self.buf` is a Python `list` of 448 ints.

**After:** `self.disp` is a `numpy.ndarray` of shape `(119, 3)`, dtype `uint8`.
`self.buf` is a `bytearray(448)` with a numpy view (`np.frombuffer`) for
fancy indexing. The numpy view and bytearray share memory — writes through
one are visible in the other with zero copy.

### Compatibility

- **API**: Fully backward-compatible. All original methods (`set_pixel`,
  `set_all`, `set_image`, `clear`, `show`, `set_brightness`, `set_rotation`,
  `get_shape`) have identical signatures and behaviour.
- **RPi.GPIO**: Works as-is. For Raspberry Pi OS Bookworm+, swap to
  `rpi-lgpio` (drop-in replacement, same `import RPi.GPIO as GPIO`).
- **spidev**: Requires v3.5+ for `writebytes2()` support (current is v3.8).
- **Python**: Requires 3.7+ (same as numpy).
