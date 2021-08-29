import asyncio
import json
import os
import re
from concurrent import futures
from logging import Logger

import cv2
import Levenshtein
import numpy as np
from PIL import Image

import resources
from app.domain.skill import Skill, Skills
from app.interface.driver.file_driver import LocalFileDriver
from app.interface.usecase.skill_usecase import SkillUsecase
from app.library.matching_template import matching_template, multi_scale_matching_template_impl
from app.library.ocr import (
    get_digit_with_single_text_line_and_eng_from_image,
    get_line_box_with_single_text_line_and_jpn_from_image)
from app.library.pillow import binarized, crop_pil, pil2cv, resize_pil
from app.usecase import const

TEMPLATE_HEIGHT = 100


class SkillInteractor(SkillUsecase):

    def __init__(self, local_file_driver: LocalFileDriver, logger: Logger, *, debug=False):
        self.local_file_driver = local_file_driver
        self.logger = logger
        self.pattern_digital = r'\D'
        self.debug = debug
        self.cache_master_skills_map_by_weight = None
        self.cache_master_skills_map_by_type = None


    async def get_skills_without_unique_from_image(self, image: Image) -> Skills:
        skills = await self.get_skills_from_image(image)
        skills_dict_array = skills.to_dict_array()

        master_skills_map_by_type = await self.get_master_skills_map_by_type()
        unique_skills = master_skills_map_by_type['unique_skills']

        result = []
        for skill_dict in skills_dict_array:
            skill_name = skill_dict['name']
            skill_level = skill_dict['level']
            is_unique_skill = False
            for unique_skill in unique_skills:
                unique_skill_name = unique_skill['name']
                if unique_skill_name == skill_name and skill_level > 0:
                    is_unique_skill = True
            if is_unique_skill is False:
                result.append(Skill(skill_name, skill_level))

        return Skills(result)

    async def get_unique_skill_from_image(self, image: Image) -> Skill:
        skills = await self.get_skills_from_image(image)
        skills_dict_array = skills.to_dict_array()

        master_skills_map_by_type = await self.get_master_skills_map_by_type()
        unique_skills = master_skills_map_by_type['unique_skills']

        for skill_dict in skills_dict_array:
            skill_name = skill_dict['name']
            skill_level = skill_dict['level']
            for unique_skill in unique_skills:
                unique_skill_name = unique_skill['name']
                if unique_skill_name == skill_name and skill_level > 0:
                    return Skill(skill_name, skill_level)

        return Skill('', 0)

    async def get_skills_from_image(self, image: Image) -> Skills:
        # get skill_tab location
        skill_tab_loc = await self.get_skill_tab_location(image)
        if skill_tab_loc is None:
            return Skills([])
        (skill_tab_loc_sx, skill_tab_loc_sy), (skill_tab_loc_ex, skill_tab_loc_ey) = skill_tab_loc
        (st_w, st_h) = skill_tab_loc_ex - skill_tab_loc_sx, skill_tab_loc_ey - skill_tab_loc_sy

        # cropped skill_area by skill_tab location
        skill_area_box = (0, skill_tab_loc_ey, image.size[0], st_h * 20)
        image = crop_pil(image, skill_area_box)
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_skills_from_image', 'cropped_skill_area.png')
            )

        # get skill_frame locations
        skill_frame_locs = await self.get_skill_frame_locations(image)

        skills = []
        for i in range(len(skill_frame_locs)):
            skills.append(Skill('', 0))

        binarized_image = binarized(image, 130)

        def p(index: int):
            (start_x, start_y), (end_x, end_y) = skill_frame_locs[index]

            cropped_skill = crop_pil(binarized_image, (
                start_x + st_w * 0.07, start_y + st_h * 0.7, start_x + st_w * 0.435, end_y - st_h * 0.55))
            skill_name = asyncio.run(self.get_skill_name_from_image(cropped_skill))
            if skill_name is None or len(skill_name) == 0:
                # 文字列によって有効なしきい値が異なるので読み取れなければしきい値を上げてリトライ
                cropped_skill = crop_pil(binarized(image, 140), (
                    start_x + st_w * 0.07, start_y + st_h * 0.7, start_x + st_w * 0.435, end_y - st_h * 0.55))
                skill_name = asyncio.run(self.get_skill_name_from_image(cropped_skill))
            if skill_name is None or len(skill_name) == 0:
                # 文字列によって有効なしきい値が異なるので読み取れなければしきい値を上げてリトライ
                cropped_skill = crop_pil(binarized(image, 160), (
                    start_x + st_w * 0.07, start_y + st_h * 0.7, start_x + st_w * 0.435, end_y - st_h * 0.55))
                skill_name = asyncio.run(self.get_skill_name_from_image(cropped_skill))

            if self.debug:
                asyncio.run(self.local_file_driver.save_image(
                    cropped_skill,
                    os.path.join('tmp', 'get_skills_from_image', 'skill' + str(index + 1) + '_name_cropped.png')
                ))

            # 通常の文字認識では○と◎と識別が難しいので追加で検証
            if '◯' in skill_name:
                cropped_for_check_circle_image = crop_pil(binarized(image, 160), (
                    start_x + st_w * 0.07, start_y + st_h * 0.7, start_x + st_w * 0.435, end_y - st_h * 0.55))
                line_box = get_line_box_with_single_text_line_and_jpn_from_image(cropped_for_check_circle_image)
                if len(line_box) != 0:
                    (s_x, s_y), (e_x, e_y) = line_box[0].position
                    word_width = 25.3
                    cropped_circle_image = crop_pil(cropped_for_check_circle_image, (e_x - word_width, s_y - 2, e_x + 2, e_y + 2))
                    if self.debug:
                        asyncio.run(self.local_file_driver.save_image(
                            cropped_circle_image,
                            os.path.join('tmp', 'get_skills_from_image', 'circle_test_' + str(index + 1) + '_cropped.png')
                        ))

                    # 要調整
                    border = 0.6
                    cv2_image = pil2cv(cropped_circle_image)
                    cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
                    circle_files = [
                        ['single.png', '◯'],
                        ['double.png', '◎'],
                    ]
                    for (circle_file, circle) in circle_files:
                        templ_circle_file = asyncio.run(self.local_file_driver.open_image(
                            os.path.join(resources.__path__[0], 'circles', circle_file)
                        ))
                        templ_circle_file = resize_pil(templ_circle_file, 25)
                        cv2_templ_circle_file = pil2cv(templ_circle_file)
                        cv2_templ_circle_file = cv2.cvtColor(
                            cv2_templ_circle_file, cv2.COLOR_BGR2GRAY)
                        result = matching_template(cv2_image, cv2_templ_circle_file)
                        ys, _ = np.where(result >= border)
                        if len(ys) > 0:
                            skill_name = skill_name.replace('◯', circle)
                            break

            if index == 0:
                # Lvがあるのは固有スキル（index = 0）だけ
                cropped_level = crop_pil(binarized_image, (
                    start_x + st_w * 0.435, start_y + st_h * 0.7, start_x + st_w * 0.5, end_y - st_h * 0.6))
                skill_level = int(asyncio.run(self.get_skill_level_from_image(cropped_level)))

                if self.debug:
                    asyncio.run(self.local_file_driver.save_image(
                        cropped_level,
                        os.path.join('tmp', 'get_skills_from_image', 'skill' + str(index + 1) + '_level_cropped.png')
                    ))
            else:
                skill_level = 0

            skills[index] = Skill(skill_name, skill_level)

        future_list = []
        with futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for i in range(len(skill_frame_locs)):
                future = executor.submit(fn=p, index=i)
                future_list.append(future)
            _ = futures.as_completed(fs=future_list)

        return Skills(skills)

    async def get_skills_from_character_modal_image(self, image: Image) -> Skills:
        # resize image width to 1024px
        image = resize_pil(image, const.INPUT_IMAGE_WIDTH, None, Image.CUBIC)
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_skills_from_character_modal_image', 'resize_width_1024.png')
            )

        # rough adjust
        image = crop_pil(image, (0, image.size[1] * 0.4, image.size[0], image.size[1] * 0.95))
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_skills_from_character_modal_image', 'rough_adjust.png')
            )

        skills = await self.get_skills_from_image(image)
        return skills

    async def get_skill_tab_location(self, image: Image):
        # optimize
        if image.size[0] != const.INPUT_IMAGE_WIDTH:
            image = resize_pil(image, const.INPUT_IMAGE_WIDTH)

        templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'images', 'ocr_skills', 'template_skill_tab_w_1024.png')
        )
        (tW, tH) = templ.size

        multi_scale_matching_template_results = multi_scale_matching_template_impl(image, templ,
                                                                                   linspace=np.linspace(1.1, 1.5, 3))
        found = None
        for multi_scale_matching_template_result in multi_scale_matching_template_results:
            r = multi_scale_matching_template_result.ratio
            result = multi_scale_matching_template_result.result

            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        if found is None:
            self.logger.debug('not found get_skill_tab')
            return None

        (_, maxLoc, r) = found
        (start_x, start_y) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (end_x, end_y) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_skill_tab_location', 'multi_scale_matching_template.png')
            )

        return (start_x, start_y), (end_x, end_y)

    async def get_skill_frame_locations(self, image: Image):
        # optimize
        if image.size[0] != const.INPUT_IMAGE_WIDTH:
            image = resize_pil(image, const.INPUT_IMAGE_WIDTH)

        templ = await self.local_file_driver.open_image(
            os.path.join(resources.__path__[0], 'images', 'ocr_skills', 'template_skill_frame_h_100.png')
        )

        cv2_image = pil2cv(image)
        cv2_templ = pil2cv(templ)

        multi_scale_matching_template_results = multi_scale_matching_template_impl(cv2_image, cv2_templ,
                                                                                   linspace=np.linspace(1.0, 1.1, 3))

        start_locs = []
        locs = []

        for i in range(len(multi_scale_matching_template_results)):
            multi_scale_matching_template_result = multi_scale_matching_template_results[i]
            r = multi_scale_matching_template_result.ratio
            result = multi_scale_matching_template_result.result

            ys, xs = np.where(result >= 0.7)
            for x, y in zip(xs, ys):
                if len(start_locs) == 0:
                    start_locs.append((x, y))
                    locs.append((
                        (int(x * r), int(y * r)),
                        (int((x + cv2_templ.shape[1]) * r), int((y + cv2_templ.shape[0]) * r))
                    ))
                else:
                    _, (nearest_x, nearest_y) = func_search_neighbourhood(start_locs, np.array([x, y]))
                    if abs(x - nearest_x) < 100 and abs(y - nearest_y) < 80:
                        continue
                    else:
                        start_locs.append((x, y))
                        locs.append((
                            (int(x * r), int(y * r)),
                            (int((x + cv2_templ.shape[1]) * r), int((y + cv2_templ.shape[0]) * r))
                        ))

        if self.debug:
            dst = cv2_image.copy()
            for i in range(len(locs)):
                (start_x, start_y), (end_x, end_y) = locs[i]
                cv2.rectangle(
                    dst,
                    (start_x, start_y),
                    (end_x, end_y),
                    color=(255, 0, 0),
                    thickness=2,
                )
            cv2.imwrite(os.path.join('tmp', 'get_skill_frame_locations', 'multi_scale_matching_template2.png'), dst)

        # sort locations
        # 左上から右下へ向かってソートする
        sorted_locs = sorted(locs, key=lambda k: k[0][1])
        for i in range(int(len(sorted_locs) / 2)):
            if sorted_locs[i * 2][0][0] > sorted_locs[i * 2 + 1][0][0]:
                sorted_locs[i * 2 + 1], sorted_locs[i * 2] = sorted_locs[i * 2], sorted_locs[i * 2 + 1]

        return sorted_locs

    async def get_skill_name_from_image(self, image: Image) -> str or None:

        master_skills_map_by_weight = await self.get_master_skills_map_by_weight()

        line_box = get_line_box_with_single_text_line_and_jpn_from_image(image)
        if len(line_box) == 0:
            return None
        else:
            (s_x, s_y), (e_x, e_y) = line_box[0].position
            word_width = 25.5

            text = line_box[0].content.replace(' ', '')
            weight = int((e_x - s_x) / word_width + 1)

            if weight not in master_skills_map_by_weight:
                return None

            # master定義されているスキルネームと類似度を計算し、最も類似度が高いスキルを返す
            # OCRの限界で読み間違えが発生しがちな文字列でも類似度を計算する
            found_str = ''
            found = 0
            for master_skill in master_skills_map_by_weight[weight]:
                skill_name = master_skill['name']
                similar = master_skill['similar']

                aro_dist = Levenshtein.jaro_winkler(text, skill_name)
                if aro_dist > found:
                    found_str = skill_name
                    found = aro_dist

                for similar_skill_name in similar:
                    aro_dist = Levenshtein.jaro_winkler(text, similar_skill_name)
                    if aro_dist > found:
                        found_str = skill_name
                        found = aro_dist

            return found_str

    async def get_skill_level_from_image(self, image: Image) -> int:
        digit_text = re.sub(self.pattern_digital, '', get_digit_with_single_text_line_and_eng_from_image(image))
        return digit_text or 0

    async def get_master_skills_map_by_weight(self):
        if self.cache_master_skills_map_by_weight is not None:
            return self.cache_master_skills_map_by_weight

        result = dict()

        master_skills_json_file = await self.local_file_driver.open(
            os.path.join(resources.__path__[0], 'master_data', 'skills.json'))
        master_skills_json = json.load(master_skills_json_file)
        for master_skills in master_skills_json.values():
            for master_skill in master_skills[0:]:
                weight = master_skill['weight']
                if weight not in result:
                    result[weight] = []
                result[weight].append(master_skill)
        master_skills_json_file.close()

        self.cache_master_skills_map_by_weight = result
        return result

    async def get_master_skills_map_by_type(self):
        if self.cache_master_skills_map_by_type is not None:
            return self.cache_master_skills_map_by_type

        result = dict()

        master_skills_json_file = await self.local_file_driver.open(
            os.path.join(resources.__path__[0], 'master_data', 'skills.json'))
        master_skills_json = json.load(master_skills_json_file)
        for master_skill_items in master_skills_json.items():
            type = master_skill_items[0]
            if type not in result:
                result[type] = master_skill_items[1]
        master_skills_json_file.close()

        self.cache_master_skills_map_by_type = result
        return result


def func_search_neighbourhood(list, p0):
    ps = np.array(list)
    L = np.array([])
    for i in range(ps.shape[0]):
        norm = np.sqrt((ps[i][0] - p0[0]) * (ps[i][0] - p0[0]) +
                       (ps[i][1] - p0[1]) * (ps[i][1] - p0[1]))
        L = np.append(L, norm)
    return np.argmin(L), ps[np.argmin(L)]
