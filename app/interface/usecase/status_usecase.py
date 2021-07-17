from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.parameters import Parameters
from app.domain.skill import Skills


class StatusUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_parameters_from_image(self, image: Image) -> Parameters:
        raise NotImplementedError

    @abstractmethod
    async def get_skills_from_image(self, image: Image) -> Skills:
        raise NotImplementedError
