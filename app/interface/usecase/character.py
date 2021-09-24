from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.character import Character

class CharacterUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_character_from_image(self, image: Image) -> Character:
        raise NotImplementedError

    @abstractmethod
    async def get_character_name_from_image(self, image: Image) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_character_rank_from_image(self, image: Image) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get_character_name_from_support_image(self, image: Image) -> str:
        raise NotImplementedError
