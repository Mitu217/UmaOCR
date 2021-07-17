import cv2
import numpy as np
from PIL import Image


def crop_pil(image, box, *, debug=False):
    cropped = image.crop(box)
    if debug:
        cropped.save('cropped.png')

    return cropped


def resize_pil(image, width=None, height=None, inter=Image.CUBIC):
    (w, h) = image.size

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = image.resize(dim, inter)

    return resized


def cv2pil(image_cv):
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_cv)
    image_pil = image_pil.convert('RGB')

    return image_pil


def pil2cv(image_pil):
    image_cv = np.asarray(image_pil)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
    return image_cv


def binarized(image: Image, r_border: int, g_border: int, b_border: int, *, reverse=False) -> Image:
    image = image.convert('RGB')
    size = image.size

    binarized_image = Image.new('RGB', size)

    for x in range(size[0]):
        for y in range(size[1]):
            r, g, b = image.getpixel((x, y))
            if r > r_border or g > g_border or b > b_border:
                if reverse:
                    r = 0
                    g = 0
                    b = 0
                else:
                    r = 255
                    g = 255
                    b = 255
            else:
                if reverse:
                    r = 255
                    g = 255
                    b = 255
                else:
                    r = 0
                    g = 0
                    b = 0
            binarized_image.putpixel((x, y), (r, g, b))

    return binarized_image
