import asyncio

from flask import jsonify, make_response, request
from PIL import Image

from app.interface.usecase.appropriate import AppropriateUsecase
from app.interface.usecase.character import CharacterUsecase
from app.interface.usecase.skill_usecase import SkillUsecase
from app.interface.usecase.status_usecase import StatusUsecase

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class StatusResource:
    character_usecase: CharacterUsecase
    status_usecase: StatusUsecase
    ability_usecase: AppropriateUsecase
    skill_usecase: SkillUsecase

    def __init__(self, status_usecase: StatusUsecase,
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
        character_name = asyncio.run(
            self.character_usecase.get_character_name_from_image(image))
        character_rank = asyncio.run(
            self.character_usecase.get_character_rank_from_image(image))
        ability_fields = asyncio.run(
            self.ability_usecase.get_character_appropriate_fields_from_image(image))
        ability_distances = asyncio.run(
            self.ability_usecase.get_character_appropriate_distances_from_image(image))
        ability_strategies = asyncio.run(
            self.ability_usecase.get_character_appropriate_strategies_from_image(image))
        parameters = asyncio.run(
            self.status_usecase.get_parameters_from_image(image))
        skills = asyncio.run(self.skill_usecase.get_skills_from_character_modal_image(image))

        data = {
            'character': character_name,
            'rank': character_rank,
            'params': parameters.to_dict(),
            'skills': skills.to_dict_array(),
            'abilities': {
                'fields': ability_fields.to_dict(),
                'distances': ability_distances.to_dict(),
                'strategies': ability_strategies.to_dict(),
            }
        }
        return make_response(jsonify({'result': 'OK', 'data': data}), 200)
