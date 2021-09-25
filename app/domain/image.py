from PIL import Image
from dataclasses import dataclass
from app.library.pillow import resize_pil

@dataclass(frozen=True)
class CharacterDetailImage:
    image: Image
    params_frame_loc: list
