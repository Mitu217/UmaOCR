from dataclasses import dataclass


@dataclass(frozen=True)
class Parameters:
    speed: int
    stamina: int
    power: int
    guts: int
    wise: int

    def to_dict(self):
        return {
            'speed': self.speed,
            'stamina': self.stamina,
            'power': self.power,
            'guts': self.guts,
            'wise': self.wise,
        }
