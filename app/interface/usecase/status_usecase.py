from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.parameters import Parameters, SupportParameters


class StatusUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_parameters_from_image(self, image: Image) -> Parameters:
        raise NotImplementedError

    @abstractmethod
    async def get_support_parameters_from_image(self, image: Image) -> SupportParameters:
        raise NotImplementedError

