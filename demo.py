import threading
import time
import colorsys
import math
from unicornhatmini import UnicornHATMini

class GraphicsDemoAction:
    def __init__(self, action_queue=None, display=None):
        self.action_queue = action_queue
        self.unicornhatmini = UnicornHATMini()
        self.unicornhatmini.set_brightness(0.1)
        self.unicornhatmini.set_rotation(0)
        self.u_width, self.u_height = self.unicornhatmini.get_shape()
        self.running = True

        # Generate a lookup table for 8-bit hue to RGB conversion
        self.hue_to_rgb = [colorsys.hsv_to_rgb(i / 359.0, 1, 1) for i in range(0, 360)]

        self.effects = [self.tunnel, self.rainbow_search, self.checker, self.swirl]
        self.t_start = time.time()

    def swirl(self, x, y, step):
        x -= (self.u_width / 2)
        y -= (self.u_height / 2)
        dist = math.sqrt(pow(x, 2) + pow(y, 2)) / 2.0
        angle = (step / 10.0) + (dist * 1.5)
        s = math.sin(angle)
        c = math.cos(angle)
        xs = x * c - y * s
        ys = x * s + y * c
        r = abs(xs + ys)
        r = r * 12.0
        r -= 20
        return (r, r + (s * 130), r + (c * 130))

    def checker(self, x, y, step):
        x -= (self.u_width / 2)
        y -= (self.u_height / 2)
        angle = (step / 10.0)
        s = math.sin(angle)
        c = math.cos(angle)
        xs = x * c - y * s
        ys = x * s + y * c
        xs -= math.sin(step / 200.0) * 40.0
        ys -= math.cos(step / 200.0) * 40.0
        scale = step % 20
        scale /= 20
        scale = (math.sin(step / 50.0) / 8.0) + 0.25
        xs *= scale
        ys *= scale
        xo = abs(xs) - int(abs(xs))
        yo = abs(ys) - int(abs(ys))
        v = 0 if (math.floor(xs) + math.floor(ys)) % 2 else 1 if xo > .1 and yo > .1 else .5
        r, g, b = self.hue_to_rgb[int(step) % 255]
        return (r * (v * 255), g * (v * 255), b * (v * 255))

    def rainbow_search(self, x, y, step):
        xs = math.sin((step) / 100.0) * 20.0
        ys = math.cos((step) / 100.0) * 20.0
        scale = ((math.sin(step / 60.0) + 1.0) / 5.0) + 0.2
        r = math.sin((x + xs) * scale) + math.cos((y + xs) * scale)
        g = math.sin((x + xs) * scale) + math.cos((y + ys) * scale)
        b = math.sin((x + ys) * scale) + math.cos((y + ys) * scale)
        return (r * 255, g * 255, b * 255)

    def tunnel(self, x, y, step):
        speed = step / 100.0
        x -= (self.u_width / 2)
        y -= (self.u_height / 2)
        xo = math.sin(step / 27.0) * 2
        yo = math.cos(step / 18.0) * 2
        x += xo
        y += yo
        if y == 0:
            if x < 0:
                angle = -(math.pi / 2)
            else:
                angle = (math.pi / 2)
        else:
            angle = math.atan(x / y)
        if y > 0:
            angle += math.pi
        angle /= 2 * math.pi  # convert angle to 0...1 range
        hyp = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
        shade = hyp / 2.1
        shade = 1 if shade > 1 else shade
        angle += speed
        depth = speed + (hyp / 10)
        col1 = self.hue_to_rgb[int(step) % 359]
        col1 = (col1[0] * 0.8, col1[1] * 0.8, col1[2] * 0.8)
        col2 = self.hue_to_rgb[int(step) % 359]
        col2 = (col2[0] * 0.3, col2[1] * 0.3, col2[2] * 0.3)
        col = col1 if int(abs(angle * 6.0)) % 2 == 0 else col2
        td = .3 if int(abs(depth * 3.0)) % 2 == 0 else 0
        col = (col[0] + td, col[1] + td, col[2] + td)
        col = (col[0] * shade, col[1] * shade, col[2] * shade)
        return (col[0] * 255, col[1] * 255, col[2] * 255)

    def run(self):
        """Main loop to run the graphical demo."""
        self.t_start = time.time()

        try:
            while self.running:
                t = time.time() - self.t_start
                step = (t * 50)
                f = t / 10.0
                fx = int(f) % len(self.effects)
                next_fx = (fx + 1) % len(self.effects)

                for y in range(self.u_height):
                    for x in range(self.u_width):
                        r, g, b = self.effects[fx](x, y, step)
                        if f % 1.0 > 0.75:
                            r2, g2, b2 = self.effects[next_fx](x, y, step)
                            ratio = (1.0 - (f % 1.0)) / 0.25
                            r = r * ratio + r2 * (1.0 - ratio)
                            g = g * ratio + g2 * (1.0 - ratio)
                            b = b * ratio + b2 * (1.0 - ratio)
                        r = int(max(0, min(255, r)))
                        g = int(max(0, min(255, g)))
                        b = int(max(0, min(255, b)))
                        self.unicornhatmini.set_pixel(x, y, r, g, b)

                self.unicornhatmini.show()
                time.sleep(1.0 / 60.0)

        except KeyboardInterrupt:
            pass

    def stop(self):
        self.running = False
        print("Stopping Graphics Demo")

