import os
from logging import Logger

import cv2
import numpy as np
from PIL import Image

from app.domain.ability import (DistanceAbilities, FieldAbilities,
                                StrategiesAbilities)
from app.interface.driver.file_driver import LocalFileDriver
from app.interface.usecase.appropriate import AppropriateUsecase
from app.library.matching_template import matching_template
from app.library.pillow import crop_pil, pil2cv, resize_pil
from app.usecase.character import get_matching_template_location
from app.usecase.const import INPUT_IMAGE_WIDTH


class AbilityInteractor(AppropriateUsecase):

    def __init__(
            self,
            local_file_driver: LocalFileDriver,
            logger: Logger,
            *,
            debug=False):
        self.local_file_driver = local_file_driver
        self.logger = logger
        self.pattern_digital = r'\D'
        self.debug = debug
        self.cache_master_characters = None

    async def get_character_appropriate_fields_from_image(self, image: Image) -> FieldAbilities:
        """
        バ場適正を抽出する
        :param image:
        :return:
        """

        # TODO:画像の最適化は上のレイヤーで行う
        image = crop_pil(
            image,
            (0, image.size[1] * 0.1, image.size[0], image.size[1] * 0.5),
        )
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_character_appropriate_fields_from_image', 'init_image.png')
            )

        # optimize
        if image.size[0] != INPUT_IMAGE_WIDTH:
            image = resize_pil(image, INPUT_IMAGE_WIDTH)

        # load template
        params_frame_templ = await self.local_file_driver.open_image(
            os.path.join('resources', 'template_matching', 'character', 'template_1024.png')
        )

        # matching template
        params_frame_loc = await get_matching_template_location(image, params_frame_templ)
        if params_frame_loc is None:
            self.logger.debug('not found params_frame_loc')
            return FieldAbilities('', '')
        (start_x, start_y), (end_x, end_y) = params_frame_loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)
        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_appropriate_fields_from_image', 'multi_scale_matching_template.png')
            )

        abilities = dict()

        # ocr seed ability
        cropped_ability_turf = crop_pil(image,
                                        (start_x + (st_x * 0.315),
                                         end_y + (st_y * 2.8),
                                         start_x + (st_x * 0.37),
                                         end_y + (st_y * 4.2)))
        ability_turf = await self.get_ability_rank_from_image(cropped_ability_turf)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_turf,
                os.path.join('tmp', 'get_character_appropriate_fields_from_image', 'cropped_ability_turf.png')
            )

        # ダート
        cropped_ability_dirt = crop_pil(image,
                                        (start_x + (st_x * 0.515),
                                         end_y + (st_y * 2.8),
                                         start_x + (st_x * 0.57),
                                         end_y + (st_y * 4.2)))
        ability_dirt = await self.get_ability_rank_from_image(cropped_ability_dirt)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_dirt,
                os.path.join('tmp', 'get_character_appropriate_fields_from_image', 'cropped_ability_dirt.png')
            )

        return FieldAbilities(ability_turf, ability_dirt)

    async def get_character_appropriate_distances_from_image(self, image: Image) -> DistanceAbilities:
        """
                距離適正を抽出する
                :param image:
                :return:
                """

        # TODO:画像の最適化は上のレイヤーで行う
        image = crop_pil(
            image,
            (0, image.size[1] * 0.1, image.size[0], image.size[1] * 0.5),
        )
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_character_appropriate_distances_from_image', 'init_image.png')
            )

        # optimize
        if image.size[0] != INPUT_IMAGE_WIDTH:
            image = resize_pil(image, INPUT_IMAGE_WIDTH)

        # load template
        params_frame_templ = await self.local_file_driver.open_image(
            os.path.join('resources', 'template_matching', 'character', 'template_1024.png')
        )

        # matching template
        params_frame_loc = await get_matching_template_location(image, params_frame_templ)
        if params_frame_loc is None:
            self.logger.debug('not found params_frame_loc')
            return DistanceAbilities('', '', '', '')
        (start_x, start_y), (end_x, end_y) = params_frame_loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)
        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_appropriate_distances_from_image', 'multi_scale_matching_template.png')
            )

        # 短距離
        cropped_ability_short = crop_pil(image,
                                         (start_x + (st_x * 0.315),
                                          end_y + (st_y * 4.35),
                                          start_x + (st_x * 0.37),
                                          end_y + (st_y * 5.75)))
        ability_short = await self.get_ability_rank_from_image(cropped_ability_short)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_short,
                os.path.join('tmp', 'get_character_appropriate_distances_from_image', 'cropped_ability_short.png')
            )

        # マイル
        cropped_ability_miles = crop_pil(image,
                                         (start_x + (st_x * 0.515),
                                          end_y + (st_y * 4.35),
                                          start_x + (st_x * 0.57),
                                          end_y + (st_y * 5.75)))
        ability_miles = await self.get_ability_rank_from_image(cropped_ability_miles)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_miles,
                os.path.join('tmp', 'get_character_appropriate_distances_from_image', 'cropped_ability_mile.png')
            )

        # 中距離
        cropped_ability_medium = crop_pil(image,
                                          (start_x + (st_x * 0.715),
                                           end_y + (st_y * 4.35),
                                           start_x + (st_x * 0.77),
                                           end_y + (st_y * 5.75)))
        ability_medium = await self.get_ability_rank_from_image(cropped_ability_medium)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_medium,
                os.path.join('tmp', 'get_character_appropriate_distances_from_image', 'cropped_ability_medium.png')
            )

        # 長距離
        cropped_ability_long = crop_pil(image,
                                        (start_x + (st_x * 0.915),
                                         end_y + (st_y * 4.35),
                                         start_x + (st_x * 0.97),
                                         end_y + (st_y * 5.75)))
        ability_long = await self.get_ability_rank_from_image(cropped_ability_long)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_long,
                os.path.join('tmp', 'get_character_appropriate_distances_from_image', 'cropped_ability_long.png')
            )

        return DistanceAbilities(ability_short, ability_miles, ability_medium, ability_long)

    async def get_character_appropriate_strategies_from_image(self, image: Image) -> StrategiesAbilities:
        """
                脚質適正を抽出する
                :param image:
                :return:
                """

        # TODO:画像の最適化は上のレイヤーで行う
        image = crop_pil(
            image,
            (0, image.size[1] * 0.1, image.size[0], image.size[1] * 0.5),
        )
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_character_appropriate_strategies_from_image', 'init_image.png')
            )

        # optimize
        if image.size[0] != INPUT_IMAGE_WIDTH:
            image = resize_pil(image, INPUT_IMAGE_WIDTH)

        # load template
        params_frame_templ = await self.local_file_driver.open_image(
            os.path.join('resources', 'template_matching', 'character', 'template_1024.png')
        )

        # matching template
        params_frame_loc = await get_matching_template_location(image, params_frame_templ)
        if params_frame_loc is None:
            self.logger.debug('not found params_frame_loc')
            return StrategiesAbilities('', '', '', '')
        (start_x, start_y), (end_x, end_y) = params_frame_loc
        (st_x, st_y) = (end_x - start_x, end_y - start_y)
        if self.debug:
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_character_appropriate_strategies_from_image', 'multi_scale_matching_template.png')
            )

        # 逃げ
        cropped_ability_first = crop_pil(image,
                                         (start_x + (st_x * 0.315),
                                          end_y + (st_y * 5.9),
                                          start_x + (st_x * 0.37),
                                          end_y + (st_y * 7.3)))
        ability_first = await self.get_ability_rank_from_image(cropped_ability_first)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_first,
                os.path.join('tmp', 'get_character_appropriate_strategies_from_image', 'cropped_ability_first.png')
            )

        # 先行
        cropped_ability_half_first = crop_pil(image,
                                              (start_x + (st_x * 0.515),
                                               end_y + (st_y * 5.9),
                                               start_x + (st_x * 0.57),
                                               end_y + (st_y * 7.3)))
        ability_half_first = await self.get_ability_rank_from_image(cropped_ability_half_first)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_half_first,
                os.path.join('tmp', 'get_character_appropriate_strategies_from_image', 'cropped_ability_half_first.png')
            )

        # 差し
        cropped_ability_half_last = crop_pil(image,
                                              (start_x + (st_x * 0.715),
                                               end_y + (st_y * 5.9),
                                               start_x + (st_x * 0.77),
                                               end_y + (st_y * 7.3)))
        ability_half_last = await self.get_ability_rank_from_image(cropped_ability_half_last)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_half_last,
                os.path.join('tmp', 'get_character_appropriate_strategies_from_image', 'cropped_ability_half_last.png')
            )

        # 追込
        cropped_ability_last = crop_pil(image,
                                         (start_x + (st_x * 0.915),
                                          end_y + (st_y * 5.9),
                                          start_x + (st_x * 0.97),
                                          end_y + (st_y * 7.3)))
        ability_last = await self.get_ability_rank_from_image(cropped_ability_last)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_ability_last,
                os.path.join('tmp', 'get_character_appropriate_strategies_from_image', 'cropped_ability_last.png')
            )

        return StrategiesAbilities(ability_first, ability_half_first, ability_half_last, ability_last)

    async def get_ability_rank_from_image(self, image: Image) -> str or None:
        border = 0.9
        cv2_image = pil2cv(image)
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)

        rank_files = [
            ['s.png', 'S'],
            ['a.png', 'A'],
            ['b.png', 'B'],
            ['c.png', 'C'],
            ['d.png', 'D'],
            ['e.png', 'E'],
            ['f.png', 'F'],
            ['g.png', 'G'],
        ]

        for (rank_file, rank) in rank_files:
            templ_rank_file = await self.local_file_driver.open_image(
                os.path.join('resources', 'template_matching', 'ability', rank_file)
            )
            templ_rank_file = resize_pil(templ_rank_file, 38)
            cv2_templ_rank_file = pil2cv(templ_rank_file)
            cv2_templ_rank_file = cv2.cvtColor(
                cv2_templ_rank_file, cv2.COLOR_BGR2GRAY)
            result = matching_template(cv2_image, cv2_templ_rank_file)
            ys, _ = np.where(result >= border)

            if len(ys) > 0:
                return rank

        return None
