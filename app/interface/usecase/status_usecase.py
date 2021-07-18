from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.parameters import Parameters


class StatusUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_parameters_from_image(self, image: Image) -> Parameters:
        raise NotImplementedError
