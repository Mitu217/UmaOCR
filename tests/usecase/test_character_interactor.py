import asyncio
import csv
import logging
import os
from unittest import TestCase

from PIL import Image

import resources
from app.domain.character import Character
from app.driver.file_driver import LocalFileDriverImpl
from app.usecase.character import CharacterInteractor
from app.library.pillow import crop_pil, resize_pil


class TestCharacterInteractor(TestCase):
    def test_get_character_nickname_from_image_and_name(self) -> None:
        for character_name, image_name, result_name in (
            ('アグネスタキオン', 'アグネスタキオン.png', 'アグネスタキオン.csv'),
            ('アグネスデジタル', 'アグネスデジタル.png', 'アグネスデジタル.csv'),
            ('ウイニングチケット', 'ウイニングチケット.png', 'ウイニングチケット.csv'),
            ('ウオッカ', 'ウオッカ.png', 'ウオッカ.csv'),
            ('スペシャルウィーク', 'スペシャルウィーク.png', 'スペシャルウィーク.csv'),
            ('スペシャルウィーク', 'スペシャルウィーク2.png', 'スペシャルウィーク2.csv'),
            ('マルゼンスキー', 'マルゼンスキー.png', 'マルゼンスキー.csv'),
            ('マルゼンスキー', 'マルゼンスキー2.png', 'マルゼンスキー2.csv'),
            ('エアグルーヴ', 'エアグルーヴ.png', 'エアグルーヴ.csv'),
            ('エアグルーヴ', 'エアグルーヴ2.png', 'エアグルーヴ2.csv'),
            ('マヤノトップガン', 'マヤノトップガン.png', 'マヤノトップガン.csv'),
            ('マヤノトップガン', 'マヤノトップガン2.png', 'マヤノトップガン2.csv'),
            ('マチカネフクキタル', 'マチカネフクキタル.png', 'マチカネフクキタル.csv'),
            ('マチカネフクキタル', 'マチカネフクキタル2.png', 'マチカネフクキタル2.csv'),
            ('トウカイテイオー', 'トウカイテイオー.png', 'トウカイテイオー.csv'),
            ('トウカイテイオー', 'トウカイテイオー2.png', 'トウカイテイオー2.csv'),
            ('メジロマックイーン', 'メジロマックイーン.png', 'メジロマックイーン.csv'),
            ('メジロマックイーン', 'メジロマックイーン2.png', 'メジロマックイーン2.csv'),
        ):
            with self.subTest(image_name=image_name):
                character_interactor = CharacterInteractor(
                    LocalFileDriverImpl(''),
                    logging.getLogger(__name__),
                )

                with Image.open(
                        os.path.join(resources.__path__[0], 'tests', 'characters', image_name)) as image:
                    optimized_resize_image = resize_pil(image, 1024, None, Image.LANCZOS)
                    got = asyncio.run(
                        character_interactor.get_character_nickname_from_image_and_name(optimized_resize_image, character_name))

                with open(
                        os.path.join(resources.__path__[0], 'tests', 'characters', result_name)) as result:
                    result_character_array = []
                    reader = csv.reader(result)
                    for row in reader:
                        result_character_array.append(Character(row[0], row[1]))
                    want = result_character_array[0].nickname
                self.assertEqual(got, want)
