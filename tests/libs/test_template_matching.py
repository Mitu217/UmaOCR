import os

import cv2

from run.libs.matching_template import multi_scale_matching_template


class TestTemplateMatching:
    def test_template_matching(self):
        base_path = os.path.join('tests')
        src_path = os.path.join(base_path, 'resources', 'ocr', 'ocr_params',
                                'source.png')
        tmpl_path = os.path.join(base_path, 'resources', 'ocr', 'ocr_params',
                                 'template.png')
        res = multi_scale_matching_template(src_path, tmpl_path)

        # draw a bounding box around the detected result and display the image
        img = cv2.imread(src_path)
        cv2.rectangle(img, res[0], res[1], (0, 0, 255), 2)
        cv2.imwrite('res.png', img)

        assert res == ((47, 724), (1123, 765))
