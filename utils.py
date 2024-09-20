import numpy as np
from PIL import ImageFont, ImageDraw, Image
from numpy.lib.stride_tricks import as_strided


def empty_queue(queue):
    while not queue.empty():
        queue.get()


def get_text_size(font: ImageFont, text):
    if hasattr(font, "getsize"):
        return font.getsize(text)
    else:
        return font.font.getsize(text)[0]


def text_to_image(text, display_w=17, display_h=7, font=ImageFont.truetype("5x7.ttf", 8)):
    text_width, text_height = get_text_size(font, text)
    # 2 * display width for padding
    image = Image.new('P', (text_width + 2 * display_w, display_h), 0)
    draw = ImageDraw.Draw(image)
    draw.text((display_w, -1), text, font=font, fill=1)
    return image


def extract_windows(array, window_width=17, window_height=7):
    height, width = array.shape
    shape = (width - window_width + 1, height - window_height + 1, window_height, window_width)
    strides = (array.strides[1], array.strides[0], array.strides[0], array.strides[1])
    windows = as_strided(array, shape=shape, strides=strides)
    return windows.transpose(1, 0, 2, 3)[0]


def image_to_arrays(image: Image, desired_width=17, short_padding=5, short_factor=1.5):
    array = np.asarray(image)
    aw = array.shape[1]
    padding = 2 * desired_width
    if (img_size := (aw - padding)) < desired_width:  # text can be on the display without movement
        if (req_padding := (desired_width - img_size)) % 2 == 0:
            padding = req_padding // 2
            return [array[:, (desired_width - padding):-(desired_width - padding)]]
        else:
            padding = int(req_padding / 2)
            return [array[:, (desired_width - padding - 1):-(desired_width - padding)]]
    elif (aw - padding) < short_factor * desired_width:  # changed padding for short text
        boundaries = (desired_width - short_padding)
        return extract_windows(array[:, boundaries:-boundaries], desired_width)  # long text
    else:
        return extract_windows(array, desired_width)


def pad_array(array, w=17):
    cols_padding = (
        (w - array.shape[1]) // 2,
        (w - array.shape[1]) - (w - array.shape[1]) // 2
    )  # equal padding left and right
    return np.pad(array, ((0, 0), cols_padding), mode='constant', constant_values=False)