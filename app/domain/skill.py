from dataclasses import dataclass

from app.domain.collection import Collection


@dataclass(frozen=True)
class NormalSkill:
    name: str
    level: int

    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
        }


@dataclass(frozen=True)
class NormalSkills(Collection[NormalSkill]):
    values: [NormalSkill]

    def to_dict_array(self):
        dict_array = []

        for value in self.values[0:]:
            dict_array.append(value.to_dict())

        return dict_array


@dataclass(frozen=True)
class UniqueSkill:
    name: str
    level: int

    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
        }

@dataclass(frozen=True)
class CharacterSkills:
    unique_skill: UniqueSkill
    normal_skills: NormalSkills

    def to_dict(self):
        return {
            'unique_skill': self.unique_skill.to_dict(),
            'normal_skills': self.normal_skills.to_dict_array(),
        }

