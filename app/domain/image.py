from PIL import Image
from dataclasses import dataclass
from app.library.pillow import resize_pil

class CharacterDetailImage:
    def __init__(self, image: Image):
        self.raw_image = image

        # 画像処理に必要な共通情報をキャッシュ
        self.image = resize_pil(image, 1024)
