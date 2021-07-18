import asyncio
import logging
import os
from unittest import TestCase

from PIL import Image

import resources
from app.domain.skill import Skill, Skills
from app.driver.file_driver import LocalFileDriverImpl
from app.usecase.skill_interactor import SkillInteractor


class TestStatusInteractor(TestCase):
    def test_get_skills_from_character_modal_image_iphone_character_1(self):
        logger = logging.getLogger('TEST')
        skill_interactor = SkillInteractor(
            LocalFileDriverImpl(''),
            logger,
        )

        with Image.open(
                os.path.join(resources.__path__[0], 'tests', 'character_modal',
                             'iphone_character_1.png')) as image:
            got = asyncio.run(
                skill_interactor.get_skills_from_character_modal_image(image))

        want = Skills([
            Skill('カッティング×DRIVE！', 6),
            Skill('勝利の鼓動', 0),
            Skill('汝、皇帝の神威を見よ', 0),
            Skill('右回り◯', 0),
            Skill('外枠得意◯', 0),
            Skill('弧線のプロフェッサー', 0),
            Skill('直線巧者', 0),
            Skill('好転一息', 0),
            Skill('注目の踊り子', 0),
            Skill('抜け出し準備', 0),
            Skill('差し駆け引き', 0),
            Skill('先行ためらい', 0),
            Skill('マイル直線◯', 0),
            Skill('危険回避', 0),
        ])

        if got == want:
            assert True
        else:
            logger.error('got: {}, want: {}', got, want)
            assert False

    def test_get_skills_from_character_modal_image_iphone_character_2(self):
        logger = logging.getLogger('TEST')
        skill_interactor = SkillInteractor(
            LocalFileDriverImpl(''),
            logger,
        )

        with Image.open(
                os.path.join(resources.__path__[0], 'tests', 'character_modal',
                             'iphone_character_2.png')) as image:
            got = asyncio.run(
                skill_interactor.get_skills_from_character_modal_image(image))

        want = Skills([
            Skill('Call me KING', 1),
            Skill('カッティング×DRIVE！', 0),
            Skill('末脚', 0),
            Skill('がんばり屋', 0),
        ])

        if got == want:
            assert True
        else:
            logger.error('got: {}, want: {}', got, want)
            assert False
