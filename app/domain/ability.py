from dataclasses import dataclass


@dataclass(frozen=True)
class FieldAbilities:
    turf: str
    dirt: str

    def to_dict(self):
        return {
            'turf': self.turf,
            'dirt': self.dirt,
        }


@dataclass(frozen=True)
class DistanceAbilities:
    short: str
    miles: str
    medium: str
    long: str

    def to_dict(self):
        return {
            'short': self.short,
            'miles': self.miles,
            'medium': self.medium,
            'long': self.long,
        }
    
    
@dataclass(frozen=True)
class StrategiesAbilities:
    first: str
    half_first: str
    half_last: str
    last: str

    def to_dict(self):
        return {
            'first': self.first,
            'half_first': self.half_first,
            'half_last': self.half_last,
            'last': self.last,
        }
