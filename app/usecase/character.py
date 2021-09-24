import json
import os
from logging import Logger

import cv2
import Levenshtein
import numpy as np
from PIL import Image

import resources
from app.interface.driver.file_driver import LocalFileDriver
from app.interface.usecase.character import CharacterUsecase
from app.library.matching_template import (matching_template, multi_scale_matching_template, multi_scale_matching_template_impl)
from app.library.ocr import get_text_with_single_text_line_and_jpn_from_image
from app.library.pillow import binarized, crop_pil, pil2cv, resize_pil
from app.domain.character import Character

TEMPLATE_WIDTH = 1024


class CharacterInteractor(CharacterUsecase):

    def __init__(self, local_file_driver: LocalFileDriver, logger: Logger, *, debug=False):
        self.local_file_driver = local_file_driver
        self.logger = logger
        self.pattern_digital = r'\D'
        self.debug = debug
        self.cache_master_characters = None

    async def get_master_characters(self):
        if self.cache_master_characters is not None:
            return self.cache_master_characters

        master_characters_json_file = await self.local_file_driver.open(
            os.path.join(resources.__path__[0], 'master_data', 'characters.json'))
        master_characters_json = json.load(master_characters_json_file)

        self.cache_master_characters = master_characters_json
        return master_characters_json or []

    async def get_master_all_characters(self):
        if self.cache_master_characters is not None:
            return self.cache_master_characters

        master_characters_json_file = await self.local_file_driver.open(
            os.path.join(resources.__path__[0], 'master_data', 'all_characters.json'))
        master_characters_json = json.load(master_characters_json_file)

        self.cache_master_characters = master_characters_json
        return master_characters_json or []

    async def get_character_from_image(self, image: Image) -> Character:
        name = await self.get_character_name_from_image(image)
        nickname = await self.get_character_nickname_from_image_and_name(image, name)
        return Character(name, nickname)

    async def get_character_nickname_from_image_and_name(self, image: Image, name: str) -> str:
        # 処理高速化のため、次の操作を行う
        #  * templateと画像のwidthを合わせる
        #  * パラメーターとキャラクター名は画像上半分にしかないため、画像の下半分を捨てる
        image = resize_pil(image, TEMPLATE_WIDTH)
        image = crop_pil(
            image,
            (0,
             image.size[1] *
             0.1,
             image.size[0],
             image.size[1] *
             0.5))
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_character_nickname_from_image_and_name', 'init_image.png')
            )

        parameter_frame_templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'images', 'ocr_params', 'template_1024.png')
        )
        parameter_frame_loc = await get_matching_template_location(image, parameter_frame_templ)
        if parameter_frame_loc is None:
            self.logger.debug('not found parameter_frame_loc')
            return ''
        (start_x, start_y), (end_x, end_y) = parameter_frame_loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)

        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_nickname_from_image_and_name', 'multi_scale_matching_template.png')
            )

        cropped_character_nickname = crop_pil(image,
                                          (start_x + (st_x * 0.5),
                                           start_y - (st_y * 6.25),
                                           end_x - (st_x * 0.05),
                                           start_y - (st_y * 5.15)))
        binarized_character_nickname = binarized(cropped_character_nickname, 150)
        text = get_text_with_single_text_line_and_jpn_from_image(binarized_character_nickname)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_character_nickname,
                os.path.join('tmp', 'get_character_nickname_from_image_and_name', 'cropped_character_nickname.png')
            )
            await self.local_file_driver.save_image(
                binarized_character_nickname,
                os.path.join('tmp', 'get_character_nickname_from_image_and_name', 'binarized_character_nickname.png')
            )

        master_characters = await self.get_master_characters()
        found_str = ''
        found = 0
        border_found = 0.5
        for master_character in master_characters:
            if name == master_character['name']:
                for character_nickname in master_character['nickname']:
                    aro_dist = Levenshtein.jaro_winkler(text, character_nickname)
                    if aro_dist > found and aro_dist > border_found:
                        found_str = character_nickname
                        found = aro_dist

        return found_str

    async def get_character_name_from_image(self, image: Image) -> str:
        """
        画像内のパラメーターの位置から、キャラクター名を取得する
        :param image:
        :return:
        """

        # 処理高速化のため、次の操作を行う
        #  * templateと画像のwidthを合わせる
        #  * パラメーターとキャラクター名は画像上半分にしかないため、画像の下半分を捨てる
        image = resize_pil(image, TEMPLATE_WIDTH)
        image = crop_pil(
            image,
            (0,
             image.size[1] *
             0.1,
             image.size[0],
             image.size[1] *
             0.5))
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_character_name_from_image', 'init_image.png')
            )

        parameter_frame_templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'images', 'ocr_params', 'template_1024.png')
        )
        parameter_frame_loc = await get_matching_template_location(image, parameter_frame_templ)
        if parameter_frame_loc is None:
            self.logger.debug('not found parameter_frame_loc')
            return ''
        (start_x, start_y), (end_x, end_y) = parameter_frame_loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)

        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_name_from_image', 'multi_scale_matching_template.png')
            )

        cropped_character_name = crop_pil(image,
                                          (start_x + (st_x * 0.5),
                                           start_y - (st_y * 5.25),
                                              end_x - (st_x * 0.05),
                                              start_y - (st_y * 4.15)))
        binarized_character_name = binarized(
            cropped_character_name, 150)
        text = get_text_with_single_text_line_and_jpn_from_image(
            binarized_character_name)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_character_name, os.path.join('tmp', 'get_character_name_from_image', 'cropped_character_name.png')
            )
            await self.local_file_driver.save_image(
                binarized_character_name, os.path.join('tmp', 'get_character_name_from_image', 'binarized_character_name.png')
            )

        # 類似度が高いキャラクター名を返す
        master_characters = await self.get_master_characters()
        found_str = ''
        found = 0
        for master_character in master_characters:
            character_name = master_character['name']
            aro_dist = Levenshtein.jaro_winkler(text, character_name)
            if aro_dist > found:
                found_str = character_name
                found = aro_dist

        return found_str

    async def get_character_rank_from_image(self, image: Image) -> str:
        """
        画像内のパラメーターの位置から、キャラクターのランクを取得する
        :param image:
        :return:
        """

        # 処理高速化のため、次の操作を行う
        #  * templateと画像のwidthを合わせる
        #  * パラメーターとキャラクター名は画像上半分にしかないため、画像の下半分を捨てる
        image = resize_pil(image, TEMPLATE_WIDTH)
        image = crop_pil(
            image,
            (0,
             image.size[1] *
             0.1,
             image.size[0],
             image.size[1] *
             0.5))
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_character_rank_from_image', 'init_image.png')
            )

        parameter_frame_templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'images', 'ocr_params', 'template_1024.png')
        )
        parameter_frame_loc = await get_matching_template_location(image, parameter_frame_templ)
        if parameter_frame_loc is None:
            self.logger.debug('not found parameter_frame_loc')
            return ''
        (start_x, start_y), (end_x, end_y) = parameter_frame_loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)

        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_rank_from_image', 'multi_scale_matching_template.png')
            )

        cropped_character_rank = crop_pil(image,
                                          (start_x + (st_x * 0.325),
                                           start_y - (st_y * 7),
                                              end_x - (st_x * 0.515),
                                              start_y - (st_y * 3.4)))
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_character_rank,
                os.path.join('tmp', 'get_character_rank_from_image', 'cropped_character_rank.png')
            )

        # 要調整
        border = 0.8
        cv2_image = pil2cv(cropped_character_rank)
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)

        rank_files = [
            ['s_plus.png', 'S+'],
            ['s.png', 'S'],
            ['a_plus.png', 'A+'],
            ['a.png', 'A'],
            ['b_plus.png', 'B+'],
            ['b.png', 'B'],
            ['c_plus.png', 'C+'],
            ['c.png', 'C'],
            ['d_plus.png', 'D+'],
            ['d.png', 'D'],
            ['e_plus.png', 'E+'],
            ['e.png', 'E'],
            ['f_plus.png', 'F+'],
            ['f.png', 'F'],
            ['g_plus.png', 'G+'],
        ]
        for (rank_file, rank) in rank_files:
            templ_rank_file = await self.local_file_driver.open_image(
                os.path.join(resources.__path__[0], 'ranks', rank_file)
            )
            templ_rank_file = resize_pil(templ_rank_file, 120)
            cv2_templ_rank_file = pil2cv(templ_rank_file)
            cv2_templ_rank_file = cv2.cvtColor(
                cv2_templ_rank_file, cv2.COLOR_BGR2GRAY)
            result = matching_template(cv2_image, cv2_templ_rank_file)
            ys, _ = np.where(result >= border)
            if len(ys) > 0:
                return rank

        return ''

    async def get_character_name_from_support_image(self, image: Image) -> str:
        templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'images', 'support_params', 'template.png')
        )
        (tW, tH) = templ.size
        cv2_templ = pil2cv(templ)

        image = resize_pil(image, TEMPLATE_WIDTH)
        cv2_image = pil2cv(image)

        # マルチスケールテンプレートマッチングでtemplateと一致する箇所の座標を抽出
        loc = multi_scale_matching_template(cv2_image, cv2_templ, np.linspace(1.0, 1.5, 10))
        if loc is None:
            return ''
        if self.debug:
            (start_x, start_y), (end_x, end_y) = loc
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_name_from_support_image', 'multi_scale_matching_template.png')
            )

        (start_x, start_y), (end_x, end_y) = loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)

        border_found = 0.8

        # for guest
        cropped_character_name = crop_pil(image, (start_x + (st_x * 0.2), start_y - (st_y * 7), end_x - (st_x * 0.3), start_y - (st_y * 5.7)))
        binarized_character_name = binarized(
            cropped_character_name, 150)
        text = get_text_with_single_text_line_and_jpn_from_image(
            binarized_character_name)
        if self.debug:
            await self.local_file_driver.save_image(
                binarized_character_name,
                os.path.join('tmp', 'get_character_name_from_support_image', 'cropped_character_name.png')
            )

        # 類似度が高いキャラクター名を返す
        master_characters = await self.get_master_all_characters()
        found_str = ''
        found = 0
        for master_character in master_characters:
            character_name = master_character['name']
            aro_dist = Levenshtein.jaro_winkler(text, character_name)
            if aro_dist > found and aro_dist > border_found:
                found_str = character_name
                found = aro_dist

        if found == 0:
            # for other
            cropped_character_name = crop_pil(image, (
            start_x + (st_x * 0.2), start_y - (st_y * 11.5), end_x - (st_x * 0.3), start_y - (st_y * 10.2)))
            binarized_character_name = binarized(
                cropped_character_name, 150)
            text = get_text_with_single_text_line_and_jpn_from_image(
                binarized_character_name)
            if self.debug:
                await self.local_file_driver.save_image(
                    binarized_character_name,
                    os.path.join('tmp', 'get_character_name_from_support_image', 'cropped_character_name.png')
                )

            # 類似度が高いキャラクター名を返す
            master_characters = await self.get_master_all_characters()
            found_str = ''
            found = 0
            for master_character in master_characters:
                character_name = master_character['name']
                aro_dist = Levenshtein.jaro_winkler(text, character_name)
                if aro_dist > found and aro_dist > border_found:
                    found_str = character_name
                    found = aro_dist

        return found_str


async def get_matching_template_location(image: Image, templ: Image, *, linspace=np.linspace(1.1, 1.5, 10)):
    if image.size[0] != TEMPLATE_WIDTH:
        image = resize_pil(image, TEMPLATE_WIDTH)
    if templ.size[0] != TEMPLATE_WIDTH:
        templ = resize_pil(templ, TEMPLATE_WIDTH)

    (tW, tH) = templ.size
    cv2_image = pil2cv(image)
    cv2_templ = pil2cv(templ)

    multi_scale_matching_template_results = multi_scale_matching_template_impl(
        cv2_image, cv2_templ, linspace=linspace)

    found = None
    for multi_scale_matching_template_result in multi_scale_matching_template_results:
        r = multi_scale_matching_template_result.ratio
        result = multi_scale_matching_template_result.result

        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)

    if found is None:
        return None

    (_, maxLoc, r) = found
    (start_x, start_y) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (end_x, end_y) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    return (start_x, start_y), (end_x, end_y)
