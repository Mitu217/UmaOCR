from abc import ABCMeta, abstractmethod

import PIL


class LocalFileDriver(metaclass=ABCMeta):
    @abstractmethod
    async def save_image(self, image: PIL.Image, path: str):
        raise NotImplementedError

    @abstractmethod
    async def open_image(self, path: str) -> PIL.Image:
        raise NotImplementedError

    @abstractmethod
    async def open(self, path: str):
        raise NotImplementedError
