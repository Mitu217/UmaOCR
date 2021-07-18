import pyocr
from PIL import Image

tools = pyocr.get_available_tools()
tool = tools[0]


def get_digit_with_single_text_line_and_eng_from_image(image: Image):
    builder = pyocr.builders.DigitBuilder(tesseract_layout=7)
    text = tool.image_to_string(image, lang="eng", builder=builder)

    return text


def get_text_with_single_text_line_and_jpn_from_image(image: Image):
    builder = pyocr.builders.TextBuilder(tesseract_layout=7)
    text = tool.image_to_string(image, lang="jpn", builder=builder)

    return text


def get_text_with_single_text_line_and_eng_from_image(image: Image):
    builder = pyocr.builders.TextBuilder(tesseract_layout=7)
    text = tool.image_to_string(image, lang="eng", builder=builder)

    return text


def get_line_box_with_single_text_line_and_jpn_from_image(image: Image):
    builder = pyocr.builders.LineBoxBuilder(tesseract_layout=6)
    text = tool.image_to_string(image, lang="jpn", builder=builder)

    return text
