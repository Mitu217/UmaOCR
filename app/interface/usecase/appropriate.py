from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.ability import (DistanceAbilities, FieldAbilities,
                                StrategiesAbilities)


class AppropriateUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_character_appropriate_fields_from_image(self, image: Image) -> FieldAbilities:
        raise NotImplementedError

    @abstractmethod
    async def get_character_appropriate_distances_from_image(self, image: Image) -> DistanceAbilities:
        raise NotImplementedError

    @abstractmethod
    async def get_character_appropriate_strategies_from_image(self, image: Image) -> StrategiesAbilities:
        raise NotImplementedError
