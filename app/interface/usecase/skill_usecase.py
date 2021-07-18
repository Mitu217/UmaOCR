from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.skill import Skills


class SkillUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_skills_from_character_modal_image(self, image: Image) -> Skills:
        raise NotImplementedError
