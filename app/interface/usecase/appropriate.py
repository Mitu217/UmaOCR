from abc import ABCMeta, abstractmethod

from app.domain.ability import (DistanceAbilities, FieldAbilities,
                                StrategiesAbilities)
from app.domain.image import CharacterDetailImage


class AppropriateUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_character_appropriate_fields_from_image(self, image: CharacterDetailImage) -> FieldAbilities:
        raise NotImplementedError

    @abstractmethod
    async def get_character_appropriate_distances_from_image(self, image: CharacterDetailImage) -> DistanceAbilities:
        raise NotImplementedError

    @abstractmethod
    async def get_character_appropriate_strategies_from_image(self, image: CharacterDetailImage) -> StrategiesAbilities:
        raise NotImplementedError
