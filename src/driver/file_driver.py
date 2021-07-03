import os

from PIL import Image

from src.interface.driver.file_driver import LocalFileDriver


class LocalFileDriverImpl(LocalFileDriver):
    root: str

    def __init__(self, root: str):
        self.root = root

    async def save_image(self, image: Image, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return image.save(os.path.join(self.root, path))

    async def open_image(self, path: str) -> Image:
        return Image.open(os.path.join(self.root, path))

    async def open(self, path: str):
        return open(os.path.join(self.root, path), 'r')
