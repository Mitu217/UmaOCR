import cv2
import numpy as np
from PIL import Image


def crop_pil(image, box, *, debug=False):
    cropped = image.crop(box)
    if debug:
        cropped.save('cropped.png')

    return cropped


def resize_pil(image, width=None, height=None, inter=Image.NEAREST):
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

    return image_pil


def pil2cv(image_pil):
    image_cv = np.asarray(image_pil)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
    return image_cv


def binarized(image: Image, threshold: int) -> Image:
    bin_img = image.convert("L")
    bin_img = bin_img.point(lambda x: 0 if x < threshold else 255)
    return bin_img
