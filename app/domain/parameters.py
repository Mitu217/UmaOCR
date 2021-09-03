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


@dataclass(frozen=True)
class SupportParameters:
    speed: int
    stamina: int
    power: int
    guts: int
    wise: int
    max_speed: int
    max_stamina: int
    max_power: int
    max_guts: int
    max_wise: int

    def to_dict(self):
        return {
            'speed': self.speed,
            'stamina': self.stamina,
            'power': self.power,
            'guts': self.guts,
            'wise': self.wise,
            'max_speed': self.max_speed,
            'max_stamina': self.max_stamina,
            'max_power': self.max_power,
            'max_guts': self.max_guts,
            'max_wise': self.max_wise,
        }
