import asyncio
import logging
import os

from multiprocessing import Pool
from PIL import Image

from app.driver.file_driver import LocalFileDriverImpl
from app.usecase.ability import AbilityInteractor
from app.usecase.character import CharacterInteractor
from app.usecase.skill_interactor import SkillInteractor
from app.usecase.status_interactor import StatusInteractor
from app.views.api import APIResource
from app.library.pillow import resize_pil
from app.usecase.const import INPUT_IMAGE_WIDTH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

status_usecase = StatusInteractor(
    LocalFileDriverImpl(''),
    logger,
)
character_usecase = CharacterInteractor(
    LocalFileDriverImpl(''),
    logger,
)
ability_usecase = AbilityInteractor(
    LocalFileDriverImpl(''),
    logger,
)
skill_usecase = SkillInteractor(
    LocalFileDriverImpl(''),
    logger,
)

def get_samples_ids():
    return os.listdir(path='./samples')

def get_sample_paths_from_id(id):
    file_names = os.listdir(path=f'./samples/{id}')
    file_names = sorted(file_names)
    paths = []
    for file_name in file_names:
        paths.append(f'./samples/{id}/{file_name}')
    return paths

def get_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_status(path):
    image = Image.open(path)
    image = resize_pil(image, INPUT_IMAGE_WIDTH)

    async def get_data():
        tasks = [
            asyncio.create_task(character_usecase.get_character_from_image(image)),
            asyncio.create_task(character_usecase.get_character_rank_from_image(image)),
            asyncio.create_task(status_usecase.get_parameters_from_image(image)),
            asyncio.create_task(skill_usecase.get_character_skills_from_character_modal_image(image)),
            asyncio.create_task(ability_usecase.get_character_appropriate_fields_from_image(image)),
            asyncio.create_task(ability_usecase.get_character_appropriate_distances_from_image(image)),
            asyncio.create_task(ability_usecase.get_character_appropriate_strategies_from_image(image)),
        ]
        results = await asyncio.gather(*tasks)

        character, character_rank, parameters, character_skills, ability_fields, ability_distances, ability_strategies = results
        character_skills_dict = character_skills.to_dict()
        return {
            'character': character.name,
            'nickname': character.nickname,
            'rank': character_rank,
            'params': parameters.to_dict(),
            'unique_skill': character_skills_dict['unique_skill'],
            'skills': character_skills_dict['normal_skills'],
            'abilities': {
                'fields': ability_fields.to_dict(),
                'distances': ability_distances.to_dict(),
                'strategies': ability_strategies.to_dict(),
            }
        }

    return asyncio.run(get_data())

def main():
    concurrency_count = 1
    chunks_num = 1

    ids = get_samples_ids()
    chunk_ids = list(get_chunks(ids, chunks_num))

    chunks_index = 0
    for ids in chunk_ids:
        chunks_index += 1
        print(f'chunks: {chunks_index}/{len(chunk_ids)}')

        paths = []
        for id in ids:
            paths.extend(get_sample_paths_from_id(id))
        with Pool(processes=concurrency_count) as p:
            result_list = p.map(func=get_status, iterable=paths)
        print(result_list)

main()