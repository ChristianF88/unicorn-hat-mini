import threading
import time
from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini

DISPLAY_BRIGHTNESS= 0.06

class TextDisplay:
    def __init__(self, display_brightness=DISPLAY_BRIGHTNESS):
        self.unicornhatmini = UnicornHATMini()
        self.display_width, self.display_height = self.unicornhatmini.get_shape()
        self.unicornhatmini.set_brightness(display_brightness)
        self.font = ImageFont.truetype("5x7.ttf", 8)  # Load the 5x7 font
        self.offset_x = 0
        self.display_running = False  # A flag to control the text display thread
        self.display_thread = None
        self.cached_image = None  # Cache the image
        self.text_color = (255, 0, 0)  # Set a fixed red color (R, G, B)
        self.lock = threading.Lock()  # Lock for thread safety

    def create_text_image(self, text):
        """Pre-generate the image for the scrolling text."""
        text_width, text_height = self.font.getsize(text)
        image = Image.new('P', (text_width + self.display_width + self.display_width, self.display_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((self.display_width, -1), text, font=self.font, fill=255)
        return image

    def display_text(self, text):
        """Scrolls the text horizontally."""
        with self.lock:
            if self.cached_image is None:
                self.cached_image = self.create_text_image(text)

        image = self.cached_image
        image_width = image.size[0]

        while True:
            with self.lock:
                if not self.display_running:
                    break

                for y in range(self.display_height):
                    for x in range(self.display_width):
                        if image.getpixel((x + self.offset_x, y)) == 255:
                            # Set the fixed color
                            self.unicornhatmini.set_pixel(x, y, *self.text_color)
                        else:
                            self.unicornhatmini.set_pixel(x, y, 0, 0, 0)

                # Move the text horizontally
                self.offset_x += 1
                if self.offset_x + self.display_width > image_width:
                    self.offset_x = 0

                self.unicornhatmini.show()

            time.sleep(0.05)

    def display_centered_text(self, text):
        """Displays non-moving text centered on the display."""
        with self.lock:
            self.unicornhatmini.clear()

            # Get the size of the text
            text_width, text_height = self.font.getsize(text)

            # Calculate the top-left corner coordinates to center the text
            x_offset = (self.display_width - text_width) // 2
            y_offset = (self.display_height - text_height) // 2

            # Create a new image to draw the centered text
            image = Image.new('P', (self.display_width, self.display_height), 0)
            draw = ImageDraw.Draw(image)
            draw.text((x_offset, y_offset), text, font=self.font, fill=255)

            # Display the centered text
            for y in range(self.display_height):
                for x in range(self.display_width):
                    if image.getpixel((x, y)) == 255:
                        self.unicornhatmini.set_pixel(x, y, *self.text_color)
                    else:
                        self.unicornhatmini.set_pixel(x, y, 0, 0, 0)

            self.unicornhatmini.show()

    def start_display(self, text, moving_text=True):
        with self.lock:
            if not self.display_running:
                self.display_running = True
                self.cached_image = None  # Reset cache when starting a new display

                if moving_text:
                    self.display_thread = threading.Thread(target=self.display_text, args=(text,))
                else:
                    self.display_thread = threading.Thread(target=self.display_centered_text, args=(text,))

                self.display_thread.daemon = True
                self.display_thread.start()

    def stop_display(self):
        with self.lock:
            if self.display_running:
                self.display_running = False
                self.cached_image = None
                self.offset_x = 0

        # Wait for the display thread to finish
        if self.display_thread is not None:
            self.display_thread.join()

        self.display_thread = None

        # Clear the display
        with self.lock:
            self.unicornhatmini.clear()
            self.unicornhatmini.show()
