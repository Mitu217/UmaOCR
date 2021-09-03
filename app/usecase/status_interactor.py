import os
import re
from logging import Logger

import numpy as np
from PIL import Image

from app.domain.parameters import Parameters, SupportParameters
from app.interface.driver.file_driver import LocalFileDriver
from app.interface.usecase.status_usecase import StatusUsecase
from app.library.matching_template import multi_scale_matching_template
from app.library.ocr import get_digit_with_single_text_line_and_eng_from_image
from app.library.pillow import binarized, crop_pil, pil2cv, resize_pil

TEMPLATE_WIDTH = 1024
TEMPLATE_HEIGHT = 100


class StatusInteractor(StatusUsecase):

    def __init__(self, local_file_driver: LocalFileDriver, logger: Logger, *, debug=False):
        self.local_file_driver = local_file_driver
        self.logger = logger
        self.pattern_digital = r'\D'
        self.debug = debug
        self.cache_master_skills_map_by_weight = None

    async def get_support_parameters_from_image(self, image: Image) -> SupportParameters:

        templ = await self.local_file_driver.open_image(
            os.path.join('resources', 'images', 'support_params', 'template.png')
        )
        (tW, tH) = templ.size
        cv2_templ = pil2cv(templ)

        cv2_image = pil2cv(image)

        # マルチスケールテンプレートマッチングでtemplateと一致する箇所の座標を抽出
        loc = multi_scale_matching_template(cv2_image, cv2_templ, np.linspace(1.0, 2.5, 10))
        if loc is None:
            return SupportParameters(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if self.debug:
            (start_x, start_y), (end_x, end_y) = loc
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_support_parameters_from_image', 'multi_scale_matching_template.png')
            )

        (start_x, start_y), (end_x, end_y) = loc

        h = (end_y - start_y) * 1.05
        w = (end_x - start_x) * 1.01
        o = w * 0.015
        p = w / 5
        lo = p * 0.38
        ro = p * 0
        lo2 = p * 0.5

        # 解像度が低いものは見ない
        self.logger.info(w)
        if w < 400:
            return SupportParameters(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        # パラメータ表示部分のcropped
        cropped_speed = crop_pil(image, (start_x - o + p * 0 + lo, end_y, start_x + p * 1 - ro, end_y + h * 1.05))
        binarized_speed = binarized(cropped_speed, 210)
        speed = await self.get_parameter_from_image(binarized_speed)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_speed, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_speed.png')
            )
        cropped_max_speed = crop_pil(image, (start_x - o + p * 0 + lo2, end_y + h, start_x + p * 1 - ro, end_y + h * 1.9))
        binarized_max_speed = binarized(cropped_max_speed, 210)
        max_speed = await self.get_parameter_from_image(binarized_max_speed)
        if len(max_speed) > 3:
            max_speed = max_speed[1:]
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_max_speed, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_max_speed.png')
            )

        cropped_stamina = crop_pil(image, (start_x + p * 1 + lo, end_y, start_x + p * 2 - ro, end_y + h * 1.05))
        binarized_stamina = binarized(cropped_stamina, 210)
        stamina = await self.get_parameter_from_image(binarized_stamina)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_stamina, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_stamina.png')
            )
        cropped_max_stamina = crop_pil(image, (start_x + p * 1 + lo2, end_y + h, start_x + p * 2 - ro, end_y + h * 1.9))
        binarized_max_stamina = binarized(cropped_max_stamina, 210)
        max_stamina = await self.get_parameter_from_image(binarized_max_stamina)
        if len(max_stamina) > 3:
            max_stamina = max_stamina[1:]
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_max_stamina, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_max_stamina.png')
            )

        cropped_power = crop_pil(image, (start_x + p * 2 + lo, end_y, start_x + p * 3 - ro, end_y + h * 1.05))
        binarized_power = binarized(cropped_power, 210)
        power = await self.get_parameter_from_image(binarized_power)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_power, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_power.png')
            )
        cropped_max_power = crop_pil(image, (start_x + p * 2 + lo2, end_y + h, start_x + p * 3 - ro, end_y + h * 1.9))
        binarized_max_power = binarized(cropped_max_power, 210)
        max_power = await self.get_parameter_from_image(binarized_max_power)
        if len(max_power) > 3:
            max_power = max_power[1:]
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_max_power, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_max_power.png')
            )

        cropped_guts = crop_pil(image, (start_x + p * 3 + lo, end_y, start_x + p * 4 - ro, end_y + h * 1.05))
        binarized_guts = binarized(cropped_guts, 210)
        guts = await self.get_parameter_from_image(binarized_guts)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_guts, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_guts.png')
            )
        cropped_max_guts = crop_pil(image, (start_x + p * 3 + lo2, end_y + h, start_x + p * 4 - ro, end_y + h * 1.9))
        binarized_max_guts = binarized(cropped_max_guts, 210)
        max_guts = await self.get_parameter_from_image(binarized_max_guts)
        if len(max_guts) > 3:
            max_guts = max_guts[1:]
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_max_guts, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_max_guts.png')
            )

        cropped_wise = crop_pil(image, (start_x + p * 4 + lo, end_y, start_x + p * 5 - ro, end_y + h * 1.05))
        binarized_wise = binarized(cropped_wise, 210)
        wise = await self.get_parameter_from_image(binarized_wise)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_wise, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_wise.png')
            )
        cropped_max_wise = crop_pil(image, (start_x + p * 4 + lo2, end_y + h, start_x + p * 5 - ro, end_y + h * 1.9))
        binarized_max_wise = binarized(cropped_max_wise, 210)
        max_wise = await self.get_parameter_from_image(binarized_max_wise)
        if len(max_wise) > 3:
            max_wise = max_wise[1:]
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_max_wise, os.path.join('tmp', 'get_support_parameters_from_image', 'cropped_max_wise.png')
            )

        return SupportParameters(
            int(speed),
            int(stamina),
            int(power),
            int(guts),
            int(wise),
            int(max_speed),
            int(max_stamina),
            int(max_power),
            int(max_guts),
            int(max_wise),
        )

    async def get_parameters_from_image(self, image: Image) -> Parameters:
        templ = await self.local_file_driver.open_image(
            os.path.join('resources', 'images', 'ocr_params', 'template_1024.png')
        )
        (tW, tH) = templ.size
        cv2_templ = pil2cv(templ)

        # 処理高速化のため、次の操作を行う
        #  * templateと画像のwidthを合わせる
        #  * パラメーターは画像上半分にしかないため、画像の下半分を捨てる
        image = resize_pil(image, tW)
        (iW, iH) = image.size
        image = crop_pil(image, (0, iH * 0.1, iW, iH * 0.5))
        cv2_image = pil2cv(image)
        if self.debug:
            await self.local_file_driver.save_image(
                image, os.path.join('tmp', 'get_parameters_from_image', 'init_image.png')
            )

        # マルチスケールテンプレートマッチングでtemplateと一致する箇所の座標を抽出
        loc = multi_scale_matching_template(cv2_image, cv2_templ, np.linspace(1.1, 1.5, 3))
        if loc is None:
            return Parameters(0, 0, 0, 0, 0)
        if self.debug:
            (start_x, start_y), (end_x, end_y) = loc
            await self.local_file_driver.save_image(
                crop_pil(image, (start_x, start_y, end_x, end_y)),
                os.path.join('tmp', 'get_parameters_from_image', 'multi_scale_matching_template.png')
            )

        (start_x, start_y), (end_x, end_y) = loc

        h = (end_y - start_y) * 2
        w = end_x - start_x
        p = w / 5
        lo = p * 0.365
        ro = p * 0.05

        # TODO: 並列化
        cropped_speed = crop_pil(image, (start_x + p * 0 + lo, end_y, start_x + p * 1 - ro, end_y + h))
        binarized_speed = binarized(cropped_speed, 210)
        speed = await self.get_parameter_from_image(binarized_speed)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_speed, os.path.join('tmp', 'get_parameters_from_image', 'cropped_speed.png')
            )
            await self.local_file_driver.save_image(
                binarized_speed, os.path.join('tmp', 'get_parameters_from_image', 'binarized_speed.png')
            )

        cropped_stamina = crop_pil(image, (start_x + p * 1 + lo, end_y, start_x + p * 2 - ro, end_y + h))
        binarized_stamina = binarized(cropped_stamina, 210)
        stamina = await self.get_parameter_from_image(binarized_stamina)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_stamina, os.path.join('tmp', 'get_parameters_from_image', 'cropped_stamina.png')
            )
            await self.local_file_driver.save_image(
                binarized_stamina, os.path.join('tmp', 'get_parameters_from_image', 'binarized_stamina.png')
            )

        cropped_power = crop_pil(image, (start_x + p * 2 + lo, end_y, start_x + p * 3 - ro, end_y + h))
        binarized_power = binarized(cropped_power, 210)
        power = await self.get_parameter_from_image(binarized_power)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_power, os.path.join('tmp', 'get_parameters_from_image', 'cropped_power.png')
            )
            await self.local_file_driver.save_image(
                binarized_power, os.path.join('tmp', 'get_parameters_from_image', 'binarized_power.png')
            )

        cropped_guts = crop_pil(image, (start_x + p * 3 + lo, end_y, start_x + p * 4 - ro, end_y + h))
        binarized_guts = binarized(cropped_guts, 210)
        guts = await self.get_parameter_from_image(binarized_guts)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_guts, os.path.join('tmp', 'get_parameters_from_image', 'cropped_guts.png')
            )
            await self.local_file_driver.save_image(
                binarized_guts, os.path.join('tmp', 'get_parameters_from_image', 'binarized_guts.png')
            )

        cropped_wise = crop_pil(image, (start_x + p * 4 + lo, end_y, start_x + p * 5 - ro, end_y + h))
        binarized_wise = binarized(cropped_wise, 210)
        wise = await self.get_parameter_from_image(binarized_wise)
        if self.debug:
            await self.local_file_driver.save_image(
                cropped_wise, os.path.join('tmp', 'get_parameters_from_image', 'cropped_wise.png')
            )
            await self.local_file_driver.save_image(
                binarized_wise, os.path.join('tmp', 'get_parameters_from_image', 'binarized_wise.png')
            )

        return Parameters(
            speed,
            stamina,
            power,
            guts,
            wise,
        )

    async def get_parameter_from_image(self, image: Image) -> int:
        digit_text = re.sub(self.pattern_digital, '', get_digit_with_single_text_line_and_eng_from_image(image))
        return digit_text or 0
