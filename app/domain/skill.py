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
