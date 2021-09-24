from dataclasses import dataclass


@dataclass(frozen=True)
class Character:
    name: str
    nickname: str

    def to_dict(self):
        return {
            'name': self.turf,
            'nickname': self.dirt,
        }
