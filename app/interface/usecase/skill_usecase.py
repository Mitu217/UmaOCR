from abc import ABCMeta, abstractmethod

from PIL import Image

from app.domain.skill import CharacterSkills, NormalSkill, NormalSkills


class SkillUsecase(metaclass=ABCMeta):
    @abstractmethod
    async def get_character_skills_from_character_modal_image(self, image: Image) -> CharacterSkills:
        raise NotImplementedError
