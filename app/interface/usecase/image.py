from abc import ABCMeta, abstractmethod
from PIL import Image
from app.domain.image import CharacterDetailImage

class ImageUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def create_character_detail_image(self, image: Image) -> CharacterDetailImage:
        raise NotImplementedError
