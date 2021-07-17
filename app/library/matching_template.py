from dataclasses import dataclass
from logging import getLogger

import cv2
import numpy
from PIL import Image

from app.library.pillow import pil2cv


def matching_template(image, templ, *, method=cv2.TM_CCOEFF_NORMED):
    return cv2.matchTemplate(image, templ, method)


def multi_scale_matching_template(image,
                                  templ,
                                  linspace,
                                  *,
                                  method=cv2.TM_CCOEFF_NORMED,
                                  logger=None,
                                  debug=False):
    logger = logger or getLogger(__name__)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templ = cv2.cvtColor(templ, cv2.COLOR_BGR2GRAY)

    loc = _multi_scale_matching_template_impl(image,
                                              templ,
                                              linspace,
                                              method=method)

    return loc


def _multi_scale_matching_template_impl(image,
                                        templ,
                                        linspace,
                                        *,
                                        method=cv2.TM_CCOEFF_NORMED):
    (tH, tW) = templ.shape[:2]

    found = None
    for scale in linspace[::-1]:
        resized = resize(image, int(image.shape[1] * scale))
        r = image.shape[1] / float(resized.shape[1])

        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        result = matching_template(resized, templ, method=method)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)

    if found is None:
        return None

    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    return (startX, startY), (endX, endY)


@dataclass(frozen=True)
class MultiScaleMatchingTemplateResult:
    ratio: float
    result: []


def multi_scale_matching_template_impl(
        image: Image,
        templ: Image,
        *,
        linspace=numpy.linspace(1.0, 1.1, 10),
        method=cv2.TM_CCOEFF_NORMED,
):
    cv2_image = pil2cv(image)
    cv2_templ = pil2cv(templ)

    (tH, tW) = cv2_templ.shape[:2]

    gray_cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
    gray_cv2_templ = cv2.cvtColor(cv2_templ, cv2.COLOR_BGR2GRAY)

    results = []

    for scale in linspace[::-1]:
        resized = resize(gray_cv2_image, int(gray_cv2_image.shape[1] * scale))
        r = gray_cv2_image.shape[1] / float(resized.shape[1])

        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        result = matching_template(resized, gray_cv2_templ, method=method)
        results.append(MultiScaleMatchingTemplateResult(r, result))

    return results


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, inter)
