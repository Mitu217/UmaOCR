import asyncio
import csv
import logging
import os
from unittest import TestCase

from PIL import Image

import resources
from app.domain.skill import CharacterSkills, NormalSkill, NormalSkills, UniqueSkill
from app.driver.file_driver import LocalFileDriverImpl
from app.usecase.skill_interactor import SkillInteractor
from app.library.pillow import crop_pil, resize_pil


class TestSkillInteractor(TestCase):
    def test_get_skills_from_image(self) -> None:
        for image_name, result_name in (
            ('image1.png', 'image1.csv'),
            ('image2.png', 'image2.csv'),
            ('image3.png', 'image3.csv'),
            ('image4.png', 'image4.csv'),
            ('image5.png', 'image5.csv'),
            ('image6.png', 'image6.csv'),
            ('image7.png', 'image7.csv'),
            ('image8.png', 'image8.csv'),
            ('image9.png', 'image9.csv'),
            ('image10.png', 'image10.csv'),
            ('image11.png', 'image11.csv'),
            ('image12.png', 'image12.csv'),
            ('image13.png', 'image13.csv'),
            ('image14.png', 'image14.csv'),
            ('image15.png', 'image15.csv'),
            ('image16.png', 'image16.csv'),
            ('image17.png', 'image17.csv'),
            ('image18.png', 'image18.csv'),
            ('image19.png', 'image19.csv'),
            ('image20.png', 'image20.csv'),
            ('image21.png', 'image21.csv'),
            ('image22.png', 'image22.csv'),
            ('image23.png', 'image23.csv'),
            ('image24.png', 'image24.csv'),
            ('image25.png', 'image25.csv'),
            ('image26.png', 'image26.csv'),
            ('image27.png', 'image27.csv'),
            ('image28.png', 'image28.csv'),
            ('image29.png', 'image29.csv'),
        ):
            with self.subTest(image_name=image_name):
                skill_interactor = SkillInteractor(
                    LocalFileDriverImpl(''),
                    logging.getLogger(__name__),
                )

                with Image.open(
                        os.path.join(resources.__path__[0], 'tests',
                                     'cropped_skills', image_name)) as image:
                    optimized_resize_image = resize_pil(image, 1024, None, Image.LANCZOS)
                    rough_adjusted_skill_area_image = crop_pil(optimized_resize_image, (0, optimized_resize_image.size[1] * 0.4, optimized_resize_image.size[0], optimized_resize_image.size[1] * 0.95))
                    got = asyncio.run(
                        skill_interactor.get_skills_from_image(rough_adjusted_skill_area_image))

                with open(
                        os.path.join(resources.__path__[0], 'tests',
                                     'cropped_skills', result_name)) as result:
                    result_skill_array = []
                    reader = csv.reader(result)
                    for row in reader:
                        result_skill_array.append(NormalSkill(row[0], int(row[1])))
                    want = NormalSkills(result_skill_array)

                self.assertEqual(got, want)

    def test_get_character_skills_from_character_modal_image_iphone_character_1(self):
        logger = logging.getLogger('TEST')
        skill_interactor = SkillInteractor(
            LocalFileDriverImpl(''),
            logger,
        )

        with Image.open(
                os.path.join(resources.__path__[0], 'tests', 'character_modal',
                             'iphone_character_1.png')) as image:
            got = asyncio.run(
                skill_interactor.get_character_skills_from_character_modal_image(image))

        want = CharacterSkills(
            UniqueSkill('カッティング×DRIVE！', 6),
            NormalSkills([
                NormalSkill('勝利の鼓動', 0),
                NormalSkill('汝、皇帝の神威を見よ', 0),
                NormalSkill('右回り◯', 0),
                NormalSkill('外枠得意◯', 0),
                NormalSkill('弧線のプロフェッサー', 0),
                NormalSkill('直線巧者', 0),
                NormalSkill('好転一息', 0),
                NormalSkill('注目の踊り子', 0),
                NormalSkill('抜け出し準備', 0),
                NormalSkill('差し駆け引き', 0),
                NormalSkill('先行ためらい', 0),
                NormalSkill('マイル直線◯', 0),
                NormalSkill('危険回避', 0),
            ]),
        )

        self.assertEqual(got, want)

    def test_get_character_skills_from_character_modal_image_iphone_character_2(self):
        logger = logging.getLogger('TEST')
        skill_interactor = SkillInteractor(
            LocalFileDriverImpl(''),
            logger,
        )

        with Image.open(
                os.path.join(resources.__path__[0], 'tests', 'character_modal',
                             'iphone_character_2.png')) as image:
            got = asyncio.run(
                skill_interactor.get_character_skills_from_character_modal_image(image))

        want = CharacterSkills(
            UniqueSkill('Call me KING', 1),
            NormalSkills([
                NormalSkill('カッティング×DRIVE！', 0),
                NormalSkill('末脚', 0),
                NormalSkill('がんばり屋', 0),
            ]),
        )

        self.assertEqual(got, want)

    def test_get_skill_tab_location(self):
        logger = logging.getLogger('TEST')
        skill_interactor = SkillInteractor(
            LocalFileDriverImpl(''),
            logger,
        )

        with Image.open(
                os.path.join(resources.__path__[0], 'tests', 'character_modal',
                             'iphone_character_1.png')) as image:
            got = asyncio.run(skill_interactor.get_skill_tab_location(image))

        want = ((42, 960), (973, 1008))

        self.assertEqual(got, want)
