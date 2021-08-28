import asyncio

from flask import jsonify, make_response, request
from PIL import Image

from app.interface.usecase.appropriate import AppropriateUsecase
from app.interface.usecase.character import CharacterUsecase
from app.interface.usecase.skill_usecase import SkillUsecase
from app.interface.usecase.status_usecase import StatusUsecase
from app.library.pillow import crop_pil, resize_pil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class StatusResource:
    character_usecase: CharacterUsecase
    status_usecase: StatusUsecase
    ability_usecase: AppropriateUsecase
    skill_usecase: SkillUsecase

    def __init__(self,
                 status_usecase: StatusUsecase,
                 character_usecase: CharacterUsecase,
                 ability_usecase: AppropriateUsecase,
                 skill_usecase: SkillUsecase):
        self.status_usecase = status_usecase
        self.character_usecase = character_usecase
        self.ability_usecase = ability_usecase
        self.skill_usecase = skill_usecase

    def index(self):
        if 'file' not in request.files:
            return make_response(jsonify({'result': 'file is required'}), 400)

        file = request.files['file']
        if file.filename == '':
            return make_response(
                jsonify({'result': 'filename must not empty'}), 400)
        if not allowed_file(file.filename):
            return make_response(
                jsonify({'result': 'support extension jpg, jpeg or png'}), 400)

        image = Image.open(file.stream)

        # resize image width to 1024px
        optimized_resize_image = resize_pil(image, 1024, None, Image.LANCZOS)

        # rough adjust
        rough_adjusted_skill_area_image = crop_pil(optimized_resize_image, (0, optimized_resize_image.size[1] * 0.4, optimized_resize_image.size[0], optimized_resize_image.size[1] * 0.95))

        async def get_data():
            tasks = [
                asyncio.create_task(self.character_usecase.get_character_name_from_image(image)),
                asyncio.create_task(self.character_usecase.get_character_rank_from_image(image)),
                asyncio.create_task(self.status_usecase.get_parameters_from_image(image)),
                asyncio.create_task(self.skill_usecase.get_unique_skill_from_image(rough_adjusted_skill_area_image)),
                asyncio.create_task(self.skill_usecase.get_skills_without_unique_from_image(rough_adjusted_skill_area_image)),
                asyncio.create_task(self.ability_usecase.get_character_appropriate_fields_from_image(image)),
                asyncio.create_task(self.ability_usecase.get_character_appropriate_distances_from_image(image)),
                asyncio.create_task(self.ability_usecase.get_character_appropriate_strategies_from_image(image)),
            ]
            results = await asyncio.gather(*tasks)

            character_name, character_rank, parameters, unique_skill, skills, ability_fields, ability_distances, ability_strategies = results
            return {
                'character': character_name,
                'rank': character_rank,
                'params': parameters.to_dict(),
                'unique_skill': unique_skill.to_dict(),
                'skills': skills.to_dict_array(),
                'abilities': {
                    'fields': ability_fields.to_dict(),
                    'distances': ability_distances.to_dict(),
                    'strategies': ability_strategies.to_dict(),
                }
            }

        data = asyncio.run(get_data())

        return make_response(jsonify({'result': 'OK', 'data': data}), 200)
