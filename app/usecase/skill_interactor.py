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
from app.library.matching_template import multi_scale_matching_template_impl
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

    async def get_skills_from_image(self, image: Image) -> Skills:
        # get skill_tab location
        skill_tab_loc = await self.get_skill_tab_location(image)
        if skill_tab_loc is None:
            return Skills([])
        (skill_tab_loc_sx, skill_tab_loc_sy), (skill_tab_loc_ex, skill_tab_loc_ey) = skill_tab_loc
        (st_w, st_h) = skill_tab_loc_ex - skill_tab_loc_sx, skill_tab_loc_ey - skill_tab_loc_sy

        # cropped skill_frame by skill_tab location
        skill_area_box = (0, skill_tab_loc_ey, image.size[0], st_h * 20)
        image = crop_pil(image, skill_area_box)
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_skills_from_image', 'cropped_skill_area.png')
            )

        skill_frame_locs = await self.get_skill_frame_locations(image)

        skills = []
        for i in range(len(skill_frame_locs)):
            skills.append(Skill('', 0))

        rgb_border = [150, 150, 150]

        def p(index: int):
            (start_x, start_y), (end_x, end_y) = skill_frame_locs[index]

            cropped_skill = crop_pil(image, (
                start_x + st_w * 0.07, start_y + st_h * 0.3, start_x + st_w * 0.435, end_y - st_h * 0.3))
            binarized_skill = binarized(cropped_skill, rgb_border[0], rgb_border[1], rgb_border[2])
            skill_name = asyncio.run(self.get_skill_name_from_image(binarized_skill))

            if self.debug:
                asyncio.run(self.local_file_driver.save_image(
                    cropped_skill,
                    os.path.join('tmp', 'get_skills_from_image', 'skill' + str(index + 1) + '_name_cropped.png')
                ))
                asyncio.run(self.local_file_driver.save_image(
                    binarized_skill,
                    os.path.join('tmp', 'get_skills_from_image', 'skill' + str(index + 1) + '_name_binarized.png')
                ))

            if index == 0:
                # Lvがあるのは固有スキル（index = 0）だけ
                cropped_level = crop_pil(image, (
                    start_x + st_w * 0.435, start_y + st_h * 0.3, start_x + st_w * 0.5, end_y - st_h * 0.3))
                binarized_level = binarized(cropped_level, rgb_border[0], rgb_border[1], rgb_border[2])
                skill_level = asyncio.run(self.get_skill_level_from_image(binarized_level))

                if self.debug:
                    asyncio.run(self.local_file_driver.save_image(
                        cropped_level,
                        os.path.join('tmp', 'get_skills_from_image', 'skill' + str(index + 1) + '_level_cropped.png')
                    ))
                    asyncio.run(self.local_file_driver.save_image(
                        binarized_level,
                        os.path.join('tmp', 'get_skills_from_image', 'skill' + str(index + 1) + '_level_binarized.png')
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
        image = resize_pil(image, const.INPUT_IMAGE_WIDTH)
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_skills_from_character_modal_image', 'resize_width_1024.png')
            )

        # rough adjust
        image = crop_pil(image, (0, image.size[1] * 0.4, image.size[0], image.size[1] * 0.9))
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
        cv2_image = pil2cv(image)
        cv2_templ = pil2cv(templ)

        multi_scale_matching_template_results = multi_scale_matching_template_impl(cv2_image, cv2_templ,
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
                                                                                   linspace=np.linspace(1.0, 1.1, 10))

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
            self.logger.info('[get_skill_name_from_image] skill_name: %s, weight: %d', text, weight)

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


def func_search_neighbourhood(list, p0):
    ps = np.array(list)
    L = np.array([])
    for i in range(ps.shape[0]):
        norm = np.sqrt((ps[i][0] - p0[0]) * (ps[i][0] - p0[0]) +
                       (ps[i][1] - p0[1]) * (ps[i][1] - p0[1]))
        L = np.append(L, norm)
    return np.argmin(L), ps[np.argmin(L)]