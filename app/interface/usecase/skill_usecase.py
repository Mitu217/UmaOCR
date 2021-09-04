from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.skill import CharacterSkills, NormalSkill, NormalSkills


class SkillUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_character_skills_from_character_modal_image(self, image: Image) -> CharacterSkills:
        raise NotImplementedError

    @abstractmethod
    async def get_skills_without_unique_from_image(self, image: Image) -> NormalSkills:
        raise NotImplementedError

    @abstractmethod
    async def get_unique_skill_from_image(self, image: Image) -> NormalSkill:
        raise NotImplementedError
