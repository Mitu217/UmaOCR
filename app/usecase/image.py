import json
import os
from logging import Logger

from PIL import Image

import resources
from app.interface.driver.file_driver import LocalFileDriver
from app.interface.usecase.image import ImageUsecase
from app.domain.image import CharacterDetailImage
from app.library.pillow import resize_pil
from app.usecase.character import get_matching_template_location

class ImageInteractor(ImageUsecase):

    def __init__(self, local_file_driver: LocalFileDriver, logger: Logger, *, debug=False):
        self.local_file_driver = local_file_driver
        self.logger = logger
        self.debug = debug

    async def create_character_detail_image(self, image: Image) -> CharacterDetailImage:
        character_detail_image_width = 1024

        resized_image = resize_pil(image, character_detail_image_width)

        params_frame_templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'template_matching', 'character', 'template_1024.png')
        )
        params_frame_loc = await get_matching_template_location(image, params_frame_templ)

        return CharacterDetailImage(
            resized_image,
            params_frame_loc,
        )