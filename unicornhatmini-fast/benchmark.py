"""Benchmark comparing original vs optimized UnicornHATMini.

Run on the Raspberry Pi to measure actual performance.
Measures three operations:
  1. set_pixel loop (119 calls) + show()
  2. set_all + show()
  3. set_pixels (bulk numpy) + show()  [optimized lib only]
"""

import time
import numpy as np


def bench(label, fn, iterations=200):
    # warmup
    for _ in range(10):
        fn()
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    elapsed = time.perf_counter() - start
    fps = iterations / elapsed
    ms_per_frame = (elapsed / iterations) * 1000
    print(f"  {label}: {ms_per_frame:.2f} ms/frame ({fps:.1f} FPS)")


def run_benchmark():
    from unicornhatmini import UnicornHATMini

    uh = UnicornHATMini()
    uh.set_brightness(0.05)

    print("Benchmarking optimized library...")

    # 1. Per-pixel set_pixel + show
    def test_set_pixel():
        for y in range(7):
            for x in range(17):
                uh.set_pixel(x, y, 255, 0, 0)
        uh.show()

    bench("set_pixel loop + show", test_set_pixel)

    # 2. set_all + show
    def test_set_all():
        uh.set_all(0, 255, 0)
        uh.show()

    bench("set_all + show", test_set_all)

    # 3. set_pixels (bulk) + show
    mask = np.ones((7, 17), dtype=bool)
    color = (0, 0, 255)

    def test_set_pixels_uniform():
        uh.set_pixels(mask, color)
        uh.show()

    bench("set_pixels uniform + show", test_set_pixels_uniform)

    # 4. set_pixels with per-pixel colours + show
    colors = np.full((7, 17, 3), (255, 128, 0), dtype=np.uint8)

    def test_set_pixels_percolor():
        uh.set_pixels(mask, colors)
        uh.show()

    bench("set_pixels per-pixel + show", test_set_pixels_percolor)

    # 5. Sparse mask (typical game frame ~20 active pixels)
    sparse_mask = np.zeros((7, 17), dtype=bool)
    sparse_mask[0, 0] = True
    sparse_mask[3, 8] = True
    sparse_mask[6, 16] = True
    for i in range(17):
        sparse_mask[3, i] = True

    def test_set_pixels_sparse():
        uh.set_pixels(sparse_mask, (255, 255, 255))
        uh.show()

    bench("set_pixels sparse + show", test_set_pixels_sparse)

    uh.clear()
    uh.show()
    print("Done.")


if __name__ == "__main__":
    run_benchmark()
